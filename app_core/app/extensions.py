"""
Extensiones de Flask para app_core.
Gestiona la inicialización del cliente gRPC de cifrado
como una extensión de la aplicación Flask.
"""

from .services.encryption_client import EncryptionClient


class EncryptionClientExtension:
    """
    Extensión de Flask que gestiona el ciclo de vida del cliente gRPC
    de cifrado. Se almacena en app.extensions["encryption"].
    """

    def __init__(self, app=None):
        self._client = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        host = app.config.get("ENCRYPTION_SERVICE_HOST", "localhost")
        port = app.config.get("ENCRYPTION_SERVICE_PORT", 50051)
        self._client = EncryptionClient(host=host, port=port)
        self._client._ensure_connection()

        if "extensions" not in app.extensions:
            app.extensions["extensions"] = {}
        app.extensions["encryption"] = self._client

        app.teardown_appcontext(self._teardown)

        print(f"[app_core] Cliente de cifrado conectado a {host}:{port}")

    def _teardown(self, exception=None):
        if self._client:
            self._client.close()

    @property
    def client(self):
        return self._client


encryption_ext = EncryptionClientExtension()
