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

# Track already-decrypted instances to avoid double decryption
_decrypted_instances = set()


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


def _encrypt_fields(mapper, connection, target):
    """Before insert/update: encrypt all declared sensitive fields."""
    encrypted_fields = getattr(target.__class__, "__encrypted_fields__", [])
    if not encrypted_fields:
        return

    for field_name in encrypted_fields:
        value = getattr(target, field_name, None)
        if value:
            encrypted_value = encrypt_field(value)
            setattr(target, field_name, encrypted_value)

    # Update lookup hash columns if they exist (e.g., username_hash)
    hash_fields = getattr(target.__class__, "__hash_fields__", {})
    for source_field, hash_column in hash_fields.items():
        # We need the original plaintext to compute the hash
        # Since we just encrypted, we need to decrypt to get it back
        encrypted_val = getattr(target, source_field, None)
        if encrypted_val:
            plaintext = decrypt_field(encrypted_val)
            setattr(target, hash_column, compute_lookup_hash(plaintext))

    # Remove from decrypted tracking since values are now encrypted
    instance_key = id(target)
    _decrypted_instances.discard(instance_key)


def _decrypt_fields(target, context):
    """After load: decrypt all declared sensitive fields."""
    instance_key = id(target)
    if instance_key in _decrypted_instances:
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

    _decrypted_instances.add(instance_key)


def _on_before_insert_or_update(mapper, connection, target):
    """Encrypt sensitive fields before persisting to DB."""
    encrypted_fields = getattr(target.__class__, "__encrypted_fields__", [])
    if not encrypted_fields:
        return

    # Store original plaintext values for hash computation
    plaintext_values = {}
    hash_fields = getattr(target.__class__, "__hash_fields__", {})
    for source_field in hash_fields:
        plaintext_values[source_field] = getattr(target, source_field, None)

    # Encrypt each field
    for field_name in encrypted_fields:
        value = getattr(target, field_name, None)
        if value:
            setattr(target, field_name, encrypt_field(value))

    # Compute lookup hashes from original plaintext
    for source_field, hash_column in hash_fields.items():
        plaintext = plaintext_values.get(source_field)
        if plaintext:
            setattr(target, hash_column, compute_lookup_hash(plaintext))

    # Mark as not decrypted since we just encrypted
    _decrypted_instances.discard(id(target))


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
                # Register encrypt on insert
                event.listen(
                    model_class, "before_insert",
                    _on_before_insert_or_update
                )
                # Register encrypt on update
                event.listen(
                    model_class, "before_update",
                    _on_before_insert_or_update
                )
                # Register decrypt on load
                event.listen(
                    model_class, "load",
                    _decrypt_fields
                )
