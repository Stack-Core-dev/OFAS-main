// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'visit.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Visit _$VisitFromJson(Map<String, dynamic> json) => Visit(
      id: json['id'] as String,
      surveyorId: json['surveyorId'] as String,
      fieldId: json['fieldId'] as String,
      phoneId: json['phoneId'] as String,
      status: $enumDecode(_$VisitStatusEnumMap, json['status']),
      selfie: VisitSelfie.fromJson(json['selfie'] as Map<String, dynamic>),
      photos: (json['photos'] as List<dynamic>?)
              ?.map((e) => VisitPhoto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      trailSnapshot:
          TrailSnapshot.fromJson(json['trailSnapshot'] as Map<String, dynamic>),
      signature:
          VisitSignature.fromJson(json['signature'] as Map<String, dynamic>),
      startedAt: DateTime.parse(json['startedAt'] as String),
      completedAt: DateTime.parse(json['completedAt'] as String),
      reviewedAt: json['reviewedAt'] == null
          ? null
          : DateTime.parse(json['reviewedAt'] as String),
      reviewedBy: json['reviewedBy'] as String?,
      reviewNotes: json['reviewNotes'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$VisitToJson(Visit instance) => <String, dynamic>{
      'id': instance.id,
      'surveyorId': instance.surveyorId,
      'fieldId': instance.fieldId,
      'phoneId': instance.phoneId,
      'status': _$VisitStatusEnumMap[instance.status]!,
      'selfie': instance.selfie,
      'photos': instance.photos,
      'trailSnapshot': instance.trailSnapshot,
      'signature': instance.signature,
      'startedAt': instance.startedAt.toIso8601String(),
      'completedAt': instance.completedAt.toIso8601String(),
      'reviewedAt': instance.reviewedAt?.toIso8601String(),
      'reviewedBy': instance.reviewedBy,
      'reviewNotes': instance.reviewNotes,
      'metadata': instance.metadata,
    };

const _$VisitStatusEnumMap = {
  VisitStatus.queued: 'queued',
  VisitStatus.syncing: 'syncing',
  VisitStatus.synced: 'synced',
  VisitStatus.failed: 'failed',
  VisitStatus.valid: 'valid',
  VisitStatus.invalid: 'invalid',
  VisitStatus.flagged: 'flagged',
};

VisitSelfie _$VisitSelfieFromJson(Map<String, dynamic> json) => VisitSelfie(
      photoId: json['photoId'] as String,
      url: json['url'] as String,
      thumbnailUrl: json['thumbnailUrl'] as String,
      capturedAt: DateTime.parse(json['capturedAt'] as String),
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      accuracyMeters: (json['accuracyMeters'] as num).toDouble(),
      satelliteCount: (json['satelliteCount'] as num).toInt(),
      faceMatchScore: (json['faceMatchScore'] as num).toDouble(),
      livenessVerified: json['livenessVerified'] as bool,
      blinkChallengeId: json['blinkChallengeId'] as String,
    );

Map<String, dynamic> _$VisitSelfieToJson(VisitSelfie instance) =>
    <String, dynamic>{
      'photoId': instance.photoId,
      'url': instance.url,
      'thumbnailUrl': instance.thumbnailUrl,
      'capturedAt': instance.capturedAt.toIso8601String(),
      'latitude': instance.latitude,
      'longitude': instance.longitude,
      'accuracyMeters': instance.accuracyMeters,
      'satelliteCount': instance.satelliteCount,
      'faceMatchScore': instance.faceMatchScore,
      'livenessVerified': instance.livenessVerified,
      'blinkChallengeId': instance.blinkChallengeId,
    };

VisitPhoto _$VisitPhotoFromJson(Map<String, dynamic> json) => VisitPhoto(
      id: json['id'] as String,
      url: json['url'] as String,
      thumbnailUrl: json['thumbnailUrl'] as String,
      capturedAt: DateTime.parse(json['capturedAt'] as String),
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      accuracyMeters: (json['accuracyMeters'] as num).toDouble(),
      satelliteCount: (json['satelliteCount'] as num).toInt(),
      sha256Hash: json['sha256Hash'] as String,
      width: (json['width'] as num).toInt(),
      height: (json['height'] as num).toInt(),
      fileSizeBytes: (json['fileSizeBytes'] as num).toInt(),
      sequenceNumber: (json['sequenceNumber'] as num?)?.toInt(),
    );

Map<String, dynamic> _$VisitPhotoToJson(VisitPhoto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'url': instance.url,
      'thumbnailUrl': instance.thumbnailUrl,
      'capturedAt': instance.capturedAt.toIso8601String(),
      'latitude': instance.latitude,
      'longitude': instance.longitude,
      'accuracyMeters': instance.accuracyMeters,
      'satelliteCount': instance.satelliteCount,
      'sha256Hash': instance.sha256Hash,
      'width': instance.width,
      'height': instance.height,
      'fileSizeBytes': instance.fileSizeBytes,
      'sequenceNumber': instance.sequenceNumber,
    };

TrailSnapshot _$TrailSnapshotFromJson(Map<String, dynamic> json) =>
    TrailSnapshot(
      trailId: json['trailId'] as String,
      entries: (json['entries'] as List<dynamic>)
          .map((e) => TrailEntry.fromJson(e as Map<String, dynamic>))
          .toList(),
      chainHash: json['chainHash'] as String,
      snapshotAt: DateTime.parse(json['snapshotAt'] as String),
    );

Map<String, dynamic> _$TrailSnapshotToJson(TrailSnapshot instance) =>
    <String, dynamic>{
      'trailId': instance.trailId,
      'entries': instance.entries,
      'chainHash': instance.chainHash,
      'snapshotAt': instance.snapshotAt.toIso8601String(),
    };

TrailEntry _$TrailEntryFromJson(Map<String, dynamic> json) => TrailEntry(
      id: json['id'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      accuracyMeters: (json['accuracyMeters'] as num).toDouble(),
      satelliteCount: (json['satelliteCount'] as num).toInt(),
      speedMps: (json['speedMps'] as num).toDouble(),
      bearingDegrees: (json['bearingDegrees'] as num).toDouble(),
      previousHash: json['previousHash'] as String,
      hash: json['hash'] as String,
      signature: json['signature'] as String,
    );

Map<String, dynamic> _$TrailEntryToJson(TrailEntry instance) =>
    <String, dynamic>{
      'id': instance.id,
      'timestamp': instance.timestamp.toIso8601String(),
      'latitude': instance.latitude,
      'longitude': instance.longitude,
      'accuracyMeters': instance.accuracyMeters,
      'satelliteCount': instance.satelliteCount,
      'speedMps': instance.speedMps,
      'bearingDegrees': instance.bearingDegrees,
      'previousHash': instance.previousHash,
      'hash': instance.hash,
      'signature': instance.signature,
    };

VisitSignature _$VisitSignatureFromJson(Map<String, dynamic> json) =>
    VisitSignature(
      algorithm: json['algorithm'] as String,
      publicKeyId: json['publicKeyId'] as String,
      signature: json['signature'] as String,
      payloadHash: json['payloadHash'] as String,
    );

Map<String, dynamic> _$VisitSignatureToJson(VisitSignature instance) =>
    <String, dynamic>{
      'algorithm': instance.algorithm,
      'publicKeyId': instance.publicKeyId,
      'signature': instance.signature,
      'payloadHash': instance.payloadHash,
    };

VisitListResponse _$VisitListResponseFromJson(Map<String, dynamic> json) =>
    VisitListResponse(
      visits: (json['visits'] as List<dynamic>)
          .map((e) => Visit.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num).toInt(),
      page: (json['page'] as num).toInt(),
      pageSize: (json['pageSize'] as num).toInt(),
      stats: VisitStats.fromJson(json['stats'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$VisitListResponseToJson(VisitListResponse instance) =>
    <String, dynamic>{
      'visits': instance.visits,
      'total': instance.total,
      'page': instance.page,
      'pageSize': instance.pageSize,
      'stats': instance.stats,
    };

VisitStats _$VisitStatsFromJson(Map<String, dynamic> json) => VisitStats(
      total: (json['total'] as num).toInt(),
      valid: (json['valid'] as num).toInt(),
      invalid: (json['invalid'] as num).toInt(),
      flagged: (json['flagged'] as num).toInt(),
      pending: (json['pending'] as num).toInt(),
      failed: (json['failed'] as num).toInt(),
    );

Map<String, dynamic> _$VisitStatsToJson(VisitStats instance) =>
    <String, dynamic>{
      'total': instance.total,
      'valid': instance.valid,
      'invalid': instance.invalid,
      'flagged': instance.flagged,
      'pending': instance.pending,
      'failed': instance.failed,
    };

ReviewVisitRequest _$ReviewVisitRequestFromJson(Map<String, dynamic> json) =>
    ReviewVisitRequest(
      status: $enumDecode(_$VisitStatusEnumMap, json['status']),
      notes: json['notes'] as String?,
      comparisonResults:
          json['comparisonResults'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$ReviewVisitRequestToJson(ReviewVisitRequest instance) =>
    <String, dynamic>{
      'status': _$VisitStatusEnumMap[instance.status]!,
      'notes': instance.notes,
      'comparisonResults': instance.comparisonResults,
    };

PhotoComparisonResult _$PhotoComparisonResultFromJson(
        Map<String, dynamic> json) =>
    PhotoComparisonResult(
      visitPhotoId: json['visitPhotoId'] as String,
      referencePhotoId: json['referencePhotoId'] as String,
      similarityScore: (json['similarityScore'] as num).toDouble(),
      isMatch: json['isMatch'] as bool,
      notes: json['notes'] as String?,
    );

Map<String, dynamic> _$PhotoComparisonResultToJson(
        PhotoComparisonResult instance) =>
    <String, dynamic>{
      'visitPhotoId': instance.visitPhotoId,
      'referencePhotoId': instance.referencePhotoId,
      'similarityScore': instance.similarityScore,
      'isMatch': instance.isMatch,
      'notes': instance.notes,
    };
