import 'package:json_annotation/json_annotation.dart';

part 'surveyor.g.dart';

@JsonSerializable()
class Surveyor {
  final String id;
  final String employeeId;
  final String fullName;
  final String email;
  final String phoneNumber;
  final String department;
  final List<FaceTemplate> faceTemplates;
  final String createdBy;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final bool isActive;
  final DateTime? lastSyncAt;

  Surveyor({
    required this.id,
    required this.employeeId,
    required this.fullName,
    required this.email,
    required this.phoneNumber,
    required this.department,
    this.faceTemplates = const [],
    required this.createdBy,
    required this.createdAt,
    this.updatedAt,
    this.isActive = true,
    this.lastSyncAt,
  });

  FaceTemplate? get activeFaceTemplate {
    try {
      return faceTemplates.where((t) => t.isActive).firstOrNull;
    } catch (_) {
      return faceTemplates.isNotEmpty ? faceTemplates.first : null;
    }
  }

  factory Surveyor.fromJson(Map<String, dynamic> json) => _$SurveyorFromJson(json);
  Map<String, dynamic> toJson() => _$SurveyorToJson(this);
}

@JsonSerializable()
class FaceTemplate {
  final String id;
  final String surveyorId;
  final String templateData;
  final double qualityScore;
  final DateTime enrolledAt;
  final bool isActive;
  final String? enrolledBy;

  FaceTemplate({
    required this.id,
    required this.surveyorId,
    required this.templateData,
    required this.qualityScore,
    required this.enrolledAt,
    this.isActive = true,
    this.enrolledBy,
  });

  factory FaceTemplate.fromJson(Map<String, dynamic> json) => _$FaceTemplateFromJson(json);
  Map<String, dynamic> toJson() => _$FaceTemplateToJson(this);
}

@JsonSerializable()
class CreateSurveyorRequest {
  final String employeeId;
  final String fullName;
  final String email;
  final String phoneNumber;
  final String department;
  final String faceImageBase64;

  CreateSurveyorRequest({
    required this.employeeId,
    required this.fullName,
    required this.email,
    required this.phoneNumber,
    required this.department,
    required this.faceImageBase64,
  });

  factory CreateSurveyorRequest.fromJson(Map<String, dynamic> json) => _$CreateSurveyorRequestFromJson(json);
  Map<String, dynamic> toJson() => _$CreateSurveyorRequestToJson(this);
}

@JsonSerializable()
class UpdateSurveyorRequest {
  final String? fullName;
  final String? email;
  final String? phoneNumber;
  final String? department;
  final String? faceImageBase64;
  final bool? isActive;

  UpdateSurveyorRequest({
    this.fullName,
    this.email,
    this.phoneNumber,
    this.department,
    this.faceImageBase64,
    this.isActive,
  });

  factory UpdateSurveyorRequest.fromJson(Map<String, dynamic> json) => _$UpdateSurveyorRequestFromJson(json);
  Map<String, dynamic> toJson() => _$UpdateSurveyorRequestToJson(this);
}

@JsonSerializable()
class SurveyorListResponse {
  final List<Surveyor> surveyors;
  final int total;
  final int page;
  final int pageSize;

  SurveyorListResponse({
    required this.surveyors,
    required this.total,
    required this.page,
    required this.pageSize,
  });

  factory SurveyorListResponse.fromJson(Map<String, dynamic> json) => _$SurveyorListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$SurveyorListResponseToJson(this);
}

@JsonSerializable()
class FaceEnrollmentResponse {
  final String templateId;
  final double qualityScore;
  final bool success;
  final String? errorMessage;

  FaceEnrollmentResponse({
    required this.templateId,
    required this.qualityScore,
    required this.success,
    this.errorMessage,
  });

  factory FaceEnrollmentResponse.fromJson(Map<String, dynamic> json) => _$FaceEnrollmentResponseFromJson(json);
  Map<String, dynamic> toJson() => _$FaceEnrollmentResponseToJson(this);
}