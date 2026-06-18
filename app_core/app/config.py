"""
Configuración central de app_core.
Carga variables de entorno desde .env usando pydantic_settings.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "helios-dev-secret-change-in-production"
    FLASK_PORT: int = 5000
    FLASK_DEBUG: bool = False
    ENCRYPTION_SERVICE_HOST: str = "localhost"
    ENCRYPTION_SERVICE_PORT: int = 50051

    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "helios"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    SQL_ECHO: bool = False

    model_config = {
        "env_file": os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
