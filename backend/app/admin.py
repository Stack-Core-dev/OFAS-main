from datetime import datetime, date
import re
from typing import List, Optional
from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc
from sqlalchemy.exc import IntegrityError

from .models import (
    User, Surveyor, Field, Phone, Assignment, Visit,
    UserRole, PhoneStatus, VisitStatus
)
from .database import get_db
from .auth import require_admin, require_super_admin, get_current_user_id, hash_password, verify_password
from .validation import (
    validate_field_payload, validate_surveyor_payload,
    validate_assignment_payload, validate_password, validate_email,
    validate_username
)
from .audit import create_audit_logger, AUDIT_ACTIONS

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/users', methods=['GET'])
@require_admin
def list_users():
    db = next(get_db())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    role = request.args.get('role')
    
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
    
    return jsonify({
        'users': [{
            'id': str(u.id),
            'username': u.username,
            'email': u.email,
            'role': u.role.value,
            'totp_enabled': u.totp_enabled,
            'is_active': u.is_active,
            'created_at': u.created_at.isoformat() + 'Z',
            'last_login': u.last_login.isoformat() + 'Z' if u.last_login else None
        } for u in users],
        'pagination': {'page': page, 'per_page': per_page, 'total': total}
    })


@admin_bp.route('/users', methods=['POST'])
@require_super_admin
def create_user():
    db = next(get_db())
    audit = create_audit_logger(db)
    data = request.get_json(silent=True) or {}
    
    if not data or not all(k in data for k in ('username', 'email', 'password', 'role')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not isinstance(data['username'], str) or not validate_username(data['username']):
        return jsonify({'error': 'Invalid username'}), 400
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email'}), 400
    
    valid, errors = validate_password(data['password'])
    if not valid:
        return jsonify({'error': 'Weak password', 'details': errors}), 400
    
    try:
        role = UserRole(data['role'])
    except ValueError:
        return jsonify({'error': 'Invalid role'}), 400
    
    if role == UserRole.SUPER_ADMIN and g.current_user.role != UserRole.SUPER_ADMIN:
        return jsonify({'error': 'Only super admin can create super admin'}), 403
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hash_password(data['password']),
        role=role
    )
    
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Username or email already exists'}), 409
    
    audit.log(
        action='USER_CREATED',
        entity_type='user',
        entity_id=str(user.id),
        user_id=get_current_user_id(),
        new_values={'username': user.username, 'role': user.role.value},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    return jsonify({'id': str(user.id), 'message': 'User created'}), 201


@admin_bp.route('/users/<uuid:user_id>', methods=['PUT'])
@require_super_admin
def update_user(user_id):
    db = next(get_db())
    audit = create_audit_logger(db)
    data = request.get_json(silent=True) or {}
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not isinstance(data, dict) or not data:
        return jsonify({'error': 'At least one user property is required'}), 400
    
    old_values = {'username': user.username, 'email': user.email, 'role': user.role.value, 'is_active': user.is_active}
    
    if 'email' in data:
        if not isinstance(data['email'], str) or not validate_email(data['email']):
            return jsonify({'error': 'Invalid email'}), 400
        user.email = data['email']
    if 'role' in data:
        try:
            next_role = UserRole(data['role'])
        except ValueError:
            return jsonify({'error': 'Invalid role'}), 400
        if str(user.id) == str(get_current_user_id()) and next_role != user.role:
            return jsonify({'error': 'You cannot change your own role'}), 400
        user.role = next_role
    if 'is_active' in data:
        if not isinstance(data['is_active'], bool):
            return jsonify({'error': 'is_active must be a boolean'}), 400
        if str(user.id) == str(get_current_user_id()) and data['is_active'] is False:
            return jsonify({'error': 'You cannot deactivate your own account'}), 400
        user.is_active = data['is_active']
    if 'password' in data:
        if not isinstance(data['password'], str):
            return jsonify({'error': 'Password must be text'}), 400
        valid, errors = validate_password(data['password'])
        if not valid:
            return jsonify({'error': 'Weak password', 'details': errors}), 400
        user.password_hash = hash_password(data['password'])
    
    user.updated_at = datetime.utcnow()
    db.commit()
    
    audit.log(
        action='USER_UPDATED',
        entity_type='user',
        entity_id=str(user.id),
        user_id=get_current_user_id(),
        old_values=old_values,
        new_values={'username': user.username, 'email': user.email, 'role': user.role.value, 'is_active': user.is_active},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    return jsonify({'message': 'User updated'})


@admin_bp.route('/users/<uuid:user_id>', methods=['DELETE'])
@require_super_admin
def delete_user(user_id):
    db = next(get_db())
    audit = create_audit_logger(db)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if str(user.id) == str(get_current_user_id()):
        return jsonify({'error': 'You cannot deactivate your own account'}), 400
    if not user.is_active:
        return jsonify({'message': 'User already inactive'})

    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()

    audit.log(
        action='USER_DEACTIVATED',
        entity_type='user',
        entity_id=str(user.id),
        user_id=get_current_user_id(),
        old_values={'is_active': True},
        new_values={'is_active': False},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )

    return jsonify({'message': 'User deactivated'})


@admin_bp.route('/surveyors', methods=['GET'])
@require_admin
def list_surveyors():
    db = next(get_db())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    active_only = request.args.get('active', 'true').lower() == 'true'
    face_status = request.args.get('face_status')  # registered, not_registered
    
    query = db.query(Surveyor)
    if active_only:
        query = query.filter(Surveyor.is_active == True)
    if face_status == 'registered':
        query = query.filter(Surveyor.face_template.isnot(None))
    elif face_status == 'not_registered':
        query = query.filter(Surveyor.face_template.is_(None))
    
    total = query.count()
    surveyors = query.order_by(Surveyor.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
    
    return jsonify({
        'surveyors': [{
            'id': str(s.id),
            'employee_id': s.employee_id,
            'full_name': s.full_name,
            'phone_number': s.phone_number,
            'email': s.email,
            'face_registration_status': 'registered' if s.face_template is not None else 'not_registered',
            'face_template_version': s.face_template_version,
            'face_template_updated_at': s.updated_at.isoformat() + 'Z' if s.face_template and s.updated_at else None,
            'is_active': s.is_active,
            'created_at': s.created_at.isoformat() + 'Z'
        } for s in surveyors],
        'pagination': {'page': page, 'per_page': per_page, 'total': total}
    })


@admin_bp.route('/surveyors', methods=['POST'])
@require_admin
def create_surveyor():
    db = next(get_db())
    audit = create_audit_logger(db)
    data = request.get_json()
    
    validation = validate_surveyor_payload(data)
    if not validation.is_valid:
        return jsonify({'error': 'Validation failed', 'details': validation.errors}), 400

    username = data['employee_id']
    account_email = data.get('email') or f"{username.lower()}@ofas.local"
    existing_user = db.query(User).filter(
        or_(User.username == username, User.email == account_email)
    ).first()
    if existing_user:
        return jsonify({'error': 'A user account with this employee ID already exists'}), 409

    surveyor = Surveyor(
        employee_id=username,
        full_name=data['full_name'],
        phone_number=data['phone_number'],
        email=data.get('email'),
        face_template=data.get('face_template')
    )
    user = User(
        username=username,
        email=account_email,
        password_hash=hash_password(data['password']),
        role=UserRole.SURVEYOR
    )

    db.add(surveyor)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Employee ID or account already exists'}), 409
    
    audit.log(
        action='SURVEYOR_CREATED',
        entity_type='surveyor',
        entity_id=str(surveyor.id),
        user_id=get_current_user_id(),
        new_values={'employee_id': surveyor.employee_id, 'full_name': surveyor.full_name},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    return jsonify({'id': str(surveyor.id), 'message': 'Surveyor created'}), 201


@admin_bp.route('/surveyors/<uuid:surveyor_id>', methods=['PUT'])
@require_admin
def update_surveyor(surveyor_id):
    db = next(get_db())
    audit = create_audit_logger(db)
    data = request.get_json(silent=True) or {}
    
    surveyor = db.query(Surveyor).filter(Surveyor.id == surveyor_id).first()
    if not surveyor:
        return jsonify({'error': 'Surveyor not found'}), 404
    if not isinstance(data, dict) or not data:
        return jsonify({'error': 'At least one surveyor property is required'}), 400
    
    old_values = {'employee_id': surveyor.employee_id, 'full_name': surveyor.full_name, 'is_active': surveyor.is_active}
    
    if 'full_name' in data:
        if not isinstance(data['full_name'], str) or not data['full_name'].strip() or len(data['full_name'].strip()) > 200:
            return jsonify({'error': 'Full name must be 1-200 characters'}), 400
        surveyor.full_name = data['full_name']
    if 'phone_number' in data:
        if not isinstance(data['phone_number'], str) or not re.match(r'^\+?[1-9]\d{1,14}$', data['phone_number']):
            return jsonify({'error': 'Invalid phone number format'}), 400
        surveyor.phone_number = data['phone_number']
    if 'email' in data:
        if data['email'] != surveyor.email and data['email'] and not validate_email(data['email']):
            return jsonify({'error': 'Invalid email'}), 400
        surveyor.email = data['email']
    if 'is_active' in data:
        if not isinstance(data['is_active'], bool):
            return jsonify({'error': 'is_active must be a boolean'}), 400
        surveyor.is_active = data['is_active']
    if 'password' in data:
        if not isinstance(data['password'], str):
            return jsonify({'error': 'Password must be text'}), 400
        valid, errors = validate_password(data['password'])
        if not valid:
            return jsonify({'error': 'Weak password', 'details': errors}), 400
        user = db.query(User).filter(User.username == surveyor.employee_id).first()
        if user:
            user.password_hash = hash_password(data['password'])
    user = db.query(User).filter(User.username == surveyor.employee_id).first()
    if user and 'is_active' in data:
        user.is_active = data['is_active']
    if 'face_template' in data:
        surveyor.face_template = data['face_template']
        surveyor.face_template_version += 1
    
    surveyor.updated_at = datetime.utcnow()
    db.commit()
    
    audit.log(
        action='SURVEYOR_UPDATED',
        entity_type='surveyor',
        entity_id=str(surveyor.id),
        user_id=get_current_user_id(),
        old_values=old_values,
        new_values={'employee_id': surveyor.employee_id, 'full_name': surveyor.full_name, 'is_active': surveyor.is_active},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    return jsonify({'message': 'Surveyor updated'})


@admin_bp.route('/surveyors/<uuid:surveyor_id>', methods=['DELETE'])
@require_admin
def delete_surveyor(surveyor_id):
    db = next(get_db())
    surveyor = db.query(Surveyor).filter(Surveyor.id == surveyor_id).first()
    if not surveyor:
        return jsonify({'error': 'Surveyor not found'}), 404
    if not surveyor.is_active:
        return jsonify({'message': 'Surveyor already inactive'})
    surveyor.is_active = False
    user = db.query(User).filter(User.username == surveyor.employee_id).first()
    if user:
        user.is_active = False
    db.commit()
    return jsonify({'message': 'Surveyor deactivated'})


@admin_bp.route('/surveyors/face-registration-stats', methods=['GET'])
@require_admin
def get_face_registration_stats():
    """Get face registration statistics for all surveyors."""
    db = next(get_db())
    
    total = db.query(Surveyor).filter(Surveyor.is_active == True).count()
    registered = db.query(Surveyor).filter(
        Surveyor.is_active == True,
        Surveyor.face_template.isnot(None)
    ).count()
    not_registered = total - registered
    
    # Get details for each status
    registered_surveyors = db.query(Surveyor.id, Surveyor.employee_id, Surveyor.full_name, 
                                     Surveyor.face_template_version, Surveyor.updated_at).filter(
        Surveyor.is_active == True,
        Surveyor.face_template.isnot(None)
    ).all()
    
    not_registered_surveyors = db.query(Surveyor.id, Surveyor.employee_id, Surveyor.full_name).filter(
        Surveyor.is_active == True,
        Surveyor.face_template.is_(None)
    ).all()
    
    return jsonify({
        'summary': {
            'total_surveyors': total,
            'face_registered': registered,
            'face_not_registered': not_registered,
            'registration_rate': round((registered / total * 100) if total > 0 else 0, 2)
        },
        'registered': [{
            'id': str(s.id),
            'employee_id': s.employee_id,
            'full_name': s.full_name,
            'face_template_version': s.face_template_version,
            'updated_at': s.updated_at.isoformat() + 'Z' if s.updated_at else None
        } for s in registered_surveyors],
        'not_registered': [{
            'id': str(s.id),
            'employee_id': s.employee_id,
            'full_name': s.full_name
        } for s in not_registered_surveyors]
    })


@admin_bp.route('/fields', methods=['GET'])
@require_admin
def list_fields():
    db = next(get_db())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    active_only = request.args.get('active', 'true').lower() == 'true'
    
    query = db.query(Field)
    if active_only:
        query = query.filter(Field.is_active == True)
    
    total = query.count()
    fields = query.order_by(Field.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
    
    return jsonify({
        'fields': [{
            'id': str(f.id),
            'field_code': f.field_code,
            'name': f.name,
            'crop_type': f.crop_type,
            'center_lat': f.center_lat,
            'center_lon': f.center_lon,
            'radius_meters': f.radius_meters,
            'reference_photos': f.reference_photos or [],
            'field_metadata': f.field_metadata or {},
            'is_active': f.is_active,
            'created_at': f.created_at.isoformat() + 'Z'
        } for f in fields],
        'pagination': {'page': page, 'per_page': per_page, 'total': total}
    })


@admin_bp.route('/fields', methods=['POST'])
@require_admin
def create_field():
    db = next(get_db())
    audit = create_audit_logger(db)
    data = request.get_json()
    
    validation = validate_field_payload(data)
    if not validation.is_valid:
        return jsonify({'error': 'Validation failed', 'details': validation.errors}), 400
    
    field = Field(
        field_code=data['field_code'],
        name=data['name'],
        crop_type=data.get('crop_type'),
        center_lat=data['center_lat'],
        center_lon=data['center_lon'],
        radius_meters=data['radius_meters'],
        reference_photos=data.get('reference_photos', []),
        field_metadata=data.get('field_metadata', data.get('metadata', {}))
    )
    
    db.add(field)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Field code already exists'}), 409
    
    audit.log(
        action='FIELD_CREATED',
        entity_type='field',
        entity_id=str(field.id),
        user_id=get_current_user_id(),
        new_values={'field_code': field.field_code, 'name': field.name},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    return jsonify({'id': str(field.id), 'message': 'Field created'}), 201


@admin_bp.route('/fields/<uuid:field_id>', methods=['PUT'])
@require_admin
def update_field(field_id):
    db = next(get_db())
    audit = create_audit_logger(db)
    data = request.get_json()
    
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        return jsonify({'error': 'Field not found'}), 404
    
    old_values = {'field_code': field.field_code, 'name': field.name, 'radius_meters': field.radius_meters, 'is_active': field.is_active}
    
    if 'name' in data:
        field.name = data['name']
    if 'crop_type' in data:
        field.crop_type = data['crop_type']
    if 'center_lat' in data and 'center_lon' in data:
        field.center_lat = data['center_lat']
        field.center_lon = data['center_lon']
    if 'radius_meters' in data:
        field.radius_meters = data['radius_meters']
    if 'reference_photos' in data:
        field.reference_photos = data['reference_photos']
    if 'field_metadata' in data:
        field.field_metadata = data['field_metadata']
    if 'is_active' in data:
        field.is_active = data['is_active']
    
    field.updated_at = datetime.utcnow()
    db.commit()
    
    audit.log(
        action='FIELD_UPDATED',
        entity_type='field',
        entity_id=str(field.id),
        user_id=get_current_user_id(),
        old_values=old_values,
        new_values={'field_code': field.field_code, 'name': field.name, 'radius_meters': field.radius_meters, 'is_active': field.is_active},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    return jsonify({'message': 'Field updated'})


@admin_bp.route('/fields/<uuid:field_id>', methods=['DELETE'])
@require_admin
def delete_field(field_id):
    db = next(get_db())
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        return jsonify({'error': 'Field not found'}), 404
    field.is_active = False
    db.commit()
    return jsonify({'message': 'Field deactivated'})


@admin_bp.route('/phones', methods=['GET'])
@require_admin
def list_phones():
    db = next(get_db())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    query = db.query(Phone)
    total = query.count()
    phones = query.order_by(Phone.registered_at.desc()).offset((page-1)*per_page).limit(per_page).all()
    
    return jsonify({
        'phones': [{
            'id': str(p.id),
            'device_id': p.device_id,
            'model': p.model,
            'android_version': p.android_version,
            'status': p.status.value,
            'registered_at': p.registered_at.isoformat() + 'Z',
            'last_seen': p.last_seen.isoformat() + 'Z' if p.last_seen else None,
            'blocked_at': p.blocked_at.isoformat() + 'Z' if p.blocked_at else None,
            'blocked_reason': p.blocked_reason
        } for p in phones],
        'pagination': {'page': page, 'per_page': per_page, 'total': total}
    })


@admin_bp.route('/phones', methods=['POST'])
@require_admin
def register_phone():
    db = next(get_db())
    audit = create_audit_logger(db)
    data = request.get_json()
    
    required = ['device_id', 'public_key']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    phone = Phone(
        device_id=data['device_id'],
        model=data.get('model'),
        android_version=data.get('android_version'),
        public_key=data['public_key'],
        key_algorithm=data.get('key_algorithm', 'ES256'),
        registered_by=g.current_user.id
    )
    
    db.add(phone)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Device ID already registered'}), 409
    
    audit.log(
        action='PHONE_REGISTERED',
        entity_type='phone',
        entity_id=str(phone.id),
        user_id=get_current_user_id(),
        new_values={'device_id': phone.device_id, 'model': phone.model},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    return jsonify({'id': str(phone.id), 'message': 'Phone registered'}), 201


@admin_bp.route('/phones/<uuid:phone_id>/block', methods=['POST'])
@require_admin
def block_phone(phone_id):
    db = next(get_db())
    audit = create_audit_logger(db)
    data = request.get_json() or {}
    
    phone = db.query(Phone).filter(Phone.id == phone_id).first()
    if not phone:
        return jsonify({'error': 'Phone not found'}), 404
    
    phone.status = PhoneStatus.BLOCKED
    phone.blocked_at = datetime.utcnow()
    phone.blocked_reason = data.get('reason', 'Blocked by admin')
    db.commit()
    
    audit.log(
        action='PHONE_BLOCKED',
        entity_type='phone',
        entity_id=str(phone.id),
        user_id=get_current_user_id(),
        new_values={'status': 'blocked', 'reason': phone.blocked_reason},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    return jsonify({'message': 'Phone blocked'})


@admin_bp.route('/assignments', methods=['GET'])
@require_admin
def list_assignments():
    db = next(get_db())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 200)
    surveyor_id = request.args.get('surveyor_id')
    
    query = db.query(Assignment)
    if surveyor_id:
        query = query.filter(Assignment.surveyor_id == surveyor_id)
    
    total = query.count()
    assignments = query.order_by(Assignment.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
    
    return jsonify({
        'assignments': [{
            'id': str(a.id),
            'surveyor_id': str(a.surveyor_id),
            'surveyor_name': a.surveyor.full_name if a.surveyor else None,
            'field_id': str(a.field_id),
            'field_code': a.field.field_code if a.field else None,
            'start_date': a.start_date.date().isoformat(),
            'end_date': a.end_date.date().isoformat(),
            'is_completed': a.is_completed,
            'completed_at': a.completed_at.isoformat() + 'Z' if a.completed_at else None
        } for a in assignments],
        'pagination': {'page': page, 'per_page': per_page, 'total': total}
    })


@admin_bp.route('/assignments', methods=['POST'])
@require_admin
def create_assignment():
    db = next(get_db())
    audit = create_audit_logger(db)
    data = request.get_json()
    
    validation = validate_assignment_payload(data)
    if not validation.is_valid:
        return jsonify({'error': 'Validation failed', 'details': validation.errors}), 400
    
    surveyor = db.query(Surveyor).filter(Surveyor.id == data['surveyor_id']).first()
    field = db.query(Field).filter(Field.id == data['field_id']).first()
    if not surveyor or not field:
        return jsonify({'error': 'Surveyor or field not found'}), 404
    
    assignment = Assignment(
        surveyor_id=data['surveyor_id'],
        field_id=data['field_id'],
        start_date=datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')),
        end_date=datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')),
        assigned_by=g.current_user.id
    )
    
    db.add(assignment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Assignment already exists'}), 409
    
    audit.log(
        action='ASSIGNMENT_CREATED',
        entity_type='assignment',
        entity_id=str(assignment.id),
        user_id=get_current_user_id(),
        new_values={'surveyor_id': str(assignment.surveyor_id), 'field_id': str(assignment.field_id)},
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    return jsonify({'id': str(assignment.id), 'message': 'Assignment created'}), 201


@admin_bp.route('/assignments/<uuid:assignment_id>', methods=['PUT'])
@require_admin
def update_assignment(assignment_id):
    db = next(get_db())
    data = request.get_json() or {}
    validation = validate_assignment_payload(data)
    if not validation.is_valid:
        return jsonify({'error': 'Validation failed', 'details': validation.errors}), 400
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    assignment.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
    assignment.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Unable to update assignment'}), 409
    return jsonify({'message': 'Assignment updated'})


@admin_bp.route('/assignments/<uuid:assignment_id>', methods=['DELETE'])
@require_admin
def delete_assignment(assignment_id):
    db = next(get_db())
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    db.delete(assignment)
    db.commit()
    return jsonify({'message': 'Assignment deleted'})


def validate_email(email: str) -> bool:
    import re
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))