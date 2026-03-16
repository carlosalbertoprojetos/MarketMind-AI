from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.social_account import SocialAccount
from app.schemas.social_account import SocialAccountCreate, SocialAccountRead, SocialAccountUpdate
from app.services.validators import get_workspace_or_404
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/social-accounts", tags=["social_accounts"])


@router.get("/", response_model=list[SocialAccountRead])
def list_social_accounts(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[SocialAccount]:
    return (
        db.query(SocialAccount)
        .filter(SocialAccount.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=SocialAccountRead, status_code=status.HTTP_201_CREATED)
def create_social_account(
    payload: SocialAccountCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> SocialAccount:
    get_workspace_or_404(db, payload.workspace_id, current_user.organization_id)
    account = SocialAccount(
        workspace_id=payload.workspace_id,
        platform=payload.platform,
        handle=payload.handle,
        external_id=payload.external_id,
        status=payload.status,
        meta=payload.meta,
        access_token_encrypted=payload.access_token,
        refresh_token_encrypted=payload.refresh_token,
        organization_id=current_user.organization_id,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/{social_account_id}", response_model=SocialAccountRead)
def read_social_account(
    social_account_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> SocialAccount:
    return get_object_or_404(db, SocialAccount, social_account_id, current_user.organization_id)


@router.patch("/{social_account_id}", response_model=SocialAccountRead)
def update_social_account(
    social_account_id: str,
    payload: SocialAccountUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> SocialAccount:
    account = get_object_or_404(db, SocialAccount, social_account_id, current_user.organization_id)
    apply_updates(account, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{social_account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_social_account(
    social_account_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    account = get_object_or_404(db, SocialAccount, social_account_id, current_user.organization_id)
    db.delete(account)
    db.commit()
    return None
