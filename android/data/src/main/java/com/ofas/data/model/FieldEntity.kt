package com.ofas.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Index
import java.util.UUID
import com.squareup.moshi.Json

@Entity(
    tableName = "fields",
    indices = [Index("fieldCode", unique = true), Index("centerLat", "centerLon")]
)
data class FieldEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    @Json(name = "field_code") val fieldCode: String,
    val name: String,
    @Json(name = "crop_type") val cropType: String?,
    @Json(name = "center_lat") val centerLat: Double,
    @Json(name = "center_lon") val centerLon: Double,
    @Json(name = "radius_meters") val radiusMeters: Double,
    @Json(name = "reference_photos") val referencePhotos: String = "[]",
    @Json(name = "field_metadata") val metadata: String = "{}",
    @Json(name = "is_active") val isActive: Boolean = true,
    @Json(name = "created_at") val createdAt: Long = System.currentTimeMillis(),
    @Json(name = "updated_at") val updatedAt: Long = System.currentTimeMillis()
)