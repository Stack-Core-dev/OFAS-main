import re
import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .config import config


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    
    def add_error(self, error: str):
        self.errors.append(error)
        self.is_valid = False


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    pattern = r'^[a-zA-Z0-9_-]{3,50}$'
    return bool(re.match(pattern, username))


def validate_password(password: str) -> Tuple[bool, List[str]]:
    errors = []
    if len(password) < 12:
        errors.append("Password must be at least 12 characters")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    return len(errors) == 0, errors


def validate_coordinates(lat: float, lon: float) -> bool:
    return -90 <= lat <= 90 and -180 <= lon <= 180


def _valid_coord_pair(lat, lon) -> bool:
    """Require a numeric, in-range latitude/longitude pair."""
    if not isinstance(lat, (int, float)) or isinstance(lat, bool):
        return False
    if not isinstance(lon, (int, float)) or isinstance(lon, bool):
        return False
    return validate_coordinates(lat, lon)


def _valid_optional_accuracy(accuracy, max_accuracy: float = 100.0) -> bool:
    """Accuracy is optional, but when supplied it must be a sane distance."""
    if accuracy is None:
        return True
    if not isinstance(accuracy, (int, float)) or isinstance(accuracy, bool):
        return False
    return validate_accuracy(accuracy, max_accuracy)


def validate_accuracy(accuracy: float, max_accuracy: float = 100.0) -> bool:
    return 0 <= accuracy <= max_accuracy


def validate_timestamp(timestamp, max_age_seconds: int = 300, 
                        allow_future: bool = False) -> bool:
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return False
    
    if not isinstance(timestamp, datetime):
        return False
    
    # Make both timezone-aware for comparison
    if timestamp.tzinfo is not None:
        now = datetime.now(timezone.utc)
    else:
        now = datetime.utcnow()
    
    if not allow_future and timestamp > now + timedelta(seconds=10):
        return False
    if timestamp < now - timedelta(seconds=max_age_seconds):
        return False
    return True


def validate_visit_id(visit_id: str) -> bool:
    pattern = r'^[a-f0-9]{64}$'
    return bool(re.match(pattern, visit_id))


def validate_base64_image(data: str, max_size_mb: int = 2) -> Tuple[bool, List[str]]:
    errors = []
    try:
        if data.startswith('data:image/'):
            data = data.split(',', 1)[1]
        decoded = base64.b64decode(data)
        size_mb = len(decoded) / (1024 * 1024)
        if size_mb > max_size_mb:
            errors.append(f"Image size {size_mb:.1f}MB exceeds maximum {max_size_mb}MB")
        if len(decoded) < 100:
            errors.append("Image data too small")
    except Exception as e:
        errors.append(f"Invalid base64 image data: {str(e)}")
    return len(errors) == 0, errors


def validate_sha256_hash(hash_str: str) -> bool:
    pattern = r'^[a-f0-9]{64}$'
    return bool(re.match(pattern, hash_str))


def validate_face_template(template: bytes) -> Tuple[bool, List[str]]:
    errors = []
    if not template:
        errors.append("Face template is empty")
        return False, errors
    if len(template) < 100:
        errors.append("Face template too small")
    if len(template) > 10000:
        errors.append("Face template too large")
    return len(errors) == 0, errors


def validate_visit_payload(payload: Dict[str, Any], app_config) -> ValidationResult:
    result = ValidationResult(True, [])
    app_config = app_config or config['default']()
    
    required_fields = [
        'visit_id', 'surveyor_id', 'field_id', 'phone_id',
        'satellite_timestamp', 'latitude', 'longitude', 'accuracy_meters',
        'selfie_photo_hash', 'selfie_latitude', 'selfie_longitude', 'field_photos',
        'face_match_score', 'liveness_verified', 'trail_snapshot', 'signature',
        'signed_by_key_id'
    ]
    
    for field in required_fields:
        if field not in payload:
            result.add_error(f"Missing required field: {field}")
    
    if not result.is_valid:
        return result
    
    if not validate_visit_id(payload['visit_id']):
        result.add_error("Invalid visit_id format")
    
    if not validate_coordinates(payload['latitude'], payload['longitude']):
        result.add_error("Invalid coordinates")
    
    if not validate_accuracy(payload['accuracy_meters'], 100.0):
        result.add_error("Accuracy out of acceptable range")
    
    if not validate_timestamp(payload['satellite_timestamp'], max_age_seconds=app_config.VISIT_MAX_AGE_SECONDS):
        result.add_error("Satellite timestamp too old or in future")
    
    if not validate_sha256_hash(payload['selfie_photo_hash']):
        result.add_error("Invalid selfie photo hash")

    if not _valid_coord_pair(payload.get('selfie_latitude'), payload.get('selfie_longitude')):
        result.add_error("Invalid selfie coordinates")

    if not _valid_optional_accuracy(payload.get('selfie_accuracy_meters')):
        result.add_error("Selfie accuracy out of acceptable range")
    
    if not isinstance(payload['face_match_score'], (int, float)) or \
       not (0 <= payload['face_match_score'] <= 1):
        result.add_error("Face match score must be between 0 and 1")
    
    if payload['face_match_score'] < app_config.FACE_MATCH_THRESHOLD:
        result.add_error(f"Face match score below threshold ({app_config.FACE_MATCH_THRESHOLD})")
    
    if not isinstance(payload['liveness_verified'], bool):
        result.add_error("liveness_verified must be a boolean")
    
    if not isinstance(payload['field_photos'], list):
        result.add_error("field_photos must be a list")
    else:
        if len(payload['field_photos']) < app_config.MIN_PHOTOS_PER_VISIT:
            result.add_error(f"Minimum {app_config.MIN_PHOTOS_PER_VISIT} field photos required")
        if len(payload['field_photos']) > app_config.MAX_PHOTOS_PER_VISIT:
            result.add_error(f"Maximum {app_config.MAX_PHOTOS_PER_VISIT} field photos allowed")
        
        for i, photo in enumerate(payload['field_photos']):
            if not isinstance(photo, dict):
                result.add_error(f"Photo {i}: must be an object")
                continue
            if 'hash' not in photo or not validate_sha256_hash(photo['hash']):
                result.add_error(f"Photo {i}: invalid hash")
            if not _valid_coord_pair(photo.get('latitude'), photo.get('longitude')):
                result.add_error(f"Photo {i}: invalid or missing coordinates")
            if not _valid_optional_accuracy(photo.get('accuracy_meters')):
                result.add_error(f"Photo {i}: accuracy out of acceptable range")
            # s3_key is optional at submit time: photos may be uploaded after the
            # visit record exists (the upload endpoint fills in the real key).
            if 's3_key' in photo and photo['s3_key'] is not None and not isinstance(photo['s3_key'], str):
                result.add_error(f"Photo {i}: s3_key must be text")
            if 'timestamp' in photo:
                try:
                    ts = datetime.fromisoformat(photo['timestamp'].replace('Z', '+00:00'))
                    if not validate_timestamp(ts, max_age_seconds=app_config.VISIT_MAX_AGE_SECONDS):
                        result.add_error(f"Photo {i}: timestamp too old")
                except Exception:
                    result.add_error(f"Photo {i}: invalid timestamp format")
    
    if not isinstance(payload['trail_snapshot'], dict):
        result.add_error("trail_snapshot must be an object")
    else:
        required_trail = ['prev_entry_hash', 'next_entry_hash', 'entries_around']
        for field in required_trail:
            if field not in payload['trail_snapshot']:
                result.add_error(f"trail_snapshot missing field: {field}")
    
    if not validate_base64_signature(payload['signature']):
        result.add_error("Invalid signature format")
    
    return result


def validate_base64_signature(sig: str) -> bool:
    try:
        decoded = base64.b64decode(sig)
        return 64 <= len(decoded) <= 128
    except Exception:
        return False


def validate_field_payload(payload: Dict[str, Any]) -> ValidationResult:
    result = ValidationResult(True, [])
    
    required = ['field_code', 'name', 'center_lat', 'center_lon', 'radius_meters']
    for field in required:
        if field not in payload:
            result.add_error(f"Missing required field: {field}")
    
    if not result.is_valid:
        return result
    
    if not re.match(r'^[A-Z0-9_-]{3,50}$', payload['field_code']):
        result.add_error("field_code must be 3-50 uppercase alphanumeric/underscore/hyphen")
    
    if not validate_coordinates(payload['center_lat'], payload['center_lon']):
        result.add_error("Invalid coordinates")
    
    if not isinstance(payload['radius_meters'], (int, float)) or payload['radius_meters'] <= 0:
        result.add_error("radius_meters must be positive number")
    
    if 'reference_photos' in payload:
        if not isinstance(payload['reference_photos'], list):
            result.add_error("reference_photos must be a list")
        elif len(payload['reference_photos']) > 10:
            result.add_error("Maximum 10 reference photos allowed")
    
    return result


def validate_surveyor_payload(payload: Dict[str, Any]) -> ValidationResult:
    result = ValidationResult(True, [])
    
    required = ['employee_id', 'full_name', 'phone_number', 'password']
    for field in required:
        if field not in payload:
            result.add_error(f"Missing required field: {field}")
    
    if not result.is_valid:
        return result

    if not isinstance(payload['employee_id'], str):
        result.add_error("employee_id must be text")
    if not isinstance(payload['full_name'], str):
        result.add_error("full_name must be text")
    if not isinstance(payload['phone_number'], str):
        result.add_error("phone_number must be text")
    if not isinstance(payload['password'], str):
        result.add_error("password must be text")
    if not result.is_valid:
        return result

    if not re.match(r'^[A-Z0-9_-]{3,50}$', payload['employee_id']):
        result.add_error("employee_id must be 3-50 uppercase alphanumeric/underscore/hyphen")
    
    if len(payload['full_name']) > 200:
        result.add_error("full_name too long (max 200 chars)")

    if not re.match(r'^\+?[1-9]\d{1,14}$', payload['phone_number']):
        result.add_error("Invalid phone number format")

    valid_password, password_errors = validate_password(payload['password'])
    if not valid_password:
        result.errors.extend(password_errors)
        result.is_valid = False
    
    if 'email' in payload and payload['email']:
        if not validate_email(payload['email']):
            result.add_error("Invalid email format")
    
    return result


def validate_assignment_payload(payload: Dict[str, Any]) -> ValidationResult:
    result = ValidationResult(True, [])
    
    required = ['surveyor_id', 'field_id', 'start_date', 'end_date']
    for field in required:
        if field not in payload:
            result.add_error(f"Missing required field: {field}")
    
    if not result.is_valid:
        return result

    try:
        start_date = datetime.fromisoformat(payload['start_date'].replace('Z', '+00:00')).date()
        end_date = datetime.fromisoformat(payload['end_date'].replace('Z', '+00:00')).date()
        if end_date < start_date:
            result.add_error("end_date must be on or after start_date")
    except (AttributeError, TypeError, ValueError):
        result.add_error("start_date and end_date must use ISO 8601 format")

    return result


def validate_trail_entry(entry: Dict[str, Any]) -> ValidationResult:
    result = ValidationResult(True, [])
    
    required = ['sequence_number', 'satellite_timestamp', 'latitude', 'longitude',
                'accuracy_meters', 'prev_hash', 'entry_hash', 'signature']
    for field in required:
        if field not in entry:
            result.add_error(f"Missing required field: {field}")
    
    if not result.is_valid:
        return result
    
    if not isinstance(entry['sequence_number'], int) or entry['sequence_number'] < 0:
        result.add_error("sequence_number must be non-negative integer")
    
    if not validate_coordinates(entry['latitude'], entry['longitude']):
        result.add_error("Invalid coordinates")
    
    if not validate_accuracy(entry['accuracy_meters']):
        result.add_error("Invalid accuracy")
    
    if not validate_sha256_hash(entry['prev_hash']):
        result.add_error("Invalid prev_hash")
    
    if not validate_sha256_hash(entry['entry_hash']):
        result.add_error("Invalid entry_hash")
    
    if not validate_base64_signature(entry['signature']):
        result.add_error("Invalid signature")
    
    try:
        ts = datetime.fromisoformat(entry['satellite_timestamp'].replace('Z', '+00:00'))
        if not validate_timestamp(ts, max_age_seconds=config['default']().TRAIL_ENTRY_MAX_AGE_SECONDS):
            result.add_error("satellite_timestamp too old")
    except Exception:
        result.add_error("Invalid satellite_timestamp format")
    
    return result