package com.ofas.data.database

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.ofas.data.model.TrailEntryEntity

@Dao
interface TrailEntryDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(entries: List<TrailEntryEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entry: TrailEntryEntity)

    @Query("SELECT * FROM trail_entries WHERE phoneId = :phoneId ORDER BY sequenceNumber ASC")
    suspend fun getAllEntries(phoneId: String): List<TrailEntryEntity>

    @Query("SELECT * FROM trail_entries WHERE phoneId = :phoneId ORDER BY sequenceNumber DESC LIMIT 1")
    suspend fun getLastEntry(phoneId: String): TrailEntryEntity?

    @Query("SELECT * FROM trail_entries WHERE phoneId = :phoneId AND satelliteTimestamp BETWEEN :startTime AND :endTime ORDER BY satelliteTimestamp ASC")
    suspend fun getEntriesInRange(phoneId: String, startTime: Long, endTime: Long): List<TrailEntryEntity>

    @Query("SELECT * FROM trail_entries WHERE phoneId = :phoneId AND entryHash = :hash")
    suspend fun getByHash(phoneId: String, hash: String): TrailEntryEntity?

    @Query("SELECT * FROM trail_entries WHERE phoneId = :phoneId AND prevHash = :prevHash")
    suspend fun getByPrevHash(phoneId: String, prevHash: String): TrailEntryEntity?

    @Query("DELETE FROM trail_entries WHERE phoneId = :phoneId AND satelliteTimestamp < :cutoffTime")
    suspend fun deleteOldEntries(phoneId: String, cutoffTime: Long)

    @Query("SELECT COUNT(*) FROM trail_entries WHERE phoneId = :phoneId")
    suspend fun countByPhone(phoneId: String): Int
}