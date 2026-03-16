from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_superuser
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.auth_service import hash_password
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user=Depends(get_current_active_user)) -> User:
    return current_user


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[User]:
    return (
        db.query(User)
        .filter(User.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_superuser),
) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        organization_id=current_user.organization_id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        is_active=payload.is_active,
        is_superuser=payload.is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> User:
    return get_object_or_404(db, User, user_id, current_user.organization_id)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> User:
    user = get_object_or_404(db, User, user_id, current_user.organization_id)
    apply_updates(user, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_superuser),
) -> None:
    user = get_object_or_404(db, User, user_id, current_user.organization_id)
    db.delete(user)
    db.commit()
    return None