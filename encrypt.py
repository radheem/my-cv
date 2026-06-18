"""Build-time AES-GCM sealing for gated content.

Mirrors the browser's Web Crypto: PBKDF2-SHA256 (key derivation) + AES-256-GCM.
A sealed blob is base64( iv[12] || ciphertext||tag ) so vault.js can split the
iv off the front and hand the rest to SubtleCrypto.decrypt (which expects the
GCM tag appended to the ciphertext).
"""

from __future__ import annotations

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PBKDF2_ITERATIONS = 200_000
SALT_BYTES = 16
IV_BYTES = 12
KEY_BYTES = 32  # AES-256


def new_salt() -> bytes:
    return os.urandom(SALT_BYTES)


def derive_key(password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, dklen=KEY_BYTES
    )


def seal(plaintext: bytes, key: bytes) -> str:
    """Encrypt and return base64( iv || ciphertext||tag )."""
    iv = os.urandom(IV_BYTES)
    ct = AESGCM(key).encrypt(iv, plaintext, None)
    return base64.b64encode(iv + ct).decode("ascii")


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")
