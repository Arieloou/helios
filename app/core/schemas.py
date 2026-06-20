# core/schemas.py

from pydantic import BaseModel
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"
    CONSULTOR = "consultor"

class CurrentUser(BaseModel):
    id: str
    email: str
    role: UserRole