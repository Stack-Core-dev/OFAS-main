package com.ofas.data.face

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Matrix
import android.util.Log
import com.ofas.security.keystore.KeyManager
import org.tensorflow.lite.DataType
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.FloatBuffer

class FaceVerifier private constructor(
    private val context: Context,
    private val keyManager: KeyManager
) {

    companion object {
        private const val TAG = "FaceVerifier"
        private const val MODEL_PATH = "face_embedding.tflite"
        private const val INPUT_SIZE = 112
        private const val EMBEDDING_SIZE = 512
        private const val MATCH_THRESHOLD = 0.6f
        private var INSTANCE: FaceVerifier? = null

        fun getInstance(context: Context, keyManager: KeyManager): FaceVerifier {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: FaceVerifier(
                    context.applicationContext,
                    keyManager
                ).also { INSTANCE = it }
            }
        }

        fun initialize(context: Context, keyManager: KeyManager) {
            getInstance(context, keyManager)
        }
    }

    private val interpreter: Interpreter by lazy {
        val modelFile = copyModelToFile()
        Interpreter(modelFile)
    }

    private fun copyModelToFile(): java.io.File {
        val file = java.io.File(context.cacheDir, MODEL_PATH)
        if (!file.exists()) {
            context.assets.open(MODEL_PATH).use { input ->
                file.outputStream().use { output ->
                    input.copyTo(output)
                }
            }
        }
        return file
    }

    fun extractEmbedding(bitmap: Bitmap): ByteArray? {
        val resized = resizeBitmap(bitmap, INPUT_SIZE, INPUT_SIZE)
        val tensorImage = TensorImage.fromBitmap(resized)
        val inputBuffer = TensorBuffer.createFixedSize(intArrayOf(1, INPUT_SIZE, INPUT_SIZE, 3), DataType.FLOAT32)
        inputBuffer.loadBuffer(tensorImage.buffer)

        val outputBuffer = TensorBuffer.createFixedSize(intArrayOf(1, EMBEDDING_SIZE), DataType.FLOAT32)
        interpreter.run(inputBuffer.buffer, outputBuffer.buffer)

        val embedding = FloatBuffer.wrap(outputBuffer.floatArray)
        val byteBuffer = ByteBuffer.allocate(EMBEDDING_SIZE * 4).order(ByteOrder.nativeOrder())
        byteBuffer.asFloatBuffer().put(embedding)
        return byteBuffer.array()
    }

    fun compareEmbeddings(embedding1: ByteArray, embedding2: ByteArray): Float {
        val float1 = ByteBuffer.wrap(embedding1).order(ByteOrder.nativeOrder()).asFloatBuffer()
        val float2 = ByteBuffer.wrap(embedding2).order(ByteOrder.nativeOrder()).asFloatBuffer()

        var dotProduct = 0f
        var norm1 = 0f
        var norm2 = 0f

        for (i in 0 until EMBEDDING_SIZE) {
            val v1 = float1.get(i)
            val v2 = float2.get(i)
            dotProduct += v1 * v2
            norm1 += v1 * v1
            norm2 += v2 * v2
        }

        return if (norm1 > 0 && norm2 > 0) {
            dotProduct / (Math.sqrt(norm1.toDouble()) * Math.sqrt(norm2.toDouble())).toFloat()
        } else 0f
    }

    fun verifyFace(liveEmbedding: ByteArray, storedEmbedding: ByteArray): Boolean {
        val similarity = compareEmbeddings(liveEmbedding, storedEmbedding)
        Log.d(TAG, "Face similarity: $similarity (threshold: $MATCH_THRESHOLD)")
        return similarity >= MATCH_THRESHOLD
    }

    fun detectBlink(bitmap: Bitmap): Boolean {
        // A liveness result must never be fabricated. The production liveness
        // pipeline must provide a real blink result before a visit is accepted.
        return false
    }

    private fun resizeBitmap(bitmap: Bitmap, width: Int, height: Int): Bitmap {
        val matrix = Matrix()
        val scaleX = width / bitmap.width.toFloat()
        val scaleY = height / bitmap.height.toFloat()
        matrix.postScale(scaleX, scaleY)
        return Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
    }

    fun close() {
        interpreter.close()
    }
}