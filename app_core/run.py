"""
Script de arranque de Helios app_core.
Ejecutar desde el directorio app_core:
    & ".venv\Scripts\python.exe" run.py
"""

from app.run import create_app
from app.config import settings

app = create_app()

if __name__ == "__main__":
    print(f"[app_core] Iniciando en http://127.0.0.1:{settings.FLASK_PORT}")
    app.run(
        host="127.0.0.1",
        port=settings.FLASK_PORT,
        debug=settings.FLASK_DEBUG,
    )
