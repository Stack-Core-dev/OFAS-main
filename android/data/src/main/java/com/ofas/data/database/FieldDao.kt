package com.ofas.data.database

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.ofas.data.model.FieldEntity

@Dao
interface FieldDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(fields: List<FieldEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(field: FieldEntity)

    @Update
    suspend fun update(field: FieldEntity)

    @Query("SELECT * FROM fields WHERE id = :id")
    suspend fun getById(id: String): FieldEntity?

    @Query("SELECT * FROM fields WHERE fieldCode = :code")
    suspend fun getByCode(code: String): FieldEntity?

    @Query("SELECT * FROM fields WHERE isActive = 1 ORDER BY createdAt DESC")
    suspend fun getAllActive(): List<FieldEntity>

    @Query("SELECT * FROM fields ORDER BY createdAt DESC LIMIT :limit OFFSET :offset")
    suspend fun getPaged(limit: Int, offset: Int): List<FieldEntity>

    @Query("SELECT COUNT(*) FROM fields WHERE isActive = 1")
    suspend fun countActive(): Int

    @Query("SELECT * FROM fields WHERE id IN (:ids)")
    suspend fun getByIds(ids: List<String>): List<FieldEntity>

    @Query("DELETE FROM fields WHERE id = :id")
    suspend fun deleteById(id: String)

    @Query("DELETE FROM fields")
    suspend fun deleteAll()
}