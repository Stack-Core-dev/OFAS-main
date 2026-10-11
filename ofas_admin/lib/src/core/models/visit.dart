import 'package:json_annotation/json_annotation.dart';
import 'package:latlong2/latlong.dart';

part 'visit.g.dart';

enum VisitStatus {
  queued,
  syncing,
  synced,
  failed,
  valid,
  invalid,
  flagged,
}

extension VisitStatusExtension on VisitStatus {
  String get value {
    switch (this) {
      case VisitStatus.queued: return 'QUEUED';
      case VisitStatus.syncing: return 'SYNCING';
      case VisitStatus.synced: return 'SYNCED';
      case VisitStatus.failed: return 'FAILED';
      case VisitStatus.valid: return 'VALID';
      case VisitStatus.invalid: return 'INVALID';
      case VisitStatus.flagged: return 'FLAGGED';
    }
  }

  static VisitStatus fromString(String value) {
    switch (value.toUpperCase()) {
      case 'QUEUED': return VisitStatus.queued;
      case 'SYNCING': return VisitStatus.syncing;
      case 'SYNCED': return VisitStatus.synced;
      case 'FAILED': return VisitStatus.failed;
      case 'VALID': return VisitStatus.valid;
      case 'INVALID': return VisitStatus.invalid;
      case 'FLAGGED': return VisitStatus.flagged;
      default: return VisitStatus.queued;
    }
  }
}

@JsonSerializable()
class Visit {
  final String id;
  final String surveyorId;
  final String fieldId;
  final String phoneId;
  final VisitStatus status;
  final VisitSelfie selfie;
  final List<VisitPhoto> photos;
  final TrailSnapshot trailSnapshot;
  final VisitSignature signature;
  final DateTime startedAt;
  final DateTime completedAt;
  final DateTime? reviewedAt;
  final String? reviewedBy;
  final String? reviewNotes;
  final Map<String, dynamic> metadata;

  Visit({
    required this.id,
    required this.surveyorId,
    required this.fieldId,
    required this.phoneId,
    required this.status,
    required this.selfie,
    this.photos = const [],
    required this.trailSnapshot,
    required this.signature,
    required this.startedAt,
    required this.completedAt,
    this.reviewedAt,
    this.reviewedBy,
    this.reviewNotes,
    this.metadata = const {},
  });

  int get photoCount => photos.length;
  
  bool get isReviewed => status == VisitStatus.valid || status == VisitStatus.invalid || status == VisitStatus.flagged;
  
  Duration get duration => completedAt.difference(startedAt);

  factory Visit.fromJson(Map<String, dynamic> json) => _$VisitFromJson(json);
  Map<String, dynamic> toJson() => _$VisitToJson(this);
}

@JsonSerializable()
class VisitSelfie {
  final String photoId;
  final String url;
  final String thumbnailUrl;
  final DateTime capturedAt;
  final double latitude;
  final double longitude;
  final double accuracyMeters;
  final int satelliteCount;
  final double faceMatchScore;
  final bool livenessVerified;
  final String blinkChallengeId;

  VisitSelfie({
    required this.photoId,
    required this.url,
    required this.thumbnailUrl,
    required this.capturedAt,
    required this.latitude,
    required this.longitude,
    required this.accuracyMeters,
    required this.satelliteCount,
    required this.faceMatchScore,
    required this.livenessVerified,
    required this.blinkChallengeId,
  });

  LatLng get location => LatLng(latitude, longitude);

  factory VisitSelfie.fromJson(Map<String, dynamic> json) => _$VisitSelfieFromJson(json);
  Map<String, dynamic> toJson() => _$VisitSelfieToJson(this);
}

@JsonSerializable()
class VisitPhoto {
  final String id;
  final String url;
  final String thumbnailUrl;
  final DateTime capturedAt;
  final double latitude;
  final double longitude;
  final double accuracyMeters;
  final int satelliteCount;
  final String sha256Hash;
  final int width;
  final int height;
  final int fileSizeBytes;
  final int? sequenceNumber;

  VisitPhoto({
    required this.id,
    required this.url,
    required this.thumbnailUrl,
    required this.capturedAt,
    required this.latitude,
    required this.longitude,
    required this.accuracyMeters,
    required this.satelliteCount,
    required this.sha256Hash,
    required this.width,
    required this.height,
    required this.fileSizeBytes,
    this.sequenceNumber,
  });

  LatLng get location => LatLng(latitude, longitude);

  factory VisitPhoto.fromJson(Map<String, dynamic> json) => _$VisitPhotoFromJson(json);
  Map<String, dynamic> toJson() => _$VisitPhotoToJson(this);
}

@JsonSerializable()
class TrailSnapshot {
  final String trailId;
  final List<TrailEntry> entries;
  final String chainHash;
  final DateTime snapshotAt;

  TrailSnapshot({
    required this.trailId,
    required this.entries,
    required this.chainHash,
    required this.snapshotAt,
  });

  bool get isValid {
    if (entries.length < 2) return true;
    for (int i = 1; i < entries.length; i++) {
      if (entries[i].previousHash != entries[i - 1].hash) {
        return false;
      }
    }
    return entries.last.hash == chainHash;
  }

  factory TrailSnapshot.fromJson(Map<String, dynamic> json) => _$TrailSnapshotFromJson(json);
  Map<String, dynamic> toJson() => _$TrailSnapshotToJson(this);
}

@JsonSerializable()
class TrailEntry {
  final String id;
  final DateTime timestamp;
  final double latitude;
  final double longitude;
  final double accuracyMeters;
  final int satelliteCount;
  final double speedMps;
  final double bearingDegrees;
  final String previousHash;
  final String hash;
  final String signature;

  TrailEntry({
    required this.id,
    required this.timestamp,
    required this.latitude,
    required this.longitude,
    required this.accuracyMeters,
    required this.satelliteCount,
    required this.speedMps,
    required this.bearingDegrees,
    required this.previousHash,
    required this.hash,
    required this.signature,
  });

  LatLng get location => LatLng(latitude, longitude);

  factory TrailEntry.fromJson(Map<String, dynamic> json) => _$TrailEntryFromJson(json);
  Map<String, dynamic> toJson() => _$TrailEntryToJson(this);
}

@JsonSerializable()
class VisitSignature {
  final String algorithm;
  final String publicKeyId;
  final String signature;
  final String payloadHash;

  VisitSignature({
    required this.algorithm,
    required this.publicKeyId,
    required this.signature,
    required this.payloadHash,
  });

  factory VisitSignature.fromJson(Map<String, dynamic> json) => _$VisitSignatureFromJson(json);
  Map<String, dynamic> toJson() => _$VisitSignatureToJson(this);
}

@JsonSerializable()
class VisitListResponse {
  final List<Visit> visits;
  final int total;
  final int page;
  final int pageSize;
  final VisitStats stats;

  VisitListResponse({
    required this.visits,
    required this.total,
    required this.page,
    required this.pageSize,
    required this.stats,
  });

  factory VisitListResponse.fromJson(Map<String, dynamic> json) => _$VisitListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$VisitListResponseToJson(this);
}

@JsonSerializable()
class VisitStats {
  final int total;
  final int valid;
  final int invalid;
  final int flagged;
  final int pending;
  final int failed;

  VisitStats({
    required this.total,
    required this.valid,
    required this.invalid,
    required this.flagged,
    required this.pending,
    required this.failed,
  });

  factory VisitStats.fromJson(Map<String, dynamic> json) => _$VisitStatsFromJson(json);
  Map<String, dynamic> toJson() => _$VisitStatsToJson(this);
}

@JsonSerializable()
class ReviewVisitRequest {
  final VisitStatus status;
  final String? notes;
  final Map<String, dynamic> comparisonResults;

  ReviewVisitRequest({
    required this.status,
    this.notes,
    this.comparisonResults = const {},
  });

  factory ReviewVisitRequest.fromJson(Map<String, dynamic> json) => _$ReviewVisitRequestFromJson(json);
  Map<String, dynamic> toJson() => _$ReviewVisitRequestToJson(this);
}

@JsonSerializable()
class PhotoComparisonResult {
  final String visitPhotoId;
  final String referencePhotoId;
  final double similarityScore;
  final bool isMatch;
  final String? notes;

  PhotoComparisonResult({
    required this.visitPhotoId,
    required this.referencePhotoId,
    required this.similarityScore,
    required this.isMatch,
    this.notes,
  });

  factory PhotoComparisonResult.fromJson(Map<String, dynamic> json) => _$PhotoComparisonResultFromJson(json);
  Map<String, dynamic> toJson() => _$PhotoComparisonResultToJson(this);
}