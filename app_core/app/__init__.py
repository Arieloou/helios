"""
Application Factory de Helios app_core.
Configura la aplicación Flask, inicializa extensiones y
registra los blueprints.
"""

import logging

from flask import Flask

from .config import settings
from .extensions import encryption_ext
from .database import db
from flask_wtf.csrf import CSRFProtect


def create_app() -> Flask:
    app = Flask(__name__)
    csrf = CSRFProtect()
    csrf.init_app(app)

    _setup_logging(app)
    _load_config(app)
    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_root_redirect(app)

    return app


def _setup_logging(app: Flask) -> None:
    log_level = logging.DEBUG if settings.FLASK_DEBUG else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    app.logger.setLevel(log_level)
    app.logger.info("Helios application starting...")


def _load_config(app: Flask) -> None:
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.FLASK_DEBUG
    app.config["ENCRYPTION_SERVICE_HOST"] = settings.ENCRYPTION_SERVICE_HOST
    app.config["ENCRYPTION_SERVICE_PORT"] = settings.ENCRYPTION_SERVICE_PORT
    db_uri = "postgresql://" + settings.DB_USER + ":" + settings.DB_PASSWORD + "@" + settings.DB_HOST + ":" + settings.DB_PORT + "/" + settings.DB_NAME
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = settings.SQL_ECHO


def _init_extensions(app: Flask) -> None:
    from flask_migrate import Migrate
    from .services.encryption_middleware import register_encryption_events

    # Encryption middleware configuration
    try:
        encryption_ext.init_app(app)
        app.logger.info("Encryption middleware initialized")
    except Exception as e:
        app.logger.error(f"Failed to initialize encryption middleware: {e}")
    
    # Database configuration
    try:
        db.init_app(app)
        app.logger.info("Database initialized")
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {e}")
    
    # Migrations configuration
    try:
        migrate = Migrate(app, db)
        migrate.init_app(app, db, compare_type=True)
        app.logger.info("Migrations initialized")
    except Exception as e:
        app.logger.error(f"Failed to initialize migrations: {e}")

    # Register encrypt/decrypt event listeners for models with __encrypted_fields__
    try:
        register_encryption_events(app, db)
        app.logger.info("Encryption events middleware registered")
    except Exception as e:
        app.logger.error(f"Failed to register encryption events middleware: {e}")
    
    app.logger.info("All extensions initialized")


def _register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from .controllers.authcontroller import auth_bp
    from .controllers.assetcontroller import asset_bp
    from .controllers.assessment_controller import assessment_bp
    from .controllers.risk_controller import risk_bp
    from .controllers.iso_controller import iso_bp
    from .controllers.ai_controller import ai_bp
    from .controllers.treatment_controller import treatment_bp
    from .controllers.dashboard_controller import dashboard_bp
    from .controllers.user_controller import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(asset_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(iso_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(treatment_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(user_bp)

    app.logger.debug("All blueprints registered")


def _register_error_handlers(app: Flask) -> None:
    from flask import jsonify

    @app.errorhandler(ConnectionError)
    def handle_encryption_unavailable(error):
        app.logger.error(f"Encryption service unavailable: {error}")
        return jsonify({
            "error": "Servicio de cifrado no disponible",
            "detail": str(error),
        }), 503

    @app.errorhandler(404)
    def handle_not_found(error):
        app.logger.warning(f"Resource not found: {error}")
        return jsonify({
            "error": "Recurso no encontrado",
            "detail": str(error),
        }), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.error(f"Internal server error: {error}")
        return jsonify({
            "error": "Error interno del servidor",
            "detail": "Ha ocurrido un error inesperado",
        }), 500

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        app.logger.warning(f"Invalid value: {error}")
        return jsonify({
            "error": "Valor inválido",
            "detail": str(error),
        }), 400

    @app.errorhandler(Exception)
    def handle_unhandled_exception(error):
        app.logger.error(f"Unhandled exception: {error}", exc_info=True)
        return jsonify({
            "error": "Error inesperado",
            "detail": "Ha ocurrido un error inesperado",
        }), 500


def _register_root_redirect(app: Flask):
    from flask import redirect, url_for

    @app.route("/")
    def index():
        app.logger.debug("Redirecting root to auth.login")
        return redirect(url_for("auth.dashboard"))
