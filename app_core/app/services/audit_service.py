import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.audit_log import AuditLog, AuditAction
from app.models.base import db


class AuditService:
    @staticmethod
    def log_action(
        table_name: str,
        record_id: str,
        action: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        old_json = json.dumps(old_values) if old_values else None
        new_json = json.dumps(new_values) if new_values else None

        audit_log = AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=old_json,
            new_values=new_json,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=datetime.now(),
        )
        db.session.add(audit_log)
        db.session.commit()
        return audit_log

    @staticmethod
    def get_by_table(table_name: str, limit: int = 100) -> List[AuditLog]:
        return AuditLog.get_by_table(table_name, limit)

    @staticmethod
    def get_by_record(table_name: str, record_id: str) -> List[AuditLog]:
        return AuditLog.get_by_record(table_name, record_id)

    @staticmethod
    def get_by_user(user_id: str, limit: int = 100) -> List[AuditLog]:
        return AuditLog.get_by_user(user_id, limit)

    @staticmethod
    def log_create(
        table_name: str,
        record_id: str,
        new_values: Dict[str, Any],
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        return AuditService.log_action(
            table_name=table_name,
            record_id=record_id,
            action=AuditAction.CREATE,
            new_values=new_values,
            user_id=user_id,
            ip_address=ip_address,
        )

    @staticmethod
    def log_update(
        table_name: str,
        record_id: str,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        return AuditService.log_action(
            table_name=table_name,
            record_id=record_id,
            action=AuditAction.UPDATE,
            old_values=old_values,
            new_values=new_values,
            user_id=user_id,
            ip_address=ip_address,
        )

    @staticmethod
    def log_delete(
        table_name: str,
        record_id: str,
        old_values: Dict[str, Any],
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        return AuditService.log_action(
            table_name=table_name,
            record_id=record_id,
            action=AuditAction.DELETE,
            old_values=old_values,
            user_id=user_id,
            ip_address=ip_address,
        )