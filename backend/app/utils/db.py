from typing import Any, Type

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.base import Base


def get_object_or_404(
    db: Session, model: Type[Base], object_id: Any, organization_id: Any | None = None
) -> Base:
    query = db.query(model).filter(model.id == object_id)
    if organization_id is not None and hasattr(model, "organization_id"):
        query = query.filter(model.organization_id == organization_id)
    obj = query.first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return obj


def apply_updates(target: Base, data: dict[str, Any]) -> Base:
    for key, value in data.items():
        setattr(target, key, value)
    return target
