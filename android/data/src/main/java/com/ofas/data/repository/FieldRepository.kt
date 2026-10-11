package com.ofas.data.repository

import com.ofas.data.database.FieldDao
import com.ofas.data.model.FieldEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class FieldRepository(private val dao: FieldDao) {

    suspend fun insertAll(fields: List<FieldEntity>) = dao.insertAll(fields)

    suspend fun replaceAssignedFields(fields: List<FieldEntity>) {
        dao.deleteAll()
        if (fields.isNotEmpty()) dao.insertAll(fields)
    }

    suspend fun insert(field: FieldEntity) = dao.insert(field)

    suspend fun update(field: FieldEntity) = dao.update(field)

    suspend fun getById(id: String): FieldEntity? = dao.getById(id)

    suspend fun getByCode(code: String): FieldEntity? = dao.getByCode(code)

    suspend fun getAllActive(): List<FieldEntity> = dao.getAllActive()

    suspend fun getPaged(limit: Int, offset: Int): List<FieldEntity> = dao.getPaged(limit, offset)

    suspend fun countActive(): Int = dao.countActive()

    suspend fun getByIds(ids: List<String>): List<FieldEntity> = dao.getByIds(ids)

    suspend fun deleteById(id: String) = dao.deleteById(id)
}