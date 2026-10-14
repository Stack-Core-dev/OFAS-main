package com.ofas.data.sync

import android.content.Context
import android.util.Log
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequest
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.ofas.data.database.OFASDatabase
import com.ofas.data.model.VisitEntity
import com.ofas.data.repository.VisitRepository
import com.ofas.data.trail.SurveyorLocationUploader
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.concurrent.TimeUnit

class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        private const val TAG = "SyncWorker"

        // Tag every sync request carries so the UI can observe all of them,
        // regardless of whether they were triggered periodically or on demand.
        const val WORK_NAME = "periodic_sync"

        // Unique names must differ between the periodic worker and the on-demand
        // worker: sharing one name would let the one-time request replace (and
        // cancel) the periodic schedule.
        private const val PERIODIC_WORK_NAME = "periodic_sync_worker"
        private const val ONE_TIME_WORK_NAME = "sync_now_worker"

        fun schedulePeriodicSync(context: Context) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
            val request = PeriodicWorkRequest.Builder(
                SyncWorker::class.java,
                1,
                TimeUnit.HOURS
            )
                .setConstraints(constraints)
                .addTag(WORK_NAME)
                .build()
            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                PERIODIC_WORK_NAME,
                ExistingPeriodicWorkPolicy.UPDATE,
                request
            )
        }

        fun cancelPeriodicSync(context: Context) {
            WorkManager.getInstance(context).cancelUniqueWork(PERIODIC_WORK_NAME)
        }

        fun enqueueNow(context: Context) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
            val request = androidx.work.OneTimeWorkRequest.Builder(SyncWorker::class.java)
                .setConstraints(constraints)
                .addTag(WORK_NAME)
                .build()
            WorkManager.getInstance(context).enqueueUniqueWork(
                ONE_TIME_WORK_NAME,
                androidx.work.ExistingWorkPolicy.KEEP,
                request
            )
        }
    }

    private val gson = Gson()

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val tokenStore = AuthTokenStore(applicationContext)
        var token = tokenStore.accessToken()
            ?: return@withContext Result.success()
        val database = OFASDatabase.getInstance(applicationContext)
        val repository = VisitRepository(database.visitDao())
        val api = ApiServiceFactory.create()

        var retry = false
        for (visit in repository.getPendingSync()) {
            if (repository.markSyncing(visit.id) == 0) continue
            try {
                var response = api.submitVisit("Bearer $token", visit.toRequest(gson))
                if (response.code() == 401) {
                    refreshSession(tokenStore, api)?.let { refreshed ->
                        token = refreshed
                        response = api.submitVisit("Bearer $token", visit.toRequest(gson))
                    }
                }
                if (response.isSuccessful && response.body()?.success == true) {
                    repository.markSynced(visit.id, System.currentTimeMillis())
                } else {
                    repository.markFailed(visit.id)
                    retry = response.code() >= 500 || response.code() == 429 || response.code() == 401
                    Log.w(TAG, "Visit ${visit.visitId} rejected with HTTP ${response.code()}")
                }
            } catch (error: Exception) {
                repository.markFailed(visit.id)
                retry = true
                Log.e(TAG, "Visit ${visit.visitId} sync failed", error)
            }
        }

        // Flush any trail location pings captured while offline (e.g. when the
        // trail foreground service was not running). Safe to run alongside the
        // service: the backend dedupes on (surveyor_id, recorded_at).
        if (!SurveyorLocationUploader.uploadPending(applicationContext)) {
            retry = true
        }

        if (retry) Result.retry() else Result.success()
    }

    private suspend fun refreshSession(tokenStore: AuthTokenStore, api: ApiService): String? {
        val refresh = tokenStore.refreshToken() ?: return null
        return try {
            val response = api.refreshToken("Bearer $refresh")
            val body = response.body()
            if (response.isSuccessful && body != null) {
                tokenStore.saveSession(body.accessToken, body.refreshToken)
                body.accessToken
            } else {
                null
            }
        } catch (_: Exception) {
            null
        }
    }
}

private fun VisitEntity.toRequest(gson: Gson): SubmitVisitRequest {
    val photosType = object : TypeToken<List<PhotoData>>() {}.type
    val trailType = object : TypeToken<TrailSnapshot>() {}.type
    return SubmitVisitRequest(
        visitId = visitId,
        surveyorId = surveyorId,
        fieldId = fieldId,
        phoneId = phoneId,
        satelliteTimestamp = java.time.Instant.ofEpochMilli(satelliteTimestamp).toString(),
        latitude = latitude,
        longitude = longitude,
        accuracyMeters = accuracyMeters,
        altitude = altitude,
        speed = speed,
        bearing = bearing,
        selfiePhotoHash = selfiePhotoHash,
        selfiePhotoS3Key = selfiePhotoS3Key,
        selfieLatitude = selfieLatitude,
        selfieLongitude = selfieLongitude,
        selfieAccuracyMeters = selfieAccuracyMeters,
        fieldPhotos = gson.fromJson(fieldPhotos, photosType) ?: emptyList(),
        faceMatchScore = faceMatchScore,
        livenessVerified = livenessVerified,
        trailSnapshot = gson.fromJson(trailSnapshot, trailType),
        signature = signature,
        signedByKeyId = signedByKeyId
    )
}
