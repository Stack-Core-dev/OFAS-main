package com.ofas.security.keystore

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import androidx.security.crypto.MasterKeys
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.PrivateKey
import java.security.PublicKey
import java.security.Signature
import java.security.spec.X509EncodedKeySpec
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec

class KeyManager private constructor(private val context: Context) {

    companion object {
        private const val KEY_ALIAS = "ofas_signing_key"
        private const val ANDROID_KEY_STORE = "AndroidKeyStore"
        private var INSTANCE: KeyManager? = null

        fun getInstance(context: Context): KeyManager {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: KeyManager(context.applicationContext).also { INSTANCE = it }
            }
        }

        fun initialize(context: Context) {
            getInstance(context)
        }
    }

    private val keyStore: KeyStore = KeyStore.getInstance(ANDROID_KEY_STORE).apply { load(null) }
    private val keyPair: java.security.KeyPair = generateOrLoadKeyPair()

    private fun generateOrLoadKeyPair(): java.security.KeyPair {
        if (keyStore.containsAlias(KEY_ALIAS)) {
            val privateKey = keyStore.getKey(KEY_ALIAS, null) as PrivateKey
            val certificate = keyStore.getCertificate(KEY_ALIAS)
            return java.security.KeyPair(certificate.publicKey, privateKey)
        }

        val keyPairGenerator = KeyPairGenerator.getInstance(KeyProperties.KEY_ALGORITHM_EC, ANDROID_KEY_STORE)
        val spec = KeyGenParameterSpec.Builder(KEY_ALIAS, KeyProperties.PURPOSE_SIGN)
            .setAlgorithmParameterSpec(java.security.spec.ECGenParameterSpec("secp256r1"))
            .setDigests(KeyProperties.DIGEST_SHA256)
            .setUserAuthenticationRequired(false)
            .setInvalidatedByBiometricEnrollment(false)
            .build()
        keyPairGenerator.initialize(spec)
        return keyPairGenerator.generateKeyPair()
    }

    fun getPublicKey(): PublicKey = keyPair.public

    fun getPublicKeyPem(): String {
        val publicKey = getPublicKey()
        val encoded = publicKey.encoded
        val base64 = Base64.encodeToString(encoded, Base64.NO_WRAP)
        return "-----BEGIN PUBLIC KEY-----\n$base64\n-----END PUBLIC KEY-----"
    }

    fun getKeyId(): String {
        val publicKey = getPublicKey()
        val encoded = publicKey.encoded
        val sha256 = java.security.MessageDigest.getInstance("SHA-256").digest(encoded)
        return Base64.encodeToString(sha256, Base64.NO_WRAP or Base64.URL_SAFE).substring(0, 16)
    }

    fun sign(data: ByteArray): ByteArray {
        val signature = Signature.getInstance("SHA256withECDSA")
        signature.initSign(keyPair.private)
        signature.update(data)
        return signature.sign()
    }

    fun verify(data: ByteArray, signatureBytes: ByteArray, publicKeyPem: String): Boolean {
        try {
            val publicKey = parsePublicKey(publicKeyPem)
            val signature = Signature.getInstance("SHA256withECDSA")
            signature.initVerify(publicKey)
            signature.update(data)
            return signature.verify(signatureBytes)
        } catch (e: Exception) {
            return false
        }
    }

    private fun parsePublicKey(pem: String): PublicKey {
        val base64 = pem.replace("-----BEGIN PUBLIC KEY-----", "")
            .replace("-----END PUBLIC KEY-----", "")
            .replace("\n", "")
            .trim()
        val encoded = Base64.decode(base64, Base64.NO_WRAP)
        val spec = X509EncodedKeySpec(encoded)
        val keyFactory = java.security.KeyFactory.getInstance("EC")
        return keyFactory.generatePublic(spec)
    }

    fun encryptData(data: ByteArray): ByteArray {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)
        val masterKey = keyStore.getKey(masterKeyAlias, null) as javax.crypto.SecretKey
        cipher.init(Cipher.ENCRYPT_MODE, masterKey)
        return cipher.iv + cipher.doFinal(data)
    }

    fun decryptData(encryptedData: ByteArray): ByteArray {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)
        val masterKey = keyStore.getKey(masterKeyAlias, null) as javax.crypto.SecretKey
        require(encryptedData.size > 12) { "Encrypted payload is missing its IV" }
        val iv = encryptedData.copyOfRange(0, 12)
        val ciphertext = encryptedData.copyOfRange(12, encryptedData.size)
        cipher.init(Cipher.DECRYPT_MODE, masterKey, GCMParameterSpec(128, iv))
        return cipher.doFinal(ciphertext)
    }
}