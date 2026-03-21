"""
Rotas de autenticacao com cookies HttpOnly para sessao e refresh.
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.token import SessionResponse, Token
from app.schemas.user import UserLogin, UserRegister
from app.services.auth_service import (
    authenticate_user,
    create_refresh_token_for_user,
    create_token_for_user,
    get_user_from_token,
)
from app.services.user_service import create_user, get_user_by_email, user_to_response
from app.utils.deps import get_current_user
from app.utils.limiter import limiter
from app.utils.security import (
    ACCESS_COOKIE_NAME,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    COOKIE_DOMAIN,
    COOKIE_PATH,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
    REFRESH_COOKIE_NAME,
    REFRESH_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    common_kwargs = {
        "httponly": True,
        "secure": COOKIE_SECURE,
        "samesite": COOKIE_SAMESITE,
        "domain": COOKIE_DOMAIN,
        "path": COOKIE_PATH,
    }
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **common_kwargs,
    )
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        **common_kwargs,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE_NAME, domain=COOKIE_DOMAIN, path=COOKIE_PATH)
    response.delete_cookie(REFRESH_COOKIE_NAME, domain=COOKIE_DOMAIN, path=COOKIE_PATH)


@router.post("/register", response_model=dict)
@limiter.limit("10/minute")
def register(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ja cadastrado",
        )
    user = create_user(db, data)
    return {"user": user_to_response(user), "message": "Usuario criado com sucesso"}


@router.post("/login", response_model=Token)
@limiter.limit("15/minute")
def login(request: Request, response: Response, data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )
    access_token = create_token_for_user(user)
    refresh_token = create_refresh_token_for_user(user)
    _set_auth_cookies(response, access_token, refresh_token)
    return Token(access_token=access_token, token_type="bearer", user=user_to_response(user))


@router.post("/refresh", response_model=Token)
def refresh_session(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessao ausente ou expirada")

    user = get_user_from_token(db, refresh_token, expected_type="refresh")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido ou expirado")

    access_token = create_token_for_user(user)
    rotated_refresh_token = create_refresh_token_for_user(user)
    _set_auth_cookies(response, access_token, rotated_refresh_token)
    return Token(access_token=access_token, token_type="bearer", user=user_to_response(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    _clear_auth_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/session", response_model=SessionResponse)
def get_session(current_user: User = Depends(get_current_user)):
    return SessionResponse(authenticated=True, user=user_to_response(current_user))
