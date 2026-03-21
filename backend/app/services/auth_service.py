"""
Servico de autenticacao: login, tokens JWT e validacao de sessao.
"""
from datetime import timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserLogin
from app.utils.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_access_token,
    verify_password,
)


def authenticate_user(db: Session, login: UserLogin) -> User | None:
    user = db.query(User).filter(User.email == login.email).first()
    if not user or not verify_password(login.password, user.password_hash):
        return None
    return user


def _create_token_for_user(user: User, *, token_type: str, expires_minutes: int) -> str:
    expires = timedelta(minutes=expires_minutes)
    return create_access_token(
        data={"sub": user.email, "user_id": user.id, "type": token_type, "jti": uuid4().hex},
        expires_delta=expires,
    )


def create_token_for_user(user: User, expires_minutes: int | None = None) -> str:
    return _create_token_for_user(
        user,
        token_type="access",
        expires_minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def create_refresh_token_for_user(user: User, expires_minutes: int | None = None) -> str:
    return _create_token_for_user(
        user,
        token_type="refresh",
        expires_minutes=expires_minutes or REFRESH_TOKEN_EXPIRE_MINUTES,
    )


def get_user_from_token(db: Session, token: str, expected_type: str = "access") -> User | None:
    payload = decode_access_token(token)
    if not payload:
        return None

    token_type = payload.get("type")
    if expected_type == "access":
        if token_type not in (None, "access"):
            return None
    elif token_type != expected_type:
        return None

    user_id = payload.get("user_id")
    if user_id is not None:
        return db.query(User).filter(User.id == user_id).first()
    email = payload.get("sub")
    if email:
        return db.query(User).filter(User.email == email).first()
    return None
