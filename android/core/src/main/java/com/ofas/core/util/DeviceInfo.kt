package com.ofas.core.util

import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.provider.Settings
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class DeviceInfo(private val context: Context) {

    val deviceId: String
        get() = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID) ?: "unknown"

    val model: String
        get() = Build.MODEL

    val manufacturer: String
        get() = Build.MANUFACTURER

    val androidVersion: String
        get() = Build.VERSION.RELEASE

    val sdkInt: Int
        get() = Build.VERSION.SDK_INT

    val isRooted: Boolean
        get() = checkRoot()

    val isDeveloperModeEnabled: Boolean
        get() = Settings.Global.getInt(context.contentResolver, Settings.Global.DEVELOPMENT_SETTINGS_ENABLED, 0) == 1

    val hasMockLocation: Boolean
        get() = checkMockLocation()

    private fun checkRoot(): Boolean {
        val suPaths = arrayOf(
            "/system/bin/su",
            "/system/xbin/su",
            "/sbin/su",
            "/system/su",
            "/system/bin/.ext/.su",
            "/system/app/Superuser.apk",
            "/data/local/xbin/su",
            "/data/local/bin/su"
        )
        if (suPaths.any { java.io.File(it).exists() }) return true
        if (Build.TAGS?.contains("test-keys") == true) return true
        return try {
            val process = java.lang.Runtime.getRuntime().exec(arrayOf("which", "su"))
            val output = process.inputStream.bufferedReader().readText()
            process.waitFor()
            output.trim().isNotEmpty()
        } catch (e: Exception) {
            false
        }
    }

    private fun checkMockLocation(): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as android.location.LocationManager
            return try {
                val method = locationManager.javaClass.getMethod("isMockLocationEnabled")
                method.invoke(locationManager) as Boolean
            } catch (e: Exception) {
                false
            }
        }
        return false
    }

    fun getEncryptedPrefs(): android.content.SharedPreferences {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        return EncryptedSharedPreferences.create(
            context,
            "ofas_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun getAppVersion(): String {
        return try {
            context.packageManager.getPackageInfo(context.packageName, 0).versionName
        } catch (e: PackageManager.NameNotFoundException) {
            "unknown"
        }
    }

    @Suppress("DEPRECATION")
    fun getAppVersionCode(): Int {
        return try {
            context.packageManager.getPackageInfo(context.packageName, 0).versionCode
        } catch (e: PackageManager.NameNotFoundException) {
            0
        }
    }
}
