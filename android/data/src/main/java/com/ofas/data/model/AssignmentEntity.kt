package com.ofas.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Index
import java.util.UUID

@Entity(
    tableName = "assignments",
    indices = [
        Index("surveyorId", "fieldId", unique = true)
    ]
)
data class AssignmentEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val surveyorId: String,
    val fieldId: String,
    val startDate: Long,
    val endDate: Long,
    val assignedBy: String?,
    val isCompleted: Boolean = false,
    val completedAt: Long? = null,
    val createdAt: Long = System.currentTimeMillis()
)