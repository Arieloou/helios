# features/assessment/models/assesment.py

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from app.core import Base, TimestampMixin
from ..schemas import AssessmentStatus

class Assessment(TimestampMixin, Base):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    period: Mapped[str] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=AssessmentStatus.ACTIVE.value)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    closed_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    archived_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    ## Validate if the __encrypted_fields__ is working correctly
    __encrypted_fields__ = ["name", "description", "period"]