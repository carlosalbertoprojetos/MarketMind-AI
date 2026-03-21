"""
Rotas de autenticação: registro e login (com rate limit para evitar abuso).
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserRegister, UserLogin
from app.schemas.token import Token
from app.services.user_service import get_user_by_email, create_user, user_to_response
from app.services.auth_service import authenticate_user, create_token_for_user
from app.utils.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict)
@limiter.limit("10/minute")
def register(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    """
    Registra novo usuário. Retorna dados do usuário (sem senha).
    """
    if get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado",
        )
    user = create_user(db, data)
    return {"user": user_to_response(user), "message": "Usuário criado com sucesso"}


@router.post("/login", response_model=Token)
@limiter.limit("15/minute")
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    """
    Login com email e senha. Retorna access_token JWT.
    """
    user = authenticate_user(db, data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )
    access_token = create_token_for_user(user)
    return Token(access_token=access_token, token_type="bearer")
