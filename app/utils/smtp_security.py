# app/utils/smtp_security.py
import os
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status
import logging
from app.config import SMTP_SECRET_KEY

logger = logging.getLogger(__name__)

# Retrieve key from environment variable
SECRET_KEY = SMTP_SECRET_KEY

if not SECRET_KEY:
    # Fallback key generated for dev mode
    SECRET_KEY = Fernet.generate_key().decode()
    print("\n" + "=" * 60)
    print("⚠️  WARNING: SMTP_SECRET_KEY not found in .env!")
    print(f"Generated Temporary Dev Key: {SECRET_KEY}")
    print("Add this line to your .env file to persist encrypted passwords across restarts:")
    print(f"SMTP_SECRET_KEY={SECRET_KEY}")
    print("=" * 60 + "\n")
else:
    print(f"🔒 SMTP Security initialized with SECRET_KEY: {SECRET_KEY}")

# Ensure key is bytes for Fernet initialization
cipher = Fernet(SECRET_KEY.encode() if isinstance(SECRET_KEY, str) else SECRET_KEY)


def encrypt_smtp_password(password: str) -> str:
    """Encrypts clear-text password before saving to DB."""
    return cipher.encrypt(password.encode()).decode()


def decrypt_smtp_password(encrypted_password: str) -> str:
    """
    Decrypts password retrieved from DB to use in SMTP connection.
    Catches key mismatches and raises a clean 400 error.
    """
    try:
        return cipher.decrypt(encrypted_password.encode()).decode()
    except InvalidToken as e:
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to decrypt SMTP password. The encryption key has changed or is invalid. Please re-save your SMTP credentials."
        )