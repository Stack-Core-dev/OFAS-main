package com.ofas.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Index
import java.util.UUID

@Entity(
    tableName = "surveyors",
    indices = [Index("employeeId", unique = true)]
)
data class SurveyorEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val employeeId: String,
    val fullName: String,
    val phoneNumber: String?,
    val email: String?,
    val faceTemplate: ByteArray? = null,
    val faceTemplateVersion: Int = 1,
    val isActive: Boolean = true,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)