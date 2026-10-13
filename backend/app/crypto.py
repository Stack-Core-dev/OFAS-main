import hashlib
import hmac
import json
import math
import base64
from datetime import datetime, timezone
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


def _scaled_int(value, scale: int) -> Optional[int]:
    """Round a float to an integer at a fixed scale using round-half-up.

    Producing integers (instead of floats) makes the canonical serialization
    byte-identical across Python and Kotlin, which is required because client
    and server independently compute the same hash.
    """
    if value is None:
        return None
    return int(math.floor(float(value) * scale + 0.5))


def _to_millis(value: datetime) -> int:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return int(round(value.timestamp() * 1000))


def canonical_json(value) -> str:
    """Deterministic JSON used for hashing/signing on both client and server."""
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


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
        'seq': int(sequence_number),
        'time': _to_millis(satellite_timestamp),
        'lat': _scaled_int(latitude, 1_000_000),
        'lon': _scaled_int(longitude, 1_000_000),
        'acc': _scaled_int(accuracy_meters, 100),
        'alt': _scaled_int(altitude, 100),
        'spd': _scaled_int(speed, 1000),
        'brg': _scaled_int(bearing, 1000),
        'prev': prev_hash
    }
    return sha256(canonical_json(data).encode())


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
        db = get_db()
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


def build_visit_signing_payload(visit) -> Dict:
    """Canonical, integer-scaled representation of a visit payload.

    The field device builds this exact structure to compute the signature, so
    every float is converted to an integer at a fixed scale to keep the JSON
    byte-identical between Python and Kotlin.
    """
    def photo_entry(photo: Dict) -> Dict:
        return {
            'hash': photo.get('hash'),
            's3_key': photo.get('s3_key'),
            'timestamp': photo.get('timestamp'),
            'latitude': _scaled_int(photo.get('latitude'), 1_000_000),
            'longitude': _scaled_int(photo.get('longitude'), 1_000_000),
            'accuracy_meters': _scaled_int(photo.get('accuracy_meters'), 100)
        }

    snapshot = visit.trail_snapshot if isinstance(visit.trail_snapshot, dict) else {}
    entries = []
    for entry in snapshot.get('entries_around', []) or []:
        entries.append({
            'sequence_number': int(entry.get('sequence_number', 0)),
            'timestamp': entry.get('timestamp'),
            'latitude': _scaled_int(entry.get('latitude'), 1_000_000),
            'longitude': _scaled_int(entry.get('longitude'), 1_000_000),
            'accuracy_meters': _scaled_int(entry.get('accuracy_meters'), 100),
            'entry_hash': entry.get('entry_hash'),
            'prev_hash': entry.get('prev_hash')
        })

    return {
        'visit_id': str(visit.visit_id),
        'surveyor_id': str(visit.surveyor_id),
        'field_id': str(visit.field_id),
        'phone_id': str(visit.phone_id),
        'satellite_timestamp': visit.satellite_timestamp,
        'latitude': _scaled_int(visit.latitude, 1_000_000),
        'longitude': _scaled_int(visit.longitude, 1_000_000),
        'accuracy_meters': _scaled_int(visit.accuracy_meters, 100),
        'selfie_photo_hash': visit.selfie_photo_hash,
        'selfie_latitude': _scaled_int(getattr(visit, 'selfie_latitude', None), 1_000_000),
        'selfie_longitude': _scaled_int(getattr(visit, 'selfie_longitude', None), 1_000_000),
        'selfie_accuracy_meters': _scaled_int(getattr(visit, 'selfie_accuracy_meters', None), 100),
        'field_photos': [photo_entry(p) for p in (visit.field_photos or [])],
        'face_match_score': _scaled_int(visit.face_match_score, 1_000_000),
        'liveness_verified': bool(visit.liveness_verified),
        'trail_snapshot': {
            'prev_entry_hash': snapshot.get('prev_entry_hash'),
            'next_entry_hash': snapshot.get('next_entry_hash'),
            'entries_around': entries
        }
    }


def verify_visit_signature(visit: Visit, phone: Phone) -> VerificationResult:
    result = VerificationResult(True, [])

    visit_data = build_visit_signing_payload(visit)
    canonical = canonical_json(visit_data)
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
    if isinstance(visit_time, str):
        visit_time = datetime.fromisoformat(visit_time.replace('Z', '+00:00'))
    if visit_time.tzinfo is not None:
        visit_time = visit_time.astimezone(timezone.utc).replace(tzinfo=None)
    entries_around = snapshot.get('entries_around', [])
    if not entries_around:
        result.add_error("No trail entries around visit timestamp")
    else:
        for entry_data in entries_around:
            entry_time = datetime.fromisoformat(entry_data['timestamp'].replace('Z', '+00:00'))
            if entry_time.tzinfo is not None:
                entry_time = entry_time.astimezone(timezone.utc).replace(tzinfo=None)
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