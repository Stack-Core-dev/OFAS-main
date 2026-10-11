package com.ofas.app

import com.ofas.data.converters.Converters
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.Date

class ConvertersTest {

    private val converters = Converters()

    @Test
    fun fromJsonList_withValidJson_returnsList() {
        val json = """["a","b","c"]"""
        val result = converters.fromJsonList(json)
        assertEquals(listOf("a", "b", "c"), result)
    }

    @Test
    fun fromJsonList_withInvalidJson_returnsEmptyList() {
        val result = converters.fromJsonList("not json")
        assertTrue(result.isEmpty())
    }

    @Test
    fun toJsonList_withValidList_returnsJson() {
        val json = converters.toJsonList(listOf("x", "y"))
        assertEquals("""["x","y"]""", json)
    }

    @Test
    fun fromJsonMap_withValidJson_returnsMap() {
        val json = """{"key":"value"}"""
        val result = converters.fromJsonMap(json)
        assertEquals("value", result["key"])
    }

    @Test
    fun toJsonMap_withValidMap_returnsJson() {
        val json = converters.toJsonMap(mapOf("a" to 1))
        assertTrue(json.contains("\"a\""))
    }

    @Test
    fun fromTimestamp_withValidValue_returnsDate() {
        val date = converters.fromTimestamp(1000L)
        assertEquals(Date(1000L), date)
    }

    @Test
    fun fromTimestamp_withNull_returnsNull() {
        assertEquals(null, converters.fromTimestamp(null))
    }

    @Test
    fun toTimestamp_withValidDate_returnsLong() {
        val date = Date(2000L)
        assertEquals(2000L, converters.toTimestamp(date))
    }

    @Test
    fun toTimestamp_withNull_returnsNull() {
        assertEquals(null, converters.toTimestamp(null))
    }
}
