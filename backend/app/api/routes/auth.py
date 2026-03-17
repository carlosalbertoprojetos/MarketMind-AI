from datetime import datetime, timedelta
import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import decode_token
from app.models.organization import Organization
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.schemas.user import (
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
    RegisterRequest,
    Token,
    TokenRefresh,
    UserLogin,
)
from app.services.auth_service import hash_password, issue_tokens, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> Token:
    existing_org = db.query(Organization).filter(Organization.slug == payload.organization_slug).first()
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization slug already exists")

    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    organization = Organization(
        name=payload.organization_name,
        slug=payload.organization_slug,
        status="active",
    )
    db.add(organization)
    db.flush()

    user = User(
        organization_id=organization.id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    tokens = issue_tokens(str(user.id))
    return Token(**tokens)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    tokens = issue_tokens(str(user.id))
    return Token(**tokens)


@router.post("/refresh", response_model=Token)
def refresh(payload: TokenRefresh, db: Session = Depends(get_db)) -> Token:
    try:
        data = decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = data.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    tokens = issue_tokens(str(user.id))
    return Token(**tokens)


@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(
    payload: PasswordResetRequest, db: Session = Depends(get_db)
) -> PasswordResetResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    # Always return success to avoid account enumeration.
    if not user:
        return PasswordResetResponse(status="ok")

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)
    reset_token = PasswordResetToken(
        organization_id=user.organization_id,
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(reset_token)
    db.commit()

    if settings.ENV == "production":
        return PasswordResetResponse(status="ok")
    return PasswordResetResponse(status="ok", reset_token=raw_token)


@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(
    payload: PasswordResetConfirm, db: Session = Depends(get_db)
) -> PasswordResetResponse:
    token_hash = hashlib.sha256(payload.token.encode("utf-8")).hexdigest()
    reset_token = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
        )
        .first()
    )
    if not reset_token or reset_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(payload.new_password)
    reset_token.used_at = datetime.utcnow()
    db.commit()

    return PasswordResetResponse(status="ok")
