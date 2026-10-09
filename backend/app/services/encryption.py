"""Encryption service — AES-256-GCM with Argon2id key derivation.

This module is intentionally kept free of FastAPI, database, or other
application-layer imports so it can be unit-tested in total isolation.

Blob format (stored in DB columns):
    base64( nonce[12] || aesgcm_output[ciphertext+tag] )

Key derivation:
    Argon2id(password, salt, time_cost=2, memory_cost=65536, parallelism=2, hash_len=32)
    -> 32-byte AES-256 key

The derived key exists **only in memory** for the lifetime of a request or
the session key cache entry.  It is never written to disk, logged, or
serialised into a JWT.
"""

import os
import base64

from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_NONCE_LEN = 12          # AES-GCM recommended nonce size
_SALT_LEN  = 16          # Argon2 salt size
_KEY_LEN   = 32          # AES-256 key size (bytes)
_TAG_LEN   = 16          # GCM authentication tag size

# Argon2id parameters — OWASP recommended minimum
_TIME_COST   = 2
_MEMORY_COST = 65536     # 64 MiB
_PARALLELISM = 2


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class EncryptionService:
    """Stateless encryption / decryption utilities."""

    # ------------------------------------------------------------------
    # Key material helpers
    # ------------------------------------------------------------------

    @staticmethod
    def generate_salt() -> bytes:
        """Return 16 cryptographically random bytes to use as an Argon2 salt."""
        return os.urandom(_SALT_LEN)

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derive a 32-byte AES-256 key from *password* and *salt* using Argon2id.

        Args:
            password: User's plaintext password (UTF-8 string).
            salt:     16-byte per-user random salt (stored in DB).

        Returns:
            32-byte key suitable for AES-256-GCM.
        """
        return hash_secret_raw(
            secret=password.encode("utf-8"),
            salt=salt,
            time_cost=_TIME_COST,
            memory_cost=_MEMORY_COST,
            parallelism=_PARALLELISM,
            hash_len=_KEY_LEN,
            type=Type.ID,
        )

    # ------------------------------------------------------------------
    # Encryption / decryption
    # ------------------------------------------------------------------

    @staticmethod
    def encrypt(plaintext: str, key: bytes) -> str:
        """Encrypt *plaintext* with AES-256-GCM.

        Args:
            plaintext: UTF-8 string to encrypt (e.g. a base64 image string).
            key:       32-byte AES-256 key produced by :meth:`derive_key`.

        Returns:
            URL-safe base64 string encoding ``nonce[12] || aesgcm_ciphertext_with_tag``.
        """
        nonce = os.urandom(_NONCE_LEN)
        aesgcm = AESGCM(key)
        # AESGCM.encrypt returns ciphertext || tag (tag appended at the end)
        ct_with_tag = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        blob = nonce + ct_with_tag
        return base64.b64encode(blob).decode("ascii")

    @staticmethod
    def decrypt(ciphertext_b64: str, key: bytes) -> str:
        """Decrypt a blob produced by :meth:`encrypt`.

        Args:
            ciphertext_b64: base64 blob from the DB column.
            key:            32-byte AES-256 key produced by :meth:`derive_key`.

        Returns:
            Original plaintext UTF-8 string.

        Raises:
            ValueError: If the blob is malformed or the GCM tag is invalid
                        (i.e. wrong key or tampered ciphertext).
        """
        try:
            blob = base64.b64decode(ciphertext_b64)
        except Exception as exc:
            raise ValueError(f"Invalid base64 in encrypted blob: {exc}") from exc

        if len(blob) < _NONCE_LEN + _TAG_LEN:
            raise ValueError(
                f"Encrypted blob too short ({len(blob)} bytes); "
                "expected at least nonce + tag bytes."
            )

        nonce = blob[:_NONCE_LEN]
        ct_with_tag = blob[_NONCE_LEN:]

        aesgcm = AESGCM(key)
        try:
            plaintext_bytes = aesgcm.decrypt(nonce, ct_with_tag, None)
        except Exception as exc:
            # cryptography raises InvalidTag; normalise to ValueError
            raise ValueError(
                "Decryption failed — wrong key or tampered ciphertext."
            ) from exc

        return plaintext_bytes.decode("utf-8")


# ---------------------------------------------------------------------------
# Module-level singleton for convenience imports
# ---------------------------------------------------------------------------

encryption_service = EncryptionService()
