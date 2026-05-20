"""
White-box tests for AESCipher (app/crypto/aes_cipher.py).

Covers:
- Happy path: encrypt / decrypt round-trip
- Internal structure: nonce uniqueness, blob layout
- All error branches: empty input, wrong key size, tampered data, bad base64
"""

import base64
import pytest

from app.crypto.aes_cipher import AESCipher


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_KEY_HEX = "a" * 64          # 32 bytes in hex — fixed key for reproducibility
VALID_KEY = bytes.fromhex(VALID_KEY_HEX)
SAMPLE_TEXT = "información confidencial del activo"


@pytest.fixture()
def cipher():
    """Returns an AESCipher instance with a deterministic test key."""
    return AESCipher(VALID_KEY)


# ---------------------------------------------------------------------------
# Happy path tests
# ---------------------------------------------------------------------------

class TestEncryptDecryptRoundtrip:
    """Verifies that encrypt → decrypt always recovers the original text."""

    def test_basic_roundtrip(self, cipher):
        """Encrypting then decrypting returns the original plaintext."""
        assert cipher.decrypt(cipher.encrypt(SAMPLE_TEXT)) == SAMPLE_TEXT

    def test_roundtrip_with_unicode(self, cipher):
        """Unicode characters (accents, Chinese, emojis) survive the round-trip."""
        texts = ["héroe", "日本語", "✅ seguridad", "contraseña_123!"]
        for text in texts:
            assert cipher.decrypt(cipher.encrypt(text)) == text, (
                f"Round-trip failed for: {text!r}"
            )

    def test_roundtrip_with_long_text(self, cipher):
        """Large payloads are handled correctly."""
        long_text = "A" * 10_000
        assert cipher.decrypt(cipher.encrypt(long_text)) == long_text

    def test_roundtrip_with_single_char(self, cipher):
        """Minimal input (1 character) is handled correctly."""
        assert cipher.decrypt(cipher.encrypt("x")) == "x"


# ---------------------------------------------------------------------------
# Internal structure tests (white-box)
# ---------------------------------------------------------------------------

class TestCiphertextStructure:
    """
    Inspects the internal binary layout of the encrypted blob.
    Format: base64( nonce[12] || ciphertext[N] || tag[16] )
    """

    def test_output_is_valid_base64(self, cipher):
        """encrypt() always returns valid Base64."""
        result = cipher.encrypt(SAMPLE_TEXT)
        # base64.b64decode raises if invalid
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_blob_minimum_length(self, cipher):
        """
        Encrypted blob must be at least NONCE_SIZE + TAG_SIZE bytes long,
        even for a 1-character input.
        """
        blob = base64.b64decode(cipher.encrypt("x"))
        nonce_size = AESCipher.NONCE_SIZE          # 12
        tag_size = 16
        assert len(blob) >= nonce_size + tag_size

    def test_blob_exact_length(self, cipher):
        """
        Total blob size = nonce(12) + plaintext_bytes(N) + GCM_tag(16).
        Verifies that no extra bytes are added.
        """
        text = "hello"
        blob = base64.b64decode(cipher.encrypt(text))
        expected = AESCipher.NONCE_SIZE + len(text.encode("utf-8")) + 16
        assert len(blob) == expected

    def test_nonce_is_unique_per_call(self, cipher):
        """
        Critical security property: each encrypt() call must use a fresh nonce.
        Reusing (key, nonce) in AES-GCM completely breaks confidentiality.
        """
        nonces = set()
        for _ in range(100):
            blob = base64.b64decode(cipher.encrypt(SAMPLE_TEXT))
            nonce = blob[:AESCipher.NONCE_SIZE]
            nonces.add(nonce)
        # All 100 nonces must be distinct
        assert len(nonces) == 100

    def test_same_plaintext_produces_different_ciphertext(self, cipher):
        """Two encryptions of the same text must produce different ciphertext."""
        ct1 = cipher.encrypt(SAMPLE_TEXT)
        ct2 = cipher.encrypt(SAMPLE_TEXT)
        assert ct1 != ct2


# ---------------------------------------------------------------------------
# Error branch tests (white-box)
# ---------------------------------------------------------------------------

class TestEncryptErrors:
    """Tests every error branch inside encrypt()."""

    def test_empty_plaintext_raises_value_error(self, cipher):
        """encrypt('') must raise ValueError (branch: empty check)."""
        with pytest.raises(ValueError, match="vacío"):
            cipher.encrypt("")

    def test_none_is_not_accepted(self, cipher):
        """None should not be silently accepted as plaintext."""
        with pytest.raises((ValueError, AttributeError, TypeError)):
            cipher.encrypt(None)  # type: ignore[arg-type]


class TestDecryptErrors:
    """Tests every error branch inside decrypt()."""

    def test_empty_ciphertext_raises_value_error(self, cipher):
        """decrypt('') must raise ValueError (branch: empty check)."""
        with pytest.raises(ValueError, match="vacío"):
            cipher.decrypt("")

    def test_invalid_base64_raises_value_error(self, cipher):
        """Invalid Base64 must raise ValueError mentioning Base64."""
        with pytest.raises(ValueError, match="Base64"):
            cipher.decrypt("@@this_is_not_base64@@")

    def test_too_short_blob_raises_value_error(self, cipher):
        """Blobs shorter than nonce+tag must raise ValueError (branch: length check)."""
        # Only 5 bytes — way below minimum (12 + 16 = 28)
        short_blob = base64.b64encode(b"short").decode()
        with pytest.raises(ValueError, match="cortos"):
            cipher.decrypt(short_blob)

    def test_tampered_ciphertext_raises_value_error(self, cipher):
        """
        Modifying even one byte of the ciphertext must fail GCM authentication.
        This tests the integrity guarantee of AES-GCM.
        """
        encrypted = cipher.encrypt(SAMPLE_TEXT)
        blob = bytearray(base64.b64decode(encrypted))
        blob[-1] ^= 0xFF        # Flip all bits in the last byte (inside the tag)
        tampered = base64.b64encode(bytes(blob)).decode()

        with pytest.raises(ValueError, match="corruptos|incorrecto|manipulado"):
            cipher.decrypt(tampered)

    def test_tampered_nonce_raises_value_error(self, cipher):
        """Modifying the nonce also fails authentication."""
        encrypted = cipher.encrypt(SAMPLE_TEXT)
        blob = bytearray(base64.b64decode(encrypted))
        blob[0] ^= 0xFF         # Flip first byte of the nonce
        tampered = base64.b64encode(bytes(blob)).decode()

        with pytest.raises(ValueError):
            cipher.decrypt(tampered)

    def test_cross_key_decryption_fails(self):
        """Ciphertext from one key cannot be decrypted with a different key."""
        key_a = AESCipher(bytes.fromhex("a" * 64))
        key_b = AESCipher(bytes.fromhex("b" * 64))

        encrypted_with_a = key_a.encrypt(SAMPLE_TEXT)

        with pytest.raises(ValueError):
            key_b.decrypt(encrypted_with_a)


# ---------------------------------------------------------------------------
# Constructor validation tests
# ---------------------------------------------------------------------------

class TestAESCipherConstructor:
    """Validates AESCipher.__init__ key size enforcement."""

    def test_valid_32_byte_key_is_accepted(self):
        """A 32-byte key must not raise."""
        cipher = AESCipher(b"\x00" * 32)
        assert cipher is not None

    def test_key_too_short_raises_value_error(self):
        """Keys shorter than 32 bytes must raise ValueError."""
        with pytest.raises(ValueError, match="32 bytes"):
            AESCipher(b"\x00" * 16)   # AES-128 key — too short for AES-256

    def test_key_too_long_raises_value_error(self):
        """Keys longer than 32 bytes must raise ValueError."""
        with pytest.raises(ValueError, match="32 bytes"):
            AESCipher(b"\x00" * 64)

    def test_empty_key_raises_value_error(self):
        """An empty key must raise ValueError."""
        with pytest.raises(ValueError, match="32 bytes"):
            AESCipher(b"")
