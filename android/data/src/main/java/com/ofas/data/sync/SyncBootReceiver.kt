package com.ofas.data.sync

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.work.WorkManager
import com.ofas.data.sync.SyncWorker
import com.ofas.data.trail.TrailForegroundService

class SyncBootReceiver : BroadcastReceiver() {

    companion object {
        private const val TAG = "SyncBootReceiver"
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            Log.i(TAG, "Boot completed, scheduling sync")
            SyncWorker.schedulePeriodicSync(context)
            // Attempt an immediate flush so any pings captured before the reboot
            // reach the backend as soon as connectivity is available.
            SyncWorker.enqueueNow(context)
            // BOOT_COMPLETED is an exemption that allows starting a foreground
            // service from the background; the location type is permitted here
            // because ACCESS_BACKGROUND_LOCATION is granted.
            TrailForegroundService.startIfEligible(context)
        }
    }
}