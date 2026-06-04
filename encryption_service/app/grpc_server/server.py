"""
Servidor gRPC asíncrono para el servicio de cifrado.

Arranca un servidor gRPC en el puerto configurado y registra
el EncryptionServiceServicer.
"""

import grpc
from concurrent import futures

from app.proto import encryption_pb2
from app.grpc_server.servicer import EncryptionServiceServicer
from app.crypto.aes_cipher import AESCipher

# gRPC service name as defined in encryption.proto
_SERVICE_NAME = "encryption.EncryptionService"


class GRPCServer:
    """Gestiona el ciclo de vida del servidor gRPC."""

    def __init__(self, port: int, cipher: AESCipher, max_workers: int = 10):
        """
        Configura el servidor gRPC.

        Args:
            port: Puerto TCP en el que escuchará el servidor.
            cipher: Instancia de AESCipher para las operaciones de cifrado.
            max_workers: Número máximo de threads para atender peticiones.
        """
        self._port = port
        self._cipher = cipher
        self._max_workers = max_workers
        self._server = None

    def _build_method_handlers(self, servicer: EncryptionServiceServicer) -> dict:
        """
        Construye el diccionario de handlers RPC usando la API estable de grpcio.
        Evita grpc.method_service_handler que no existe en la API pública.

        Args:
            servicer: Instancia del servicer con la lógica de cifrado.

        Returns:
            Dict con los handlers de cada método RPC.
        """
        return {
            "Encrypt": grpc.unary_unary_rpc_method_handler(
                servicer.Encrypt,
                request_deserializer=encryption_pb2.EncryptRequest.FromString,
                response_serializer=encryption_pb2.EncryptResponse.SerializeToString,
            ),
            "Decrypt": grpc.unary_unary_rpc_method_handler(
                servicer.Decrypt,
                request_deserializer=encryption_pb2.DecryptRequest.FromString,
                response_serializer=encryption_pb2.DecryptResponse.SerializeToString,
            ),
        }

    def start(self):
        """Arranca el servidor gRPC de forma síncrona (bloqueante para threads)."""
        self._server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=self._max_workers)
        )

        # Construir y registrar handlers directamente (API estable grpcio 1.51+)
        servicer = EncryptionServiceServicer(self._cipher)
        method_handlers = self._build_method_handlers(servicer)
        self._server.add_registered_method_handlers(_SERVICE_NAME, method_handlers)

        # Escuchar en el puerto configurado
        listen_addr = f"0.0.0.0:{self._port}"
        self._server.add_insecure_port(listen_addr)
        self._server.start()

        print(f"[gRPC] Servidor de cifrado escuchando en puerto {self._port}")

        return self._server

    def stop(self, grace: int = 5):
        """
        Detiene el servidor gRPC de forma limpia.

        Args:
            grace: Segundos de gracia para terminar peticiones en curso.
        """
        if self._server:
            self._server.stop(grace)
            print(f"[gRPC] Servidor detenido.")

    def wait_for_termination(self):
        """Bloquea hasta que el servidor se detenga."""
        if self._server:
            self._server.wait_for_termination()
