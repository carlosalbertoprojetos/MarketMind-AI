"""
Dependencias FastAPI: banco de dados e usuario autenticado via JWT header ou cookie.
"""
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_user_from_token
from app.utils.security import ACCESS_COOKIE_NAME

security = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif request.cookies.get(ACCESS_COOKIE_NAME):
        token = request.cookies.get(ACCESS_COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticacao ausente",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_from_token(db, token, expected_type="access")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
