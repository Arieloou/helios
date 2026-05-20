"""
White-box tests for Settings (app/config.py).

Covers:
- Key loading from hex / base64
- Auto-generation when key is absent
- Rejection of invalid key formats and sizes
"""

import os
import base64
import pytest
from unittest.mock import patch

from app.config import Settings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_settings(key_value: str) -> Settings:
    """Instantiates Settings overriding ENCRYPTION_KEY without .env side-effects."""
    with patch.dict(os.environ, {"ENCRYPTION_KEY": key_value}, clear=False):
        return Settings(ENCRYPTION_KEY=key_value)


# ---------------------------------------------------------------------------
# Hex key loading
# ---------------------------------------------------------------------------

class TestHexKeyLoading:
    """get_key_bytes() must decode a 64-char hex string into 32 bytes."""

    def test_valid_hex_key_returns_32_bytes(self):
        settings = _make_settings("a" * 64)
        key = settings.get_key_bytes()
        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_hex_key_content_is_correct(self):
        """The decoded bytes must match the expected value."""
        settings = _make_settings("ff" * 32)   # 32 bytes all 0xFF
        assert settings.get_key_bytes() == b"\xff" * 32

    def test_hex_key_case_insensitive(self):
        """Hex decoding should handle uppercase letters."""
        settings_lower = _make_settings("ab" * 32)
        settings_upper = _make_settings("AB" * 32)
        assert settings_lower.get_key_bytes() == settings_upper.get_key_bytes()


# ---------------------------------------------------------------------------
# Base64 key loading
# ---------------------------------------------------------------------------

class TestBase64KeyLoading:
    """get_key_bytes() must decode a base64-encoded 32-byte key."""

    def test_valid_base64_key_returns_32_bytes(self):
        raw_key = b"\x01" * 32
        b64_key = base64.b64encode(raw_key).decode()
        settings = _make_settings(b64_key)
        assert settings.get_key_bytes() == raw_key

    def test_base64_key_content_is_correct(self):
        raw_key = bytes(range(32))           # 0x00..0x1F
        b64_key = base64.b64encode(raw_key).decode()
        settings = _make_settings(b64_key)
        assert settings.get_key_bytes() == raw_key


# ---------------------------------------------------------------------------
# Auto-generation when key is absent
# ---------------------------------------------------------------------------

class TestKeyAutoGeneration:
    """When ENCRYPTION_KEY is empty, a random 32-byte key is generated."""

    def test_empty_key_generates_32_bytes(self):
        settings = _make_settings("")
        key = settings.get_key_bytes()
        assert len(key) == 32

    def test_auto_generated_keys_are_random(self):
        """Two auto-generated keys must differ (no hardcoded fallback)."""
        settings_a = _make_settings("")
        settings_b = _make_settings("")
        assert settings_a.get_key_bytes() != settings_b.get_key_bytes()

    def test_auto_generated_key_stores_hex_in_settings(self, capsys):
        """After auto-generation, ENCRYPTION_KEY is updated and printed."""
        settings = _make_settings("")
        settings.get_key_bytes()
        # The generated key must be a valid 64-char hex string
        assert len(settings.ENCRYPTION_KEY) == 64
        assert all(c in "0123456789abcdef" for c in settings.ENCRYPTION_KEY)


# ---------------------------------------------------------------------------
# Invalid key rejection
# ---------------------------------------------------------------------------

class TestInvalidKeyRejection:
    """get_key_bytes() must raise ValueError for keys with wrong size."""

    def test_hex_key_too_short_raises(self):
        """A 16-byte hex key (32 hex chars) must be rejected."""
        with pytest.raises(ValueError):
            _make_settings("a" * 32).get_key_bytes()   # 32 hex chars = 16 bytes

    def test_hex_key_too_long_raises(self):
        """A 64-byte hex key (128 hex chars) must be rejected."""
        with pytest.raises(ValueError):
            _make_settings("a" * 128).get_key_bytes()  # 128 hex chars = 64 bytes

    def test_non_hex_non_base64_raises(self):
        """Garbage strings that are neither valid hex nor base64 must raise."""
        with pytest.raises(ValueError):
            _make_settings("this_is_not_a_valid_key_at_all!!").get_key_bytes()


# ---------------------------------------------------------------------------
# Default port values
# ---------------------------------------------------------------------------

class TestDefaultPorts:
    """Verify default port assignments defined in Settings."""

    def test_default_grpc_port(self):
        settings = _make_settings("a" * 64)
        assert settings.GRPC_PORT == 50051

    def test_default_api_port(self):
        settings = _make_settings("a" * 64)
        assert settings.API_PORT == 8000
