"""
Serviço de gerenciamento de usuários: criação e busca por email.
"""
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserRegister, UserResponse
from app.utils.security import hash_password


def get_user_by_email(db: Session, email: str) -> User | None:
    """Retorna usuário por email ou None."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Retorna usuário por id ou None."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, data: UserRegister) -> User:
    """Cria novo usuário com senha hasheada."""
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def user_to_response(user: User) -> UserResponse:
    """Converte modelo User para schema de resposta."""
    return UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )
