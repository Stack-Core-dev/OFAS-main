package com.ofas.data.database

import android.content.Context
import android.util.Base64
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.ofas.data.model.FieldEntity
import com.ofas.data.model.SurveyorEntity
import com.ofas.data.model.VisitEntity
import com.ofas.data.model.TrailEntryEntity
import com.ofas.data.model.PhoneEntity
import com.ofas.data.model.AssignmentEntity
import com.ofas.data.converters.Converters
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import net.sqlcipher.database.SupportFactory
import java.security.SecureRandom

@Database(
    entities = [
        FieldEntity::class,
        SurveyorEntity::class,
        VisitEntity::class,
        TrailEntryEntity::class,
        PhoneEntity::class,
        AssignmentEntity::class
    ],
    version = 3,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class OFASDatabase : RoomDatabase() {

    abstract fun fieldDao(): FieldDao
    abstract fun surveyorDao(): SurveyorDao
    abstract fun visitDao(): VisitDao
    abstract fun trailEntryDao(): TrailEntryDao
    abstract fun phoneDao(): PhoneDao
    abstract fun assignmentDao(): AssignmentDao

    companion object {
        @Volatile
        private var INSTANCE: OFASDatabase? = null

        fun getInstance(context: Context): OFASDatabase {
            return INSTANCE ?: synchronized(this) {
                net.sqlcipher.database.SQLiteDatabase.loadLibs(context)
                val passphrase = getOrCreatePassphrase(context)
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    OFASDatabase::class.java,
                    "ofas.db"
                )
                    .openHelperFactory(SupportFactory(passphrase))
                    .addMigrations(MIGRATION_2_3)
                    .build()
                    .also { INSTANCE = it }
            }
        }

        private val MIGRATION_2_3 = object : androidx.room.migration.Migration(2, 3) {
            override fun migrate(database: androidx.sqlite.db.SupportSQLiteDatabase) {
                database.execSQL("DROP TABLE IF EXISTS assignments_new")
                database.execSQL(
                    "CREATE TABLE assignments_new (" +
                        "id TEXT NOT NULL PRIMARY KEY, surveyorId TEXT NOT NULL, fieldId TEXT NOT NULL, " +
                        "startDate INTEGER NOT NULL, endDate INTEGER NOT NULL, assignedBy TEXT, " +
                        "isCompleted INTEGER NOT NULL, completedAt INTEGER, createdAt INTEGER NOT NULL)"
                )
                database.execSQL(
                    "INSERT INTO assignments_new (id, surveyorId, fieldId, startDate, endDate, assignedBy, isCompleted, completedAt, createdAt) " +
                        "SELECT id, surveyorId, fieldId, assignedDate, assignedDate, assignedBy, isCompleted, completedAt, createdAt FROM assignments"
                )
                database.execSQL("DROP TABLE assignments")
                database.execSQL("ALTER TABLE assignments_new RENAME TO assignments")
                database.execSQL("CREATE UNIQUE INDEX index_assignments_surveyorId_fieldId ON assignments (surveyorId, fieldId)")
            }
        }

        private fun getOrCreatePassphrase(context: Context): ByteArray {
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
            val prefs = EncryptedSharedPreferences.create(
                context,
                "ofas_database_key",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
            val existing = prefs.getString("passphrase", null)
            if (existing != null) return Base64.decode(existing, Base64.DEFAULT)
            val bytes = ByteArray(32)
            SecureRandom().nextBytes(bytes)
            prefs.edit().putString("passphrase", Base64.encodeToString(bytes, Base64.NO_WRAP)).apply()
            return bytes
        }
    }
}