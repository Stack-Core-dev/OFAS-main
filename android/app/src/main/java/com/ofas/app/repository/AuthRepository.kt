package com.ofas.app.repository

import android.content.Context
import android.util.Base64
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.ofas.data.sync.FaceTemplateData
import com.ofas.data.sync.LoginResponse
import com.ofas.data.sync.UserData
import com.ofas.data.sync.AuthTokenStore
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    @dagger.hilt.android.qualifiers.ApplicationContext private val context: Context
) {

    companion object {
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
        private const val KEY_USER_DATA = "user_data"
        private const val KEY_TOKEN_EXPIRY = "token_expiry"
        private const val KEY_DEVICE_ENROLLED = "device_enrolled"
        private const val KEY_FACE_TEMPLATES = "face_templates"
    }

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedPrefs = EncryptedSharedPreferences.create(
        context,
        "ofas_auth_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    private val gson = Gson()
    private val tokenStore = AuthTokenStore(context)
    private val faceTemplatesType = object : TypeToken<List<FaceTemplateData>>() {}.type

    fun saveAuthData(response: LoginResponse) {
        val expiry = parseJwtExpiry(response.accessToken) ?: (System.currentTimeMillis() + 3600000L)
        encryptedPrefs.edit()
            .putString(KEY_ACCESS_TOKEN, response.accessToken)
            .putString(KEY_REFRESH_TOKEN, response.refreshToken)
            .putLong(KEY_TOKEN_EXPIRY, expiry)
            .apply()
        saveUserData(response.user)
    }

    private fun parseJwtExpiry(token: String): Long? {
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

    fun saveUserData(user: UserData) {
        encryptedPrefs.edit()
            .putString(KEY_USER_DATA, gson.toJson(user))
            .apply()
    }

    fun saveFaceTemplates(templates: List<FaceTemplateData>) {
        val normalized = templates.map { data ->
            val raw = data.template
            val encoded = if (!raw.isNullOrBlank() && raw.isHexString()) {
                Base64.encodeToString(hexToBytes(raw), Base64.NO_WRAP)
            } else {
                raw
            }
            data.copy(template = encoded)
        }
        encryptedPrefs.edit()
            .putString(KEY_FACE_TEMPLATES, gson.toJson(normalized))
            .apply()
    }

    fun decodeFaceTemplate(stored: String): ByteArray {
        return if (stored.isHexString()) {
            hexToBytes(stored)
        } else {
            Base64.decode(stored, Base64.NO_WRAP)
        }
    }

    private fun String.isHexString(): Boolean =
        length % 2 == 0 && matches(Regex("[0-9a-fA-F]+"))

    private fun hexToBytes(hex: String): ByteArray =
        hex.chunked(2).map { it.toInt(16).toByte() }.toByteArray()

    fun getFaceTemplates(): List<FaceTemplateData> {
        val json = encryptedPrefs.getString(KEY_FACE_TEMPLATES, null)
        return json?.let { gson.fromJson(it, faceTemplatesType) } ?: emptyList()
    }

    fun getFaceTemplate(surveyorId: String): FaceTemplateData? {
        return getFaceTemplates().firstOrNull { it.surveyorId == surveyorId }
    }

    fun hasFaceTemplate(surveyorId: String): Boolean {
        return getFaceTemplate(surveyorId)?.template?.isNotBlank() == true
    }

    fun updateFaceTemplateLocal(surveyorId: String, template: ByteArray, version: Int) {
        val templateBase64 = Base64.encodeToString(template, Base64.NO_WRAP)
        val templates = getFaceTemplates().toMutableList()
        val index = templates.indexOfFirst { it.surveyorId == surveyorId }
        if (index >= 0) {
            templates[index] = templates[index].copy(template = templateBase64, version = version)
        } else {
            templates.add(FaceTemplateData(surveyorId, templateBase64, version))
        }
        saveFaceTemplates(templates)
    }

    fun saveSurveyorId(id: String) = tokenStore.saveSurveyorId(id)

    fun getSurveyorId(): String? = tokenStore.surveyorId()

    fun getAccessToken(): String? = tokenStore.accessToken()

    fun getRefreshToken(): String? = encryptedPrefs.getString(KEY_REFRESH_TOKEN, null)

    fun getUserData(): UserData? {
        val json = encryptedPrefs.getString(KEY_USER_DATA, null)
        return json?.let { gson.fromJson(it, UserData::class.java) }
    }

    fun markDeviceEnrolled() {
        encryptedPrefs.edit().putBoolean(KEY_DEVICE_ENROLLED, true).apply()
    }

    fun isDeviceEnrolled(): Boolean =
        encryptedPrefs.getBoolean(KEY_DEVICE_ENROLLED, false) && getUserData() != null

    fun isTokenValid(): Boolean {
        val expiry = encryptedPrefs.getLong(KEY_TOKEN_EXPIRY, 0)
        return System.currentTimeMillis() < expiry && !getAccessToken().isNullOrBlank()
    }

    fun clearAuthData() {
        encryptedPrefs.edit().clear().apply()
    }

    fun getAuthHeader(): String? =
        getAccessToken()?.takeIf { it.isNotBlank() }?.let { "Bearer $it" }
}
