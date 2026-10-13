import os
import secrets
import hashlib
import hmac
import base64
import json
from datetime import datetime, timedelta
from typing import Optional, Tuple
from functools import wraps

import pyotp
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import request, jsonify, g, current_app
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    get_jwt_identity, get_jwt, verify_jwt_in_request
)
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from sqlalchemy.orm import Session

from .models import User, UserRole, Phone, PhoneStatus
from .database import get_db

ph = PasswordHasher()
jwt = JWTManager()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False

def generate_totp_secret() -> str:
    return pyotp.random_base32()

def get_totp_uri(secret: str, username: str, issuer: str = "OFAS") -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(username, issuer_name=issuer)

def verify_totp(secret: str, token: str, valid_window: int = 1) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=valid_window)

def verify_passkey_challenge(credential_id: str, client_data_json: str, 
                              authenticator_data: bytes, signature: bytes,
                              public_key_pem: str, challenge: str) -> bool:
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        client_data = json.loads(base64.urlsafe_b64decode(client_data_json + '=='))
        if client_data.get('challenge') != challenge:
            return False
        if client_data.get('type') != 'webauthn.get':
            return False
        
        auth_data = authenticator_data
        rp_id_hash = auth_data[:32]
        flags = auth_data[32]
        sign_count = int.from_bytes(auth_data[33:37], 'big')
        rp_id_hash_expected = hashlib.sha256(current_app.config['PASSKEY_RP_ID'].encode()).digest()
        
        if rp_id_hash != rp_id_hash_expected:
            return False
        
        if not (flags & 0x01):
            return False
        
        client_data_hash = hashlib.sha256(client_data_json.encode()).digest()
        signed_data = auth_data + client_data_hash
        
        public_key.verify(
            signature,
            signed_data,
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except Exception:
        return False

def create_tokens(user: User) -> Tuple[str, str]:
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role.value, 'username': user.username}
    )
    refresh_token = create_refresh_token(
        identity=str(user.id),
        additional_claims={'role': user.role.value}
    )
    return access_token, refresh_token

def get_current_user() -> Optional[User]:
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        db = get_db()
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    except Exception:
        return None

def get_current_user_id() -> Optional[str]:
    try:
        verify_jwt_in_request()
        return get_jwt_identity()
    except Exception:
        return None

def require_role(*allowed_roles: UserRole):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            if user.role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            g.current_user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_super_admin(f):
    return require_role(UserRole.SUPER_ADMIN)(f)

def require_admin(f):
    return require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN)(f)

def require_surveyor(f):
    return require_role(UserRole.SURVEYOR)(f)

def verify_phone_signature(phone: Phone, data: bytes, signature_b64: str) -> bool:
    try:
        public_key_pem = phone.public_key
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        signature = base64.b64decode(signature_b64)
        
        if phone.key_algorithm == 'ES256':
            public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        else:
            return False
        return True
    except Exception:
        return False

def generate_challenge() -> str:
    return secrets.token_urlsafe(32)

def hash_data(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def verify_hmac(key: bytes, data: bytes, signature: str) -> bool:
    expected = hmac.new(key, data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)