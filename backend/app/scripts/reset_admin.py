import os

from app.core.database import SessionLocal
from app.models.user import User
from app.services.auth_service import hash_password
from app.utils.seed import seed_demo


def main() -> None:
    email = os.getenv("ADMIN_EMAIL", "admin@marketmind.ai").strip()
    password = os.getenv("ADMIN_PASSWORD", "secret")

    with SessionLocal() as db:
        seed_demo(db)
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise SystemExit(f"Admin user not found: {email}")
        user.hashed_password = hash_password(password)
        db.commit()

    print(f"Admin reset OK: {email}")


if __name__ == "__main__":
    main()
