// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'audit.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AuditLog _$AuditLogFromJson(Map<String, dynamic> json) => AuditLog(
      id: json['id'] as String,
      actorId: json['actorId'] as String,
      actorRole: json['actorRole'] as String,
      action: json['action'] as String,
      resourceType: json['resourceType'] as String,
      resourceId: json['resourceId'] as String,
      oldValues: json['oldValues'] as Map<String, dynamic>,
      newValues: json['newValues'] as Map<String, dynamic>,
      ipAddress: json['ipAddress'] as String,
      userAgent: json['userAgent'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      hash: json['hash'] as String,
      previousHash: json['previousHash'] as String,
      chainValid: json['chainValid'] as bool? ?? true,
    );

Map<String, dynamic> _$AuditLogToJson(AuditLog instance) => <String, dynamic>{
      'id': instance.id,
      'actorId': instance.actorId,
      'actorRole': instance.actorRole,
      'action': instance.action,
      'resourceType': instance.resourceType,
      'resourceId': instance.resourceId,
      'oldValues': instance.oldValues,
      'newValues': instance.newValues,
      'ipAddress': instance.ipAddress,
      'userAgent': instance.userAgent,
      'timestamp': instance.timestamp.toIso8601String(),
      'hash': instance.hash,
      'previousHash': instance.previousHash,
      'chainValid': instance.chainValid,
    };

AuditLogListResponse _$AuditLogListResponseFromJson(
        Map<String, dynamic> json) =>
    AuditLogListResponse(
      logs: (json['logs'] as List<dynamic>)
          .map((e) => AuditLog.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num).toInt(),
      page: (json['page'] as num).toInt(),
      pageSize: (json['pageSize'] as num).toInt(),
      chainIntegrityValid: json['chainIntegrityValid'] as bool,
    );

Map<String, dynamic> _$AuditLogListResponseToJson(
        AuditLogListResponse instance) =>
    <String, dynamic>{
      'logs': instance.logs,
      'total': instance.total,
      'page': instance.page,
      'pageSize': instance.pageSize,
      'chainIntegrityValid': instance.chainIntegrityValid,
    };

AuditLogFilter _$AuditLogFilterFromJson(Map<String, dynamic> json) =>
    AuditLogFilter(
      actorId: json['actorId'] as String?,
      actorRole: json['actorRole'] as String?,
      action: json['action'] as String?,
      resourceType: json['resourceType'] as String?,
      resourceId: json['resourceId'] as String?,
      fromDate: json['fromDate'] == null
          ? null
          : DateTime.parse(json['fromDate'] as String),
      toDate: json['toDate'] == null
          ? null
          : DateTime.parse(json['toDate'] as String),
      page: (json['page'] as num?)?.toInt() ?? 1,
      pageSize: (json['pageSize'] as num?)?.toInt() ?? 20,
    );

Map<String, dynamic> _$AuditLogFilterToJson(AuditLogFilter instance) =>
    <String, dynamic>{
      'actorId': instance.actorId,
      'actorRole': instance.actorRole,
      'action': instance.action,
      'resourceType': instance.resourceType,
      'resourceId': instance.resourceId,
      'fromDate': instance.fromDate?.toIso8601String(),
      'toDate': instance.toDate?.toIso8601String(),
      'page': instance.page,
      'pageSize': instance.pageSize,
    };

ChainIntegrityReport _$ChainIntegrityReportFromJson(
        Map<String, dynamic> json) =>
    ChainIntegrityReport(
      isValid: json['isValid'] as bool,
      totalEntries: (json['totalEntries'] as num).toInt(),
      validEntries: (json['validEntries'] as num).toInt(),
      brokenEntries: (json['brokenEntries'] as num).toInt(),
      breaks: (json['breaks'] as List<dynamic>)
          .map((e) => ChainBreak.fromJson(e as Map<String, dynamic>))
          .toList(),
      checkedAt: DateTime.parse(json['checkedAt'] as String),
    );

Map<String, dynamic> _$ChainIntegrityReportToJson(
        ChainIntegrityReport instance) =>
    <String, dynamic>{
      'isValid': instance.isValid,
      'totalEntries': instance.totalEntries,
      'validEntries': instance.validEntries,
      'brokenEntries': instance.brokenEntries,
      'breaks': instance.breaks,
      'checkedAt': instance.checkedAt.toIso8601String(),
    };

ChainBreak _$ChainBreakFromJson(Map<String, dynamic> json) => ChainBreak(
      entryId: json['entryId'] as String,
      index: (json['index'] as num).toInt(),
      expectedHash: json['expectedHash'] as String,
      actualHash: json['actualHash'] as String,
      previousEntryId: json['previousEntryId'] as String,
    );

Map<String, dynamic> _$ChainBreakToJson(ChainBreak instance) =>
    <String, dynamic>{
      'entryId': instance.entryId,
      'index': instance.index,
      'expectedHash': instance.expectedHash,
      'actualHash': instance.actualHash,
      'previousEntryId': instance.previousEntryId,
    };
