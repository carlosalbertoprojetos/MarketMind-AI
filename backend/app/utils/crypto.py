"""
Criptografia simétrica para credenciais (usuário/senha de sites).
Usa Fernet (cryptography) com chave derivada de SECRET_KEY.
"""
import base64
import hashlib
import os

from app.utils.security import SECRET_KEY

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    Fernet = None


def _get_fernet_key() -> bytes:
    """Deriva uma chave Fernet de 32 bytes a partir de SECRET_KEY."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"marketingai_credentials",
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(SECRET_KEY.encode()))
    return key


def encrypt_credential(value: str) -> str | None:
    """Criptografa uma string (ex: senha). Retorna base64 ou None se crypto indisponível."""
    if not value or not Fernet:
        return value
    try:
        f = Fernet(_get_fernet_key())
        return f.encrypt(value.encode()).decode()
    except Exception:
        return None


def decrypt_credential(encrypted: str) -> str | None:
    """Descriptografa uma string. Retorna None se falhar ou crypto indisponível."""
    if not encrypted or not Fernet:
        return encrypted
    try:
        f = Fernet(_get_fernet_key())
        return f.decrypt(encrypted.encode()).decode()
    except Exception:
        return None
