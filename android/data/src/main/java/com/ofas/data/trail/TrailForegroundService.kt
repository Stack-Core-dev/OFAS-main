package com.ofas.data.trail

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.IBinder
import android.util.Log
import com.ofas.data.database.OFASDatabase
import com.ofas.security.keystore.KeyManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

class TrailForegroundService : Service() {

    companion object {
        private const val TAG = "TrailForegroundService"
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "ofas_trail_channel"

        @Volatile
        private var running = false

        fun start(context: Context) {
            val intent = Intent(context, TrailForegroundService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        /**
         * Starts trail recording when allowed to run: within work hours and with
         * a location permission granted. Callers should invoke this from a context
         * that is allowed to start a foreground service (app foreground or a
         * BOOT_COMPLETED receiver); background starts are rejected by the OS.
         * Never throws - a rejected start is logged and retried on the next trigger.
         */
        fun startIfEligible(context: Context) {
            if (running) {
                Log.i(TAG, "startIfEligible: already running")
                return
            }
            if (!TrailWorkHours.isWithinWorkHours()) {
                Log.i(TAG, "startIfEligible: outside work hours, skipping")
                return
            }
            val fine = context.checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) ==
                PackageManager.PERMISSION_GRANTED
            val coarse = context.checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) ==
                PackageManager.PERMISSION_GRANTED
            if (!fine && !coarse) {
                Log.i(TAG, "startIfEligible: no location permission, skipping")
                return
            }
            try {
                start(context)
                Log.i(TAG, "startIfEligible: requested trail recording start")
            } catch (e: Exception) {
                Log.w(TAG, "startIfEligible: unable to start now; will retry on next trigger", e)
            }
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, TrailForegroundService::class.java))
        }
    }

    private lateinit var trailManager: TrailManager
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        try {
            startForeground(NOTIFICATION_ID, createNotification())
        } catch (e: Exception) {
            Log.e(TAG, "Unable to start foreground service (missing permission?)", e)
            stopSelf()
            return
        }

        val database = OFASDatabase.getInstance(this)
        val keyManager = KeyManager.getInstance(this)
        trailManager = TrailManager.getInstance(this, database, keyManager)
        trailManager.onEntryRecorded = {
            uploadPendingLocations()
        }
        trailManager.startRecording()
        uploadPendingLocations()
        running = true
        Log.i(TAG, "Trail recording started")
    }

    private fun uploadPendingLocations() {
        scope.launch {
            SurveyorLocationUploader.uploadPending(applicationContext)
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_STICKY
    }

    override fun onDestroy() {
        running = false
        if (::trailManager.isInitialized) {
            trailManager.stopRecording()
            trailManager.onEntryRecorded = null
        }
        scope.cancel()
        Log.i(TAG, "Trail recording stopped")
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "OFAS Trail Recording",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Records trail entries during field visits"
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        val builder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Notification.Builder(this, CHANNEL_ID)
        } else {
            @Suppress("DEPRECATION")
            Notification.Builder(this)
        }
        return builder
            .setContentTitle("OFAS Trail Recording")
            .setContentText("Recording trail entries...")
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .build()
    }
}
