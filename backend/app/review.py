from datetime import datetime
from typing import Optional
from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_

from .models import Visit, Surveyor, Field, User, TrailEntry, VisitStatus
from .database import get_db
from .auth import require_admin, get_current_user_id
from .audit import create_audit_logger

review_bp = Blueprint('review', __name__, url_prefix='/api/review')


@review_bp.route('/visits', methods=['GET'])
@require_admin
def list_visits():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status')
    surveyor_id = request.args.get('surveyor_id')
    field_id = request.args.get('field_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = db.query(Visit)
    
    if status:
        if status == 'unreviewed':
            query = query.filter(Visit.review_status.is_(None))
        else:
            try:
                query = query.filter(Visit.review_status == VisitStatus(status))
            except ValueError:
                return jsonify({'error': 'Invalid status'}), 400
    
    if surveyor_id:
        query = query.filter(Visit.surveyor_id == surveyor_id)
    
    if field_id:
        query = query.filter(Visit.field_id == field_id)
    
    if date_from:
        query = query.filter(Visit.satellite_timestamp >= datetime.fromisoformat(date_from))
    if date_to:
        query = query.filter(Visit.satellite_timestamp <= datetime.fromisoformat(date_to))
    
    total = query.count()
    visits = query.order_by(desc(Visit.satellite_timestamp)).offset((page-1)*per_page).limit(per_page).all()
    
    return jsonify({
        'visits': [{
            'id': str(v.id),
            'visit_id': v.visit_id,
            'surveyor_id': str(v.surveyor_id),
            'surveyor_name': v.surveyor.full_name if v.surveyor else None,
            'field_id': str(v.field_id),
            'field_code': v.field.field_code if v.field else None,
            'satellite_timestamp': v.satellite_timestamp.isoformat() + 'Z',
            'latitude': v.latitude,
            'longitude': v.longitude,
            'accuracy_meters': v.accuracy_meters,
            'selfie_photo_s3_key': v.selfie_photo_s3_key,
            'field_photos': v.field_photos,
            'face_match_score': v.face_match_score,
            'liveness_verified': v.liveness_verified,
            'status': v.status.value,
            'review_status': v.review_status.value if v.review_status else None,
            'reviewed_by': str(v.reviewed_by) if v.reviewed_by else None,
            'reviewed_at': v.reviewed_at.isoformat() + 'Z' if v.reviewed_at else None,
            'review_notes': v.review_notes,
            'synced_at': v.synced_at.isoformat() + 'Z' if v.synced_at else None
        } for v in visits],
        'pagination': {'page': page, 'per_page': per_page, 'total': total}
    })


@review_bp.route('/visits/<uuid:visit_id>', methods=['GET'])
@require_admin
def get_visit_detail(visit_id):
    db = get_db()
    
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        return jsonify({'error': 'Visit not found'}), 404
    
    trail_entries = db.query(TrailEntry).filter(
        TrailEntry.phone_id == visit.phone_id
    ).order_by(TrailEntry.sequence_number).all()
    
    return jsonify({
        'visit': {
            'id': str(visit.id),
            'visit_id': visit.visit_id,
            'surveyor': {
                'id': str(visit.surveyor_id),
                'employee_id': visit.surveyor.employee_id,
                'full_name': visit.surveyor.full_name
            } if visit.surveyor else None,
            'field': {
                'id': str(visit.field_id),
                'field_code': visit.field.field_code,
                'name': visit.field.name,
                'center_lat': visit.field.center_lat,
                'center_lon': visit.field.center_lon,
                'radius_meters': visit.field.radius_meters
            } if visit.field else None,
            'phone_id': str(visit.phone_id),
            'satellite_timestamp': visit.satellite_timestamp.isoformat() + 'Z',
            'latitude': visit.latitude,
            'longitude': visit.longitude,
            'accuracy_meters': visit.accuracy_meters,
            'altitude': visit.altitude,
            'speed': visit.speed,
            'bearing': visit.bearing,
            'selfie_photo_hash': visit.selfie_photo_hash,
            'selfie_photo_s3_key': visit.selfie_photo_s3_key,
            'selfie_latitude': visit.selfie_latitude,
            'selfie_longitude': visit.selfie_longitude,
            'selfie_accuracy_meters': visit.selfie_accuracy_meters,
            'field_photos': visit.field_photos,
            'face_match_score': visit.face_match_score,
            'liveness_verified': visit.liveness_verified,
            'trail_snapshot': visit.trail_snapshot,
            'signature': visit.signature,
            'signed_by_key_id': visit.signed_by_key_id,
            'status': visit.status.value,
            'review_status': visit.review_status.value if visit.review_status else None,
            'reviewed_by': str(visit.reviewed_by) if visit.reviewed_by else None,
            'reviewed_at': visit.reviewed_at.isoformat() + 'Z' if visit.reviewed_at else None,
            'review_notes': visit.review_notes,
            'synced_at': visit.synced_at.isoformat() + 'Z' if visit.synced_at else None
        },
        'trail_entries': [{
            'sequence_number': t.sequence_number,
            'satellite_timestamp': t.satellite_timestamp.isoformat() + 'Z',
            'latitude': t.latitude,
            'longitude': t.longitude,
            'accuracy_meters': t.accuracy_meters,
            'entry_hash': t.entry_hash,
            'prev_hash': t.prev_hash
        } for t in trail_entries]
    })


@review_bp.route('/visits/<uuid:visit_id>/review', methods=['POST'])
@require_admin
def review_visit(visit_id):
    db = get_db()
    audit = create_audit_logger(db)
    data = request.get_json()
    
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        return jsonify({'error': 'Visit not found'}), 404
    
    decision = data.get('decision')
    if decision not in ('VALID', 'INVALID', 'FLAGGED'):
        return jsonify({'error': 'Invalid decision. Must be VALID, INVALID, or FLAGGED'}), 400
    
    notes = data.get('notes', '')
    
    old_status = visit.review_status
    old_visit_status = visit.status
    visit.review_status = VisitStatus(decision.lower())
    visit.reviewed_by = g.current_user.id
    visit.reviewed_at = datetime.utcnow()
    visit.review_notes = notes
    
    if decision == 'VALID':
        visit.status = VisitStatus.VALID
    elif decision == 'INVALID':
        visit.status = VisitStatus.INVALID
    elif decision == 'FLAGGED':
        visit.status = VisitStatus.FLAGGED
    
    db.commit()
    
    audit.log(
        action='VISIT_REVIEWED',
        entity_type='visit',
        entity_id=str(visit.id),
        user_id=get_current_user_id(),
        visit_id=str(visit.id),
        old_values={'review_status': old_status.value if old_status else None, 'status': old_visit_status.value},
        new_values={'review_status': visit.review_status.value, 'status': visit.status.value, 'notes': notes},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.commit()
    
    return jsonify({
        'message': 'Visit reviewed',
        'review_status': visit.review_status.value,
        'reviewed_at': visit.reviewed_at.isoformat() + 'Z'
    })


@review_bp.route('/visits/<uuid:visit_id>/compare', methods=['POST'])
@require_admin
def compare_faces(visit_id):
    db = get_db()
    data = request.get_json()
    
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        return jsonify({'error': 'Visit not found'}), 404
    
    is_same = data.get('is_same')
    if not isinstance(is_same, bool):
        return jsonify({'error': 'is_same must be boolean'}), 400
    
    reason = data.get('reason', '')
    
    audit = create_audit_logger(db)
    audit.log(
        action='VISIT_STATUS_CHANGED',
        entity_type='visit',
        entity_id=str(visit.id),
        user_id=get_current_user_id(),
        visit_id=str(visit.id),
        new_values={'face_comparison': 'same' if is_same else 'different', 'reason': reason},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.commit()
    
    return jsonify({'message': 'Comparison recorded'})


@review_bp.route('/stats', methods=['GET'])
@require_admin
def get_review_stats():
    db = get_db()
    
    total = db.query(func.count(Visit.id)).scalar()
    by_status = dict(db.query(Visit.review_status, func.count(Visit.id))
                     .group_by(Visit.review_status).all())
    by_field = db.query(Field.field_code, func.count(Visit.id)).join(Visit).group_by(Field.field_code).all()
    by_surveyor = db.query(Surveyor.employee_id, func.count(Visit.id)).join(Visit).group_by(Surveyor.employee_id).all()
    
    pending = db.query(func.count(Visit.id)).filter(Visit.review_status.is_(None)).scalar()
    
    return jsonify({
        'total_visits': total,
        'pending_review': pending,
        'by_review_status': {k.value if k else 'unreviewed': v for k, v in by_status.items()},
        'by_field': {k: v for k, v in by_field},
        'by_surveyor': {k: v for k, v in by_surveyor}
    })


@review_bp.route('/photos/<s3_key>', methods=['GET'])
@require_admin
def get_photo_url(s3_key):
    from .config import config
    app_config = config['default']()
    
    if not app_config.S3_ENDPOINT_URL:
        return jsonify({'error': 'S3 not configured'}), 500
    
    presigned_url = f"{app_config.S3_ENDPOINT_URL}/{app_config.S3_BUCKET}/{s3_key}"
    return jsonify({'url': presigned_url})


@review_bp.route('/photos/<path:s3_key>/raw', methods=['GET'])
@require_admin
def stream_photo(s3_key):
    """Stream the stored photo bytes through the API so the admin SPA can
    render evidence without direct access to the internal S3/MinIO host."""
    from flask import Response
    from .config import config
    from .upload import get_s3_client

    app_config = config['default']()
    s3 = get_s3_client()
    if not s3:
        return jsonify({'error': 'S3 not configured'}), 503

    try:
        obj = s3.get_object(Bucket=app_config.S3_BUCKET, Key=s3_key)
    except Exception:
        return jsonify({'error': 'Photo not found'}), 404

    data = obj['Body'].read()
    return Response(data, mimetype=obj.get('ContentType', 'image/jpeg'))