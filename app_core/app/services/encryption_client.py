"""
Cliente gRPC para el servicio de cifrado de Helios.

Permite a app_core comunicarse con el encryption_service
para cifrar y descifrar información vía gRPC.

Uso:
    from app.services.encryption_client import EncryptionClient

    client = EncryptionClient()
    encrypted = client.encrypt("texto sensible")
    original = client.decrypt(encrypted)
"""

import grpc

from app.services.proto import encryption_pb2
from app.services.proto import encryption_pb2_grpc


class EncryptionClient:
    """
    Cliente gRPC para comunicarse con el servicio de cifrado.

    Gestiona la conexión gRPC y proporciona métodos de alto nivel
    para cifrar y descifrar texto.
    """

    def __init__(self, host: str = "localhost", port: int = 50051):
        """
        Inicializa el cliente gRPC.

        Args:
            host: Dirección del servidor gRPC del encryption_service.
            port: Puerto del servidor gRPC.
        """
        self._target = f"{host}:{port}"
        self._channel = None
        self._stub = None

    def _ensure_connection(self):
        """Establece la conexión gRPC si no existe."""
        if self._channel is None:
            self._channel = grpc.insecure_channel(self._target)
            self._stub = encryption_pb2_grpc.EncryptionServiceStub(self._channel)

    def encrypt(self, plaintext: str) -> str:
        """
        Cifra un texto plano enviándolo al servicio de cifrado.

        Args:
            plaintext: Texto plano a cifrar.

        Returns:
            Texto cifrado en Base64.

        Raises:
            ConnectionError: Si no se puede conectar al servicio.
            ValueError: Si el servicio reporta un error de cifrado.
        """
        self._ensure_connection()

        try:
            request = encryption_pb2.EncryptRequest(plaintext=plaintext)
            response = self._stub.Encrypt(request, timeout=10)

            if not response.success:
                raise ValueError(f"Error de cifrado: {response.message}")

            return response.ciphertext

        except grpc.RpcError as e:
            raise ConnectionError(
                f"No se pudo conectar al servicio de cifrado en {self._target}: "
                f"{e.code()} - {e.details()}"
            )

    def decrypt(self, ciphertext: str) -> str:
        """
        Descifra un texto cifrado enviándolo al servicio de cifrado.

        Args:
            ciphertext: Texto cifrado en Base64 (obtenido de encrypt()).

        Returns:
            Texto plano original.

        Raises:
            ConnectionError: Si no se puede conectar al servicio.
            ValueError: Si el servicio reporta un error de descifrado.
        """
        self._ensure_connection()

        try:
            request = encryption_pb2.DecryptRequest(ciphertext=ciphertext)
            response = self._stub.Decrypt(request, timeout=10)

            if not response.success:
                raise ValueError(f"Error de descifrado: {response.message}")

            return response.plaintext

        except grpc.RpcError as e:
            raise ConnectionError(
                f"No se pudo conectar al servicio de cifrado en {self._target}: "
                f"{e.code()} - {e.details()}"
            )

    def close(self):
        """Cierra la conexión gRPC."""
        if self._channel:
            self._channel.close()
            self._channel = None
            self._stub = None

    def __enter__(self):
        """Soporte para context manager (with statement)."""
        self._ensure_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del context manager."""
        self.close()
        return False

    def __del__(self):
        """Cleanup al destruir el objeto."""
        self.close()
