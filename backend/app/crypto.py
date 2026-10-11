import hashlib
import hmac
import json
import base64
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature

from .models import Phone, TrailEntry, Visit
from .config import config


@dataclass
class VerificationResult:
    is_valid: bool
    errors: List[str]
    
    def add_error(self, error: str):
        self.errors.append(error)
        self.is_valid = False


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def compute_entry_hash(entry_data: Dict) -> str:
    canonical = json.dumps(entry_data, sort_keys=True, separators=(',', ':'))
    return sha256(canonical.encode())


def compute_trail_entry_hash(
    sequence_number: int,
    satellite_timestamp: datetime,
    latitude: float,
    longitude: float,
    accuracy_meters: float,
    altitude: Optional[float],
    speed: Optional[float],
    bearing: Optional[float],
    prev_hash: str
) -> str:
    data = {
        'seq': sequence_number,
        'time': satellite_timestamp.isoformat() + 'Z',
        'lat': latitude,
        'lon': longitude,
        'acc': accuracy_meters,
        'alt': altitude,
        'spd': speed,
        'brg': bearing,
        'prev': prev_hash
    }
    return compute_entry_hash(data)


def verify_trail_chain(entries: List[TrailEntry]) -> VerificationResult:
    result = VerificationResult(True, [])
    
    if not entries:
        result.add_error("No trail entries provided")
        return result
    
    sorted_entries = sorted(entries, key=lambda e: e.sequence_number)
    
    for i, entry in enumerate(sorted_entries):
        expected_hash = compute_trail_entry_hash(
            entry.sequence_number,
            entry.satellite_timestamp,
            entry.latitude,
            entry.longitude,
            entry.accuracy_meters,
            entry.altitude,
            entry.speed,
            entry.bearing,
            entry.prev_hash
        )
        
        if entry.entry_hash != expected_hash:
            result.add_error(f"Entry {entry.sequence_number}: hash mismatch")
        
        if i == 0:
            if entry.prev_hash != "0" * 64:
                result.add_error(f"First entry prev_hash must be zeros")
        else:
            prev_entry = sorted_entries[i - 1]
            if entry.prev_hash != prev_entry.entry_hash:
                result.add_error(f"Entry {entry.sequence_number}: prev_hash doesn't match previous entry_hash")
        
        if not verify_signature(entry.phone_id, entry.signature, entry.entry_hash):
            result.add_error(f"Entry {entry.sequence_number}: invalid signature")
    
    return result


def verify_signature(phone_id: str, signature_b64: str, data_hash: str) -> bool:
    from .database import get_db
    try:
        db = next(get_db())
        phone = db.query(Phone).filter(Phone.id == phone_id).first()
        if not phone:
            return False
        
        public_key_pem = phone.public_key
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        signature = base64.b64decode(signature_b64)
        
        if phone.key_algorithm == 'ES256':
            public_key.verify(
                signature,
                data_hash.encode(),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        return False
    except (InvalidSignature, Exception):
        return False


def verify_visit_signature(visit: Visit, phone: Phone) -> VerificationResult:
    result = VerificationResult(True, [])
    
    visit_data = {
        'visit_id': visit.visit_id,
        'surveyor_id': str(visit.surveyor_id),
        'field_id': str(visit.field_id),
        'phone_id': str(visit.phone_id),
        'satellite_timestamp': visit.satellite_timestamp.isoformat() + 'Z',
        'latitude': visit.latitude,
        'longitude': visit.longitude,
        'accuracy_meters': visit.accuracy_meters,
        'selfie_photo_hash': visit.selfie_photo_hash,
        'field_photos': visit.field_photos,
        'face_match_score': visit.face_match_score,
        'liveness_verified': visit.liveness_verified,
        'trail_snapshot': visit.trail_snapshot,
    }
    
    canonical = json.dumps(visit_data, sort_keys=True, separators=(',', ':'))
    data_hash = sha256(canonical.encode())
    
    try:
        public_key_pem = phone.public_key
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        signature = base64.b64decode(visit.signature)
        
        if phone.key_algorithm == 'ES256':
            public_key.verify(signature, data_hash.encode(), ec.ECDSA(hashes.SHA256()))
        else:
            result.add_error(f"Unsupported key algorithm: {phone.key_algorithm}")
    except InvalidSignature:
        result.add_error("Visit signature verification failed")
    except Exception as e:
        result.add_error(f"Signature verification error: {str(e)}")
    
    return result


def verify_photo_hash(photo_data: bytes, expected_hash: str) -> bool:
    actual_hash = sha256(photo_data)
    return hmac.compare_digest(actual_hash, expected_hash)


def verify_trail_snapshot(visit: Visit, db_entries: List[TrailEntry]) -> VerificationResult:
    result = VerificationResult(True, [])
    
    snapshot = visit.trail_snapshot
    if not isinstance(snapshot, dict):
        result.add_error("Invalid trail_snapshot format")
        return result
    
    required = ['prev_entry_hash', 'next_entry_hash', 'entries_around']
    for field in required:
        if field not in snapshot:
            result.add_error(f"trail_snapshot missing: {field}")
            return result
    
    if snapshot['prev_entry_hash'] != "0" * 64:
        prev_entry = next((e for e in db_entries if e.entry_hash == snapshot['prev_entry_hash']), None)
        if not prev_entry:
            result.add_error("Previous trail entry not found in database")
    
    if snapshot['next_entry_hash'] != "0" * 64:
        next_entry = next((e for e in db_entries if e.entry_hash == snapshot['next_entry_hash']), None)
        if not next_entry:
            result.add_error("Next trail entry not found in database")
    
    visit_time = visit.satellite_timestamp
    entries_around = snapshot.get('entries_around', [])
    if not entries_around:
        result.add_error("No trail entries around visit timestamp")
    else:
        for entry_data in entries_around:
            entry_time = datetime.fromisoformat(entry_data['timestamp'].replace('Z', '+00:00'))
            time_diff = abs((visit_time - entry_time).total_seconds())
            if time_diff > 300:
                result.add_error(f"Trail entry time gap too large: {time_diff}s")
    
    return result


def generate_key_pair() -> Tuple[str, str]:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    
    return private_pem, public_pem


def get_key_id(public_key_pem: str) -> str:
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return sha256(der)[:16]


def constant_time_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)