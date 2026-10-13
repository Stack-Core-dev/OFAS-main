package com.ofas.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Index
import java.util.UUID

@Entity(
    tableName = "visits",
    indices = [
        Index("visitId", unique = true),
        Index("surveyorId"),
        Index("fieldId"),
        Index("phoneId"),
        Index("satelliteTimestamp"),
        Index("status"),
        Index("syncedAt")
    ]
)
data class VisitEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val visitId: String,
    val surveyorId: String,
    val fieldId: String,
    val phoneId: String,
    val satelliteTimestamp: Long,
    val latitude: Double,
    val longitude: Double,
    val accuracyMeters: Double,
    val altitude: Double?,
    val speed: Double?,
    val bearing: Double?,
    val selfiePhotoHash: String,
    val selfiePhotoS3Key: String?,
    val selfieLatitude: Double?,
    val selfieLongitude: Double?,
    val selfieAccuracyMeters: Double?,
    val fieldPhotos: String,
    val faceMatchScore: Float,
    val livenessVerified: Boolean,
    val trailSnapshot: String,
    val signature: String,
    val signedByKeyId: String,
    val status: String = "QUEUED",
    val reviewStatus: String? = null,
    val reviewedBy: String? = null,
    val reviewedAt: Long? = null,
    val reviewNotes: String? = null,
    val syncedAt: Long? = null,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)