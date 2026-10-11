// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'assignment.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Assignment _$AssignmentFromJson(Map<String, dynamic> json) => Assignment(
      id: json['id'] as String,
      surveyorId: json['surveyorId'] as String,
      fieldId: json['fieldId'] as String,
      assignedDate: DateTime.parse(json['assignedDate'] as String),
      assignedBy: json['assignedBy'] as String,
      status: $enumDecode(_$AssignmentStatusEnumMap, json['status']),
      startedAt: json['startedAt'] == null
          ? null
          : DateTime.parse(json['startedAt'] as String),
      completedAt: json['completedAt'] == null
          ? null
          : DateTime.parse(json['completedAt'] as String),
      visitId: json['visitId'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$AssignmentToJson(Assignment instance) =>
    <String, dynamic>{
      'id': instance.id,
      'surveyorId': instance.surveyorId,
      'fieldId': instance.fieldId,
      'assignedDate': instance.assignedDate.toIso8601String(),
      'assignedBy': instance.assignedBy,
      'status': _$AssignmentStatusEnumMap[instance.status]!,
      'startedAt': instance.startedAt?.toIso8601String(),
      'completedAt': instance.completedAt?.toIso8601String(),
      'visitId': instance.visitId,
      'metadata': instance.metadata,
    };

const _$AssignmentStatusEnumMap = {
  AssignmentStatus.pending: 'pending',
  AssignmentStatus.inProgress: 'inProgress',
  AssignmentStatus.completed: 'completed',
  AssignmentStatus.cancelled: 'cancelled',
  AssignmentStatus.missed: 'missed',
};

CreateAssignmentRequest _$CreateAssignmentRequestFromJson(
        Map<String, dynamic> json) =>
    CreateAssignmentRequest(
      surveyorId: json['surveyorId'] as String,
      fieldId: json['fieldId'] as String,
      assignedDate: DateTime.parse(json['assignedDate'] as String),
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$CreateAssignmentRequestToJson(
        CreateAssignmentRequest instance) =>
    <String, dynamic>{
      'surveyorId': instance.surveyorId,
      'fieldId': instance.fieldId,
      'assignedDate': instance.assignedDate.toIso8601String(),
      'metadata': instance.metadata,
    };

BulkAssignRequest _$BulkAssignRequestFromJson(Map<String, dynamic> json) =>
    BulkAssignRequest(
      surveyorIds: (json['surveyorIds'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      fieldIds:
          (json['fieldIds'] as List<dynamic>).map((e) => e as String).toList(),
      assignedDate: DateTime.parse(json['assignedDate'] as String),
    );

Map<String, dynamic> _$BulkAssignRequestToJson(BulkAssignRequest instance) =>
    <String, dynamic>{
      'surveyorIds': instance.surveyorIds,
      'fieldIds': instance.fieldIds,
      'assignedDate': instance.assignedDate.toIso8601String(),
    };

AssignmentListResponse _$AssignmentListResponseFromJson(
        Map<String, dynamic> json) =>
    AssignmentListResponse(
      assignments: (json['assignments'] as List<dynamic>)
          .map((e) => Assignment.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num).toInt(),
      page: (json['page'] as num).toInt(),
      pageSize: (json['pageSize'] as num).toInt(),
      stats: AssignmentStats.fromJson(json['stats'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$AssignmentListResponseToJson(
        AssignmentListResponse instance) =>
    <String, dynamic>{
      'assignments': instance.assignments,
      'total': instance.total,
      'page': instance.page,
      'pageSize': instance.pageSize,
      'stats': instance.stats,
    };

AssignmentStats _$AssignmentStatsFromJson(Map<String, dynamic> json) =>
    AssignmentStats(
      total: (json['total'] as num).toInt(),
      pending: (json['pending'] as num).toInt(),
      inProgress: (json['inProgress'] as num).toInt(),
      completed: (json['completed'] as num).toInt(),
      missed: (json['missed'] as num).toInt(),
      cancelled: (json['cancelled'] as num).toInt(),
    );

Map<String, dynamic> _$AssignmentStatsToJson(AssignmentStats instance) =>
    <String, dynamic>{
      'total': instance.total,
      'pending': instance.pending,
      'inProgress': instance.inProgress,
      'completed': instance.completed,
      'missed': instance.missed,
      'cancelled': instance.cancelled,
    };

SurveyorDaySchedule _$SurveyorDayScheduleFromJson(Map<String, dynamic> json) =>
    SurveyorDaySchedule(
      surveyorId: json['surveyorId'] as String,
      surveyorName: json['surveyorName'] as String,
      date: DateTime.parse(json['date'] as String),
      assignments: (json['assignments'] as List<dynamic>)
          .map((e) => Assignment.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalFields: (json['totalFields'] as num?)?.toInt(),
      completedFields: (json['completedFields'] as num?)?.toInt(),
    );

Map<String, dynamic> _$SurveyorDayScheduleToJson(
        SurveyorDaySchedule instance) =>
    <String, dynamic>{
      'surveyorId': instance.surveyorId,
      'surveyorName': instance.surveyorName,
      'date': instance.date.toIso8601String(),
      'assignments': instance.assignments,
      'totalFields': instance.totalFields,
      'completedFields': instance.completedFields,
    };
