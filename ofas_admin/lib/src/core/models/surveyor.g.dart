// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'surveyor.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Surveyor _$SurveyorFromJson(Map<String, dynamic> json) => Surveyor(
      id: json['id'] as String,
      employeeId: json['employeeId'] as String,
      fullName: json['fullName'] as String,
      email: json['email'] as String,
      phoneNumber: json['phoneNumber'] as String,
      department: json['department'] as String,
      faceTemplates: (json['faceTemplates'] as List<dynamic>?)
              ?.map((e) => FaceTemplate.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      createdBy: json['createdBy'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: json['updatedAt'] == null
          ? null
          : DateTime.parse(json['updatedAt'] as String),
      isActive: json['isActive'] as bool? ?? true,
      lastSyncAt: json['lastSyncAt'] == null
          ? null
          : DateTime.parse(json['lastSyncAt'] as String),
    );

Map<String, dynamic> _$SurveyorToJson(Surveyor instance) => <String, dynamic>{
      'id': instance.id,
      'employeeId': instance.employeeId,
      'fullName': instance.fullName,
      'email': instance.email,
      'phoneNumber': instance.phoneNumber,
      'department': instance.department,
      'faceTemplates': instance.faceTemplates,
      'createdBy': instance.createdBy,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt?.toIso8601String(),
      'isActive': instance.isActive,
      'lastSyncAt': instance.lastSyncAt?.toIso8601String(),
    };

FaceTemplate _$FaceTemplateFromJson(Map<String, dynamic> json) => FaceTemplate(
      id: json['id'] as String,
      surveyorId: json['surveyorId'] as String,
      templateData: json['templateData'] as String,
      qualityScore: (json['qualityScore'] as num).toDouble(),
      enrolledAt: DateTime.parse(json['enrolledAt'] as String),
      isActive: json['isActive'] as bool? ?? true,
      enrolledBy: json['enrolledBy'] as String?,
    );

Map<String, dynamic> _$FaceTemplateToJson(FaceTemplate instance) =>
    <String, dynamic>{
      'id': instance.id,
      'surveyorId': instance.surveyorId,
      'templateData': instance.templateData,
      'qualityScore': instance.qualityScore,
      'enrolledAt': instance.enrolledAt.toIso8601String(),
      'isActive': instance.isActive,
      'enrolledBy': instance.enrolledBy,
    };

CreateSurveyorRequest _$CreateSurveyorRequestFromJson(
        Map<String, dynamic> json) =>
    CreateSurveyorRequest(
      employeeId: json['employeeId'] as String,
      fullName: json['fullName'] as String,
      email: json['email'] as String,
      phoneNumber: json['phoneNumber'] as String,
      department: json['department'] as String,
      faceImageBase64: json['faceImageBase64'] as String,
    );

Map<String, dynamic> _$CreateSurveyorRequestToJson(
        CreateSurveyorRequest instance) =>
    <String, dynamic>{
      'employeeId': instance.employeeId,
      'fullName': instance.fullName,
      'email': instance.email,
      'phoneNumber': instance.phoneNumber,
      'department': instance.department,
      'faceImageBase64': instance.faceImageBase64,
    };

UpdateSurveyorRequest _$UpdateSurveyorRequestFromJson(
        Map<String, dynamic> json) =>
    UpdateSurveyorRequest(
      fullName: json['fullName'] as String?,
      email: json['email'] as String?,
      phoneNumber: json['phoneNumber'] as String?,
      department: json['department'] as String?,
      faceImageBase64: json['faceImageBase64'] as String?,
      isActive: json['isActive'] as bool?,
    );

Map<String, dynamic> _$UpdateSurveyorRequestToJson(
        UpdateSurveyorRequest instance) =>
    <String, dynamic>{
      'fullName': instance.fullName,
      'email': instance.email,
      'phoneNumber': instance.phoneNumber,
      'department': instance.department,
      'faceImageBase64': instance.faceImageBase64,
      'isActive': instance.isActive,
    };

SurveyorListResponse _$SurveyorListResponseFromJson(
        Map<String, dynamic> json) =>
    SurveyorListResponse(
      surveyors: (json['surveyors'] as List<dynamic>)
          .map((e) => Surveyor.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num).toInt(),
      page: (json['page'] as num).toInt(),
      pageSize: (json['pageSize'] as num).toInt(),
    );

Map<String, dynamic> _$SurveyorListResponseToJson(
        SurveyorListResponse instance) =>
    <String, dynamic>{
      'surveyors': instance.surveyors,
      'total': instance.total,
      'page': instance.page,
      'pageSize': instance.pageSize,
    };

FaceEnrollmentResponse _$FaceEnrollmentResponseFromJson(
        Map<String, dynamic> json) =>
    FaceEnrollmentResponse(
      templateId: json['templateId'] as String,
      qualityScore: (json['qualityScore'] as num).toDouble(),
      success: json['success'] as bool,
      errorMessage: json['errorMessage'] as String?,
    );

Map<String, dynamic> _$FaceEnrollmentResponseToJson(
        FaceEnrollmentResponse instance) =>
    <String, dynamic>{
      'templateId': instance.templateId,
      'qualityScore': instance.qualityScore,
      'success': instance.success,
      'errorMessage': instance.errorMessage,
    };
