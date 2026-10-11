// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'phone.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Phone _$PhoneFromJson(Map<String, dynamic> json) => Phone(
      id: json['id'] as String,
      deviceId: json['deviceId'] as String,
      model: json['model'] as String,
      manufacturer: json['manufacturer'] as String,
      androidVersion: json['androidVersion'] as String,
      publicKey: json['publicKey'] as String,
      status: json['status'] as String,
      registeredBy: json['registeredBy'] as String,
      registeredAt: DateTime.parse(json['registeredAt'] as String),
      lastSeenAt: json['lastSeenAt'] == null
          ? null
          : DateTime.parse(json['lastSeenAt'] as String),
      blockedAt: json['blockedAt'] == null
          ? null
          : DateTime.parse(json['blockedAt'] as String),
      blockedBy: json['blockedBy'] as String?,
      blockReason: json['blockReason'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$PhoneToJson(Phone instance) => <String, dynamic>{
      'id': instance.id,
      'deviceId': instance.deviceId,
      'model': instance.model,
      'manufacturer': instance.manufacturer,
      'androidVersion': instance.androidVersion,
      'publicKey': instance.publicKey,
      'status': instance.status,
      'registeredBy': instance.registeredBy,
      'registeredAt': instance.registeredAt.toIso8601String(),
      'lastSeenAt': instance.lastSeenAt?.toIso8601String(),
      'blockedAt': instance.blockedAt?.toIso8601String(),
      'blockedBy': instance.blockedBy,
      'blockReason': instance.blockReason,
      'metadata': instance.metadata,
    };

RegisterPhoneRequest _$RegisterPhoneRequestFromJson(
        Map<String, dynamic> json) =>
    RegisterPhoneRequest(
      deviceId: json['deviceId'] as String,
      model: json['model'] as String,
      manufacturer: json['manufacturer'] as String,
      androidVersion: json['androidVersion'] as String,
      publicKey: json['publicKey'] as String,
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$RegisterPhoneRequestToJson(
        RegisterPhoneRequest instance) =>
    <String, dynamic>{
      'deviceId': instance.deviceId,
      'model': instance.model,
      'manufacturer': instance.manufacturer,
      'androidVersion': instance.androidVersion,
      'publicKey': instance.publicKey,
      'metadata': instance.metadata,
    };

UpdatePhoneStatusRequest _$UpdatePhoneStatusRequestFromJson(
        Map<String, dynamic> json) =>
    UpdatePhoneStatusRequest(
      status: json['status'] as String,
      reason: json['reason'] as String?,
    );

Map<String, dynamic> _$UpdatePhoneStatusRequestToJson(
        UpdatePhoneStatusRequest instance) =>
    <String, dynamic>{
      'status': instance.status,
      'reason': instance.reason,
    };

PhoneListResponse _$PhoneListResponseFromJson(Map<String, dynamic> json) =>
    PhoneListResponse(
      phones: (json['phones'] as List<dynamic>)
          .map((e) => Phone.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num).toInt(),
      page: (json['page'] as num).toInt(),
      pageSize: (json['pageSize'] as num).toInt(),
    );

Map<String, dynamic> _$PhoneListResponseToJson(PhoneListResponse instance) =>
    <String, dynamic>{
      'phones': instance.phones,
      'total': instance.total,
      'page': instance.page,
      'pageSize': instance.pageSize,
    };

PhoneStats _$PhoneStatsFromJson(Map<String, dynamic> json) => PhoneStats(
      total: (json['total'] as num).toInt(),
      active: (json['active'] as num).toInt(),
      blocked: (json['blocked'] as num).toInt(),
      lost: (json['lost'] as num).toInt(),
      neverUsed: (json['neverUsed'] as num).toInt(),
    );

Map<String, dynamic> _$PhoneStatsToJson(PhoneStats instance) =>
    <String, dynamic>{
      'total': instance.total,
      'active': instance.active,
      'blocked': instance.blocked,
      'lost': instance.lost,
      'neverUsed': instance.neverUsed,
    };
