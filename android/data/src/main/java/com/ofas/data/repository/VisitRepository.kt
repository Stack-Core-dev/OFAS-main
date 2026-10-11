package com.ofas.data.repository

import com.ofas.data.database.VisitDao
import com.ofas.data.model.VisitEntity

class VisitRepository(private val dao: VisitDao) {

    suspend fun insertAll(visits: List<VisitEntity>) = dao.insertAll(visits)

    suspend fun insert(visit: VisitEntity) = dao.insert(visit)

    suspend fun update(visit: VisitEntity) = dao.update(visit)

    suspend fun getById(id: String): VisitEntity? = dao.getById(id)

    suspend fun getByVisitId(visitId: String): VisitEntity? = dao.getByVisitId(visitId)

    suspend fun getBySurveyor(surveyorId: String): List<VisitEntity> = dao.getBySurveyor(surveyorId)

    suspend fun getByField(fieldId: String): List<VisitEntity> = dao.getByField(fieldId)

    suspend fun getByStatuses(statuses: List<String>): List<VisitEntity> = dao.getByStatuses(statuses)

    suspend fun getPendingSync(): List<VisitEntity> = dao.getPendingSync()
    suspend fun markSyncing(id: String): Int = dao.markSyncing(id, System.currentTimeMillis())
    suspend fun markSynced(id: String, timestamp: Long): Int =
        dao.markSynced(id, timestamp, System.currentTimeMillis())
    suspend fun markFailed(id: String): Int = dao.markFailed(id, System.currentTimeMillis())

    suspend fun getPaged(limit: Int, offset: Int): List<VisitEntity> = dao.getPaged(limit, offset)

    suspend fun countBySurveyor(surveyorId: String): Int = dao.countBySurveyor(surveyorId)

    suspend fun countSyncedToday(surveyorId: String): Int = dao.countSyncedToday(surveyorId)
}