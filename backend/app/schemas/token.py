"""
Schema de resposta de login (token JWT e tipo).
"""
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
