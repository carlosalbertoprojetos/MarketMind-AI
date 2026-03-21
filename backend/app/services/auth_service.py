"""
Serviço de autenticação: login e validação de token JWT.
"""
from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserLogin
from app.utils.security import (
    verify_password,
    create_access_token,
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


def authenticate_user(db: Session, login: UserLogin) -> User | None:
    """
    Verifica email e senha. Retorna o usuário se válido, None caso contrário.
    """
    user = db.query(User).filter(User.email == login.email).first()
    if not user or not verify_password(login.password, user.password_hash):
        return None
    return user


def create_token_for_user(user: User, expires_minutes: int | None = None) -> str:
    """Gera access_token JWT para o usuário (subject = email para compatibilidade)."""
    expires = timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(data={"sub": user.email, "user_id": user.id}, expires_delta=expires)


def get_user_from_token(db: Session, token: str) -> User | None:
    """
    Valida o token JWT e retorna o usuário correspondente.
    Espera payload com 'sub' (email) ou 'user_id'.
    """
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("user_id")
    if user_id is not None:
        return db.query(User).filter(User.id == user_id).first()
    email = payload.get("sub")
    if email:
        return db.query(User).filter(User.email == email).first()
    return None
