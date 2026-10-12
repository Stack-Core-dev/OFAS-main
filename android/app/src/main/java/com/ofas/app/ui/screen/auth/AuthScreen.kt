package com.ofas.app.ui.screen.auth

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ofas.app.viewmodel.AuthViewModel
import com.ofas.app.ui.navigation.NavRoutes

@Composable
fun AuthScreen(
    navController: androidx.navigation.NavHostController,
    authViewModel: AuthViewModel = hiltViewModel()
) {
    var currentScreen by remember { mutableStateOf(AuthScreenType.Login) }

    val authState by authViewModel.authState.collectAsStateWithLifecycle()
    val isLoading by authViewModel.isLoading.collectAsStateWithLifecycle()
    val error by authViewModel.error.collectAsStateWithLifecycle()

    androidx.compose.runtime.LaunchedEffect(authState) {
        when (authState) {
            is AuthViewModel.AuthState.Authenticated -> {
                navController.navigate(NavRoutes.HOME) {
                    popUpTo(NavRoutes.AUTH) { inclusive = true }
                }
            }
            is AuthViewModel.AuthState.RequiresFaceAuth -> {
                currentScreen = AuthScreenType.FaceAuth
            }
            is AuthViewModel.AuthState.RequiresFaceEnrollment -> {
                currentScreen = AuthScreenType.FaceEnrollment
            }
            is AuthViewModel.AuthState.Unauthenticated -> {
                currentScreen = AuthScreenType.Login
            }
            else -> {}
        }
    }

    when (currentScreen) {
        AuthScreenType.Login -> {
            LoginScreen(
                onLogin = { username, password ->
                    authViewModel.login(username, password)
                },
                isLoading = isLoading,
                error = error
            )
        }
        AuthScreenType.FaceAuth -> {
            FaceAuthScreen(
                onVerified = {
                    authViewModel.completeFaceAuth()
                },
                onCancel = {
                    currentScreen = AuthScreenType.Login
                    authViewModel.logout()
                }
            )
        }
        AuthScreenType.FaceEnrollment -> {
            FaceEnrollmentScreen(
                onEnrolled = {
                    authViewModel.completeFaceEnrollment()
                },
                onCancel = {
                    currentScreen = AuthScreenType.Login
                    authViewModel.logout()
                }
            )
        }
    }
}

enum class AuthScreenType {
    Login, FaceAuth, FaceEnrollment
}