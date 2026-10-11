import 'package:json_annotation/json_annotation.dart';
import 'package:latlong2/latlong.dart';

part 'field.g.dart';

@JsonSerializable()
class Field {
  final String id;
  final String name;
  final String description;
  final double centerLatitude;
  final double centerLongitude;
  final double radiusMeters;
  final String cropType;
  final String season;
  final List<FieldPhoto> referencePhotos;
  final String createdBy;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final bool isActive;

  Field({
    required this.id,
    required this.name,
    required this.description,
    required this.centerLatitude,
    required this.centerLongitude,
    required this.radiusMeters,
    required this.cropType,
    required this.season,
    this.referencePhotos = const [],
    required this.createdBy,
    required this.createdAt,
    this.updatedAt,
    this.isActive = true,
  });

  LatLng get center => LatLng(centerLatitude, centerLongitude);
  
  bool containsPoint(LatLng point) {
    final distance = const Distance().as(LengthUnit.Meter, center, point);
    return distance <= radiusMeters;
  }

  factory Field.fromJson(Map<String, dynamic> json) => _$FieldFromJson(json);
  Map<String, dynamic> toJson() => _$FieldToJson(this);
}

@JsonSerializable()
class FieldPhoto {
  final String id;
  final String url;
  final String thumbnailUrl;
  final int width;
  final int height;
  final DateTime capturedAt;
  final double? latitude;
  final double? longitude;

  FieldPhoto({
    required this.id,
    required this.url,
    required this.thumbnailUrl,
    required this.width,
    required this.height,
    required this.capturedAt,
    this.latitude,
    this.longitude,
  });

  factory FieldPhoto.fromJson(Map<String, dynamic> json) => _$FieldPhotoFromJson(json);
  Map<String, dynamic> toJson() => _$FieldPhotoToJson(this);
}

@JsonSerializable()
class CreateFieldRequest {
  final String name;
  final String description;
  final double centerLatitude;
  final double centerLongitude;
  final double radiusMeters;
  final String cropType;
  final String season;
  final List<String> referencePhotoIds;

  CreateFieldRequest({
    required this.name,
    required this.description,
    required this.centerLatitude,
    required this.centerLongitude,
    required this.radiusMeters,
    required this.cropType,
    required this.season,
    this.referencePhotoIds = const [],
  });

  factory CreateFieldRequest.fromJson(Map<String, dynamic> json) => _$CreateFieldRequestFromJson(json);
  Map<String, dynamic> toJson() => _$CreateFieldRequestToJson(this);
}

@JsonSerializable()
class UpdateFieldRequest {
  final String? name;
  final String? description;
  final double? centerLatitude;
  final double? centerLongitude;
  final double? radiusMeters;
  final String? cropType;
  final String? season;
  final List<String>? referencePhotoIds;
  final bool? isActive;

  UpdateFieldRequest({
    this.name,
    this.description,
    this.centerLatitude,
    this.centerLongitude,
    this.radiusMeters,
    this.cropType,
    this.season,
    this.referencePhotoIds,
    this.isActive,
  });

  factory UpdateFieldRequest.fromJson(Map<String, dynamic> json) => _$UpdateFieldRequestFromJson(json);
  Map<String, dynamic> toJson() => _$UpdateFieldRequestToJson(this);
}

@JsonSerializable()
class FieldListResponse {
  final List<Field> fields;
  final int total;
  final int page;
  final int pageSize;

  FieldListResponse({
    required this.fields,
    required this.total,
    required this.page,
    required this.pageSize,
  });

  factory FieldListResponse.fromJson(Map<String, dynamic> json) => _$FieldListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$FieldListResponseToJson(this);
}