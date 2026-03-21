"""
Utilitarios de seguranca: hash de senha (bcrypt), JWT e cookies de sessao.
"""
import os
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_SECRET_KEY = "marketingai-secret-key-alterar-em-producao"
SECRET_KEY = os.environ.get("SECRET_KEY", DEFAULT_SECRET_KEY)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))
ACCESS_COOKIE_NAME = os.environ.get("ACCESS_COOKIE_NAME", "marketingai_access_token")
REFRESH_COOKIE_NAME = os.environ.get("REFRESH_COOKIE_NAME", "marketingai_refresh_token")
COOKIE_DOMAIN = os.environ.get("COOKIE_DOMAIN") or None
COOKIE_PATH = os.environ.get("COOKIE_PATH", "/")
COOKIE_SAMESITE = os.environ.get("COOKIE_SAMESITE", "lax")
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "false").strip().lower() in ("1", "true", "yes")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
