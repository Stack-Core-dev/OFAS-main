package com.ofas.data.trail

import android.content.Context
import android.Manifest
import android.content.pm.PackageManager
import android.location.Location
import android.util.Log
import androidx.core.content.ContextCompat
import com.ofas.data.database.OFASDatabase
import com.ofas.data.model.TrailEntryEntity
import com.ofas.security.keystore.KeyManager
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import com.google.android.gms.tasks.CancellationTokenSource
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import java.security.MessageDigest
import java.util.concurrent.TimeUnit

class TrailManager private constructor(
    private val context: Context,
    private val database: OFASDatabase,
    private val keyManager: KeyManager
) {

    companion object {
        private const val TRAIL_INTERVAL_MINUTES = 5
        private const val TAG = "TrailManager"
        private var INSTANCE: TrailManager? = null

        fun getInstance(
            context: Context,
            database: OFASDatabase,
            keyManager: KeyManager
        ): TrailManager {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: TrailManager(
                    context.applicationContext,
                    database,
                    keyManager
                ).also { INSTANCE = it }
            }
        }

        fun initialize(
            context: Context,
            database: OFASDatabase,
            keyManager: KeyManager
        ) {
            getInstance(context, database, keyManager)
        }
    }

    private var isRecording = false
    private var currentSequence = 0
    private var lastEntryHash = "0".repeat(64)
    private val scope = CoroutineScope(Dispatchers.IO)

    fun startRecording() {
        if (isRecording) return
        isRecording = true
        loadLastEntry()
        scheduleNextRecording()
    }

    suspend fun captureEntryNow(): TrailEntryEntity? {
        val location = getCurrentLocation()
        return location?.let {
            currentSequence++
            val entry = createTrailEntry(it)
            database.trailEntryDao().insert(entry)
            lastEntryHash = entry.entryHash
            Log.d(TAG, "Recorded trail entry #$currentSequence (on demand)")
            entry
        }
    }

    fun stopRecording() {
        isRecording = false
    }

    private fun loadLastEntry() {
        scope.launch {
            val lastEntry = database.trailEntryDao().getLastEntry(getDeviceId())
            lastEntry?.let {
                currentSequence = it.sequenceNumber
                lastEntryHash = it.entryHash
            }
        }
    }

    private fun scheduleNextRecording() {
        scope.launch {
            while (isRecording) {
                recordTrailEntry()
                delay(TimeUnit.MINUTES.toMillis(TRAIL_INTERVAL_MINUTES.toLong()))
            }
        }
    }

    private fun recordTrailEntry() {
        scope.launch {
            val location = getCurrentLocation()
            location?.let {
                currentSequence++
                val entry = createTrailEntry(it)
                database.trailEntryDao().insert(entry)
                lastEntryHash = entry.entryHash
                Log.d(TAG, "Recorded trail entry #$currentSequence")
            }
        }
    }

    private suspend fun getCurrentLocation(): Location? {
        val hasFineLocation = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        val hasCoarseLocation = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        if (!hasFineLocation && !hasCoarseLocation) {
            Log.w(TAG, "Location permission is not granted")
            return null
        }

        return try {
            val location = LocationServices.getFusedLocationProviderClient(context)
                .getCurrentLocation(
                    Priority.PRIORITY_HIGH_ACCURACY,
                    CancellationTokenSource().token
                )
                .await()
            location?.takeUnless { it.isMock }
        } catch (e: Exception) {
            Log.e(TAG, "Unable to obtain current GNSS location", e)
            null
        }
    }

    private fun createTrailEntry(location: Location): TrailEntryEntity {
        val timestamp = System.currentTimeMillis()
        val data = buildEntryData(timestamp, location)
        val entryHash = computeHash(data)
        val signature = keyManager.sign(data.toByteArray())

        return TrailEntryEntity(
            phoneId = getDeviceId(),
            sequenceNumber = currentSequence,
            satelliteTimestamp = timestamp,
            latitude = location.latitude,
            longitude = location.longitude,
            accuracyMeters = location.accuracy.toDouble(),
            altitude = location.altitude,
            speed = location.speed.toDouble(),
            bearing = location.bearing.toDouble(),
            prevHash = lastEntryHash,
            entryHash = entryHash,
            signature = android.util.Base64.encodeToString(signature, android.util.Base64.NO_WRAP),
            createdAt = System.currentTimeMillis()
        )
    }

    private fun buildEntryData(timestamp: Long, location: Location): String {
        return """{"seq":$currentSequence,"time":$timestamp,"lat":${location.latitude},"lon":${location.longitude},"acc":${location.accuracy},"prev":"$lastEntryHash"}"""
    }

    private fun computeHash(data: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
        val hash = digest.digest(data.toByteArray())
        return hash.joinToString("") { "%02x".format(it) }
    }

    private fun getDeviceId(): String {
        return android.provider.Settings.Secure.getString(
            context.contentResolver,
            android.provider.Settings.Secure.ANDROID_ID
        ) ?: "unknown"
    }

    suspend fun getTrailEntriesAround(timestamp: Long, windowMinutes: Int = 5): List<TrailEntryEntity> {
        val startTime = timestamp - TimeUnit.MINUTES.toMillis(windowMinutes.toLong())
        val endTime = timestamp + TimeUnit.MINUTES.toMillis(windowMinutes.toLong())
        return database.trailEntryDao().getEntriesInRange(getDeviceId(), startTime, endTime)
    }

    suspend fun verifyChain(): Boolean {
        val entries = database.trailEntryDao().getAllEntries(getDeviceId())
        var expectedPrev = "0".repeat(64)
        for (entry in entries) {
            if (entry.prevHash != expectedPrev) return false
            val data = buildEntryData(entry.satelliteTimestamp, entry.toLocation())
            if (computeHash(data) != entry.entryHash) return false
            if (!keyManager.verify(data.toByteArray(), android.util.Base64.decode(entry.signature, android.util.Base64.NO_WRAP), keyManager.getPublicKeyPem())) {
                return false
            }
            expectedPrev = entry.entryHash
        }
        return true
    }
}

private fun TrailEntryEntity.toLocation(): Location {
    val loc = Location("trail")
    loc.latitude = latitude
    loc.longitude = longitude
    loc.accuracy = accuracyMeters.toFloat()
    altitude?.let { loc.altitude = it }
    speed?.let { loc.speed = it.toFloat() }
    bearing?.let { loc.bearing = it.toFloat() }
    return loc
}