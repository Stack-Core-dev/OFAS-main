import 'package:json_annotation/json_annotation.dart';

part 'phone.g.dart';

@JsonSerializable()
class Phone {
  final String id;
  final String deviceId;
  final String model;
  final String manufacturer;
  final String androidVersion;
  final String publicKey;
  final String status;
  final String registeredBy;
  final DateTime registeredAt;
  final DateTime? lastSeenAt;
  final DateTime? blockedAt;
  final String? blockedBy;
  final String? blockReason;
  final Map<String, dynamic> metadata;

  Phone({
    required this.id,
    required this.deviceId,
    required this.model,
    required this.manufacturer,
    required this.androidVersion,
    required this.publicKey,
    required this.status,
    required this.registeredBy,
    required this.registeredAt,
    this.lastSeenAt,
    this.blockedAt,
    this.blockedBy,
    this.blockReason,
    this.metadata = const {},
  });

  bool get isActive => status == 'ACTIVE';
  bool get isBlocked => status == 'BLOCKED';
  bool get isLost => status == 'LOST';

  factory Phone.fromJson(Map<String, dynamic> json) => _$PhoneFromJson(json);
  Map<String, dynamic> toJson() => _$PhoneToJson(this);
}

@JsonSerializable()
class RegisterPhoneRequest {
  final String deviceId;
  final String model;
  final String manufacturer;
  final String androidVersion;
  final String publicKey;
  final Map<String, dynamic> metadata;

  RegisterPhoneRequest({
    required this.deviceId,
    required this.model,
    required this.manufacturer,
    required this.androidVersion,
    required this.publicKey,
    this.metadata = const {},
  });

  factory RegisterPhoneRequest.fromJson(Map<String, dynamic> json) => _$RegisterPhoneRequestFromJson(json);
  Map<String, dynamic> toJson() => _$RegisterPhoneRequestToJson(this);
}

@JsonSerializable()
class UpdatePhoneStatusRequest {
  final String status;
  final String? reason;

  UpdatePhoneStatusRequest({
    required this.status,
    this.reason,
  });

  factory UpdatePhoneStatusRequest.fromJson(Map<String, dynamic> json) => _$UpdatePhoneStatusRequestFromJson(json);
  Map<String, dynamic> toJson() => _$UpdatePhoneStatusRequestToJson(this);
}

@JsonSerializable()
class PhoneListResponse {
  final List<Phone> phones;
  final int total;
  final int page;
  final int pageSize;

  PhoneListResponse({
    required this.phones,
    required this.total,
    required this.page,
    required this.pageSize,
  });

  factory PhoneListResponse.fromJson(Map<String, dynamic> json) => _$PhoneListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$PhoneListResponseToJson(this);
}

@JsonSerializable()
class PhoneStats {
  final int total;
  final int active;
  final int blocked;
  final int lost;
  final int neverUsed;

  PhoneStats({
    required this.total,
    required this.active,
    required this.blocked,
    required this.lost,
    required this.neverUsed,
  });

  factory PhoneStats.fromJson(Map<String, dynamic> json) => _$PhoneStatsFromJson(json);
  Map<String, dynamic> toJson() => _$PhoneStatsToJson(this);
}