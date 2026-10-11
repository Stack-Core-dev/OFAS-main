package com.ofas.data.database

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.ofas.data.model.SurveyorEntity

@Dao
interface SurveyorDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(surveyors: List<SurveyorEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(surveyor: SurveyorEntity)

    @Update
    suspend fun update(surveyor: SurveyorEntity)

    @Query("SELECT * FROM surveyors WHERE id = :id")
    suspend fun getById(id: String): SurveyorEntity?

    @Query("SELECT * FROM surveyors WHERE employeeId = :employeeId")
    suspend fun getByEmployeeId(employeeId: String): SurveyorEntity?

    @Query("SELECT * FROM surveyors WHERE isActive = 1 ORDER BY createdAt DESC")
    suspend fun getAllActive(): List<SurveyorEntity>

    @Query("SELECT * FROM surveyors ORDER BY createdAt DESC LIMIT :limit OFFSET :offset")
    suspend fun getPaged(limit: Int, offset: Int): List<SurveyorEntity>

    @Query("SELECT COUNT(*) FROM surveyors WHERE isActive = 1")
    suspend fun countActive(): Int

    @Query("SELECT * FROM surveyors WHERE isActive = 1 AND faceTemplate IS NOT NULL")
    suspend fun getAllWithFaceTemplates(): List<SurveyorEntity>

    @Query("DELETE FROM surveyors WHERE id = :id")
    suspend fun deleteById(id: String)
}