// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'field.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Field _$FieldFromJson(Map<String, dynamic> json) => Field(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      centerLatitude: (json['centerLatitude'] as num).toDouble(),
      centerLongitude: (json['centerLongitude'] as num).toDouble(),
      radiusMeters: (json['radiusMeters'] as num).toDouble(),
      cropType: json['cropType'] as String,
      season: json['season'] as String,
      referencePhotos: (json['referencePhotos'] as List<dynamic>?)
              ?.map((e) => FieldPhoto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      createdBy: json['createdBy'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: json['updatedAt'] == null
          ? null
          : DateTime.parse(json['updatedAt'] as String),
      isActive: json['isActive'] as bool? ?? true,
    );

Map<String, dynamic> _$FieldToJson(Field instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'centerLatitude': instance.centerLatitude,
      'centerLongitude': instance.centerLongitude,
      'radiusMeters': instance.radiusMeters,
      'cropType': instance.cropType,
      'season': instance.season,
      'referencePhotos': instance.referencePhotos,
      'createdBy': instance.createdBy,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt?.toIso8601String(),
      'isActive': instance.isActive,
    };

FieldPhoto _$FieldPhotoFromJson(Map<String, dynamic> json) => FieldPhoto(
      id: json['id'] as String,
      url: json['url'] as String,
      thumbnailUrl: json['thumbnailUrl'] as String,
      width: (json['width'] as num).toInt(),
      height: (json['height'] as num).toInt(),
      capturedAt: DateTime.parse(json['capturedAt'] as String),
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$FieldPhotoToJson(FieldPhoto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'url': instance.url,
      'thumbnailUrl': instance.thumbnailUrl,
      'width': instance.width,
      'height': instance.height,
      'capturedAt': instance.capturedAt.toIso8601String(),
      'latitude': instance.latitude,
      'longitude': instance.longitude,
    };

CreateFieldRequest _$CreateFieldRequestFromJson(Map<String, dynamic> json) =>
    CreateFieldRequest(
      name: json['name'] as String,
      description: json['description'] as String,
      centerLatitude: (json['centerLatitude'] as num).toDouble(),
      centerLongitude: (json['centerLongitude'] as num).toDouble(),
      radiusMeters: (json['radiusMeters'] as num).toDouble(),
      cropType: json['cropType'] as String,
      season: json['season'] as String,
      referencePhotoIds: (json['referencePhotoIds'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$CreateFieldRequestToJson(CreateFieldRequest instance) =>
    <String, dynamic>{
      'name': instance.name,
      'description': instance.description,
      'centerLatitude': instance.centerLatitude,
      'centerLongitude': instance.centerLongitude,
      'radiusMeters': instance.radiusMeters,
      'cropType': instance.cropType,
      'season': instance.season,
      'referencePhotoIds': instance.referencePhotoIds,
    };

UpdateFieldRequest _$UpdateFieldRequestFromJson(Map<String, dynamic> json) =>
    UpdateFieldRequest(
      name: json['name'] as String?,
      description: json['description'] as String?,
      centerLatitude: (json['centerLatitude'] as num?)?.toDouble(),
      centerLongitude: (json['centerLongitude'] as num?)?.toDouble(),
      radiusMeters: (json['radiusMeters'] as num?)?.toDouble(),
      cropType: json['cropType'] as String?,
      season: json['season'] as String?,
      referencePhotoIds: (json['referencePhotoIds'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      isActive: json['isActive'] as bool?,
    );

Map<String, dynamic> _$UpdateFieldRequestToJson(UpdateFieldRequest instance) =>
    <String, dynamic>{
      'name': instance.name,
      'description': instance.description,
      'centerLatitude': instance.centerLatitude,
      'centerLongitude': instance.centerLongitude,
      'radiusMeters': instance.radiusMeters,
      'cropType': instance.cropType,
      'season': instance.season,
      'referencePhotoIds': instance.referencePhotoIds,
      'isActive': instance.isActive,
    };

FieldListResponse _$FieldListResponseFromJson(Map<String, dynamic> json) =>
    FieldListResponse(
      fields: (json['fields'] as List<dynamic>)
          .map((e) => Field.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num).toInt(),
      page: (json['page'] as num).toInt(),
      pageSize: (json['pageSize'] as num).toInt(),
    );

Map<String, dynamic> _$FieldListResponseToJson(FieldListResponse instance) =>
    <String, dynamic>{
      'fields': instance.fields,
      'total': instance.total,
      'page': instance.page,
      'pageSize': instance.pageSize,
    };
