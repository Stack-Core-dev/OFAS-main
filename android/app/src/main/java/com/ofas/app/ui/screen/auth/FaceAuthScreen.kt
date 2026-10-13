package com.ofas.app.ui.screen.auth

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ofas.app.ui.screen.startVerificationCamera
import com.ofas.app.viewmodel.FaceVerificationViewModel

@Composable
fun FaceAuthScreen(
    onVerified: () -> Unit,
    onReEnroll: () -> Unit,
    onCancel: () -> Unit
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
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Face Verification", fontSize = 28.sp, color = MaterialTheme.colorScheme.primary)
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            "Confirm this device with your enrolled face to continue.",
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

        if (state is FaceVerificationViewModel.VerificationState.Failed) {
            Spacer(modifier = Modifier.height(16.dp))
            Icon(
                imageVector = Icons.Default.Warning,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.error
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                (state as FaceVerificationViewModel.VerificationState.Failed).message,
                color = MaterialTheme.colorScheme.error
            )
        }

        Spacer(modifier = Modifier.height(24.dp))
        Button(
            onClick = {
                imageAnalyzer?.setCaptureCallback { bitmap -> viewModel.verify(null, bitmap) }
                imageAnalyzer?.captureCurrentFrame()
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            enabled = !isWorking
        ) {
            Icon(Icons.Default.CheckCircle, contentDescription = null)
            Spacer(modifier = Modifier.height(1.dp))
            Text("Verify Face")
        }
        Spacer(modifier = Modifier.height(12.dp))
        OutlinedButton(onClick = onCancel, modifier = Modifier.fillMaxWidth()) {
            Text("Cancel")
        }
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            "Having trouble? Re-register your face",
            color = MaterialTheme.colorScheme.primary,
            modifier = Modifier
                .fillMaxWidth()
                .clickable(onClick = onReEnroll)
                .padding(vertical = 8.dp),
            textAlign = TextAlign.Center
        )
    }
}
