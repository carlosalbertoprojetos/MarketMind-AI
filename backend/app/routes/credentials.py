"""Rotas de credenciais para login em URLs externas (scraping)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.deps import get_current_user
from app.schemas.credentials import CredentialsCreate, CredentialsResponse
from app.services.credentials_service import (
    list_by_user,
    get_by_id,
    create as create_cred,
    delete as delete_cred,
    to_response,
)

router = APIRouter(prefix="/credentials", tags=["credentials"])


@router.get("", response_model=list[CredentialsResponse])
def list_credentials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista credenciais do usuário (sem expor senhas)."""
    creds = list_by_user(db, current_user.id)
    return [to_response(c) for c in creds]


@router.post("", response_model=CredentialsResponse, status_code=status.HTTP_201_CREATED)
def create_credentials(
    data: CredentialsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Salva credenciais criptografadas para uso no scraping."""
    cred = create_cred(db, current_user.id, data)
    return to_response(cred)


@router.delete("/{cred_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_credentials(
    cred_id: int,
    db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
    """Remove credencial."""
    cred = get_by_id(db, cred_id, current_user.id)
    if not cred:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credencial não encontrada")
    delete_cred(db, cred)
