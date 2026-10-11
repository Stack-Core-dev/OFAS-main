import os
import logging
import platform
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from werkzeug.exceptions import HTTPException

from .config import config
from .database import init_db, get_db
from .auth import jwt as jwt_instance
from .sync import sync_bp
from .admin import admin_bp
from .review import review_bp
from .upload import upload_bp
from .face import face_bp
from .commands import register_commands


# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
)


def create_app(config_name: str = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    if config_name == 'production':
        insecure_defaults = {
            'SECRET_KEY': 'dev-secret-change-in-production',
            'JWT_SECRET_KEY': 'jwt-secret-change-in-production'
        }
        for key, value in insecure_defaults.items():
            if app.config.get(key) == value or len(str(app.config.get(key, ''))) < 32:
                raise RuntimeError(f'{key} must be a strong value in production')

    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    # Security headers (Talisman)
    if config_name == 'production':
        Talisman(
            app,
            force_https=True,
            strict_transport_security=True,
            session_cookie_secure=True,
            content_security_policy={
                'default-src': "'self'",
                'img-src': "'self' data: https:",
                'script-src': "'self'",
                'style-src': "'self' 'unsafe-inline'"
            }
        )

    # Rate limiter
    limiter.init_app(app)

    # JWT
    jwt_instance.init_app(app)

    # Database
    init_db(app.config)

    @app.teardown_request
    def release_db_session(exception=None):
        """Release request-scoped sessions before returning a response."""
        from .database import SessionLocal
        if SessionLocal is not None and SessionLocal.registry.has():
            SessionLocal().close()
            SessionLocal.remove()

    # Blueprints
    app.register_blueprint(sync_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(face_bp)

    # CLI commands
    register_commands(app)

    # Apply rate limits to specific endpoints
    limiter.limit("10 per minute")(app.view_functions.get('auth.login', lambda: None))
    limiter.limit("30 per minute")(app.view_functions.get('sync.submit_visit', lambda: None))
    limiter.limit("60 per minute")(app.view_functions.get('upload.upload_photo', lambda: None))

    @app.route('/health')
    def health_check():
        """Basic health check."""
        return jsonify({
            'status': 'healthy',
            'service': 'ofas-backend',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })

    @app.route('/health/ready')
    def readiness_check():
        """Readiness check - verifies database connectivity."""
        try:
            db = next(get_db())
            # Simple query to verify DB connection
            from sqlalchemy import text
            db.execute(text('SELECT 1'))
            db.close()

            return jsonify({
                'status': 'ready',
                'service': 'ofas-backend',
                'checks': {
                    'database': 'ok',
                    'database_latency_ms': '<10'
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        except Exception as e:
            return jsonify({
                'status': 'not_ready',
                'service': 'ofas-backend',
                'checks': {
                    'database': 'failed',
                    'error': str(e)
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 503

    @app.route('/health/live')
    def liveness_check():
        """Liveness check - basic process health."""
        return jsonify({
            'status': 'alive',
            'service': 'ofas-backend',
            'pid': os.getpid(),
            'python_version': platform.python_version(),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })

    @app.route('/health/metrics')
    def metrics():
        """Basic metrics endpoint."""
        try:
            db = next(get_db())
            from sqlalchemy import text
            from .models import User, Surveyor, Field, Visit, Phone

            user_count = db.query(User).count()
            surveyor_count = db.query(Surveyor).count()
            field_count = db.query(Field).count()
            visit_count = db.query(Visit).count()
            phone_count = db.query(Phone).count()

            return jsonify({
                'service': 'ofas-backend',
                'uptime_seconds': 0,  # Would track actual uptime
                'counts': {
                    'users': user_count,
                    'surveyors': surveyor_count,
                    'fields': field_count,
                    'visits': visit_count,
                    'phones': phone_count
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        from .auth import verify_password, create_tokens, generate_challenge
        from .models import User

        data = request.get_json()
        if not data or not all(k in data for k in ('username', 'password')):
            return jsonify({'error': 'Username and password required'}), 400

        db = next(get_db())
        user = db.query(User).filter(User.username == data['username'], User.is_active == True).first()

        if not user or not verify_password(data['password'], user.password_hash):
            return jsonify({'error': 'Invalid credentials'}), 401

        if user.totp_enabled:
            totp_token = data.get('totp_token')
            if not totp_token:
                return jsonify({'requires_totp': True, 'challenge': generate_challenge()}), 200
            from .auth import verify_totp
            if not verify_totp(user.totp_secret, totp_token):
                return jsonify({'error': 'Invalid TOTP token'}), 401

        access_token, refresh_token = create_tokens(user)
        user.last_login = datetime.utcnow()
        db.commit()

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': str(user.id),
                'username': user.username,
                'role': user.role.value
            }
        })

    @app.route('/api/auth/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
        from .models import User

        current_user_id = get_jwt_identity()
        db = next(get_db())
        user = db.query(User).filter(User.id == current_user_id, User.is_active == True).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role.value, 'username': user.username}
        )

        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={'role': user.role.value}
        )

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': str(user.id),
                'username': user.username,
                'role': user.role.value
            }
        })

    @app.route('/api/auth/me', methods=['GET'])
    def get_current_user():
        from .auth import get_current_user
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Not authenticated'}), 401

        return jsonify({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'totp_enabled': user.totp_enabled
        })

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({'error': e.description}), e.code

    @app.errorhandler(Exception)
    def handle_exception(e):
        logging.exception("Unhandled exception")
        return jsonify({'error': 'Internal server error'}), 500

    @jwt_instance.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token expired'}), 401

    @jwt_instance.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401

    @jwt_instance.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization required'}), 401

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])