"""
Configuración del servicio de cifrado.
Carga variables de entorno desde .env usando pydantic_settings.
"""

import os
import secrets
import base64
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración central del encryption_service."""

    # Clave de cifrado AES-256 en formato hexadecimal (64 caracteres hex = 32 bytes).
    # Si no se proporciona, se genera una automáticamente al arrancar.
    ENCRYPTION_KEY: str = ""

    # Puerto del servidor gRPC
    GRPC_PORT: int = 50051

    # Puerto de la API REST (FastAPI / health check)
    API_PORT: int = 8000

    model_config = {
        "env_file": os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def get_key_bytes(self) -> bytes:
        """
        Devuelve la clave de cifrado como bytes (32 bytes para AES-256).
        Si no se configuró una clave, genera una automáticamente.
        """
        if not self.ENCRYPTION_KEY:
            key = secrets.token_bytes(32)
            self.ENCRYPTION_KEY = key.hex()
            print(f"[AVISO] No se encontró ENCRYPTION_KEY en .env")
            print(f"[CLAVE GENERADA] {self.ENCRYPTION_KEY}")
            print(f"[TIP] Agrega esta línea a tu archivo .env para persistir la clave:")
            print(f'ENCRYPTION_KEY={self.ENCRYPTION_KEY}')
            return key

        # Intentar decodificar como hexadecimal
        try:
            key_bytes = bytes.fromhex(self.ENCRYPTION_KEY)
            if len(key_bytes) == 32:
                return key_bytes
        except ValueError:
            pass

        # Intentar decodificar como Base64
        try:
            key_bytes = base64.b64decode(self.ENCRYPTION_KEY)
            if len(key_bytes) == 32:
                return key_bytes
        except Exception:
            pass

        raise ValueError(
            f"ENCRYPTION_KEY inválida. Debe ser 32 bytes codificados en hex (64 caracteres) "
            f"o en base64 (44 caracteres). Valor actual tiene {len(self.ENCRYPTION_KEY)} caracteres."
        )


# Instancia global de configuración
settings = Settings()
