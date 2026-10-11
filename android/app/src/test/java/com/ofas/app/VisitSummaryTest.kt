package com.ofas.app

import com.ofas.app.ui.screen.VisitSummary
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class VisitSummaryTest {

    @Test
    fun visitSummary_holdsCorrectValues() {
        val summary = VisitSummary(
            fieldName = "Test Field",
            surveyorName = "John",
            timestamp = "2026-10-07",
            latitude = 28.6139,
            longitude = 77.2090,
            accuracy = 3.2,
            photoCount = 5,
            faceMatchScore = 0.85f,
            livenessVerified = true,
            trailSynced = true
        )
        assertEquals("Test Field", summary.fieldName)
        assertEquals("John", summary.surveyorName)
        assertEquals(5, summary.photoCount)
        assertTrue(summary.livenessVerified)
        assertTrue(summary.trailSynced)
    }

    @Test
    fun visitSummary_withFailedLiveness_returnsFalse() {
        val summary = VisitSummary(
            fieldName = "F",
            surveyorName = "S",
            timestamp = "T",
            latitude = 0.0,
            longitude = 0.0,
            accuracy = 0.0,
            photoCount = 0,
            faceMatchScore = 0.0f,
            livenessVerified = false,
            trailSynced = false
        )
        assertFalse(summary.livenessVerified)
        assertFalse(summary.trailSynced)
    }
}
