import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 86400 * 30))
    
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f'postgresql://ofas:ofas@localhost:5432/ofas'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'false').lower() == 'true'
    
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    S3_BUCKET = os.environ.get('S3_BUCKET', 'ofas-photos')
    S3_REGION = os.environ.get('S3_REGION', 'us-east-1')
    
    TOTP_ISSUER = 'OFAS'
    PASSKEY_RP_ID = os.environ.get('PASSKEY_RP_ID', 'localhost')
    PASSKEY_RP_NAME = 'OFAS'
    PASSKEY_ORIGIN = os.environ.get('PASSKEY_ORIGIN', 'http://localhost:5000')
    
    TRAIL_INTERVAL_SECONDS = int(os.environ.get('TRAIL_INTERVAL_SECONDS', 300))
    TRAIL_ACCURACY_THRESHOLD = float(os.environ.get('TRAIL_ACCURACY_THRESHOLD', 50.0))
    FIELD_RADIUS_TOLERANCE = float(os.environ.get('FIELD_RADIUS_TOLERANCE', 10.0))
    FACE_MATCH_THRESHOLD = float(os.environ.get('FACE_MATCH_THRESHOLD', 0.6))
    MAX_PHOTO_SIZE_MB = int(os.environ.get('MAX_PHOTO_SIZE_MB', 2))
    MAX_PHOTOS_PER_VISIT = int(os.environ.get('MAX_PHOTOS_PER_VISIT', 10))
    MIN_PHOTOS_PER_VISIT = int(os.environ.get('MIN_PHOTOS_PER_VISIT', 3))
    
    SYNC_BATCH_SIZE = int(os.environ.get('SYNC_BATCH_SIZE', 100))
    VISIT_RETENTION_DAYS = int(os.environ.get('VISIT_RETENTION_DAYS', 365))
    
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    AUDIT_LOG_PATH = BASE_DIR / 'audit.log'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    S3_ENDPOINT_URL = None

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}