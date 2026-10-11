package com.ofas.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Index
import java.util.UUID

@Entity(
    tableName = "phones",
    indices = [Index("deviceId", unique = true)]
)
data class PhoneEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val deviceId: String,
    val model: String?,
    val androidVersion: String?,
    val publicKey: String,
    val keyAlgorithm: String = "ES256",
    val status: String = "ACTIVE",
    val registeredBy: String?,
    val registeredAt: Long = System.currentTimeMillis(),
    val lastSeen: Long? = null,
    val blockedAt: Long? = null,
    val blockedReason: String? = null
)