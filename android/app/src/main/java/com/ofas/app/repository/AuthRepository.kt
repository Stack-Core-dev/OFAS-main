package com.ofas.app.repository

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.google.gson.Gson
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

    fun saveAuthData(response: LoginResponse) {
        encryptedPrefs.edit()
            .putString(KEY_ACCESS_TOKEN, response.accessToken)
            .putString(KEY_REFRESH_TOKEN, response.refreshToken)
            .putLong(KEY_TOKEN_EXPIRY, System.currentTimeMillis() + 3600000)
            .apply()
        saveUserData(response.user)
    }

    fun saveUserData(user: UserData) {
        encryptedPrefs.edit()
            .putString(KEY_USER_DATA, gson.toJson(user))
            .apply()
    }

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
