# features/assessment/schemas/assessment_dto.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class AssessmentStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    CLOSED = "closed"

# DTO para crear una evaluación
class AssessmentCreate(BaseModel):
    name: str
    description: str
    period: str

# DTO para devolver los datos al frontend (Reemplaza a tu to_dict)
class AssessmentResponse(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]
    period: Optional[str]
    status: AssessmentStatus
    created_by: Optional[str]
    created_at: Optional[datetime]
    archived_at: Optional[datetime]
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True # Permite leer directamente desde SQLAlchemy