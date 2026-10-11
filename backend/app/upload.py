import os
import uuid
import base64
import hashlib
from datetime import datetime
from typing import Optional
from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import Visit, Surveyor, Field
from .database import get_db
from .auth import require_admin, require_role, get_current_user_id
from .models import UserRole
from .validation import validate_base64_image
from .audit import create_audit_logger

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')


def get_s3_client():
    """Get configured S3/MinIO client."""
    if not boto3:
        return None

    app_config = current_app.config
    return boto3.client(
        's3',
        endpoint_url=app_config.get('S3_ENDPOINT_URL'),
        aws_access_key_id=app_config.get('S3_ACCESS_KEY'),
        aws_secret_access_key=app_config.get('S3_SECRET_KEY'),
        region_name=app_config.get('S3_REGION', 'us-east-1'),
        config=boto3.session.Config(signature_version='s3v4')
    )


def ensure_bucket_exists():
    """Ensure the S3 bucket exists."""
    s3 = get_s3_client()
    if not s3:
        return False

    bucket = current_app.config.get('S3_BUCKET', 'ofas-photos')
    try:
        s3.head_bucket(Bucket=bucket)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            try:
                s3.create_bucket(Bucket=bucket)
                return True
            except ClientError:
                return False
        return False


@upload_bp.route('/photo', methods=['POST'])
@require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.SURVEYOR)
def upload_photo():
    """
    Upload a photo for a visit.
    Expected JSON:
    {
        "visit_id": "uuid",
        "photo_type": "selfie|field",
        "photo_index": 0,
        "image": "base64 encoded image",
        "metadata": {...}
    }
    """
    if not boto3:
        return jsonify({'error': 'S3 upload not configured'}), 503

    if not ensure_bucket_exists():
        return jsonify({'error': 'S3 bucket not accessible'}), 503

    db = next(get_db())
    audit = create_audit_logger(db)

    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'Invalid JSON'}), 400

    required = ['visit_id', 'photo_type', 'photo_index', 'image']
    for field in required:
        if field not in payload:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    visit = db.query(Visit).filter(Visit.id == payload['visit_id']).first()
    if not visit:
        return jsonify({'error': 'Visit not found'}), 404

    current_user = getattr(g, 'current_user', None)
    if current_user and current_user.role == UserRole.SURVEYOR:
        surveyor = db.query(Surveyor).filter(
            Surveyor.id == visit.surveyor_id,
            (Surveyor.email == current_user.email) |
            (Surveyor.employee_id == current_user.username)
        ).first()
        if not surveyor:
            return jsonify({'error': 'Visit does not belong to authenticated surveyor'}), 403

    photo_type = payload['photo_type']
    if photo_type not in ('selfie', 'field'):
        return jsonify({'error': 'photo_type must be selfie or field'}), 400

    photo_index = payload['photo_index']
    if not isinstance(photo_index, int) or photo_index < 0:
        return jsonify({'error': 'photo_index must be non-negative integer'}), 400

    # Validate image
    is_valid, errors = validate_base64_image(
        payload['image'],
        max_size_mb=current_app.config.get('MAX_PHOTO_SIZE_MB', 2)
    )
    if not is_valid:
        return jsonify({'error': 'Invalid image', 'details': errors}), 400

    # Decode image
    image_data = payload['image']
    if image_data.startswith('data:image/'):
        image_data = image_data.split(',', 1)[1]
    image_bytes = base64.b64decode(image_data)

    # Generate hash
    photo_hash = hashlib.sha256(image_bytes).hexdigest()

    # Generate S3 key
    ext = '.jpg'  # Assume JPEG
    s3_key = f"visits/{visit.id}/{photo_type}_{photo_index}_{uuid.uuid4().hex[:8]}{ext}"

    # Upload to S3/MinIO
    s3 = get_s3_client()
    try:
        s3.put_object(
            Bucket=current_app.config['S3_BUCKET'],
            Key=s3_key,
            Body=image_bytes,
            ContentType='image/jpeg',
            Metadata={
                'visit_id': str(visit.id),
                'photo_type': photo_type,
                'photo_index': str(photo_index),
                'hash': photo_hash,
                'uploaded_at': datetime.utcnow().isoformat() + 'Z'
            }
        )
    except ClientError as e:
        return jsonify({'error': 'Failed to upload to S3', 'details': str(e)}), 500

    # Update visit record
    if photo_type == 'selfie':
        visit.selfie_photo_hash = photo_hash
        visit.selfie_photo_s3_key = s3_key
    else:
        # Update field_photos array
        field_photos = visit.field_photos or []
        if photo_index >= len(field_photos):
            field_photos.extend([None] * (photo_index - len(field_photos) + 1))
        field_photos[photo_index] = {
            'hash': photo_hash,
            's3_key': s3_key,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'metadata': payload.get('metadata', {})
        }
        visit.field_photos = field_photos

    visit.updated_at = datetime.utcnow()
    db.commit()

    audit.log(
        action='PHOTO_UPLOADED',
        entity_type='photo',
        entity_id=s3_key,
        user_id=get_current_user_id(),
        visit_id=str(visit.id),
        new_values={
            'photo_type': photo_type,
            'photo_index': photo_index,
            'hash': photo_hash,
            's3_key': s3_key
        },
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )

    # Generate presigned URL for immediate access
    presigned_url = None
    try:
        presigned_url = get_s3_client().generate_presigned_url(
            'get_object',
            Params={'Bucket': current_app.config['S3_BUCKET'], 'Key': s3_key},
            ExpiresIn=3600
        )
    except Exception:
        pass

    return jsonify({
        'success': True,
        'photo_hash': photo_hash,
        's3_key': s3_key,
        'presigned_url': presigned_url
    }), 201


@upload_bp.route('/photo/<path:s3_key>', methods=['GET'])
def get_photo_presigned_url(s3_key):
    """Get presigned URL for a photo."""
    if not boto3:
        return jsonify({'error': 'S3 not configured'}), 503

    s3 = get_s3_client()
    try:
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': current_app.config['S3_BUCKET'], 'Key': s3_key},
            ExpiresIn=3600
        )
        return jsonify({'url': presigned_url})
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return jsonify({'error': 'Photo not found'}), 404
        return jsonify({'error': 'Failed to generate URL'}), 500


@upload_bp.route('/photo/<path:s3_key>', methods=['DELETE'])
@require_admin
def delete_photo(s3_key):
    """Delete a photo (admin only)."""
    if not boto3:
        return jsonify({'error': 'S3 not configured'}), 503

    s3 = get_s3_client()
    try:
        s3.delete_object(Bucket=current_app.config['S3_BUCKET'], Key=s3_key)
    except ClientError as e:
        return jsonify({'error': 'Failed to delete photo', 'details': str(e)}), 500

    # Note: This doesn't remove reference from Visit, just deletes from S3
    # In production, you'd want to update the Visit record too

    return jsonify({'message': 'Photo deleted'})