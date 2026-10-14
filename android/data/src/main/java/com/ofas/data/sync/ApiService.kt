package com.ofas.data.sync

import com.ofas.data.model.VisitEntity
import com.ofas.data.model.FieldEntity
import com.ofas.data.model.SurveyorEntity
import com.ofas.data.model.TrailEntryEntity
import com.ofas.data.model.PhoneEntity
import com.ofas.data.model.AssignmentEntity
import retrofit2.Response
import retrofit2.http.*
import com.squareup.moshi.Json

interface ApiService {

    @GET("api/sync/fields")
    suspend fun getAssignedFields(@Header("Authorization") authHeader: String): Response<SyncFieldsResponse>

    @POST("api/sync/submit")
    suspend fun submitVisit(
        @Header("Authorization") authHeader: String,
        @Body request: SubmitVisitRequest
    ): Response<SubmitVisitResponse>

    @GET("api/sync/status")
    suspend fun getSyncStatus(@Header("Authorization") authHeader: String): Response<SyncStatusResponse>

    @POST("api/sync/location")
    suspend fun uploadLocationPings(
        @Header("Authorization") authHeader: String,
        @Body request: LocationPingRequest
    ): Response<LocationPingResponse>

    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @POST("api/auth/refresh")
    suspend fun refreshToken(@Header("Authorization") authHeader: String): Response<LoginResponse>

    @GET("api/admin/surveyors")
    suspend fun getSurveyors(@Header("Authorization") authHeader: String): Response<SurveyorsResponse>

    @GET("api/admin/fields")
    suspend fun getFields(@Header("Authorization") authHeader: String): Response<FieldsResponse>

    @GET("api/admin/phones")
    suspend fun getPhones(@Header("Authorization") authHeader: String): Response<PhonesResponse>

    @GET("api/admin/assignments")
    suspend fun getAssignments(@Header("Authorization") authHeader: String): Response<AssignmentsResponse>

    @GET("api/review/visits")
    suspend fun getVisitsForReview(@Header("Authorization") authHeader: String): Response<VisitsResponse>

    @POST("api/review/visits/{visitId}/review")
    suspend fun reviewVisit(
        @Header("Authorization") authHeader: String,
        @Path("visitId") visitId: String,
        @Body request: ReviewRequest
    ): Response<ReviewResponse>

    @GET("api/review/stats")
    suspend fun getReviewStats(@Header("Authorization") authHeader: String): Response<StatsResponse>

    @POST("api/face/enroll")
    suspend fun enrollFaceTemplate(
        @Header("Authorization") authHeader: String,
        @Body request: EnrollFaceTemplateRequest
    ): Response<EnrollFaceTemplateResponse>

    @GET("api/face/enroll/status")
    suspend fun getFaceEnrollmentStatus(@Header("Authorization") authHeader: String): Response<FaceEnrollmentStatusResponse>

    @GET("api/auth/me")
    suspend fun getAccount(@Header("Authorization") authHeader: String): Response<AccountData>

    @POST("api/auth/change-password")
    suspend fun changePassword(
        @Header("Authorization") authHeader: String,
        @Body request: ChangePasswordRequest
    ): Response<ChangePasswordResponse>

    @POST("api/auth/register-device")
    suspend fun registerDevice(
        @Header("Authorization") authHeader: String,
        @Body request: RegisterDeviceRequest
    ): Response<RegisterDeviceResponse>
}

data class SyncFieldsResponse(
    val fields: List<SyncFieldData>,
    @Json(name = "face_templates") val faceTemplates: List<FaceTemplateData>,
    @Json(name = "surveyor_id") val surveyorId: String
)

data class SyncFieldData(
    val id: String,
    @Json(name = "field_code") val fieldCode: String,
    val name: String,
    @Json(name = "crop_type") val cropType: String?,
    @Json(name = "center_lat") val centerLat: Double,
    @Json(name = "center_lon") val centerLon: Double,
    @Json(name = "radius_meters") val radiusMeters: Double,
    @Json(name = "is_active") val isActive: Boolean = true
) {
    fun toEntity() = FieldEntity(
        id = id,
        fieldCode = fieldCode,
        name = name,
        cropType = cropType,
        centerLat = centerLat,
        centerLon = centerLon,
        radiusMeters = radiusMeters,
        isActive = isActive
    )
}

data class FaceTemplateData(
    @Json(name = "surveyor_id") val surveyorId: String,
    val template: String?,
    val version: Int
)

data class SubmitVisitRequest(
    @Json(name = "visit_id") val visitId: String,
    @Json(name = "surveyor_id") val surveyorId: String,
    @Json(name = "field_id") val fieldId: String,
    @Json(name = "phone_id") val phoneId: String,
    @Json(name = "satellite_timestamp") val satelliteTimestamp: String,
    val latitude: Double,
    val longitude: Double,
    @Json(name = "accuracy_meters") val accuracyMeters: Double,
    val altitude: Double?,
    val speed: Double?,
    val bearing: Double?,
    @Json(name = "selfie_photo_hash") val selfiePhotoHash: String,
    @Json(name = "selfie_photo_s3_key") val selfiePhotoS3Key: String?,
    @Json(name = "selfie_latitude") val selfieLatitude: Double?,
    @Json(name = "selfie_longitude") val selfieLongitude: Double?,
    @Json(name = "selfie_accuracy_meters") val selfieAccuracyMeters: Double?,
    @Json(name = "field_photos") val fieldPhotos: List<PhotoData>,
    @Json(name = "face_match_score") val faceMatchScore: Float,
    @Json(name = "liveness_verified") val livenessVerified: Boolean,
    @Json(name = "trail_snapshot") val trailSnapshot: TrailSnapshot,
    val signature: String,
    @Json(name = "signed_by_key_id") val signedByKeyId: String
)

data class PhotoData(
    val hash: String,
    @Json(name = "s3_key") val s3Key: String? = null,
    val timestamp: String?,
    val latitude: Double? = null,
    val longitude: Double? = null,
    @Json(name = "accuracy_meters") val accuracyMeters: Double? = null
)

data class TrailSnapshot(
    @Json(name = "prev_entry_hash") val prevEntryHash: String,
    @Json(name = "next_entry_hash") val nextEntryHash: String,
    @Json(name = "entries_around") val entriesAround: List<TrailEntryData>
)

data class TrailEntryData(
    @Json(name = "sequence_number") val sequenceNumber: Int,
    val timestamp: String,
    val latitude: Double,
    val longitude: Double,
    @Json(name = "accuracy_meters") val accuracyMeters: Double,
    @Json(name = "entry_hash") val entryHash: String,
    @Json(name = "prev_hash") val prevHash: String,
    val signature: String? = null
)

data class SubmitVisitResponse(
    val success: Boolean,
    @Json(name = "visit_id") val visitId: String,
    @Json(name = "server_visit_id") val serverVisitId: String,
    @Json(name = "synced_at") val syncedAt: String
)

data class SyncStatusResponse(
    @Json(name = "pending_count") val pendingCount: Int,
    @Json(name = "synced_today") val syncedToday: Int,
    @Json(name = "server_time") val serverTime: String
)

data class LocationPingRequest(
    @Json(name = "device_id") val deviceId: String,
    val pings: List<LocationPing>
)

data class LocationPing(
    @Json(name = "recorded_at") val recordedAt: String,
    val latitude: Double,
    val longitude: Double,
    @Json(name = "accuracy_meters") val accuracyMeters: Double? = null,
    val altitude: Double? = null,
    val speed: Double? = null,
    val bearing: Double? = null,
    val source: String = "trail"
)

data class LocationPingResponse(
    val success: Boolean,
    val received: Int,
    val stored: Int,
    val skipped: Int,
    val errors: List<String> = emptyList()
)

data class LoginRequest(
    val username: String,
    val password: String,
    @Json(name = "totp_token")
    val totpToken: String?
)

data class LoginResponse(
    @Json(name = "access_token")
    val accessToken: String,
    @Json(name = "refresh_token")
    val refreshToken: String,
    val user: UserData
)

data class SurveyorsResponse(
    val surveyors: List<SurveyorEntity>,
    val pagination: PaginationData
)

data class FieldsResponse(
    val fields: List<FieldEntity>,
    val pagination: PaginationData
)

data class PhonesResponse(
    val phones: List<PhoneEntity>,
    val pagination: PaginationData
)

data class AssignmentsResponse(
    val assignments: List<AssignmentEntity>,
    val pagination: PaginationData
)

data class VisitsResponse(
    val visits: List<VisitEntity>,
    val pagination: PaginationData
)

data class ReviewRequest(
    val decision: String,
    val notes: String
)

data class ReviewResponse(
    val message: String,
    val reviewStatus: String,
    val reviewedAt: String
)

data class StatsResponse(
    val totalVisits: Int,
    val pendingReview: Int,
    val byReviewStatus: Map<String, Int>,
    val byField: Map<String, Int>,
    val bySurveyor: Map<String, Int>
)

data class PaginationData(
    val page: Int,
    val perPage: Int,
    val total: Int
)

data class EnrollFaceTemplateRequest(
    @Json(name = "template") val template: String,
    @Json(name = "version") val version: Int = 1
)

data class EnrollFaceTemplateResponse(
    val message: String,
    @Json(name = "surveyor_id") val surveyorId: String,
    val version: Int
)

data class FaceEnrollmentStatusResponse(
    @Json(name = "surveyor_id") val surveyorId: String,
    @Json(name = "employee_id") val employeeId: String,
    @Json(name = "full_name") val fullName: String,
    @Json(name = "has_template") val hasTemplate: Boolean,
    val version: Int,
    @Json(name = "updated_at") val updatedAt: String?
)

data class AccountData(
    val id: String,
    val username: String,
    val email: String,
    val role: String,
    @Json(name = "totp_enabled") val totpEnabled: Boolean = false
)

data class ChangePasswordRequest(
    @Json(name = "current_password") val currentPassword: String,
    @Json(name = "new_password") val newPassword: String
)

data class RegisterDeviceRequest(
    val deviceId: String,
    val publicKey: String,
    val model: String,
    @Json(name = "android_version")
    val androidVersion: String
)

data class RegisterDeviceResponse(
    val phoneId: String
)

data class ChangePasswordResponse(
    val message: String
)