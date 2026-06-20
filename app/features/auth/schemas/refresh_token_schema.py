# features/auth/schemas/refresh_token_schema.py

from pydantic import BaseModel
from datetime import datetime

class RefreshTokenResponse(BaseModel):
    user_id: str
    revoked: bool
    expires_at: datetime

    model_config = {"from_attributes": True}