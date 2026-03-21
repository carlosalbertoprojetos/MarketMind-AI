"""Schemas para credenciais de login em URLs externas."""
from pydantic import BaseModel


class CredentialsCreate(BaseModel):
    site_name: str
    login_url: str | None = None
    username: str | None = None
    password: str | None = None


class CredentialsResponse(BaseModel):
    id: int
    site_name: str
    login_url: str
    has_username: bool = False
    has_password: bool = False

    class Config:
        from_attributes = True
