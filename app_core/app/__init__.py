"""
Application Factory de Helios app_core.
Configura la aplicación Flask, inicializa extensiones y
registra los blueprints.
"""

from flask import Flask

from .config import settings
from .extensions import encryption_ext


def create_app() -> Flask:
    app = Flask(__name__)

    _load_config(app)
    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)

    return app


def _load_config(app: Flask):
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["ENCRYPTION_SERVICE_HOST"] = settings.ENCRYPTION_SERVICE_HOST
    app.config["ENCRYPTION_SERVICE_PORT"] = settings.ENCRYPTION_SERVICE_PORT


def _init_extensions(app: Flask):
    encryption_ext.init_app(app)


def _register_blueprints(app: Flask):
    from .controllers.authcontroller import auth_bp
    from .controllers.assetcontroller import asset_bp
    from .controllers.assessment_controller import assessment_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(asset_bp)
    app.register_blueprint(assessment_bp)


def _register_error_handlers(app: Flask):
    @app.errorhandler(ConnectionError)
    def handle_encryption_unavailable(error):
        from flask import jsonify

        return jsonify({
            "error": "Servicio de cifrado no disponible",
            "detail": str(error),
        }), 503
