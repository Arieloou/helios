"""
Encryption Middleware for SQLAlchemy ORM.
Hooks into SQLAlchemy events to transparently encrypt/decrypt
sensitive model fields using the EncryptionService (gRPC).

Models declare encrypted fields via __encrypted_fields__ class attribute.
"""

import hashlib
import logging

from flask import current_app
from sqlalchemy import event

logger = logging.getLogger(__name__)

# Instance-level flag name to track decryption state
_DECRYPTED_FLAG = "_encryption_middleware_decrypted"


def _get_encryption_client():
    """Retrieve the encryption client from the Flask app context."""
    try:
        return current_app.extensions.get("encryption")
    except RuntimeError:
        # Outside of app context (e.g., during migration)
        return None


def compute_lookup_hash(value: str) -> str:
    """Compute a deterministic SHA-256 hash for encrypted field lookups."""
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def encrypt_field(value: str) -> str:
    """Encrypt a single field value via the EncryptionService."""
    if not value:
        return value
    client = _get_encryption_client()
    if client is None:
        logger.warning("Encryption client unavailable, storing plaintext")
        return value
    return client.encrypt(value)


def decrypt_field(value: str) -> str:
    """Decrypt a single field value via the EncryptionService."""
    if not value:
        return value
    client = _get_encryption_client()
    if client is None:
        logger.warning("Encryption client unavailable, returning raw value")
        return value
    try:
        return client.decrypt(value)
    except (ValueError, ConnectionError) as e:
        logger.error(f"Failed to decrypt field: {e}")
        return value


def _decrypt_fields(target, context):
    """
    After load: decrypt all declared sensitive fields.
    Uses a per-instance flag instead of a global set to avoid
    Python id() memory address reuse bugs.
    """
    # Check per-instance flag to avoid double decryption
    if getattr(target, _DECRYPTED_FLAG, False):
        return

    encrypted_fields = getattr(target.__class__, "__encrypted_fields__", [])
    if not encrypted_fields:
        return

    for field_name in encrypted_fields:
        value = getattr(target, field_name, None)
        if value:
            decrypted_value = decrypt_field(value)
            # Use __dict__ to bypass SQLAlchemy change tracking
            target.__dict__[field_name] = decrypted_value

    # Mark this specific instance as decrypted
    target.__dict__[_DECRYPTED_FLAG] = True


def _on_before_insert_or_update(mapper, connection, target):
    """Encrypt sensitive fields before persisting to DB."""
    encrypted_fields = getattr(target.__class__, "__encrypted_fields__", [])
    if not encrypted_fields:
        return

    # Store original plaintext values for hash computation and post-write restore
    plaintext_values = {}
    for field_name in encrypted_fields:
        plaintext_values[field_name] = getattr(target, field_name, None)

    # Encrypt each field for DB storage
    for field_name in encrypted_fields:
        value = plaintext_values[field_name]
        if value:
            setattr(target, field_name, encrypt_field(value))

    # Compute lookup hashes from original plaintext
    hash_fields = getattr(target.__class__, "__hash_fields__", {})
    for source_field, hash_column in hash_fields.items():
        plaintext = plaintext_values.get(source_field)
        if plaintext:
            setattr(target, hash_column, compute_lookup_hash(plaintext))

    # Store plaintext for post-flush restore (avoid encrypted values in memory)
    target.__dict__["_plaintext_backup"] = plaintext_values
    # Clear decrypted flag since values are now encrypted
    target.__dict__[_DECRYPTED_FLAG] = False


def _on_after_insert_or_update(mapper, connection, target):
    """
    After insert/update: restore plaintext values to the in-memory object.
    Without this, the object would hold encrypted values after a commit,
    causing templates to render ciphertext.
    """
    plaintext_backup = target.__dict__.pop("_plaintext_backup", None)
    if not plaintext_backup:
        return

    for field_name, plaintext in plaintext_backup.items():
        if plaintext:
            target.__dict__[field_name] = plaintext

    # Mark as decrypted since we restored plaintext
    target.__dict__[_DECRYPTED_FLAG] = True


def register_encryption_events(app, db):
    """
    Register SQLAlchemy event listeners for all models
    that declare __encrypted_fields__.
    Must be called after db.init_app(app).
    """
    with app.app_context():
        # Iterate over all mapped models and register events
        for mapper in db.Model.registry.mappers:
            model_class = mapper.class_
            encrypted_fields = getattr(model_class, "__encrypted_fields__", None)

            if encrypted_fields:
                # Encrypt before writing to DB
                event.listen(
                    model_class, "before_insert",
                    _on_before_insert_or_update
                )
                event.listen(
                    model_class, "before_update",
                    _on_before_insert_or_update
                )
                # Restore plaintext after writing to DB
                event.listen(
                    model_class, "after_insert",
                    _on_after_insert_or_update
                )
                event.listen(
                    model_class, "after_update",
                    _on_after_insert_or_update
                )
                # Decrypt after loading from DB
                event.listen(
                    model_class, "load",
                    _decrypt_fields
                )
