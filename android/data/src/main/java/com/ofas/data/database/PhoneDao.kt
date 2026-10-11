package com.ofas.data.database

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.ofas.data.model.PhoneEntity

@Dao
interface PhoneDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(phone: PhoneEntity)

    @Update
    suspend fun update(phone: PhoneEntity)

    @Query("SELECT * FROM phones WHERE id = :id")
    suspend fun getById(id: String): PhoneEntity?

    @Query("SELECT * FROM phones WHERE deviceId = :deviceId")
    suspend fun getByDeviceId(deviceId: String): PhoneEntity?

    @Query("SELECT * FROM phones WHERE status = 'ACTIVE'")
    suspend fun getActivePhones(): List<PhoneEntity>

    @Query("SELECT * FROM phones ORDER BY registeredAt DESC")
    suspend fun getAll(): List<PhoneEntity>
}