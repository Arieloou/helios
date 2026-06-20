from sqlalchemy.ext.asyncio import AsyncSession
from app.features.audit.models import AuditLog

class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_audit_log(
        self, action: str, 
        user_id: str, 
        request_id: str, 
        status: str, 
        duration_ms: int, 
        error: str) -> None:

        audit_log = AuditLog(
            action=action, 
            user_id=user_id, 
            request_id=request_id, 
            status=status, 
            duration_ms=duration_ms, 
            error=error)
        
        self.session.add(audit_log)
        await self.session.commit()