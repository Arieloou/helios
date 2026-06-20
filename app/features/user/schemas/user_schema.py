# features/user/schemas/user_schema.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# DTO para crear un usuario
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: UserRole

# schemas.py — todos opcionales, así Pydantic sabe distinguir "no vino" de "vino vacío"
class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    role: str | None = None

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

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthMessageResponse(BaseModel):
    message: str
