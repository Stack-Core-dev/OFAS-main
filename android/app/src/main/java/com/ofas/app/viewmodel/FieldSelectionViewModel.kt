package com.ofas.app.viewmodel

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ofas.data.model.FieldEntity
import com.ofas.data.repository.FieldRepository
import com.ofas.data.sync.ApiService
import com.ofas.data.sync.AuthTokenStore
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class FieldSelectionViewModel @Inject constructor(
    private val fieldRepository: FieldRepository,
    private val apiService: ApiService,
    @ApplicationContext context: Context
) : ViewModel() {
    private val tokenStore = AuthTokenStore(context)
    private val _fields = MutableStateFlow<List<FieldEntity>>(emptyList())
    val fields = _fields.asStateFlow()
    private val _surveyorId = MutableStateFlow<String?>(null)
    val surveyorId = _surveyorId.asStateFlow()

    init {
        _surveyorId.value = tokenStore.surveyorId()
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            val token = tokenStore.accessToken()
            if (!token.isNullOrBlank()) {
                runCatching {
                    apiService.getAssignedFields("Bearer $token")
                }.getOrNull()?.takeIf { it.isSuccessful }?.body()?.let { response ->
                    val entities = response.fields.map { it.toEntity() }
                    fieldRepository.replaceAssignedFields(entities)
                    _fields.value = entities
                    _surveyorId.value = response.surveyorId
                    tokenStore.saveSurveyorId(response.surveyorId)
                    return@launch
                }
            }
            _fields.value = fieldRepository.getAllActive()
        }
    }
}
