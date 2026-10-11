"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-10-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, BYTEA
from geoalchemy2 import Geometry

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('super_admin', 'admin', 'surveyor', name='userrole'), nullable=False, server_default='admin'),
        sa.Column('totp_secret', sa.String(32)),
        sa.Column('totp_enabled', sa.Boolean, default=False),
        sa.Column('passkey_credential_id', sa.String(255)),
        sa.Column('passkey_public_key', sa.Text),
        sa.Column('passkey_sign_count', sa.Integer, default=0),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('last_login', sa.DateTime),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table(
        'surveyors',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('employee_id', sa.String(50), unique=True, nullable=False),
        sa.Column('full_name', sa.String(200), nullable=False),
        sa.Column('phone_number', sa.String(20)),
        sa.Column('email', sa.String(255)),
        sa.Column('face_template', BYTEA),
        sa.Column('face_template_version', sa.Integer, default=1),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_surveyors_employee_id', 'surveyors', ['employee_id'])

    op.create_table(
        'phones',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('device_id', sa.String(100), unique=True, nullable=False),
        sa.Column('model', sa.String(100)),
        sa.Column('android_version', sa.String(20)),
        sa.Column('public_key', sa.Text, nullable=False),
        sa.Column('key_algorithm', sa.String(50), default='ES256'),
        sa.Column('status', sa.Enum('active', 'blocked', 'lost', name='phonestatus'), default='active', nullable=False),
        sa.Column('registered_by', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('registered_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('last_seen', sa.DateTime),
        sa.Column('blocked_at', sa.DateTime),
        sa.Column('blocked_reason', sa.Text),
    )
    op.create_index('ix_phones_device_id', 'phones', ['device_id'])

    op.create_table(
        'fields',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('field_code', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('crop_type', sa.String(100)),
        sa.Column('center_lat', sa.Float, nullable=False),
        sa.Column('center_lon', sa.Float, nullable=False),
        sa.Column('center_point', Geometry('POINT', srid=4326)),
        sa.Column('radius_meters', sa.Float, nullable=False, default=100.0),
        sa.Column('reference_photos', JSONB, default=list),
        sa.Column('metadata', JSONB, default=dict),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_fields_field_code', 'fields', ['field_code'])
    op.create_index('ix_fields_center', 'fields', ['center_lat', 'center_lon'])

    op.create_table(
        'assignments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('surveyor_id', UUID(as_uuid=True), sa.ForeignKey('surveyors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assigned_date', sa.DateTime, nullable=False),
        sa.Column('assigned_by', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('is_completed', sa.Boolean, default=False),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint('uq_assignment', 'assignments', ['surveyor_id', 'field_id', 'assigned_date'])
    op.create_index('ix_assignments_date_surveyor', 'assignments', ['assigned_date', 'surveyor_id'])

    op.create_table(
        'visits',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('visit_id', sa.String(64), unique=True, nullable=False),
        sa.Column('surveyor_id', UUID(as_uuid=True), sa.ForeignKey('surveyors.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('phone_id', UUID(as_uuid=True), sa.ForeignKey('phones.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('satellite_timestamp', sa.DateTime, nullable=False),
        sa.Column('latitude', sa.Float, nullable=False),
        sa.Column('longitude', sa.Float, nullable=False),
        sa.Column('accuracy_meters', sa.Float, nullable=False),
        sa.Column('altitude', sa.Float),
        sa.Column('speed', sa.Float),
        sa.Column('bearing', sa.Float),
        sa.Column('selfie_photo_hash', sa.String(64), nullable=False),
        sa.Column('selfie_photo_s3_key', sa.String(255)),
        sa.Column('field_photos', JSONB, nullable=False, default=list),
        sa.Column('face_match_score', sa.Float),
        sa.Column('liveness_verified', sa.Boolean, default=False),
        sa.Column('trail_snapshot', JSONB, nullable=False),
        sa.Column('signature', sa.String(255), nullable=False),
        sa.Column('signed_by_key_id', sa.String(100), nullable=False),
        sa.Column('status', sa.Enum('queued', 'syncing', 'synced', 'failed', 'valid', 'invalid', 'flagged', name='visitstatus'), default='queued', nullable=False),
        sa.Column('review_status', sa.Enum('queued', 'syncing', 'synced', 'failed', 'valid', 'invalid', 'flagged', name='visitstatus_review')),
        sa.Column('reviewed_by', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('reviewed_at', sa.DateTime),
        sa.Column('review_notes', sa.Text),
        sa.Column('synced_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_visits_visit_id', 'visits', ['visit_id'])
    op.create_index('ix_visits_satellite_time', 'visits', ['satellite_timestamp'])
    op.create_index('ix_visits_status_sync', 'visits', ['status', 'synced_at'])

    op.create_table(
        'trail_entries',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('phone_id', UUID(as_uuid=True), sa.ForeignKey('phones.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sequence_number', sa.Integer, nullable=False),
        sa.Column('satellite_timestamp', sa.DateTime, nullable=False),
        sa.Column('latitude', sa.Float, nullable=False),
        sa.Column('longitude', sa.Float, nullable=False),
        sa.Column('accuracy_meters', sa.Float, nullable=False),
        sa.Column('altitude', sa.Float),
        sa.Column('speed', sa.Float),
        sa.Column('bearing', sa.Float),
        sa.Column('prev_hash', sa.String(64), nullable=False),
        sa.Column('entry_hash', sa.String(64), nullable=False),
        sa.Column('signature', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint('uq_trail_sequence', 'trail_entries', ['phone_id', 'sequence_number'])
    op.create_index('ix_trail_phone_time', 'trail_entries', ['phone_id', 'satellite_timestamp'])
    op.create_index('ix_trail_entry_hash', 'trail_entries', ['entry_hash'])

    op.create_table(
        'audit_log',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('sequence_number', sa.Integer, nullable=False, unique=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', UUID(as_uuid=True)),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('visit_id', UUID(as_uuid=True), sa.ForeignKey('visits.id', ondelete='SET NULL')),
        sa.Column('phone_id', UUID(as_uuid=True), sa.ForeignKey('phones.id', ondelete='SET NULL')),
        sa.Column('old_values', JSONB),
        sa.Column('new_values', JSONB),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text),
        sa.Column('prev_hash', sa.String(64), nullable=False),
        sa.Column('entry_hash', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_audit_entity', 'audit_log', ['entity_type', 'entity_id'])
    op.create_index('ix_audit_user_time', 'audit_log', ['user_id', 'created_at'])
    op.create_index('ix_audit_created', 'audit_log', ['created_at'])
    op.create_index('ix_audit_entry_hash', 'audit_log', ['entry_hash'])


def downgrade():
    op.drop_table('audit_log')
    op.drop_table('trail_entries')
    op.drop_table('visits')
    op.drop_table('assignments')
    op.drop_table('fields')
    op.drop_table('phones')
    op.drop_table('surveyors')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS phonestatus')
    op.execute('DROP TYPE IF EXISTS visitstatus')
    op.execute('DROP TYPE IF EXISTS visitstatus_review')