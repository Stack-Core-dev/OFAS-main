package com.ofas.data.face

import android.content.Context
import android.graphics.Bitmap
import android.util.Log
import com.google.android.gms.tasks.Tasks
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.face.FaceDetection
import com.google.mlkit.vision.face.FaceDetector
import com.google.mlkit.vision.face.FaceDetectorOptions
import com.ofas.security.keystore.KeyManager
import org.tensorflow.lite.Interpreter
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder

class FaceVerifier private constructor(
    private val context: Context,
    private val keyManager: KeyManager
) {

    companion object {
        private const val TAG = "FaceVerifier"
        private const val MODEL_PATH = "face_embedding.tflite"
        private const val INPUT_SIZE = 112
        private const val EMBEDDING_SIZE = 192

        // MobileFaceNet embeddings are compared by Euclidean distance (lower = closer).
        // A genuine match on a well-cropped face is typically well under this value,
        // while two different people stay above it.
        const val MATCH_THRESHOLD = 0.8f

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
        Interpreter(modelFile, Interpreter.Options().setNumThreads(2))
    }

    private val faceDetector: FaceDetector by lazy {
        val options = FaceDetectorOptions.Builder()
            .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
            .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_NONE)
            .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_NONE)
            .setMinFaceSize(0.15f)
            .build()
        FaceDetection.getClient(options)
    }

    private fun copyModelToFile(): File {
        val file = File(context.cacheDir, MODEL_PATH)
        if (!file.exists()) {
            context.assets.open(MODEL_PATH).use { input ->
                file.outputStream().use { output ->
                    input.copyTo(output)
                }
            }
        }
        return file
    }

    /**
     * Detects the largest face in [bitmap], crops it and returns a 192-float
     * embedding. Returns null when no face is detected so callers can retry
     * instead of comparing a meaningless embedding.
     */
    fun extractEmbedding(bitmap: Bitmap): ByteArray? {
        val faceBitmap = cropLargestFace(bitmap) ?: return null
        val prepared = Bitmap.createScaledBitmap(faceBitmap, INPUT_SIZE, INPUT_SIZE, true)

        val input = ByteBuffer
            .allocateDirect(1 * INPUT_SIZE * INPUT_SIZE * 3 * 4)
            .order(ByteOrder.nativeOrder())

        val pixels = IntArray(INPUT_SIZE * INPUT_SIZE)
        prepared.getPixels(pixels, 0, INPUT_SIZE, 0, 0, INPUT_SIZE, INPUT_SIZE)
        for (pixel in pixels) {
            input.putFloat(((pixel shr 16 and 0xFF) - 128) / 128f)
            input.putFloat(((pixel shr 8 and 0xFF) - 128) / 128f)
            input.putFloat(((pixel and 0xFF) - 128) / 128f)
        }
        input.rewind()

        val output = ByteBuffer
            .allocateDirect(1 * EMBEDDING_SIZE * 4)
            .order(ByteOrder.nativeOrder())

        interpreter.run(input, output)

        output.rewind()
        val embedding = ByteArray(EMBEDDING_SIZE * 4)
        output.get(embedding)
        return embedding
    }

    private fun cropLargestFace(bitmap: Bitmap): Bitmap? {
        val faces = try {
            Tasks.await(faceDetector.process(InputImage.fromBitmap(bitmap, 0)))
        } catch (e: Exception) {
            Log.w(TAG, "Face detection failed", e)
            return null
        }

        val face = faces.maxByOrNull { it.boundingBox.width() * it.boundingBox.height() }
            ?: run {
                Log.d(TAG, "No face detected")
                return null
            }

        val box = face.boundingBox
        val pad = (box.width() * 0.25f).toInt().coerceAtLeast(8)
        val left = (box.left - pad).coerceAtLeast(0)
        val top = (box.top - pad).coerceAtLeast(0)
        val right = (box.right + pad).coerceAtMost(bitmap.width)
        val bottom = (box.bottom + pad).coerceAtMost(bitmap.height)

        val width = right - left
        val height = bottom - top
        if (width <= 0 || height <= 0) return null

        return Bitmap.createBitmap(bitmap, left, top, width, height)
    }

    fun compareEmbeddings(embedding1: ByteArray, embedding2: ByteArray): Float {
        val float1 = ByteBuffer.wrap(embedding1).order(ByteOrder.nativeOrder()).asFloatBuffer()
        val float2 = ByteBuffer.wrap(embedding2).order(ByteOrder.nativeOrder()).asFloatBuffer()

        var sum = 0.0
        for (i in 0 until EMBEDDING_SIZE) {
            val diff = float1.get(i) - float2.get(i)
            sum += diff.toDouble() * diff.toDouble()
        }
        return Math.sqrt(sum).toFloat()
    }

    fun verifyFace(liveEmbedding: ByteArray, storedEmbedding: ByteArray): Boolean {
        val distance = compareEmbeddings(liveEmbedding, storedEmbedding)
        Log.d(TAG, "Face distance: $distance (threshold: $MATCH_THRESHOLD)")
        return distance <= MATCH_THRESHOLD
    }

    fun detectBlink(bitmap: Bitmap): Boolean {
        // A liveness result must never be fabricated. The production liveness
        // pipeline must provide a real blink result before a visit is accepted.
        return false
    }

    fun close() {
        interpreter.close()
        faceDetector.close()
    }
}