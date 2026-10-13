"""Unit tests for validation module."""

import pytest
import base64
from datetime import datetime, timedelta

from app.validation import (
    validate_email, validate_username, validate_password,
    validate_coordinates, validate_accuracy, validate_timestamp,
    validate_visit_id, validate_sha256_hash, validate_base64_image,
    validate_face_template, validate_visit_payload,
    validate_field_payload, validate_surveyor_payload,
    validate_assignment_payload
)
from app.config import Config


class TestBasicValidation:
    def test_validate_email_valid(self):
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@domain.org") is True

    def test_validate_email_invalid(self):
        assert validate_email("invalid") is False
        assert validate_email("@domain.com") is False
        assert validate_email("user@") is False

    def test_validate_username_valid(self):
        assert validate_username("user123") is True
        assert validate_username("user_name") is True
        assert validate_username("user-name") is True

    def test_validate_username_invalid(self):
        assert validate_username("ab") is False  # too short
        assert validate_username("user@name") is False
        assert validate_username("user name") is False

    def test_validate_password(self):
        valid, errors = validate_password("TestPass123!")
        assert valid is True
        assert len(errors) == 0

    def test_validate_password_too_short(self):
        valid, errors = validate_password("Short1!")
        assert valid is False
        assert any("12 characters" in e for e in errors)

    def test_validate_password_missing_uppercase(self):
        valid, errors = validate_password("testpass123!")
        assert valid is False
        assert any("uppercase" in e for e in errors)

    def test_validate_password_missing_lowercase(self):
        valid, errors = validate_password("TESTPASS123!")
        assert valid is False
        assert any("lowercase" in e for e in errors)

    def test_validate_password_missing_digit(self):
        valid, errors = validate_password("TestPass!")
        assert valid is False
        assert any("digit" in e for e in errors)

    def test_validate_password_missing_special(self):
        valid, errors = validate_password("TestPass123")
        assert valid is False
        assert any("special" in e for e in errors)

    def test_validate_surveyor_requires_phone_and_password(self):
        result = validate_surveyor_payload({
            "employee_id": "SURVEYOR_01",
            "full_name": "Field Surveyor",
        })
        assert result.is_valid is False
        assert any("phone_number" in error for error in result.errors)
        assert any("password" in error for error in result.errors)

    def test_validate_surveyor_accepts_phone_and_strong_password_without_email(self):
        result = validate_surveyor_payload({
            "employee_id": "SURVEYOR_01",
            "full_name": "Field Surveyor",
            "phone_number": "+15551234567",
            "password": "StrongSurveyor123!",
        })
        assert result.is_valid is True


class TestCoordinateValidation:
    def test_validate_coordinates_valid(self):
        assert validate_coordinates(28.6139, 77.2090) is True
        assert validate_coordinates(-90, -180) is True
        assert validate_coordinates(90, 180) is True

    def test_validate_coordinates_invalid(self):
        assert validate_coordinates(91, 0) is False
        assert validate_coordinates(0, 181) is False
        assert validate_coordinates(-91, 0) is False


class TestAccuracyValidation:
    def test_validate_accuracy_valid(self):
        assert validate_accuracy(5.0) is True
        assert validate_accuracy(0.0) is True
        assert validate_accuracy(100.0) is True

    def test_validate_accuracy_invalid(self):
        assert validate_accuracy(-1.0) is False
        assert validate_accuracy(101.0) is False


class TestTimestampValidation:
    def test_validate_timestamp_recent(self):
        now = datetime.utcnow()
        assert validate_timestamp(now) is True

    def test_validate_timestamp_too_old(self):
        old = datetime.utcnow() - timedelta(hours=2)
        assert validate_timestamp(old, max_age_seconds=3600) is False

    def test_validate_timestamp_future(self):
        future = datetime.utcnow() + timedelta(minutes=5)
        assert validate_timestamp(future, allow_future=True) is True
        assert validate_timestamp(future, allow_future=False) is False


class TestHashValidation:
    def test_validate_visit_id_valid(self):
        assert validate_visit_id("a" * 64) is True
        assert validate_visit_id("f" * 64) is True

    def test_validate_visit_id_invalid(self):
        assert validate_visit_id("short") is False
        assert validate_visit_id("g" * 64) is False
        assert validate_visit_id("") is False

    def test_validate_sha256_hash_valid(self):
        assert validate_sha256_hash("a" * 64) is True

    def test_validate_sha256_hash_invalid(self):
        assert validate_sha256_hash("short") is False
        assert validate_sha256_hash("g" * 64) is False


class TestVisitPayloadValidation:
    def test_validate_visit_payload_valid(self):
        config = Config()
        payload = {
            'visit_id': 'a' * 64,
            'surveyor_id': '00000000-0000-0000-0000-000000000001',
            'field_id': '00000000-0000-0000-0000-000000000002',
            'phone_id': '00000000-0000-0000-0000-000000000003',
            'satellite_timestamp': datetime.utcnow().isoformat() + 'Z',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'accuracy_meters': 5.0,
            'selfie_photo_hash': 'a' * 64,
            'selfie_latitude': 28.6139,
            'selfie_longitude': 77.2090,
            'selfie_accuracy_meters': 5.0,
            'field_photos': [
                {'hash': 'b' * 64, 's3_key': 'key1', 'timestamp': datetime.utcnow().isoformat() + 'Z', 'latitude': 28.6139, 'longitude': 77.2090, 'accuracy_meters': 5.0},
                {'hash': 'c' * 64, 's3_key': 'key2', 'timestamp': datetime.utcnow().isoformat() + 'Z', 'latitude': 28.6139, 'longitude': 77.2090, 'accuracy_meters': 5.0},
                {'hash': 'd' * 64, 's3_key': 'key3', 'timestamp': datetime.utcnow().isoformat() + 'Z', 'latitude': 28.6139, 'longitude': 77.2090, 'accuracy_meters': 5.0},
            ],
            'face_match_score': 0.85,
            'liveness_verified': True,
            'trail_snapshot': {'prev_entry_hash': '0' * 64, 'next_entry_hash': '0' * 64, 'entries_around': []},
            'signature': base64.b64encode(b's' * 64).decode(),
            'signed_by_key_id': 'key123'
        }
        result = validate_visit_payload(payload, config)
        assert result.is_valid is True

    def test_validate_visit_payload_missing_fields(self):
        config = Config()
        result = validate_visit_payload({}, config)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_visit_payload_low_face_score(self):
        config = Config()
        payload = {
            'visit_id': 'a' * 64,
            'surveyor_id': '00000000-0000-0000-0000-000000000001',
            'field_id': '00000000-0000-0000-0000-000000000002',
            'phone_id': '00000000-0000-0000-0000-000000000003',
            'satellite_timestamp': datetime.utcnow().isoformat() + 'Z',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'accuracy_meters': 5.0,
            'selfie_photo_hash': 'a' * 64,
            'selfie_latitude': 28.6139,
            'selfie_longitude': 77.2090,
            'selfie_accuracy_meters': 5.0,
            'field_photos': [{'hash': 'b' * 64, 's3_key': 'key1', 'timestamp': datetime.utcnow().isoformat() + 'Z', 'latitude': 28.6139, 'longitude': 77.2090, 'accuracy_meters': 5.0}],
            'face_match_score': 0.5,  # Below threshold
            'liveness_verified': True,
            'trail_snapshot': {'prev_entry_hash': '0' * 64, 'next_entry_hash': '0' * 64, 'entries_around': []},
            'signature': base64.b64encode(b'sig').decode(),
            'signed_by_key_id': 'key123'
        }
        result = validate_visit_payload(payload, config)
        assert result.is_valid is False
        assert any("threshold" in e for e in result.errors)