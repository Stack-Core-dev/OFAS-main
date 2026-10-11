from datetime import datetime, date
from typing import List, Dict, Any, Optional
from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from .models import (
    User, Surveyor, Field, Assignment, Visit, TrailEntry, Phone, PhoneStatus, VisitStatus
)
from .database import get_db
from .auth import require_surveyor, get_current_user_id
from .validation import validate_visit_payload
from .crypto import verify_visit_signature, verify_trail_chain, verify_trail_snapshot
from .geospatial import validate_visit_location
from .audit import create_audit_logger, AUDIT_ACTIONS

sync_bp = Blueprint('sync', __name__, url_prefix='/api/sync')

def _current_surveyor(db):
    user = getattr(g, 'current_user', None)
    if not user:
        return None
    return db.query(Surveyor).filter(
        Surveyor.is_active == True,
        (Surveyor.email == user.email) | (Surveyor.employee_id == user.username)
    ).first()


@sync_bp.route('/fields', methods=['GET'])
@require_surveyor
def get_assigned_fields():
    db = next(get_db())
    surveyor = _current_surveyor(db)
    
    if not surveyor:
        return jsonify({'error': 'Surveyor profile not found'}), 404
    
    assignments = db.query(Assignment).filter(
        Assignment.surveyor_id == surveyor.id
    ).all()
    today = date.today()
    assignments = [
        assignment for assignment in assignments
        if assignment.start_date.date() <= today <= assignment.end_date.date()
    ]
    
    field_ids = [a.field_id for a in assignments]
    fields = db.query(Field).filter(
        Field.id.in_(field_ids),
        Field.is_active == True
    ).all() if field_ids else []
    
    face_templates = db.query(Surveyor.id, Surveyor.face_template, Surveyor.face_template_version).filter(
        Surveyor.is_active == True,
        Surveyor.face_template.isnot(None)
    ).all()
    
    return jsonify({
        'surveyor_id': str(surveyor.id),
        'fields': [{
            'id': str(f.id),
            'field_code': f.field_code,
            'name': f.name,
            'crop_type': f.crop_type,
            'center_lat': f.center_lat,
            'center_lon': f.center_lon,
            'radius_meters': f.radius_meters,
            'reference_photos': f.reference_photos or [],
            'field_metadata': f.field_metadata or {}
        } for f in fields],
        'face_templates': [{
            'surveyor_id': str(s.id),
            'template': s.face_template.hex() if s.face_template else None,
            'version': s.face_template_version
        } for s in face_templates]
    })


@sync_bp.route('/submit', methods=['POST'])
@require_surveyor
def submit_visit():
    user_id = get_current_user_id()
    db = next(get_db())
    audit = create_audit_logger(db)
    
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    validation = validate_visit_payload(payload, sync_bp.app.config if hasattr(sync_bp, 'app') else None)
    if not validation.is_valid:
        return jsonify({'error': 'Validation failed', 'details': validation.errors}), 400
    
    surveyor = _current_surveyor(db)
    if not surveyor or str(surveyor.id) != str(payload['surveyor_id']):
        return jsonify({'error': 'Surveyor does not match authenticated account'}), 403

    visit_date = datetime.fromisoformat(
        payload['satellite_timestamp'].replace('Z', '+00:00')
    ).date()
    assignment = db.query(Assignment).filter(
        Assignment.surveyor_id == surveyor.id,
        Assignment.field_id == payload['field_id'],
        func.date(Assignment.start_date) <= visit_date,
        func.date(Assignment.end_date) >= visit_date
    ).first()
    if not assignment:
        return jsonify({'error': 'Field is not assigned to this surveyor for the visit date'}), 403

    phone = db.query(Phone).filter(
        Phone.id == payload['phone_id'],
        Phone.status == PhoneStatus.ACTIVE
    ).first()
    if not phone:
        return jsonify({'error': 'Phone not found or blocked'}), 403
    
    visit_id_exists = db.query(Visit).filter(Visit.visit_id == payload['visit_id']).first()
    if visit_id_exists:
        return jsonify({'error': 'Visit ID already exists'}), 409
    
    sig_result = verify_visit_signature(
        type('obj', (object,), payload)(),
        phone
    )
    if not sig_result.is_valid:
        return jsonify({'error': 'Signature verification failed', 'details': sig_result.errors}), 400
    
    location_valid, distance, loc_msg = validate_visit_location(
        db, payload['latitude'], payload['longitude'],
        payload['accuracy_meters'], payload['field_id']
    )
    if not location_valid:
        return jsonify({'error': 'Location validation failed', 'details': loc_msg}), 400
    
    trail_entries = db.query(TrailEntry).filter(
        TrailEntry.phone_id == payload['phone_id']
    ).order_by(TrailEntry.sequence_number).all()

    if not trail_entries:
        for entry_data in payload['trail_snapshot'].get('entries_around', []):
            db.add(TrailEntry(
                phone_id=payload['phone_id'],
                sequence_number=entry_data['sequence_number'],
                satellite_timestamp=datetime.fromisoformat(
                    entry_data['timestamp'].replace('Z', '+00:00')
                ),
                latitude=entry_data['latitude'],
                longitude=entry_data['longitude'],
                accuracy_meters=entry_data['accuracy_meters'],
                altitude=entry_data.get('altitude'),
                speed=entry_data.get('speed'),
                bearing=entry_data.get('bearing'),
                prev_hash=entry_data['prev_hash'],
                entry_hash=entry_data['entry_hash'],
                signature=entry_data.get('signature', '')
            ))
        db.flush()
        trail_entries = db.query(TrailEntry).filter(
            TrailEntry.phone_id == payload['phone_id']
        ).order_by(TrailEntry.sequence_number).all()
    
    trail_result = verify_trail_chain(trail_entries)
    if not trail_result.is_valid:
        return jsonify({'error': 'Trail chain verification failed', 'details': trail_result.errors}), 400
    
    snapshot_result = verify_trail_snapshot(
        type('obj', (object,), payload)(),
        trail_entries
    )
    if not snapshot_result.is_valid:
        return jsonify({'error': 'Trail snapshot verification failed', 'details': snapshot_result.errors}), 400
    
    visit = Visit(
        visit_id=payload['visit_id'],
        surveyor_id=payload['surveyor_id'],
        field_id=payload['field_id'],
        phone_id=payload['phone_id'],
        satellite_timestamp=datetime.fromisoformat(payload['satellite_timestamp'].replace('Z', '+00:00')),
        latitude=payload['latitude'],
        longitude=payload['longitude'],
        accuracy_meters=payload['accuracy_meters'],
        altitude=payload.get('altitude'),
        speed=payload.get('speed'),
        bearing=payload.get('bearing'),
        selfie_photo_hash=payload['selfie_photo_hash'],
        selfie_photo_s3_key=payload.get('selfie_photo_s3_key'),
        field_photos=payload['field_photos'],
        face_match_score=payload['face_match_score'],
        liveness_verified=payload['liveness_verified'],
        trail_snapshot=payload['trail_snapshot'],
        signature=payload['signature'],
        signed_by_key_id=payload['signed_by_key_id'],
        status=VisitStatus.SYNCED,
        synced_at=datetime.utcnow()
    )
    
    db.add(visit)
    db.flush()
    
    audit.log(
        action='VISIT_SUBMITTED',
        entity_type='visit',
        entity_id=str(visit.id),
        user_id=get_current_user_id(),
        visit_id=str(visit.id),
        phone_id=payload['phone_id'],
        new_values={'visit_id': payload['visit_id'], 'status': 'synced'},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    db.commit()
    
    return jsonify({
        'success': True,
        'visit_id': payload['visit_id'],
        'server_visit_id': str(visit.id),
        'synced_at': visit.synced_at.isoformat() + 'Z'
    }), 201


@sync_bp.route('/status', methods=['GET'])
@require_surveyor
def get_sync_status():
    db = next(get_db())
    surveyor = _current_surveyor(db)
    
    if not surveyor:
        return jsonify({'error': 'Surveyor profile not found'}), 404
    
    pending = db.query(Visit).filter(
        Visit.surveyor_id == surveyor.id,
        Visit.status.in_([VisitStatus.QUEUED, VisitStatus.SYNCING, VisitStatus.FAILED])
    ).count()
    
    synced_today = db.query(Visit).filter(
        Visit.surveyor_id == surveyor.id,
        Visit.status == VisitStatus.SYNCED,
        func.date(Visit.synced_at) == date.today()
    ).count()
    
    return jsonify({
        'pending_count': pending,
        'synced_today': synced_today,
        'server_time': datetime.utcnow().isoformat() + 'Z'
    })