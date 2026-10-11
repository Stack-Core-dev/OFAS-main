package com.ofas.app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ofas.app.repository.AuthRepository
import com.ofas.data.sync.ApiService
import com.ofas.data.sync.LoginRequest
import com.ofas.data.sync.LoginResponse
import com.ofas.data.sync.UserData
import com.ofas.data.repository.FieldRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val apiService: ApiService,
    private val fieldRepository: FieldRepository
) : ViewModel() {

    private val _authState = MutableStateFlow<AuthState>(AuthState.Idle)
    val authState = _authState.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error = _error.asStateFlow()

    sealed class AuthState {
        data object Idle : AuthState()
        data class Authenticated(val user: UserData) : AuthState()
        data class RequiresFaceAuth(val user: UserData) : AuthState()
        data object Unauthenticated : AuthState()
    }

    init {
        checkAuthStatus()
    }

    private fun checkAuthStatus() {
        val user = authRepository.getUserData()
        if (user != null && (authRepository.isDeviceEnrolled() || authRepository.isTokenValid())) {
            _authState.value = AuthState.RequiresFaceAuth(user)
        } else {
            _authState.value = AuthState.Unauthenticated
        }
    }

    fun login(username: String, password: String, totpToken: String? = null) {
        _isLoading.value = true
        _error.value = null

        viewModelScope.launch {
            try {
                val response = apiService.login(LoginRequest(username, password, totpToken))
                if (response.isSuccessful && response.body() != null) {
                    val loginResponse = response.body()!!
                    authRepository.saveAuthData(loginResponse)
                    if (loginResponse.user.role == "surveyor" && !syncAssignedFields()) {
                        authRepository.clearAuthData()
                        _error.value = "Login succeeded, but assigned fields could not be downloaded."
                        _authState.value = AuthState.Unauthenticated
                        return@launch
                    }
                    _authState.value = AuthState.RequiresFaceAuth(loginResponse.user)
                } else {
                    _error.value = response.message().ifBlank { "Login failed" }
                    _authState.value = AuthState.Unauthenticated
                }
            } catch (e: Exception) {
                _error.value = "Network error: ${e.message ?: "unable to contact server"}"
                _authState.value = AuthState.Unauthenticated
            } finally {
                _isLoading.value = false
            }
        }

    }

    private suspend fun syncAssignedFields(): Boolean {
        val authHeader = authRepository.getAuthHeader() ?: return false
        return try {
            val response = apiService.getAssignedFields(authHeader)
            if (!response.isSuccessful || response.body() == null) return false
            val fields = response.body()!!.fields.map { it.toEntity() }
            fieldRepository.replaceAssignedFields(fields)
            true
        } catch (_: Exception) {
            false
        }
    }

    fun completeFaceAuth() {
        val currentState = _authState.value
        if (currentState is AuthState.RequiresFaceAuth) {
            authRepository.markDeviceEnrolled()
            _authState.value = AuthState.Authenticated(currentState.user)
        }
    }

    fun logout() {
        authRepository.clearAuthData()
        _authState.value = AuthState.Unauthenticated
    }

    fun refreshToken() {
        viewModelScope.launch {
            val refreshToken = authRepository.getRefreshToken()
            if (refreshToken.isNullOrBlank()) {
                logout()
                return@launch
            }

            try {
                val response = apiService.refreshToken("Bearer $refreshToken")
                if (response.isSuccessful && response.body() != null) {
                    val loginResponse = response.body()!!
                    authRepository.saveAuthData(loginResponse)
                    authRepository.getUserData()?.let {
                        _authState.value = AuthState.Authenticated(it)
                    }
                } else {
                    logout()
                }
            } catch (_: Exception) {
                logout()
            }
        }
    }

    fun getAuthHeader(): String? = authRepository.getAuthHeader()
}
