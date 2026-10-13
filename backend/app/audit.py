import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import AuditLog, User
from .database import get_db


AUDIT_ACTIONS = {
    'USER_LOGIN', 'USER_LOGOUT', 'USER_CREATED', 'USER_UPDATED', 'USER_DELETED',
    'USER_DEACTIVATED',
    'ROLE_CHANGED', 'PASSWORD_CHANGED', 'TOTP_ENABLED', 'TOTP_DISABLED', 'PASSKEY_REGISTERED',
    'SURVEYOR_CREATED', 'SURVEYOR_UPDATED', 'SURVEYOR_DELETED',
    'FACE_TEMPLATE_ENROLLED', 'FACE_TEMPLATE_UPDATED', 'FACE_TEMPLATE_DELETED',
    'FIELD_CREATED', 'FIELD_UPDATED', 'FIELD_DELETED',
    'PHONE_REGISTERED', 'PHONE_BLOCKED', 'PHONE_UNBLOCKED',
    'ASSIGNMENT_CREATED', 'ASSIGNMENT_UPDATED', 'ASSIGNMENT_DELETED',
    'VISIT_SUBMITTED', 'VISIT_REVIEWED', 'VISIT_STATUS_CHANGED',
    'PHOTO_UPLOADED',
    'AUDIT_LOG_ACCESSED', 'CONFIG_CHANGED', 'BACKUP_CREATED',
    'SUPER_ADMIN_ACTION_APPROVED', 'SUPER_ADMIN_ACTION_REJECTED',
}


class AuditLogger:
    def __init__(self, db: Session):
        self.db = db
    
    def _get_last_hash(self) -> str:
        last_entry = self.db.query(AuditLog).order_by(
            AuditLog.sequence_number.desc()
        ).first()
        return last_entry.entry_hash if last_entry else "0" * 64
    
    def _get_next_sequence(self) -> int:
        max_seq = self.db.query(func.max(AuditLog.sequence_number)).scalar()
        return (max_seq or 0) + 1
    
    def _compute_hash(self, entry: AuditLog) -> str:
        data = {
            'seq': entry.sequence_number,
            'action': entry.action,
            'entity_type': entry.entity_type,
            'entity_id': str(entry.entity_id) if entry.entity_id else None,
            'user_id': str(entry.user_id) if entry.user_id else None,
            'visit_id': str(entry.visit_id) if entry.visit_id else None,
            'phone_id': str(entry.phone_id) if entry.phone_id else None,
            'old_values': entry.old_values,
            'new_values': entry.new_values,
            'ip': entry.ip_address,
            'ua': entry.user_agent,
            'prev': entry.prev_hash,
            'time': entry.created_at.isoformat() + 'Z'
        }
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def log(
        self,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        visit_id: Optional[str] = None,
        phone_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        if action not in AUDIT_ACTIONS:
            raise ValueError(f"Invalid audit action: {action}")
        
        sequence = self._get_next_sequence()
        prev_hash = self._get_last_hash()
        
        entry = AuditLog(
            sequence_number=sequence,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            visit_id=visit_id,
            phone_id=phone_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            prev_hash=prev_hash,
            entry_hash="",
            created_at=datetime.utcnow()
        )
        
        entry.entry_hash = self._compute_hash(entry)
        
        self.db.add(entry)
        self.db.flush()
        
        return entry


def create_audit_logger(db: Session) -> AuditLogger:
    return AuditLogger(db)


def verify_audit_chain(db: Session, start_seq: int = 1, end_seq: Optional[int] = None) -> Dict[str, Any]:
    query = db.query(AuditLog).filter(AuditLog.sequence_number >= start_seq)
    if end_seq:
        query = query.filter(AuditLog.sequence_number <= end_seq)
    
    entries = query.order_by(AuditLog.sequence_number).all()
    
    result = {
        'valid': True,
        'total_checked': len(entries),
        'errors': [],
        'broken_at': None
    }
    
    expected_prev = "0" * 64
    for entry in entries:
        if entry.prev_hash != expected_prev:
            result['valid'] = False
            result['errors'].append(
                f"Sequence {entry.sequence_number}: prev_hash mismatch "
                f"(expected {expected_prev[:16]}..., got {entry.prev_hash[:16]}...)"
            )
            result['broken_at'] = entry.sequence_number
            break
        
        logger = AuditLogger(db)
        computed_hash = logger._compute_hash(entry)
        if entry.entry_hash != computed_hash:
            result['valid'] = False
            result['errors'].append(
                f"Sequence {entry.sequence_number}: entry_hash mismatch"
            )
            result['broken_at'] = entry.sequence_number
            break
        
        expected_prev = entry.entry_hash
    
    return result


def get_audit_trail(
    db: Session,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[AuditLog]:
    query = db.query(AuditLog)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    
    return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()


def get_audit_stats(db: Session) -> Dict[str, Any]:
    total = db.query(func.count(AuditLog.id)).scalar()
    by_action = dict(db.query(
        AuditLog.action, func.count(AuditLog.id)
    ).group_by(AuditLog.action).all())
    by_entity = dict(db.query(
        AuditLog.entity_type, func.count(AuditLog.id)
    ).group_by(AuditLog.entity_type).all())
    
    latest = db.query(AuditLog).order_by(AuditLog.created_at.desc()).first()
    
    return {
        'total_entries': total,
        'by_action': by_action,
        'by_entity_type': by_entity,
        'latest_entry': latest.created_at.isoformat() if latest else None,
        'chain_verified': verify_audit_chain(db)['valid']
    }