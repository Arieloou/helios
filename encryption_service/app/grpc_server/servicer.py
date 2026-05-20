"""
Implementación del servicer gRPC para el servicio de cifrado.

Esta clase implementa los métodos RPC definidos en encryption.proto,
delegando la lógica de cifrado/descifrado a AESCipher.
"""

from app.proto import encryption_pb2
from app.proto import encryption_pb2_grpc
from app.crypto.aes_cipher import AESCipher


class EncryptionServiceServicer(encryption_pb2_grpc.EncryptionServiceServicer):
    """Implementación concreta del servicio gRPC de cifrado."""

    def __init__(self, cipher: AESCipher):
        """
        Inicializa el servicer con una instancia de AESCipher.

        Args:
            cipher: Instancia de AESCipher configurada con la clave maestra.
        """
        self._cipher = cipher

    def Encrypt(self, request, context):
        """
        Cifra el texto plano recibido.

        Args:
            request: EncryptRequest con el campo 'plaintext'.
            context: Contexto gRPC de la llamada.

        Returns:
            EncryptResponse con el texto cifrado en Base64.
        """
        try:
            if not request.plaintext:
                return encryption_pb2.EncryptResponse(
                    ciphertext="",
                    success=False,
                    message="Error: el texto plano no puede estar vacío.",
                )

            ciphertext = self._cipher.encrypt(request.plaintext)

            return encryption_pb2.EncryptResponse(
                ciphertext=ciphertext,
                success=True,
                message="Cifrado exitoso.",
            )

        except Exception as e:
            return encryption_pb2.EncryptResponse(
                ciphertext="",
                success=False,
                message=f"Error durante el cifrado: {str(e)}",
            )

    def Decrypt(self, request, context):
        """
        Descifra el texto cifrado recibido.

        Args:
            request: DecryptRequest con el campo 'ciphertext' (Base64).
            context: Contexto gRPC de la llamada.

        Returns:
            DecryptResponse con el texto plano descifrado.
        """
        try:
            if not request.ciphertext:
                return encryption_pb2.DecryptResponse(
                    plaintext="",
                    success=False,
                    message="Error: el texto cifrado no puede estar vacío.",
                )

            plaintext = self._cipher.decrypt(request.ciphertext)

            return encryption_pb2.DecryptResponse(
                plaintext=plaintext,
                success=True,
                message="Descifrado exitoso.",
            )

        except ValueError as e:
            return encryption_pb2.DecryptResponse(
                plaintext="",
                success=False,
                message=f"Error de descifrado: {str(e)}",
            )

        except Exception as e:
            return encryption_pb2.DecryptResponse(
                plaintext="",
                success=False,
                message=f"Error inesperado durante el descifrado: {str(e)}",
            )
