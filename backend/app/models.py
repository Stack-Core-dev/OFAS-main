import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, Text, Float, ForeignKey,
    Enum as SQLEnum, Index, UniqueConstraint, CheckConstraint, text
)
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship, declarative_base
from geoalchemy2 import Geometry

from .database import Base, GUID, BinaryData, JSONBData, GeometryData

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SURVEYOR = "surveyor"

class VisitStatus(str, enum.Enum):
    QUEUED = "queued"
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"
    VALID = "valid"
    INVALID = "invalid"
    FLAGGED = "flagged"

class PhoneStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    LOST = "lost"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.ADMIN)
    totp_secret = Column(String(32))
    totp_enabled = Column(Boolean, default=False)
    passkey_credential_id = Column(String(255))
    passkey_public_key = Column(Text)
    passkey_sign_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    
    audit_logs = relationship("AuditLog", back_populates="user", lazy="dynamic")
    
    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"

class Surveyor(Base):
    __tablename__ = 'surveyors'
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    phone_number = Column(String(20))
    email = Column(String(255))
    face_template = Column(BinaryData)
    face_template_version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    visits = relationship("Visit", back_populates="surveyor", lazy="dynamic")
    assignments = relationship("Assignment", back_populates="surveyor", lazy="dynamic")
    
    def __repr__(self):
        return f"<Surveyor {self.employee_id} - {self.full_name}>"

class Phone(Base):
    __tablename__ = 'phones'
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    device_id = Column(String(100), unique=True, nullable=False, index=True)
    model = Column(String(100))
    android_version = Column(String(20))
    public_key = Column(Text, nullable=False)
    key_algorithm = Column(String(50), default='ES256')
    status = Column(SQLEnum(PhoneStatus), default=PhoneStatus.ACTIVE, nullable=False)
    registered_by = Column(GUID, ForeignKey('users.id'))
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime)
    blocked_at = Column(DateTime)
    blocked_reason = Column(Text)
    
    visits = relationship("Visit", back_populates="phone", lazy="dynamic")
    
    def __repr__(self):
        return f"<Phone {self.device_id} ({self.status.value})>"

class Field(Base):
    __tablename__ = 'fields'
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    field_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    crop_type = Column(String(100))
    center_lat = Column(Float, nullable=False)
    center_lon = Column(Float, nullable=False)
    center_point = Column(GeometryData)
    radius_meters = Column(Float, nullable=False, default=100.0)
    reference_photos = Column(JSONBData, default=list)
    field_metadata = Column(JSONBData, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    visits = relationship("Visit", back_populates="field", lazy="dynamic")
    assignments = relationship("Assignment", back_populates="field", lazy="dynamic")
    
    __table_args__ = (
        CheckConstraint('radius_meters > 0', name='check_positive_radius'),
        Index('idx_fields_center', 'center_lat', 'center_lon'),
    )
    
    def __repr__(self):
        return f"<Field {self.field_code} - {self.name}>"

class Assignment(Base):
    __tablename__ = 'assignments'
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    surveyor_id = Column(GUID, ForeignKey('surveyors.id', ondelete='CASCADE'), nullable=False)
    field_id = Column(GUID, ForeignKey('fields.id', ondelete='CASCADE'), nullable=False)
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    assigned_by = Column(GUID, ForeignKey('users.id'))
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    surveyor = relationship("Surveyor", back_populates="assignments")
    field = relationship("Field", back_populates="assignments")
    
    __table_args__ = (
        UniqueConstraint('surveyor_id', 'field_id', name='uq_assignment'),
        CheckConstraint('end_date >= start_date', name='check_assignment_date_range'),
    )
    
    def __repr__(self):
        return f"<Assignment {self.surveyor_id} -> {self.field_id} ({self.start_date} to {self.end_date})>"

class Visit(Base):
    __tablename__ = 'visits'
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    visit_id = Column(String(64), unique=True, nullable=False, index=True)
    surveyor_id = Column(GUID, ForeignKey('surveyors.id', ondelete='RESTRICT'), nullable=False)
    field_id = Column(GUID, ForeignKey('fields.id', ondelete='RESTRICT'), nullable=False)
    phone_id = Column(GUID, ForeignKey('phones.id', ondelete='RESTRICT'), nullable=False)
    
    satellite_timestamp = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy_meters = Column(Float, nullable=False)
    altitude = Column(Float)
    speed = Column(Float)
    bearing = Column(Float)
    
    selfie_photo_hash = Column(String(64), nullable=False)
    selfie_photo_s3_key = Column(String(255))
    selfie_latitude = Column(Float)
    selfie_longitude = Column(Float)
    selfie_accuracy_meters = Column(Float)
    field_photos = Column(JSONBData, nullable=False, default=list)
    
    face_match_score = Column(Float)
    liveness_verified = Column(Boolean, default=False)
    trail_snapshot = Column(JSONBData, nullable=False)
    signature = Column(String(255), nullable=False)
    signed_by_key_id = Column(String(100), nullable=False)
    
    status = Column(SQLEnum(VisitStatus), default=VisitStatus.QUEUED, nullable=False, index=True)
    review_status = Column(SQLEnum(VisitStatus), nullable=True)
    reviewed_by = Column(GUID, ForeignKey('users.id'))
    reviewed_at = Column(DateTime)
    review_notes = Column(Text)
    
    synced_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    surveyor = relationship("Surveyor", back_populates="visits")
    field = relationship("Field", back_populates="visits")
    phone = relationship("Phone", back_populates="visits")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    audit_logs = relationship("AuditLog", back_populates="visit", lazy="dynamic")
    
    __table_args__ = (
        CheckConstraint('accuracy_meters >= 0', name='check_accuracy_positive'),
        CheckConstraint('face_match_score >= 0 AND face_match_score <= 1', name='check_face_score_range'),
        Index('idx_visits_satellite_time', 'satellite_timestamp'),
        Index('idx_visits_status_sync', 'status', 'synced_at'),
    )
    
    def __repr__(self):
        return f"<Visit {self.visit_id} ({self.status.value})>"

class TrailEntry(Base):
    __tablename__ = 'trail_entries'
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    phone_id = Column(GUID, ForeignKey('phones.id', ondelete='CASCADE'), nullable=False)
    sequence_number = Column(Integer, nullable=False)
    satellite_timestamp = Column(DateTime, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy_meters = Column(Float, nullable=False)
    altitude = Column(Float)
    speed = Column(Float)
    bearing = Column(Float)
    prev_hash = Column(String(64), nullable=False)
    entry_hash = Column(String(64), nullable=False, index=True)
    signature = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('phone_id', 'sequence_number', name='uq_trail_sequence'),
        Index('idx_trail_phone_time', 'phone_id', 'satellite_timestamp'),
    )
    
    def __repr__(self):
        return f"<TrailEntry {self.phone_id} #{self.sequence_number}>"

class SurveyorLocation(Base):
    __tablename__ = 'surveyor_locations'

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    surveyor_id = Column(GUID, ForeignKey('surveyors.id', ondelete='CASCADE'), nullable=False, index=True)
    phone_id = Column(GUID, ForeignKey('phones.id', ondelete='SET NULL'))
    device_id = Column(String(100), index=True)

    recorded_at = Column(DateTime, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy_meters = Column(Float)
    altitude = Column(Float)
    speed = Column(Float)
    bearing = Column(Float)
    source = Column(String(50), default='trail', nullable=False)

    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    surveyor = relationship("Surveyor")

    __table_args__ = (
        UniqueConstraint('surveyor_id', 'recorded_at', name='uq_surveyor_location_time'),
        Index('idx_surveyor_locations_surveyor_time', 'surveyor_id', 'recorded_at'),
        Index('idx_surveyor_locations_received', 'received_at'),
    )

    def __repr__(self):
        return f"<SurveyorLocation {self.surveyor_id} @ {self.recorded_at}>"

class AuditLog(Base):
    __tablename__ = 'audit_log'
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    sequence_number = Column(Integer, nullable=False, unique=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(GUID, nullable=True, index=True)
    user_id = Column(GUID, ForeignKey('users.id', ondelete='SET NULL'))
    visit_id = Column(GUID, ForeignKey('visits.id', ondelete='SET NULL'))
    phone_id = Column(GUID, ForeignKey('phones.id', ondelete='SET NULL'))
    old_values = Column(JSONBData)
    new_values = Column(JSONBData)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    prev_hash = Column(String(64), nullable=False)
    entry_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    user = relationship("User", back_populates="audit_logs")
    visit = relationship("Visit", back_populates="audit_logs")
    
    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_user_time', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AuditLog #{self.sequence_number} {self.action} on {self.entity_type}>"