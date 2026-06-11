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
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = settings.SQL_ECHO


def _init_extensions(app: Flask):
    from flask_migrate import Migrate
    from .database import db

    encryption_ext.init_app(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    app.logger.info("Database and migrations initialized")


def _register_blueprints(app: Flask):
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


def _register_error_handlers(app: Flask):
    @app.errorhandler(ConnectionError)
    def handle_encryption_unavailable(error):
        from flask import jsonify

        return jsonify({
            "error": "Servicio de cifrado no disponible",
            "detail": str(error),
        }), 503
