import 'package:dio/dio.dart';
import 'package:ofas_admin/src/core/models/user.dart';
import 'package:ofas_admin/src/core/models/field.dart';
import 'package:ofas_admin/src/core/models/surveyor.dart';
import 'package:ofas_admin/src/core/models/phone.dart';
import 'package:ofas_admin/src/core/models/visit.dart';
import 'package:ofas_admin/src/core/models/assignment.dart';
import 'package:ofas_admin/src/core/models/audit.dart';
import 'package:ofas_admin/src/core/constants/app_constants.dart';

class ApiClient {
  final Dio _dio;
  
  ApiClient(this._dio);
  
  // Auth
  Future<AuthTokens> login(LoginRequest request) async {
    final response = await _dio.post('/auth/login', data: request.toJson());
    return AuthTokens.fromJson(response.data);
  }
  
  Future<AuthTokens> refreshToken(String refreshToken) async {
    final response = await _dio.post('/auth/refresh', data: {'refresh_token': refreshToken});
    return AuthTokens.fromJson(response.data);
  }
  
  Future<MfaSetupResponse> setupMfa() async {
    final response = await _dio.post('/auth/mfa/setup');
    return MfaSetupResponse.fromJson(response.data);
  }
  
  Future<void> verifyMfa(String code, String tempToken) async {
    await _dio.post('/auth/mfa/verify', data: {'code': code, 'temp_token': tempToken});
  }
  
  Future<PasskeyRegistrationOptions> getPasskeyRegistrationOptions() async {
    final response = await _dio.post('/auth/passkey/registration/options');
    return PasskeyRegistrationOptions.fromJson(response.data);
  }
  
  Future<void> verifyPasskeyRegistration(Map<String, dynamic> body) async {
    await _dio.post('/auth/passkey/registration/verify', data: body);
  }
  
  Future<Map<String, dynamic>> getPasskeyAuthenticationOptions() async {
    final response = await _dio.post('/auth/passkey/authentication/options');
    return response.data;
  }
  
  Future<AuthTokens> verifyPasskeyAuthentication(Map<String, dynamic> body) async {
    final response = await _dio.post('/auth/passkey/authentication/verify', data: body);
    return AuthTokens.fromJson(response.data);
  }
  
  Future<User> getCurrentUser() async {
    final response = await _dio.get('/auth/me');
    return User.fromJson(response.data);
  }
  
  Future<void> logout() async {
    await _dio.post('/auth/logout');
  }
  
  // Fields
  Future<FieldListResponse> getFields({
    int page = 1,
    int pageSize = 20,
    String? search,
    String? cropType,
    String? season,
    bool? isActive,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page,
      'page_size': pageSize,
    };
    if (search != null) queryParams['search'] = search;
    if (cropType != null) queryParams['crop_type'] = cropType;
    if (season != null) queryParams['season'] = season;
    if (isActive != null) queryParams['is_active'] = isActive;
    
    final response = await _dio.get('/fields', queryParameters: queryParams);
    return FieldListResponse.fromJson(response.data);
  }
  
  Future<Field> getField(String id) async {
    final response = await _dio.get('/fields/$id');
    return Field.fromJson(response.data);
  }
  
  Future<Field> createField(CreateFieldRequest request) async {
    final response = await _dio.post('/fields', data: request.toJson());
    return Field.fromJson(response.data);
  }
  
  Future<Field> updateField(String id, UpdateFieldRequest request) async {
    final response = await _dio.patch('/fields/$id', data: request.toJson());
    return Field.fromJson(response.data);
  }
  
  Future<void> deleteField(String id) async {
    await _dio.delete('/fields/$id');
  }
  
  Future<FieldPhoto> uploadFieldPhoto(String fieldId, MultipartFile photo) async {
    final formData = FormData.fromMap({'photo': photo});
    final response = await _dio.post('/fields/$fieldId/photos', data: formData);
    return FieldPhoto.fromJson(response.data);
  }
  
  Future<void> deleteFieldPhoto(String fieldId, String photoId) async {
    await _dio.delete('/fields/$fieldId/photos/$photoId');
  }
  
  // Surveyors
  Future<SurveyorListResponse> getSurveyors({
    int page = 1,
    int pageSize = 20,
    String? search,
    String? department,
    bool? isActive,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page,
      'page_size': pageSize,
    };
    if (search != null) queryParams['search'] = search;
    if (department != null) queryParams['department'] = department;
    if (isActive != null) queryParams['is_active'] = isActive;
    
    final response = await _dio.get('/surveyors', queryParameters: queryParams);
    return SurveyorListResponse.fromJson(response.data);
  }
  
  Future<Surveyor> getSurveyor(String id) async {
    final response = await _dio.get('/surveyors/$id');
    return Surveyor.fromJson(response.data);
  }
  
  Future<Surveyor> createSurveyor(CreateSurveyorRequest request) async {
    final response = await _dio.post('/surveyors', data: request.toJson());
    return Surveyor.fromJson(response.data);
  }
  
  Future<Surveyor> updateSurveyor(String id, UpdateSurveyorRequest request) async {
    final response = await _dio.patch('/surveyors/$id', data: request.toJson());
    return Surveyor.fromJson(response.data);
  }
  
  Future<void> deleteSurveyor(String id) async {
    await _dio.delete('/surveyors/$id');
  }
  
  Future<FaceEnrollmentResponse> enrollFace(String surveyorId, MultipartFile faceImage) async {
    final formData = FormData.fromMap({'face_image': faceImage});
    final response = await _dio.post('/surveyors/$surveyorId/face/enroll', data: formData);
    return FaceEnrollmentResponse.fromJson(response.data);
  }
  
  Future<void> deleteFaceTemplate(String surveyorId, String templateId) async {
    await _dio.delete('/surveyors/$surveyorId/face/$templateId');
  }
  
  // Phones
  Future<PhoneListResponse> getPhones({
    int page = 1,
    int pageSize = 20,
    String? status,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page,
      'page_size': pageSize,
    };
    if (status != null) queryParams['status'] = status;
    
    final response = await _dio.get('/phones', queryParameters: queryParams);
    return PhoneListResponse.fromJson(response.data);
  }
  
  Future<PhoneStats> getPhoneStats() async {
    final response = await _dio.get('/phones/stats');
    return PhoneStats.fromJson(response.data);
  }
  
  Future<Phone> getPhone(String id) async {
    final response = await _dio.get('/phones/$id');
    return Phone.fromJson(response.data);
  }
  
  Future<Phone> registerPhone(RegisterPhoneRequest request) async {
    final response = await _dio.post('/phones', data: request.toJson());
    return Phone.fromJson(response.data);
  }
  
  Future<Phone> updatePhoneStatus(String id, UpdatePhoneStatusRequest request) async {
    final response = await _dio.patch('/phones/$id/status', data: request.toJson());
    return Phone.fromJson(response.data);
  }
  
  Future<void> deletePhone(String id) async {
    await _dio.delete('/phones/$id');
  }
  
  // Assignments
  Future<AssignmentListResponse> getAssignments({
    int page = 1,
    int pageSize = 20,
    String? surveyorId,
    String? fieldId,
    String? dateFrom,
    String? dateTo,
    String? status,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page,
      'page_size': pageSize,
    };
    if (surveyorId != null) queryParams['surveyor_id'] = surveyorId;
    if (fieldId != null) queryParams['field_id'] = fieldId;
    if (dateFrom != null) queryParams['date_from'] = dateFrom;
    if (dateTo != null) queryParams['date_to'] = dateTo;
    if (status != null) queryParams['status'] = status;
    
    final response = await _dio.get('/assignments', queryParameters: queryParams);
    return AssignmentListResponse.fromJson(response.data);
  }
  
  Future<List<SurveyorDaySchedule>> getSchedule({
    required String dateFrom,
    required String dateTo,
    String? surveyorId,
  }) async {
    final queryParams = <String, dynamic>{
      'date_from': dateFrom,
      'date_to': dateTo,
    };
    if (surveyorId != null) queryParams['surveyor_id'] = surveyorId;
    
    final response = await _dio.get('/assignments/schedule', queryParameters: queryParams);
    return (response.data as List).map((e) => SurveyorDaySchedule.fromJson(e)).toList();
  }
  
  Future<Assignment> getAssignment(String id) async {
    final response = await _dio.get('/assignments/$id');
    return Assignment.fromJson(response.data);
  }
  
  Future<Assignment> createAssignment(CreateAssignmentRequest request) async {
    final response = await _dio.post('/assignments', data: request.toJson());
    return Assignment.fromJson(response.data);
  }
  
  Future<List<Assignment>> bulkAssign(BulkAssignRequest request) async {
    final response = await _dio.post('/assignments/bulk', data: request.toJson());
    return (response.data as List).map((e) => Assignment.fromJson(e)).toList();
  }
  
  Future<Assignment> updateAssignment(String id, Map<String, dynamic> body) async {
    final response = await _dio.patch('/assignments/$id', data: body);
    return Assignment.fromJson(response.data);
  }
  
  Future<void> deleteAssignment(String id) async {
    await _dio.delete('/assignments/$id');
  }
  
  // Visits
  Future<VisitListResponse> getVisits({
    int page = 1,
    int pageSize = 20,
    String? surveyorId,
    String? fieldId,
    String? phoneId,
    String? status,
    String? dateFrom,
    String? dateTo,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page,
      'page_size': pageSize,
    };
    if (surveyorId != null) queryParams['surveyor_id'] = surveyorId;
    if (fieldId != null) queryParams['field_id'] = fieldId;
    if (phoneId != null) queryParams['phone_id'] = phoneId;
    if (status != null) queryParams['status'] = status;
    if (dateFrom != null) queryParams['date_from'] = dateFrom;
    if (dateTo != null) queryParams['date_to'] = dateTo;
    
    final response = await _dio.get('/visits', queryParameters: queryParams);
    return VisitListResponse.fromJson(response.data);
  }
  
  Future<VisitStats> getVisitStats({
    String? dateFrom,
    String? dateTo,
  }) async {
    final queryParams = <String, dynamic>{};
    if (dateFrom != null) queryParams['date_from'] = dateFrom;
    if (dateTo != null) queryParams['date_to'] = dateTo;
    
    final response = await _dio.get('/visits/stats', queryParameters: queryParams);
    return VisitStats.fromJson(response.data);
  }
  
  Future<Visit> getVisit(String id) async {
    final response = await _dio.get('/visits/$id');
    return Visit.fromJson(response.data);
  }
  
  Future<String> getVisitPhotoUrl(String visitId, String photoId) async {
    final response = await _dio.get('/visits/$visitId/photos/$photoId');
    return response.data['url'];
  }
  
  Future<Visit> reviewVisit(String id, ReviewVisitRequest request) async {
    final response = await _dio.post('/visits/$id/review', data: request.toJson());
    return Visit.fromJson(response.data);
  }
  
  Future<List<PhotoComparisonResult>> comparePhotos(String visitId, Map<String, dynamic> body) async {
    final response = await _dio.post('/visits/$visitId/compare', data: body);
    return (response.data as List).map((e) => PhotoComparisonResult.fromJson(e)).toList();
  }
  
  Future<Response> exportVisits({
    String? dateFrom,
    String? dateTo,
    String format = 'csv',
    String? status,
  }) async {
    final queryParams = <String, dynamic>{
      'format': format,
    };
    if (dateFrom != null) queryParams['date_from'] = dateFrom;
    if (dateTo != null) queryParams['date_to'] = dateTo;
    if (status != null) queryParams['status'] = status;
    
    return _dio.get('/visits/export', queryParameters: queryParams, options: Options(responseType: ResponseType.bytes));
  }
  
  // Audit
  Future<AuditLogListResponse> getAuditLogs({
    int page = 1,
    int pageSize = 20,
    String? actorId,
    String? actorRole,
    String? action,
    String? resourceType,
    String? resourceId,
    DateTime? fromDate,
    DateTime? toDate,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page,
      'page_size': pageSize,
    };
    if (actorId != null) queryParams['actor_id'] = actorId;
    if (actorRole != null) queryParams['actor_role'] = actorRole;
    if (action != null) queryParams['action'] = action;
    if (resourceType != null) queryParams['resource_type'] = resourceType;
    if (resourceId != null) queryParams['resource_id'] = resourceId;
    if (fromDate != null) queryParams['from_date'] = fromDate.toIso8601String();
    if (toDate != null) queryParams['to_date'] = toDate.toIso8601String();
    
    final response = await _dio.get('/audit', queryParameters: queryParams);
    return AuditLogListResponse.fromJson(response.data);
  }
  
  Future<ChainIntegrityReport> checkChainIntegrity() async {
    final response = await _dio.get('/audit/integrity');
    return ChainIntegrityReport.fromJson(response.data);
  }
  
  Future<Response> exportAuditLogs({
    DateTime? fromDate,
    DateTime? toDate,
    String format = 'csv',
  }) async {
    final queryParams = <String, dynamic>{
      'format': format,
    };
    if (fromDate != null) queryParams['from_date'] = fromDate.toIso8601String();
    if (toDate != null) queryParams['to_date'] = toDate.toIso8601String();
    
    return _dio.get('/audit/export', queryParameters: queryParams, options: Options(responseType: ResponseType.bytes));
  }
  
  // Dashboard
  Future<DashboardStats> getDashboardStats() async {
    final response = await _dio.get('/dashboard/stats');
    return DashboardStats.fromJson(response.data);
  }
  
  Future<List<Visit>> getRecentVisits({int limit = 10}) async {
    final response = await _dio.get('/dashboard/recent-visits', queryParameters: {'limit': limit});
    return (response.data as List).map((e) => Visit.fromJson(e)).toList();
  }
  
  Future<List<Visit>> getPendingReviews({int limit = 10}) async {
    final response = await _dio.get('/dashboard/pending-reviews', queryParameters: {'limit': limit});
    return (response.data as List).map((e) => Visit.fromJson(e)).toList();
  }
}

class DashboardStats {
  final int totalFields;
  final int activeFields;
  final int totalSurveyors;
  final int activeSurveyors;
  final int totalPhones;
  final int activePhones;
  final int totalVisits;
  final int pendingVisits;
  final int validVisits;
  final int invalidVisits;
  final int flaggedVisits;
  final int todayAssignments;
  final int completedToday;
  final double syncRate;
  final Map<String, int> visitsByStatus;
  final Map<String, int> visitsByDay;

  DashboardStats({
    required this.totalFields,
    required this.activeFields,
    required this.totalSurveyors,
    required this.activeSurveyors,
    required this.totalPhones,
    required this.activePhones,
    required this.totalVisits,
    required this.pendingVisits,
    required this.validVisits,
    required this.invalidVisits,
    required this.flaggedVisits,
    required this.todayAssignments,
    required this.completedToday,
    required this.syncRate,
    required this.visitsByStatus,
    required this.visitsByDay,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      totalFields: json['total_fields'] ?? 0,
      activeFields: json['active_fields'] ?? 0,
      totalSurveyors: json['total_surveyors'] ?? 0,
      activeSurveyors: json['active_surveyors'] ?? 0,
      totalPhones: json['total_phones'] ?? 0,
      activePhones: json['active_phones'] ?? 0,
      totalVisits: json['total_visits'] ?? 0,
      pendingVisits: json['pending_visits'] ?? 0,
      validVisits: json['valid_visits'] ?? 0,
      invalidVisits: json['invalid_visits'] ?? 0,
      flaggedVisits: json['flagged_visits'] ?? 0,
      todayAssignments: json['today_assignments'] ?? 0,
      completedToday: json['completed_today'] ?? 0,
      syncRate: (json['sync_rate'] ?? 0.0).toDouble(),
      visitsByStatus: Map<String, int>.from(json['visits_by_status'] ?? {}),
      visitsByDay: Map<String, int>.from(json['visits_by_day'] ?? {}),
    );
  }
}