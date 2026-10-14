package com.ofas.app

import android.app.Application
import android.content.Context
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.ProcessLifecycleOwner
import com.ofas.data.database.OFASDatabase
import com.ofas.data.repository.FieldRepository
import com.ofas.data.repository.SurveyorRepository
import com.ofas.data.repository.VisitRepository
import com.ofas.data.sync.SyncWorker
import com.ofas.data.sync.NetworkStatusMonitor
import com.ofas.data.trail.TrailForegroundService
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
        observeAppForeground()
    }

    /**
     * A foreground-service start is only permitted while the app is in the
     * foreground (or from an exempted context such as BOOT_COMPLETED). Starting
     * it from [onCreate] fails when the process is launched in the background,
     * so start it the moment the app first becomes visible instead. The service
     * runs with START_STICKY and persists once started.
     */
    private fun observeAppForeground() {
        ProcessLifecycleOwner.get().lifecycle.addObserver(
            LifecycleEventObserver { _, event ->
                if (event == Lifecycle.Event.ON_START) {
                    TrailForegroundService.startIfEligible(this)
                }
            }
        )
    }

    companion object {
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
