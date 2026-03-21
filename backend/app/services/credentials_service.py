"""Serviço de credenciais: criar, listar, obter (com senha descriptografada) e remover."""
from sqlalchemy.orm import Session

from app.models.credentials import Credentials
from app.schemas.credentials import CredentialsCreate, CredentialsResponse
from app.utils.crypto import encrypt_credential, decrypt_credential


def list_by_user(db: Session, user_id: int) -> list[Credentials]:
    return db.query(Credentials).filter(Credentials.user_id == user_id).order_by(Credentials.site_name).all()


def get_by_id(db: Session, cred_id: int, user_id: int) -> Credentials | None:
    return db.query(Credentials).filter(
        Credentials.id == cred_id,
        Credentials.user_id == user_id,
    ).first()


def create(db: Session, user_id: int, data: CredentialsCreate) -> Credentials:
    cred = Credentials(
        user_id=user_id,
        site_name=data.site_name,
        login_url=data.login_url or None,
        username_encrypted=encrypt_credential(data.username) if data.username else None,
        password_encrypted=encrypt_credential(data.password) if data.password else None,
    )
    db.add(cred)
    db.commit()
    db.refresh(cred)
    return cred


def delete(db: Session, cred: Credentials) -> None:
    db.delete(cred)
    db.commit()


def to_response(cred: Credentials) -> CredentialsResponse:
    return CredentialsResponse(
        id=cred.id,
        site_name=cred.site_name,
        login_url=cred.login_url or cred.site_name,
        has_username=bool(cred.username_encrypted),
        has_password=bool(cred.password_encrypted),
    )


def get_plain_credentials(db: Session, cred_id: int, user_id: int) -> tuple[str | None, str | None, str | None]:
    """Retorna (login_url, username, password) em texto plano para uso no pipeline."""
    cred = get_by_id(db, cred_id, user_id)
    if not cred:
        return None, None, None
    login_url = cred.login_url or cred.site_name
    user = decrypt_credential(cred.username_encrypted) if cred.username_encrypted else None
    pwd = decrypt_credential(cred.password_encrypted) if cred.password_encrypted else None
    return login_url, user, pwd
