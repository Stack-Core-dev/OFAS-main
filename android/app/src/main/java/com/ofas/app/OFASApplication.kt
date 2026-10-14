package com.ofas.app

import android.Manifest
import android.app.Application
import android.content.Context
import android.content.pm.PackageManager
import android.util.Log
import androidx.core.content.ContextCompat
import com.ofas.data.database.OFASDatabase
import com.ofas.data.repository.FieldRepository
import com.ofas.data.repository.SurveyorRepository
import com.ofas.data.repository.VisitRepository
import com.ofas.data.sync.SyncWorker
import com.ofas.data.sync.NetworkStatusMonitor
import com.ofas.data.trail.TrailForegroundService
import com.ofas.data.trail.TrailWorkHours
import com.ofas.security.keystore.KeyManager
import com.ofas.data.trail.TrailManager
import com.ofas.data.face.FaceVerifier
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class OFASApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        KeyManager.initialize(this)
        initializeRepositories(this)
        TrailManager.initialize(this, database, KeyManager.getInstance(this))
        FaceVerifier.initialize(this, KeyManager.getInstance(this))
        SyncWorker.schedulePeriodicSync(this)
        NetworkStatusMonitor.initialize(this)
        startTrailRecordingIfEligible()
    }

    private fun startTrailRecordingIfEligible() {
        if (!TrailWorkHours.isWithinWorkHours()) return
        val hasLocation = ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED || ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        if (!hasLocation) return
        try {
            TrailForegroundService.start(this)
        } catch (e: Exception) {
            Log.w(TAG, "Unable to start trail recording", e)
        }
    }

    companion object {
        private const val TAG = "OFASApplication"
        private var _database: OFASDatabase? = null

        val database: OFASDatabase
            get() = _database ?: throw IllegalStateException("Database not initialized")

        lateinit var fieldRepository: FieldRepository
            private set

        lateinit var surveyorRepository: SurveyorRepository
            private set

        lateinit var visitRepository: VisitRepository
            private set

        lateinit var keyManager: KeyManager
            private set

        fun getDatabase(context: Context): OFASDatabase {
            return OFASDatabase.getInstance(context)
        }

        fun initializeRepositories(context: Context) {
            _database = getDatabase(context)
            fieldRepository = FieldRepository(database.fieldDao())
            surveyorRepository = SurveyorRepository(database.surveyorDao())
            visitRepository = VisitRepository(database.visitDao())
            keyManager = KeyManager.getInstance(context)
        }
    }
}
