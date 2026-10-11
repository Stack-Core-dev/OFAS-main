import 'package:json_annotation/json_annotation.dart';

part 'audit.g.dart';

@JsonSerializable()
class AuditLog {
  final String id;
  final String actorId;
  final String actorRole;
  final String action;
  final String resourceType;
  final String resourceId;
  final Map<String, dynamic> oldValues;
  final Map<String, dynamic> newValues;
  final String ipAddress;
  final String userAgent;
  final DateTime timestamp;
  final String hash;
  final String previousHash;
  final bool chainValid;

  AuditLog({
    required this.id,
    required this.actorId,
    required this.actorRole,
    required this.action,
    required this.resourceType,
    required this.resourceId,
    required this.oldValues,
    required this.newValues,
    required this.ipAddress,
    required this.userAgent,
    required this.timestamp,
    required this.hash,
    required this.previousHash,
    this.chainValid = true,
  });

  factory AuditLog.fromJson(Map<String, dynamic> json) => _$AuditLogFromJson(json);
  Map<String, dynamic> toJson() => _$AuditLogToJson(this);
}

@JsonSerializable()
class AuditLogListResponse {
  final List<AuditLog> logs;
  final int total;
  final int page;
  final int pageSize;
  final bool chainIntegrityValid;

  AuditLogListResponse({
    required this.logs,
    required this.total,
    required this.page,
    required this.pageSize,
    required this.chainIntegrityValid,
  });

  factory AuditLogListResponse.fromJson(Map<String, dynamic> json) => _$AuditLogListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$AuditLogListResponseToJson(this);
}

@JsonSerializable()
class AuditLogFilter {
  final String? actorId;
  final String? actorRole;
  final String? action;
  final String? resourceType;
  final String? resourceId;
  final DateTime? fromDate;
  final DateTime? toDate;
  final int page;
  final int pageSize;

  AuditLogFilter({
    this.actorId,
    this.actorRole,
    this.action,
    this.resourceType,
    this.resourceId,
    this.fromDate,
    this.toDate,
    this.page = 1,
    this.pageSize = 20,
  });

  factory AuditLogFilter.fromJson(Map<String, dynamic> json) => _$AuditLogFilterFromJson(json);
  Map<String, dynamic> toJson() => _$AuditLogFilterToJson(this);
}

@JsonSerializable()
class ChainIntegrityReport {
  final bool isValid;
  final int totalEntries;
  final int validEntries;
  final int brokenEntries;
  final List<ChainBreak> breaks;
  final DateTime checkedAt;

  ChainIntegrityReport({
    required this.isValid,
    required this.totalEntries,
    required this.validEntries,
    required this.brokenEntries,
    required this.breaks,
    required this.checkedAt,
  });

  factory ChainIntegrityReport.fromJson(Map<String, dynamic> json) => _$ChainIntegrityReportFromJson(json);
  Map<String, dynamic> toJson() => _$ChainIntegrityReportToJson(this);
}

@JsonSerializable()
class ChainBreak {
  final String entryId;
  final int index;
  final String expectedHash;
  final String actualHash;
  final String previousEntryId;

  ChainBreak({
    required this.entryId,
    required this.index,
    required this.expectedHash,
    required this.actualHash,
    required this.previousEntryId,
  });

  factory ChainBreak.fromJson(Map<String, dynamic> json) => _$ChainBreakFromJson(json);
  Map<String, dynamic> toJson() => _$ChainBreakToJson(this);
}

enum AuditAction {
  create,
  read,
  update,
  delete,
  login,
  logout,
  review,
  approve,
  reject,
  assign,
  unassign,
  block,
  unblock,
  enroll,
  sync,
  export,
  import,
}

extension AuditActionExtension on AuditAction {
  String get value {
    switch (this) {
      case AuditAction.create: return 'CREATE';
      case AuditAction.read: return 'READ';
      case AuditAction.update: return 'UPDATE';
      case AuditAction.delete: return 'DELETE';
      case AuditAction.login: return 'LOGIN';
      case AuditAction.logout: return 'LOGOUT';
      case AuditAction.review: return 'REVIEW';
      case AuditAction.approve: return 'APPROVE';
      case AuditAction.reject: return 'REJECT';
      case AuditAction.assign: return 'ASSIGN';
      case AuditAction.unassign: return 'UNASSIGN';
      case AuditAction.block: return 'BLOCK';
      case AuditAction.unblock: return 'UNBLOCK';
      case AuditAction.enroll: return 'ENROLL';
      case AuditAction.sync: return 'SYNC';
      case AuditAction.export: return 'EXPORT';
      case AuditAction.import: return 'IMPORT';
    }
  }
  
  static AuditAction fromString(String value) {
    return AuditAction.values.firstWhere(
      (e) => e.value == value,
      orElse: () => AuditAction.read,
    );
  }
}