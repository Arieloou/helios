import uuid
from datetime import datetime
from typing import Dict, List, Optional

from .base import db, TimestampMixin


class AuditAction:
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditLog(db.Model, TimestampMixin):
    __tablename__ = "audit_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    table_name = db.Column(db.String(100), nullable=False, index=True)
    record_id = db.Column(db.String(36), nullable=False, index=True)
    action = db.Column(db.String(20), nullable=False)
    old_values = db.Column(db.Text, nullable=True)
    new_values = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.String(36), nullable=True, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False, index=True)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "table_name": self.table_name,
            "record_id": self.record_id,
            "action": self.action,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_by_id(cls, audit_id: str) -> Optional["AuditLog"]:
        return cls.query.get(audit_id)

    @classmethod
    def get_by_table(cls, table_name: str, limit: int = 100) -> List["AuditLog"]:
        return cls.query.filter_by(table_name=table_name).order_by(cls.timestamp.desc()).limit(limit).all()

    @classmethod
    def get_by_record(cls, table_name: str, record_id: str) -> List["AuditLog"]:
        return cls.query.filter_by(table_name=table_name, record_id=record_id).order_by(cls.timestamp.desc()).all()

    @classmethod
    def get_by_user(cls, user_id: str, limit: int = 100) -> List["AuditLog"]:
        return cls.query.filter_by(user_id=user_id).order_by(cls.timestamp.desc()).limit(limit).all()