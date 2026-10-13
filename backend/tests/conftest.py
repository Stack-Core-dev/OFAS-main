import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure testing before any app imports
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Delay all app imports until pytest_sessionstart
# This prevents circular import issues during test collection

def pytest_sessionstart(session):
    """Initialize database before test collection."""
    # Configure testing before any app imports
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

    # Import and initialize database BEFORE any app imports
    from app.config import TestingConfig
    # Ensure SQLALCHEMY_DATABASE_URI is set
    TestingConfig.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    from app.database import init_db, create_tables
    init_db(TestingConfig())
    create_tables()

    # Now it's safe to import the app
    from app.app import create_app
    from app.database import get_db
    from app.models import User, UserRole

    print("Database initialized for testing")


# Fixtures
import pytest

@pytest.fixture
def app():
    from app.app import create_app
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    from app.database import get_db
    with app.app_context():
        db = get_db()
        yield db
        db.close()