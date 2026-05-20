"""
Módulo de cifrado AES-256-GCM.

Proporciona cifrado autenticado (authenticated encryption) con:
- AES-256 en modo GCM (Galois/Counter Mode)
- Nonce de 12 bytes generado aleatoriamente por operación
- Tag de autenticación de 16 bytes

Formato del texto cifrado (base64):
    base64( nonce[12] || tag[16] || ciphertext[N] )
"""

import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class AESCipher:
    """Cifrador AES-256-GCM para texto plano."""
    NONCE_SIZE = 12  # bytes (96 bits, recomendado para GCM)
    KEY_SIZE = 32    # bytes (256 bits)

    def __init__(self, key: bytes):
        """
        Inicializa el cifrador con una clave de 32 bytes.

        Args:
            key: Clave AES-256 de exactamente 32 bytes.

        Raises:
            ValueError: Si la clave no tiene 32 bytes.
        """
        if len(key) != self.KEY_SIZE:
            raise ValueError(
                f"La clave debe tener exactamente {self.KEY_SIZE} bytes, "
                f"pero se recibieron {len(key)} bytes."
            )
        self._aesgcm = AESGCM(key)

    def encrypt(self, plaintext: str) -> str:
        """
        Cifra un texto plano y devuelve el resultado en Base64.

        Args:
            plaintext: Texto plano a cifrar (UTF-8).

        Returns:
            String en Base64 conteniendo: nonce || tag || ciphertext.

        Raises:
            ValueError: Si el texto plano está vacío.
        """
        if not plaintext:
            raise ValueError("El texto plano no puede estar vacío.")

        # Generar nonce aleatorio único para esta operación
        nonce = os.urandom(self.NONCE_SIZE)

        # Cifrar (GCM produce ciphertext + tag concatenados)
        plaintext_bytes = plaintext.encode("utf-8")
        ciphertext_with_tag = self._aesgcm.encrypt(nonce, plaintext_bytes, None)

        # AESGCM.encrypt() devuelve ciphertext || tag (tag = últimos 16 bytes)
        # Empaquetamos como: nonce || ciphertext_with_tag
        encrypted_blob = nonce + ciphertext_with_tag

        return base64.b64encode(encrypted_blob).decode("utf-8")

    def decrypt(self, ciphertext_b64: str) -> str:
        """
        Descifra un texto cifrado en Base64.

        Args:
            ciphertext_b64: String en Base64 con formato nonce || ciphertext || tag.

        Returns:
            Texto plano original (UTF-8).

        Raises:
            ValueError: Si el formato es inválido o la autenticación falla.
        """
        if not ciphertext_b64:
            raise ValueError("El texto cifrado no puede estar vacío.")

        try:
            encrypted_blob = base64.b64decode(ciphertext_b64)
        except Exception as e:
            raise ValueError(f"Error decodificando Base64: {e}")

        if len(encrypted_blob) < self.NONCE_SIZE + 16:
            raise ValueError(
                f"Datos cifrados demasiado cortos. Se esperaban al menos "
                f"{self.NONCE_SIZE + 16} bytes, pero se recibieron {len(encrypted_blob)}."
            )

        # Extraer nonce y ciphertext_with_tag
        nonce = encrypted_blob[:self.NONCE_SIZE]
        ciphertext_with_tag = encrypted_blob[self.NONCE_SIZE:]

        try:
            plaintext_bytes = self._aesgcm.decrypt(nonce, ciphertext_with_tag, None)
        except Exception:
            raise ValueError(
                "Error de descifrado: los datos están corruptos, la clave es incorrecta, "
                "o el texto cifrado ha sido manipulado."
            )

        return plaintext_bytes.decode("utf-8")
