import os
import base64
import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Master salt and key derivation for encryption at rest
_ENCRYPTION_SALT = b"ai_job_assistant_encryption_salt_2026_v1"
_SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("APP_ENCRYPTION_KEY", "ai-job-assistant-secure-master-encryption-key-2026"))

# Derive a 32-byte URL-safe base64 key for Fernet AES-128-CBC + HMAC-SHA256 authenticated encryption
_kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=_ENCRYPTION_SALT,
    iterations=100000,
)
_DERIVED_KEY = base64.urlsafe_b64encode(_kdf.derive(_SECRET_KEY.encode("utf-8")))
_fernet = Fernet(_DERIVED_KEY)

MASK_VALUE = "••••••••••••••••"

def encrypt_secret(plaintext: Optional[str]) -> Optional[str]:
    """
    Encrypts a sensitive secret string (such as Gmail App Password) for secure storage at rest.
    If already encrypted, returns as is.
    """
    if not plaintext or not plaintext.strip():
        return ""
    
    clean_text = plaintext.strip()
    # Check if already a valid Fernet token
    if clean_text.startswith("gAAAAA"):
        try:
            _fernet.decrypt(clean_text.encode("utf-8"))
            return clean_text
        except Exception:
            pass

    try:
        encrypted_bytes = _fernet.encrypt(clean_text.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return clean_text


def decrypt_secret(ciphertext: Optional[str]) -> Optional[str]:
    """
    Decrypts an encrypted secret string for in-memory use during SMTP operations.
    If the text is legacy plaintext (unencrypted), safely returns the plaintext without throwing errors.
    """
    if not ciphertext or not ciphertext.strip():
        return ""
    
    clean_text = ciphertext.strip()
    if is_masked(clean_text):
        return ""

    if clean_text.startswith("gAAAAA"):
        try:
            decrypted_bytes = _fernet.decrypt(clean_text.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except InvalidToken:
            logger.warning("Invalid encryption token when decrypting secret.")
            return clean_text
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return clean_text
            
    # Legacy unencrypted fallback
    return clean_text


def mask_secret(secret: Optional[str]) -> str:
    """
    Returns a masked representation for API responses so plaintext secrets are never leaked.
    """
    if secret and secret.strip():
        return MASK_VALUE
    return ""


def is_masked(val: Optional[str]) -> bool:
    """
    Checks if a submitted value is the mask placeholder.
    """
    if not val:
        return False
    return val.strip() == MASK_VALUE or all(c in "•*●" for c in val.strip())
