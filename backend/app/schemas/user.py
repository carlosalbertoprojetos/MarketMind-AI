"""
Schemas de usuário: registro, resposta, login.
"""
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: str | None = None

    class Config:
        from_attributes = True
