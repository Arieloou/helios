# core/security.py

import hashlib

from jose import JWTError, jwt
from datetime import datetime, timezone
from app.core.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": True}
        )
        return payload
    except JWTError:
        raise ValueError("Token inválido o expirado")
    except Exception as e:
        raise ValueError(f"Error al decodificar token: {str(e)}")