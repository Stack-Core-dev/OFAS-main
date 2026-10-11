package com.ofas.data.converters

import androidx.room.TypeConverter
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.lang.reflect.Type
import java.util.*

class Converters {

    private val gson = Gson()

    @TypeConverter
    fun fromJsonList(json: String): List<String> {
        val type: Type = object : TypeToken<List<String>>() {}.type
        return try {
            gson.fromJson(json, type) ?: emptyList()
        } catch (e: Exception) {
            emptyList()
        }
    }

    @TypeConverter
    fun toJsonList(list: List<String>): String {
        return gson.toJson(list)
    }

    @TypeConverter
    fun fromJsonMap(json: String): Map<String, Any> {
        val type: Type = object : TypeToken<Map<String, Any>>() {}.type
        return gson.fromJson(json, type) ?: emptyMap()
    }

    @TypeConverter
    fun toJsonMap(map: Map<String, Any>): String {
        return gson.toJson(map)
    }

    @TypeConverter
    fun fromTimestamp(timestamp: Long?): Date? {
        return timestamp?.let { Date(it) }
    }

    @TypeConverter
    fun toTimestamp(date: Date?): Long? {
        return date?.time
    }
}