package com.ofas.data.trail

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import com.ofas.data.database.OFASDatabase
import com.ofas.security.keystore.KeyManager

class TrailForegroundService : Service() {

    companion object {
        private const val TAG = "TrailForegroundService"
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "ofas_trail_channel"

        fun start(context: Context) {
            val intent = Intent(context, TrailForegroundService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, TrailForegroundService::class.java))
        }
    }

    private lateinit var trailManager: TrailManager

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
        trailManager.startRecording()
        Log.d(TAG, "Trail recording started")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_STICKY
    }

    override fun onDestroy() {
        if (::trailManager.isInitialized) {
            trailManager.stopRecording()
        }
        Log.d(TAG, "Trail recording stopped")
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
