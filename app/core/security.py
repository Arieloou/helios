from jose import JWTError, jwt
from datetime import datetime, timezone
from app.core.config import settings

ALGORITHM = "HS256"

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload
    except JWTError:
        raise ValueError("Token inválido o expirado")