package com.ofas.app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ofas.app.repository.AuthRepository
import com.ofas.data.sync.ApiService
import com.ofas.data.sync.FaceTemplateData
import com.ofas.data.sync.LoginRequest
import com.ofas.data.sync.LoginResponse
import com.ofas.data.sync.SyncFieldsResponse
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
        data class RequiresFaceEnrollment(val user: UserData) : AuthState()
        data object Unauthenticated : AuthState()
    }

    init {
        checkAuthStatus()
    }

    private fun checkAuthStatus() {
        val user = authRepository.getUserData()
        if (user != null && (authRepository.isDeviceEnrolled() || authRepository.isTokenValid())) {
            val surveyorId = authRepository.getSurveyorId() ?: user.id
            if (user.role == "surveyor" && !authRepository.hasFaceTemplate(surveyorId)) {
                _authState.value = AuthState.RequiresFaceEnrollment(user)
            } else {
                _authState.value = AuthState.RequiresFaceAuth(user)
            }
        } else {
            _authState.value = AuthState.Unauthenticated
        }
    }

    fun login(username: String, password: String, totpToken: String? = null) {
        _isLoading.value = true
        _error.value = null

        viewModelScope.launch {
            try {
                val response = apiService.login(
                    LoginRequest(username.trim(), password.trim(), totpToken)
                )
                if (response.isSuccessful && response.body() != null) {
                    val loginResponse = response.body()!!
                    authRepository.saveAuthData(loginResponse)
                    if (loginResponse.user.role == "surveyor") {
                        val syncResult = syncAssignedFields()
                        if (!syncResult) {
                            authRepository.clearAuthData()
                            _error.value = "Login succeeded, but assigned fields could not be downloaded."
                            _authState.value = AuthState.Unauthenticated
                            return@launch
                        }
                        // Check if surveyor has face template after sync
                        val surveyorId = authRepository.getSurveyorId() ?: loginResponse.user.id
                        if (!authRepository.hasFaceTemplate(surveyorId)) {
                            _authState.value = AuthState.RequiresFaceEnrollment(loginResponse.user)
                        } else {
                            _authState.value = AuthState.RequiresFaceAuth(loginResponse.user)
                        }
                    } else {
                        _authState.value = AuthState.Authenticated(loginResponse.user)
                    }
                } else {
                    _error.value = loginErrorMessage(response, response.errorBody()?.string())
                    _authState.value = AuthState.Unauthenticated
                }
            } catch (e: Exception) {
                android.util.Log.e("AuthViewModel", "login failed", e)
                _error.value = "Network error: ${e.message ?: "unable to contact server"}"
                _authState.value = AuthState.Unauthenticated
            } finally {
                _isLoading.value = false
            }
        }

    }

    private fun loginErrorMessage(response: retrofit2.Response<*>, body: String?): String {
        val serverMessage = try {
            body?.takeIf { it.isNotBlank() }
                ?.let { org.json.JSONObject(it).optString("error", "") }
                .orEmpty()
        } catch (_: Exception) {
            ""
        }
        return when {
            serverMessage.isNotBlank() -> serverMessage
            response.code() == 429 -> "Too many attempts. Please wait a minute and try again."
            response.code() == 401 -> "Invalid username or password."
            response.code() >= 500 -> "Server error. Please try again later."
            else -> response.message().ifBlank { "Login failed" }
        }
    }

    private suspend fun syncAssignedFields(): Boolean {
        val authHeader = authRepository.getAuthHeader() ?: return false
        return try {
            val response = apiService.getAssignedFields(authHeader)
            if (!response.isSuccessful || response.body() == null) {
                val msg = response.message().ifBlank { "Failed to sync assigned fields" }
                _error.value = "Field sync failed: $msg"
                return false
            }
            val syncResponse = response.body()!!
            val fields = syncResponse.fields.map { it.toEntity() }
            fieldRepository.replaceAssignedFields(fields)
            authRepository.saveSurveyorId(syncResponse.surveyorId)
            authRepository.saveFaceTemplates(syncResponse.faceTemplates)
            true
        } catch (e: Exception) {
            _error.value = "Field sync error: ${e.message ?: "unknown error"}"
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

    fun completeFaceEnrollment() {
        val currentState = _authState.value
        val user = when (currentState) {
            is AuthState.RequiresFaceEnrollment -> currentState.user
            is AuthState.RequiresFaceAuth -> currentState.user
            else -> null
        }
        if (user != null) {
            authRepository.markDeviceEnrolled()
            _authState.value = AuthState.Authenticated(user)
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
