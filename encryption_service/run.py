"""
Script de arranque del servicio de cifrado.
Ejecutar desde el directorio encryption_service:
    & ".venv\\Scripts\\python.exe" run.py
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=settings.API_PORT,
        reload=True,
    )
