"""
Punto de entrada de la aplicación Flask de Helios app_core.
Ejecutar desde el directorio app_core/app:
    & "../.venv/Scripts/python.exe" run.py

O desde app_core:
    & ".venv/Scripts/python.exe" -m app.run
"""

from flask import Flask

from app.config import settings
from app.extensions import encryption_ext


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["ENCRYPTION_SERVICE_HOST"] = settings.ENCRYPTION_SERVICE_HOST
    app.config["ENCRYPTION_SERVICE_PORT"] = settings.ENCRYPTION_SERVICE_PORT

    encryption_ext.init_app(app)

    from app.controllers.authcontroller import auth_bp
    from app.controllers.assetcontroller import asset_bp
    from app.controllers.assessment_controller import assessment_bp
    from app.controllers.risk_controller import risk_bp
    from app.controllers.iso_controller import iso_bp
    from app.controllers.ai_controller import ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(asset_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(iso_bp)
    app.register_blueprint(ai_bp)

    @app.errorhandler(ConnectionError)
    def handle_encryption_unavailable(error):
        from flask import jsonify
        return jsonify({
            "error": "Servicio de cifrado no disponible",
            "detail": str(error),
        }), 503

    return app


if __name__ == "__main__":
    app = create_app()
    print(f"[app_core] Iniciando en http://127.0.0.1:{settings.FLASK_PORT}")
    app.run(
        host="127.0.0.1",
        port=settings.FLASK_PORT,
        debug=settings.FLASK_DEBUG,
    )
