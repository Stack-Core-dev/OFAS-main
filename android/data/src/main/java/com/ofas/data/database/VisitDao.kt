package com.ofas.data.database

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.ofas.data.model.VisitEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface VisitDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(visits: List<VisitEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(visit: VisitEntity)

    @Update
    suspend fun update(visit: VisitEntity)

    @Query("SELECT * FROM visits WHERE id = :id")
    suspend fun getById(id: String): VisitEntity?

    @Query("SELECT * FROM visits WHERE visitId = :visitId")
    suspend fun getByVisitId(visitId: String): VisitEntity?

    @Query("SELECT * FROM visits WHERE surveyorId = :surveyorId ORDER BY satelliteTimestamp DESC")
    suspend fun getBySurveyor(surveyorId: String): List<VisitEntity>

    @Query("SELECT * FROM visits WHERE fieldId = :fieldId ORDER BY satelliteTimestamp DESC")
    suspend fun getByField(fieldId: String): List<VisitEntity>

    @Query("SELECT * FROM visits WHERE status IN (:statuses) ORDER BY createdAt ASC")
    suspend fun getByStatuses(statuses: List<String>): List<VisitEntity>

    @Query("SELECT * FROM visits WHERE syncedAt IS NULL AND status IN ('QUEUED', 'SYNCING', 'FAILED') ORDER BY createdAt ASC")
    suspend fun getPendingSync(): List<VisitEntity>

    @Query("SELECT COUNT(*) FROM visits WHERE syncedAt IS NULL AND status IN ('QUEUED', 'SYNCING', 'FAILED')")
    suspend fun getPendingSyncCount(): Int

    @Query("SELECT COUNT(*) FROM visits WHERE syncedAt IS NULL AND status IN ('QUEUED', 'SYNCING', 'FAILED')")
    fun observePendingSyncCount(): Flow<Int>

    @Query("UPDATE visits SET status = 'SYNCING', updatedAt = :updatedAt WHERE id = :id AND status IN ('QUEUED', 'FAILED')")
    suspend fun markSyncing(id: String, updatedAt: Long): Int

    @Query("UPDATE visits SET status = 'SYNCED', syncedAt = :syncedAt, updatedAt = :updatedAt WHERE id = :id")
    suspend fun markSynced(id: String, syncedAt: Long, updatedAt: Long): Int

    @Query("UPDATE visits SET status = 'FAILED', updatedAt = :updatedAt WHERE id = :id")
    suspend fun markFailed(id: String, updatedAt: Long): Int

    @Query("SELECT * FROM visits ORDER BY satelliteTimestamp DESC LIMIT :limit OFFSET :offset")
    suspend fun getPaged(limit: Int, offset: Int): List<VisitEntity>

    @Query("SELECT COUNT(*) FROM visits WHERE surveyorId = :surveyorId")
    suspend fun countBySurveyor(surveyorId: String): Int

    @Query("SELECT COUNT(*) FROM visits WHERE surveyorId = :surveyorId AND date(satelliteTimestamp/1000, 'unixepoch') = date('now')")
    suspend fun countToday(surveyorId: String): Int

    @Query("SELECT COUNT(*) FROM visits WHERE status = 'SYNCED' AND date(syncedAt/1000, 'unixepoch') = date('now') AND surveyorId = :surveyorId")
    suspend fun countSyncedToday(surveyorId: String): Int
}