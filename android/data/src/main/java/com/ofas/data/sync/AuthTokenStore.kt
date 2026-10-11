package com.ofas.data.sync

import android.content.Context
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

    fun surveyorId(): String? = preferences.getString("surveyor_id", null)

    fun saveSurveyorId(id: String) {
        preferences.edit().putString("surveyor_id", id).apply()
    }
}
