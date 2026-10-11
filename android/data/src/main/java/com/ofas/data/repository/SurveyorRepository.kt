package com.ofas.data.repository

import com.ofas.data.database.SurveyorDao
import com.ofas.data.model.SurveyorEntity

class SurveyorRepository(private val dao: SurveyorDao) {

    suspend fun insertAll(surveyors: List<SurveyorEntity>) = dao.insertAll(surveyors)

    suspend fun insert(surveyor: SurveyorEntity) = dao.insert(surveyor)

    suspend fun update(surveyor: SurveyorEntity) = dao.update(surveyor)

    suspend fun getById(id: String): SurveyorEntity? = dao.getById(id)

    suspend fun getByEmployeeId(employeeId: String): SurveyorEntity? = dao.getByEmployeeId(employeeId)

    suspend fun getAllActive(): List<SurveyorEntity> = dao.getAllActive()

    suspend fun getPaged(limit: Int, offset: Int): List<SurveyorEntity> = dao.getPaged(limit, offset)

    suspend fun countActive(): Int = dao.countActive()

    suspend fun getAllWithFaceTemplates(): List<SurveyorEntity> = dao.getAllWithFaceTemplates()

    suspend fun deleteById(id: String) = dao.deleteById(id)
}