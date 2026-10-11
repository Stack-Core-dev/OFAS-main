import 'package:json_annotation/json_annotation.dart';

part 'assignment.g.dart';

enum AssignmentStatus {
  pending,
  inProgress,
  completed,
  cancelled,
  missed,
}

extension AssignmentStatusExtension on AssignmentStatus {
  String get value {
    switch (this) {
      case AssignmentStatus.pending: return 'PENDING';
      case AssignmentStatus.inProgress: return 'IN_PROGRESS';
      case AssignmentStatus.completed: return 'COMPLETED';
      case AssignmentStatus.cancelled: return 'CANCELLED';
      case AssignmentStatus.missed: return 'MISSED';
    }
  }

  static AssignmentStatus fromString(String value) {
    switch (value.toUpperCase()) {
      case 'PENDING': return AssignmentStatus.pending;
      case 'IN_PROGRESS': return AssignmentStatus.inProgress;
      case 'COMPLETED': return AssignmentStatus.completed;
      case 'CANCELLED': return AssignmentStatus.cancelled;
      case 'MISSED': return AssignmentStatus.missed;
      default: return AssignmentStatus.pending;
    }
  }
}

@JsonSerializable()
class Assignment {
  final String id;
  final String surveyorId;
  final String fieldId;
  final DateTime assignedDate;
  final String assignedBy;
  final AssignmentStatus status;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final String? visitId;
  final Map<String, dynamic> metadata;

  Assignment({
    required this.id,
    required this.surveyorId,
    required this.fieldId,
    required this.assignedDate,
    required this.assignedBy,
    required this.status,
    this.startedAt,
    this.completedAt,
    this.visitId,
    this.metadata = const {},
  });

  bool get isCompleted => status == AssignmentStatus.completed;
  bool get isPending => status == AssignmentStatus.pending;
  bool get isInProgress => status == AssignmentStatus.inProgress;

  factory Assignment.fromJson(Map<String, dynamic> json) => _$AssignmentFromJson(json);
  Map<String, dynamic> toJson() => _$AssignmentToJson(this);
}

@JsonSerializable()
class CreateAssignmentRequest {
  final String surveyorId;
  final String fieldId;
  final DateTime assignedDate;
  final Map<String, dynamic> metadata;

  CreateAssignmentRequest({
    required this.surveyorId,
    required this.fieldId,
    required this.assignedDate,
    this.metadata = const {},
  });

  factory CreateAssignmentRequest.fromJson(Map<String, dynamic> json) => _$CreateAssignmentRequestFromJson(json);
  Map<String, dynamic> toJson() => _$CreateAssignmentRequestToJson(this);
}

@JsonSerializable()
class BulkAssignRequest {
  final List<String> surveyorIds;
  final List<String> fieldIds;
  final DateTime assignedDate;

  BulkAssignRequest({
    required this.surveyorIds,
    required this.fieldIds,
    required this.assignedDate,
  });

  factory BulkAssignRequest.fromJson(Map<String, dynamic> json) => _$BulkAssignRequestFromJson(json);
  Map<String, dynamic> toJson() => _$BulkAssignRequestToJson(this);
}

@JsonSerializable()
class AssignmentListResponse {
  final List<Assignment> assignments;
  final int total;
  final int page;
  final int pageSize;
  final AssignmentStats stats;

  AssignmentListResponse({
    required this.assignments,
    required this.total,
    required this.page,
    required this.pageSize,
    required this.stats,
  });

  factory AssignmentListResponse.fromJson(Map<String, dynamic> json) => _$AssignmentListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$AssignmentListResponseToJson(this);
}

@JsonSerializable()
class AssignmentStats {
  final int total;
  final int pending;
  final int inProgress;
  final int completed;
  final int missed;
  final int cancelled;

  AssignmentStats({
    required this.total,
    required this.pending,
    required this.inProgress,
    required this.completed,
    required this.missed,
    required this.cancelled,
  });

  factory AssignmentStats.fromJson(Map<String, dynamic> json) => _$AssignmentStatsFromJson(json);
  Map<String, dynamic> toJson() => _$AssignmentStatsToJson(this);
}

@JsonSerializable()
class SurveyorDaySchedule {
  final String surveyorId;
  final String surveyorName;
  final DateTime date;
  final List<Assignment> assignments;
  final int? totalFields;
  final int? completedFields;

  SurveyorDaySchedule({
    required this.surveyorId,
    required this.surveyorName,
    required this.date,
    required this.assignments,
    this.totalFields,
    this.completedFields,
  });

  factory SurveyorDaySchedule.fromJson(Map<String, dynamic> json) => _$SurveyorDayScheduleFromJson(json);
  Map<String, dynamic> toJson() => _$SurveyorDayScheduleToJson(this);
}