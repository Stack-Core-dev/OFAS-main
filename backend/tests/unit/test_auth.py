"""Unit tests for authentication module."""

import pytest
import hmac
import hashlib
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

from app.auth import (
    hash_password, verify_password, generate_totp_secret, verify_totp,
    create_tokens, generate_challenge, hash_data, verify_hmac
)
from app.models import User, UserRole


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password

    def test_verify_password_correct(self):
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert verify_password("WrongPassword123!", hashed) is False

    def test_different_hashes_for_same_password(self):
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # Argon2 uses salt


class TestTOTP:
    def test_generate_totp_secret(self):
        secret = generate_totp_secret()
        assert isinstance(secret, str)
        assert len(secret) == 32  # Base32 encoded

    def test_verify_totp_valid(self):
        secret = generate_totp_secret()
        import pyotp
        totp = pyotp.TOTP(secret)
        token = totp.now()
        assert verify_totp(secret, token) is True

    def test_verify_totp_invalid(self):
        secret = generate_totp_secret()
        assert verify_totp(secret, "000000") is False


class TestTokenCreation:
    def test_create_tokens_returns_tuple(self, app):
        """Test token creation with app context."""
        with app.app_context():
            user = Mock()
            user.id = "test-id"
            user.username = "testuser"
            user.role = Mock(value="admin")

            access, refresh = create_tokens(user)
            assert isinstance(access, str)
            assert isinstance(refresh, str)
            assert len(access) > 0
            assert len(refresh) > 0


class TestCryptoUtilities:
    def test_generate_challenge(self):
        challenge = generate_challenge()
        assert isinstance(challenge, str)
        assert len(challenge) > 0

    def test_hash_data(self):
        data = b"test data"
        hashed = hash_data(data)
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA256 hex

    def test_verify_hmac_valid(self):
        key = b"secret"
        data = b"data"
        signature = hmac.new(key, data, hashlib.sha256).hexdigest()
        assert verify_hmac(key, data, signature) is True

    def test_verify_hmac_invalid(self):
        key = b"secret"
        data = b"data"
        assert verify_hmac(key, data, "invalidsignature") is False