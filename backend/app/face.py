from datetime import datetime
from typing import Optional
from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy.orm import Session

from .models import Surveyor
from .database import get_db
from .auth import require_admin, get_current_user_id
from .validation import validate_face_template
from .audit import create_audit_logger

face_bp = Blueprint('face', __name__, url_prefix='/api/face')


@face_bp.route('/templates', methods=['GET'])
@require_admin
def list_face_templates():
    """List all surveyors with face templates."""
    db = next(get_db())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    query = db.query(Surveyor).filter(Surveyor.face_template.isnot(None))

    total = query.count()
    surveyors = query.order_by(Surveyor.updated_at.desc()).offset((page-1)*per_page).limit(per_page).all()

    return jsonify({
        'templates': [{
            'surveyor_id': str(s.id),
            'employee_id': s.employee_id,
            'full_name': s.full_name,
            'has_template': s.face_template is not None,
            'version': s.face_template_version,
            'updated_at': s.updated_at.isoformat() + 'Z' if s.updated_at else None
        } for s in surveyors],
        'pagination': {'page': page, 'per_page': per_page, 'total': total}
    })


@face_bp.route('/templates/<uuid:surveyor_id>', methods=['GET'])
@require_admin
def get_face_template(surveyor_id):
    """Get face template for a surveyor (admin only)."""
    db = next(get_db())

    surveyor = db.query(Surveyor).filter(Surveyor.id == surveyor_id).first()
    if not surveyor:
        return jsonify({'error': 'Surveyor not found'}), 404

    if not surveyor.face_template:
        return jsonify({'error': 'No face template found'}), 404

    return jsonify({
        'surveyor_id': str(surveyor.id),
        'employee_id': surveyor.employee_id,
        'full_name': surveyor.full_name,
        'template': surveyor.face_template.hex() if surveyor.face_template else None,
        'version': surveyor.face_template_version,
        'updated_at': surveyor.updated_at.isoformat() + 'Z' if surveyor.updated_at else None
    })


@face_bp.route('/templates/<uuid:surveyor_id>', methods=['POST'])
@require_admin
def upload_face_template(surveyor_id):
    """
    Upload face template for a surveyor.
    Expected JSON:
    {
        "template": "base64 encoded face template bytes",
        "version": 1
    }
    """
    db = next(get_db())
    audit = create_audit_logger(db)

    surveyor = db.query(Surveyor).filter(Surveyor.id == surveyor_id).first()
    if not surveyor:
        return jsonify({'error': 'Surveyor not found'}), 404

    payload = request.get_json()
    if not payload or 'template' not in payload:
        return jsonify({'error': 'Missing template data'}), 400

    # Validate template
    import base64
    try:
        template_bytes = base64.b64decode(payload['template'])
    except Exception:
        return jsonify({'error': 'Invalid base64 template'}), 400

    is_valid, errors = validate_face_template(template_bytes)
    if not is_valid:
        return jsonify({'error': 'Invalid face template', 'details': errors}), 400

    # Store template
    old_version = surveyor.face_template_version
    surveyor.face_template = template_bytes
    surveyor.face_template_version = payload.get('version', surveyor.face_template_version + 1)
    surveyor.updated_at = datetime.utcnow()

    db.commit()

    audit.log(
        action='FACE_TEMPLATE_UPDATED',
        entity_type='surveyor',
        entity_id=str(surveyor.id),
        user_id=get_current_user_id(),
        old_values={'version': old_version},
        new_values={'version': surveyor.face_template_version},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )

    return jsonify({
        'message': 'Face template uploaded',
        'surveyor_id': str(surveyor.id),
        'version': surveyor.face_template_version
    })


@face_bp.route('/templates/<uuid:surveyor_id>', methods=['DELETE'])
@require_admin
def delete_face_template(surveyor_id):
    """Delete face template for a surveyor."""
    db = next(get_db())
    audit = create_audit_logger(db)

    surveyor = db.query(Surveyor).filter(Surveyor.id == surveyor_id).first()
    if not surveyor:
        return jsonify({'error': 'Surveyor not found'}), 404

    if not surveyor.face_template:
        return jsonify({'error': 'No face template to delete'}), 404

    audit.log(
        action='FACE_TEMPLATE_DELETED',
        entity_type='surveyor',
        entity_id=str(surveyor.id),
        user_id=get_current_user_id(),
        old_values={'version': surveyor.face_template_version},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )

    surveyor.face_template = None
    surveyor.face_template_version = 1
    surveyor.updated_at = datetime.utcnow()
    db.commit()

    return jsonify({'message': 'Face template deleted'})