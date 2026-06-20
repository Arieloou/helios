from core import Base, TimestampMixin

import uuid

class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[str] = mapped_column(String, nullable=True)
    request_id: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String)        # SUCCESS / FAILURE
    duration_ms: Mapped[int] = mapped_column(Integer)
    error: Mapped[str] = mapped_column(Text, nullable=True)