package com.ofas.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Index
import java.util.UUID

@Entity(
    tableName = "trail_entries",
    indices = [
        Index("phoneId", "sequenceNumber", unique = true),
        Index("phoneId", "satelliteTimestamp"),
        Index("entryHash")
    ]
)
data class TrailEntryEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val phoneId: String,
    val sequenceNumber: Int,
    val satelliteTimestamp: Long,
    val latitude: Double,
    val longitude: Double,
    val accuracyMeters: Double,
    val altitude: Double?,
    val speed: Double?,
    val bearing: Double?,
    val prevHash: String,
    val entryHash: String,
    val signature: String,
    val createdAt: Long = System.currentTimeMillis()
)