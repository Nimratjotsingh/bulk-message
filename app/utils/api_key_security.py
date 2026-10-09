# app/utils/api_key_security.py
import hashlib
import secrets

KEY_PREFIX = "elvaren_"

def generate_raw_api_key() -> str:
    """Generates a secure raw API key (e.g. 'bk_live_8f3d...')."""
    random_part = secrets.token_urlsafe(32)
    return f"{KEY_PREFIX}{random_part}"

def hash_api_key(raw_key: str) -> str:
    """Computes a SHA-256 hash of the raw API key for secure storage."""
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

def extract_key_prefix(raw_key: str) -> str:
    """Extracts a short prefix for identification in management UI."""
    return raw_key[:12]