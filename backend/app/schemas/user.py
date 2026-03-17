from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from app.schemas.common import IDSchema, ORMBase, TenantSchema, TimestampSchema


class UserBase(ORMBase):
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(ORMBase):
    full_name: str | None = None
    is_active: bool | None = None


class UserRead(UserBase, TenantSchema, IDSchema, TimestampSchema):
    last_login_at: datetime | None = None


class UserLogin(ORMBase):
    email: EmailStr
    password: str


class Token(ORMBase):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(ORMBase):
    sub: UUID


class TokenRefresh(ORMBase):
    refresh_token: str


class RegisterRequest(ORMBase):
    organization_name: str
    organization_slug: str
    full_name: str | None = None
    email: EmailStr
    password: str


class PasswordResetRequest(ORMBase):
    email: EmailStr


class PasswordResetConfirm(ORMBase):
    token: str
    new_password: str


class PasswordResetResponse(ORMBase):
    status: str
    reset_token: str | None = None
