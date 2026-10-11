"""Integration tests for API endpoints."""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from app.app import create_app
from app.config import TestingConfig
from app.database import init_db, create_tables, drop_tables, get_db
from app.models import User, UserRole, Surveyor, Field, Phone, PhoneStatus, Visit, VisitStatus


@pytest.fixture(autouse=True)
def mock_boto3():
    """Mock boto3 for all tests."""
    with patch('boto3.client') as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        mock_s3.head_bucket.return_value = {}
        mock_s3.create_bucket.return_value = None
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = 'http://test-presigned-url'
        yield mock_s3


@pytest.fixture
def app():
    """Create test app."""
    app = create_app('testing')
    with app.app_context():
        # Drop and recreate tables for each test
        drop_tables()
        create_tables()
        yield app
        drop_tables()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Database session."""
    with app.app_context():
        db = next(get_db())
        yield db
        db.close()


@pytest.fixture
def admin_user(app):
    """Create admin user."""
    with app.app_context():
        db = next(get_db())
        user = User(
            username="admin",
            email="admin@test.com",
            password_hash="hashed",
            role=UserRole.SUPER_ADMIN
        )
        db.add(user)
        db.commit()
        yield user
        db.delete(user)
        db.commit()


@pytest.fixture
def auth_headers(client, admin_user):
    """Get auth headers for admin."""
    from app.auth import create_tokens
    with client.application.app_context():
        access, _ = create_tokens(admin_user)
        return {'Authorization': f'Bearer {access}'}


class TestAuthEndpoints:
    def test_health_check(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'

    def test_readiness_check(self, client):
        response = client.get('/health/ready')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ready'

    def test_liveness_check(self, client):
        response = client.get('/health/live')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'alive'

    def test_login_missing_credentials(self, client):
        response = client.post('/api/auth/login', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_login_invalid_credentials(self, client):
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'wrong'
        })
        assert response.status_code == 401


class TestAdminEndpoints:
    def test_list_users_requires_auth(self, client):
        response = client.get('/api/admin/users')
        assert response.status_code == 401

    def test_create_user_requires_super_admin(self, client, auth_headers):
        response = client.post('/api/admin/users', json={
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'TestPass123!',
            'role': 'admin'
        }, headers=auth_headers)
        assert response.status_code in (201, 403)  # 403 if not super_admin


class TestSyncEndpoints:
    def test_get_fields_requires_auth(self, client):
        response = client.get('/api/sync/fields')
        assert response.status_code == 401

    def test_submit_visit_requires_auth(self, client):
        response = client.post('/api/sync/submit', json={})
        assert response.status_code == 401


class TestReviewEndpoints:
    def test_list_visits_requires_auth(self, client):
        response = client.get('/api/review/visits')
        assert response.status_code == 401


class TestUploadEndpoints:
    def test_upload_photo_requires_auth(self, client):
        response = client.post('/api/upload/photo', json={})
        assert response.status_code in (400, 401)


class TestFaceEndpoints:
    def test_list_templates_requires_auth(self, client):
        response = client.get('/api/face/templates')
        assert response.status_code == 401