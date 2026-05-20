"""
White-box tests for EncryptionServiceServicer (app/grpc_server/servicer.py).

Simulates gRPC calls by invoking servicer methods directly,
using a mock context to capture gRPC status codes without running a server.
"""

import pytest
from unittest.mock import MagicMock

from app.crypto.aes_cipher import AESCipher
from app.grpc_server.servicer import EncryptionServiceServicer
from app.proto import encryption_pb2


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_KEY = bytes.fromhex("b" * 64)   # Fixed 32-byte key for tests


@pytest.fixture()
def cipher():
    return AESCipher(VALID_KEY)


@pytest.fixture()
def servicer(cipher):
    return EncryptionServiceServicer(cipher)


@pytest.fixture()
def grpc_context():
    """Mocks a gRPC ServicerContext — no real server needed."""
    return MagicMock()


# ---------------------------------------------------------------------------
# Encrypt RPC tests
# ---------------------------------------------------------------------------

class TestEncryptRPC:
    """Tests the Encrypt RPC method of the servicer."""

    def test_encrypt_returns_success_true(self, servicer, grpc_context):
        request = encryption_pb2.EncryptRequest(plaintext="texto de prueba")
        response = servicer.Encrypt(request, grpc_context)
        assert response.success is True

    def test_encrypt_returns_non_empty_ciphertext(self, servicer, grpc_context):
        request = encryption_pb2.EncryptRequest(plaintext="texto de prueba")
        response = servicer.Encrypt(request, grpc_context)
        assert len(response.ciphertext) > 0

    def test_encrypt_ciphertext_differs_from_plaintext(self, servicer, grpc_context):
        """The ciphertext must not be the plain text in disguise."""
        plaintext = "texto de prueba"
        request = encryption_pb2.EncryptRequest(plaintext=plaintext)
        response = servicer.Encrypt(request, grpc_context)
        assert response.ciphertext != plaintext

    def test_encrypt_with_empty_plaintext_returns_failure(self, servicer, grpc_context):
        """Empty plaintext must return success=False, not raise an exception."""
        request = encryption_pb2.EncryptRequest(plaintext="")
        response = servicer.Encrypt(request, grpc_context)
        assert response.success is False
        assert response.ciphertext == ""
        assert "vacío" in response.message.lower()

    def test_encrypt_failure_message_is_descriptive(self, servicer, grpc_context):
        """Error message must explain why the operation failed."""
        request = encryption_pb2.EncryptRequest(plaintext="")
        response = servicer.Encrypt(request, grpc_context)
        assert len(response.message) > 0

    def test_encrypt_success_message_is_present(self, servicer, grpc_context):
        """Success response must also include a message field."""
        request = encryption_pb2.EncryptRequest(plaintext="cualquier texto")
        response = servicer.Encrypt(request, grpc_context)
        assert len(response.message) > 0


# ---------------------------------------------------------------------------
# Decrypt RPC tests
# ---------------------------------------------------------------------------

class TestDecryptRPC:
    """Tests the Decrypt RPC method of the servicer."""

    def _encrypt(self, servicer, grpc_context, plaintext: str) -> str:
        """Helper: encrypt via RPC and return ciphertext."""
        req = encryption_pb2.EncryptRequest(plaintext=plaintext)
        return servicer.Encrypt(req, grpc_context).ciphertext

    def test_decrypt_recovers_original_plaintext(self, servicer, grpc_context):
        original = "dato sensible del sistema"
        ct = self._encrypt(servicer, grpc_context, original)
        request = encryption_pb2.DecryptRequest(ciphertext=ct)
        response = servicer.Decrypt(request, grpc_context)
        assert response.success is True
        assert response.plaintext == original

    def test_decrypt_with_empty_ciphertext_returns_failure(self, servicer, grpc_context):
        """Empty ciphertext must return success=False without crashing."""
        request = encryption_pb2.DecryptRequest(ciphertext="")
        response = servicer.Decrypt(request, grpc_context)
        assert response.success is False
        assert response.plaintext == ""

    def test_decrypt_with_invalid_base64_returns_failure(self, servicer, grpc_context):
        """Invalid Base64 must return success=False with an error message."""
        request = encryption_pb2.DecryptRequest(ciphertext="@@garbage@@")
        response = servicer.Decrypt(request, grpc_context)
        assert response.success is False
        assert response.plaintext == ""

    def test_decrypt_with_tampered_data_returns_failure(self, servicer, grpc_context):
        """Tampered ciphertext must fail GCM authentication → success=False."""
        import base64
        ct = self._encrypt(servicer, grpc_context, "datos importantes")
        blob = bytearray(base64.b64decode(ct))
        blob[-1] ^= 0xFF        # Corrupt the last byte (GCM tag)
        tampered = base64.b64encode(bytes(blob)).decode()

        request = encryption_pb2.DecryptRequest(ciphertext=tampered)
        response = servicer.Decrypt(request, grpc_context)
        assert response.success is False

    def test_decrypt_failure_message_is_not_empty(self, servicer, grpc_context):
        """Error responses must always include a descriptive message."""
        request = encryption_pb2.DecryptRequest(ciphertext="@@invalid@@")
        response = servicer.Decrypt(request, grpc_context)
        assert len(response.message) > 0

    def test_decrypt_does_not_raise_exceptions(self, servicer, grpc_context):
        """
        The servicer must NEVER propagate exceptions to gRPC.
        It must always return a DecryptResponse, even for bad input.
        """
        bad_inputs = ["", "@@bad@@", "dGVzdA==", "A" * 200]
        for bad in bad_inputs:
            request = encryption_pb2.DecryptRequest(ciphertext=bad)
            # Should not raise — must always return a response object
            response = servicer.Decrypt(request, grpc_context)
            assert isinstance(response, encryption_pb2.DecryptResponse)

    def test_encrypt_does_not_raise_exceptions(self, servicer, grpc_context):
        """
        The Encrypt method must also never propagate exceptions.
        """
        bad_inputs = ["", "   "]
        for bad in bad_inputs:
            request = encryption_pb2.EncryptRequest(plaintext=bad)
            response = servicer.Encrypt(request, grpc_context)
            assert isinstance(response, encryption_pb2.EncryptResponse)


# ---------------------------------------------------------------------------
# Round-trip integrity test (end-to-end through servicer)
# ---------------------------------------------------------------------------

class TestRoundTripThroughServicer:
    """Verifies encrypt → decrypt cycle works at the RPC layer."""

    @pytest.mark.parametrize("text", [
        "contraseña secreta",
        "user@helios.com",
        "127.0.0.1:5432",
        "A" * 500,
        "日本語テスト",
        "!@#$%^&*()_+-=[]{}|;':\",./<>?",
    ])
    def test_roundtrip_various_inputs(self, servicer, grpc_context, text):
        """Parameterized round-trip: encrypts and decrypts a variety of inputs."""
        enc_req = encryption_pb2.EncryptRequest(plaintext=text)
        enc_resp = servicer.Encrypt(enc_req, grpc_context)
        assert enc_resp.success is True, f"Encrypt failed for: {text!r}"

        dec_req = encryption_pb2.DecryptRequest(ciphertext=enc_resp.ciphertext)
        dec_resp = servicer.Decrypt(dec_req, grpc_context)
        assert dec_resp.success is True, f"Decrypt failed for: {text!r}"
        assert dec_resp.plaintext == text
