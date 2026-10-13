package com.ofas.data.sync

import android.content.Context
import android.util.Base64
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class AuthTokenStore(context: Context) {
    private val preferences = EncryptedSharedPreferences.create(
        context,
        "ofas_auth_prefs",
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun accessToken(): String? = preferences.getString("access_token", null)

    fun refreshToken(): String? = preferences.getString("refresh_token", null)

    fun saveSession(accessToken: String, refreshToken: String) {
        val expiry = parseExpiry(accessToken) ?: (System.currentTimeMillis() + 3600000L)
        preferences.edit()
            .putString("access_token", accessToken)
            .putString("refresh_token", refreshToken)
            .putLong("token_expiry", expiry)
            .apply()
    }

    private fun parseExpiry(token: String): Long? {
        return try {
            val parts = token.split(".")
            if (parts.size < 2) return null
            val payload = String(
                Base64.decode(parts[1], Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING)
            )
            Regex("\"exp\"\\s*:\\s*(\\d+)")
                .find(payload)
                ?.groupValues
                ?.get(1)
                ?.toLongOrNull()
                ?.times(1000L)
        } catch (_: Exception) {
            null
        }
    }

    fun surveyorId(): String? = preferences.getString("surveyor_id", null)

    fun saveSurveyorId(id: String) {
        preferences.edit().putString("surveyor_id", id).apply()
    }
}
