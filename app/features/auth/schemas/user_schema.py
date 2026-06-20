from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"

# DTO para crear un usuario
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: UserRole

# DTO para devolver los datos al frontend (Reemplaza a to_dict)
class UserOut(BaseModel):
    id: str
    name: Optional[str]
    email: Optional[str]
    role: Optional[UserRole]
    is_active: Optional[bool]
    failed_attempts: Optional[int]
    locked_until: Optional[datetime]

    class Config:
        from_attributes = True # Permite leer directamente desde SQLAlchemy