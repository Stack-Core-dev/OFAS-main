"""Integration tests for crypto module."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from app.crypto import (
    sha256, compute_entry_hash, compute_trail_entry_hash,
    verify_trail_chain, verify_visit_signature, verify_photo_hash,
    verify_trail_snapshot, generate_key_pair, get_key_id
)
from app.models import TrailEntry, Phone, Visit, PhoneStatus


class TestCryptoUtilities:
    def test_sha256(self):
        data = b"test data"
        hashed = sha256(data)
        assert isinstance(hashed, str)
        assert len(hashed) == 64

    def test_compute_entry_hash(self):
        entry = {'seq': 1, 'time': '2024-01-01T00:00:00Z', 'lat': 1.0, 'lon': 2.0}
        hash1 = compute_entry_hash(entry)
        hash2 = compute_entry_hash(entry)
        assert hash1 == hash2
        assert len(hash1) == 64

    def test_compute_trail_entry_hash(self):
        hash_val = compute_trail_entry_hash(
            sequence_number=1,
            satellite_timestamp=datetime.utcnow(),
            latitude=28.6139,
            longitude=77.2090,
            accuracy_meters=5.0,
            altitude=None,
            speed=None,
            bearing=None,
            prev_hash="0" * 64
        )
        assert len(hash_val) == 64


class TestKeyGeneration:
    def test_generate_key_pair(self):
        private, public = generate_key_pair()
        assert isinstance(private, str)
        assert isinstance(public, str)
        assert "PRIVATE KEY" in private
        assert "PUBLIC KEY" in public

    def test_get_key_id(self):
        private, public = generate_key_pair()
        key_id = get_key_id(public)
        assert isinstance(key_id, str)
        assert len(key_id) == 16