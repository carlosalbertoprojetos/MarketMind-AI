from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.user import User
from app.services.auth_service import hash_password


def seed_demo(db: Session) -> dict[str, str]:
    existing = db.query(Organization).filter(Organization.slug == "marketmind").first()
    if existing:
        return {"status": "exists", "organization_id": str(existing.id)}

    org = Organization(name="MarketMind", slug="marketmind", status="active")
    db.add(org)
    db.flush()

    user = User(
        organization_id=org.id,
        email="admin@marketmind.ai",
        full_name="Admin",
        hashed_password=hash_password("secret"),
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(org)
    db.refresh(user)
    return {"status": "created", "organization_id": str(org.id), "user_id": str(user.id)}