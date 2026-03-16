from app.core import security


def hash_password(password: str) -> str:
    return security.get_password_hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return security.verify_password(password, hashed)


def issue_tokens(subject: str) -> dict[str, str]:
    return {
        "access_token": security.create_access_token(subject),
        "refresh_token": security.create_refresh_token(subject),
        "token_type": "bearer",
    }