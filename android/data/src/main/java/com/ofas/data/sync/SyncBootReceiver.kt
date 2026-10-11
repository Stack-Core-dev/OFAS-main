package com.ofas.data.sync

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.work.WorkManager
import com.ofas.data.sync.SyncWorker

class SyncBootReceiver : BroadcastReceiver() {

    companion object {
        private const val TAG = "SyncBootReceiver"
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            Log.d(TAG, "Boot completed, scheduling sync")
            SyncWorker.schedulePeriodicSync(context)
        }
    }
}