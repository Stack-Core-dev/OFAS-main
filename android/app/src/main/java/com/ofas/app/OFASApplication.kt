package com.ofas.app

import android.app.Application
import android.content.Context
import com.ofas.data.database.OFASDatabase
import com.ofas.data.repository.FieldRepository
import com.ofas.data.repository.SurveyorRepository
import com.ofas.data.repository.VisitRepository
import com.ofas.data.sync.SyncWorker
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
