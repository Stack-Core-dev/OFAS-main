package com.ofas.data.database

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.ofas.data.model.AssignmentEntity

@Dao
interface AssignmentDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(assignments: List<AssignmentEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(assignment: AssignmentEntity)

    @Update
    suspend fun update(assignment: AssignmentEntity)

    @Query("SELECT * FROM assignments WHERE id = :id")
    suspend fun getById(id: String): AssignmentEntity?

    @Query("SELECT * FROM assignments WHERE surveyorId = :surveyorId")
    suspend fun getBySurveyor(surveyorId: String): List<AssignmentEntity>

    @Query("SELECT * FROM assignments WHERE fieldId = :fieldId")
    suspend fun getByField(fieldId: String): List<AssignmentEntity>
}