from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.membership import Membership
from app.schemas.membership import MembershipCreate, MembershipRead, MembershipUpdate
from app.services.validators import get_user_or_404, get_workspace_or_404
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/memberships", tags=["memberships"])


@router.get("/", response_model=list[MembershipRead])
def list_memberships(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[Membership]:
    return (
        db.query(Membership)
        .filter(Membership.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=MembershipRead, status_code=status.HTTP_201_CREATED)
def create_membership(
    payload: MembershipCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Membership:
    get_user_or_404(db, payload.user_id, current_user.organization_id)
    get_workspace_or_404(db, payload.workspace_id, current_user.organization_id)
    membership = Membership(
        **payload.model_dump(), organization_id=current_user.organization_id
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


@router.get("/{membership_id}", response_model=MembershipRead)
def read_membership(
    membership_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Membership:
    return get_object_or_404(db, Membership, membership_id, current_user.organization_id)


@router.patch("/{membership_id}", response_model=MembershipRead)
def update_membership(
    membership_id: str,
    payload: MembershipUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Membership:
    membership = get_object_or_404(db, Membership, membership_id, current_user.organization_id)
    apply_updates(membership, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(membership)
    return membership


@router.delete("/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_membership(
    membership_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    membership = get_object_or_404(db, Membership, membership_id, current_user.organization_id)
    db.delete(membership)
    db.commit()
    return None