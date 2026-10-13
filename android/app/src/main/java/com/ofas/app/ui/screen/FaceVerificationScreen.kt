package com.ofas.app.ui.screen

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.google.common.util.concurrent.ListenableFuture
import com.ofas.app.ui.screen.auth.FaceCaptureAnalyzer
import com.ofas.app.viewmodel.FaceVerificationViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.asExecutor

@Composable
fun FaceVerificationScreen(
    surveyorId: String,
    fieldId: String,
    onVerified: () -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val viewModel: FaceVerificationViewModel = hiltViewModel()
    val previewView = remember { PreviewView(context) }
    var imageAnalyzer by remember { mutableStateOf<FaceCaptureAnalyzer?>(null) }
    var permissionGranted by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) ==
                PackageManager.PERMISSION_GRANTED
        )
    }
    val requestPermission = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { permissionGranted = it }
    var cameraError by remember { mutableStateOf<String?>(null) }

    val state by viewModel.state.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        if (!permissionGranted) requestPermission.launch(Manifest.permission.CAMERA)
    }

    LaunchedEffect(permissionGranted) {
        if (permissionGranted) {
            startVerificationCamera(context, lifecycleOwner, previewView, onError = { cameraError = it }) { analyzer ->
                imageAnalyzer = analyzer
            }
        }
    }

    LaunchedEffect(state) {
        if (state is FaceVerificationViewModel.VerificationState.Verified) {
            viewModel.reset()
            onVerified()
        }
    }

    val isWorking = state is FaceVerificationViewModel.VerificationState.Verifying

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Face Verification",
            fontSize = 28.sp,
            color = MaterialTheme.colorScheme.onSurface
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Confirm your identity before visiting field $fieldId.",
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(16.dp))

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(280.dp)
        ) {
            AndroidView(
                factory = { previewView },
                modifier = Modifier.fillMaxSize()
            )
            if (!permissionGranted) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black.copy(alpha = 0.6f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        "Camera permission is required. Enable it in Settings > Apps > OFAS > Permissions > Camera.",
                        color = Color.White,
                        modifier = Modifier.padding(16.dp)
                    )
                }
            }
            if (cameraError != null) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black.copy(alpha = 0.7f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        "Camera error: $cameraError",
                        color = Color.White,
                        modifier = Modifier.padding(16.dp)
                    )
                }
            }
            if (isWorking) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black.copy(alpha = 0.5f)),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(color = Color.White)
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
        VerificationStatusRow("Surveyor", surveyorId)
        VerificationStatusRow("Field", fieldId)

        when (val current = state) {
            is FaceVerificationViewModel.VerificationState.Failed -> {
                Spacer(modifier = Modifier.height(12.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Warning,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.error
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(current.message, color = MaterialTheme.colorScheme.error)
                }
            }
            is FaceVerificationViewModel.VerificationState.Verified -> {
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    "Verified (score ${(current.score * 100).toInt()}%)",
                    color = MaterialTheme.colorScheme.primary
                )
            }
            else -> {}
        }

        Spacer(modifier = Modifier.weight(1f))
        Button(
            onClick = { captureAndVerify(imageAnalyzer, viewModel, surveyorId) },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            enabled = !isWorking,
            shape = RoundedCornerShape(16.dp)
        ) {
            Icon(Icons.Default.CheckCircle, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text(if (state is FaceVerificationViewModel.VerificationState.Failed) "Retry Verification" else "Capture & Verify")
        }
    }
}

@Composable
private fun VerificationStatusRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, color = MaterialTheme.colorScheme.onSurface)
    }
}

private fun captureAndVerify(
    analyzer: FaceCaptureAnalyzer?,
    viewModel: FaceVerificationViewModel,
    surveyorId: String
) {
    analyzer?.setCaptureCallback { bitmap ->
        viewModel.verify(surveyorId, bitmap)
    }
    analyzer?.captureCurrentFrame()
}

internal fun startVerificationCamera(
    context: Context,
    lifecycleOwner: LifecycleOwner,
    previewView: PreviewView,
    onError: (String) -> Unit = {},
    onAnalyzerReady: (FaceCaptureAnalyzer) -> Unit
) {
    val cameraProviderFuture: ListenableFuture<ProcessCameraProvider> =
        ProcessCameraProvider.getInstance(context)
    cameraProviderFuture.addListener({
        try {
            val cameraProvider = cameraProviderFuture.get()
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }

            val analyzer = FaceCaptureAnalyzer()
            val imageAnalysis = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
                .also { it.setAnalyzer(Dispatchers.IO.asExecutor(), analyzer) }

            val cameraSelector = if (cameraProvider.hasCamera(CameraSelector.DEFAULT_FRONT_CAMERA)) {
                CameraSelector.DEFAULT_FRONT_CAMERA
            } else {
                CameraSelector.DEFAULT_BACK_CAMERA
            }

            cameraProvider.unbindAll()
            cameraProvider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                preview,
                imageAnalysis
            )
            onAnalyzerReady(analyzer)
        } catch (e: Throwable) {
            android.util.Log.w("FaceVerification", "Camera start failed", e)
            onError(e.message ?: e.javaClass.simpleName)
        }
    }, ContextCompat.getMainExecutor(context))
}
