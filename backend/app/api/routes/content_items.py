from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.content_item import ContentItem
from app.schemas.content_item import ContentItemCreate, ContentItemRead, ContentItemUpdate
from app.services.validators import (
    get_campaign_or_404,
    get_content_item_or_404,
    get_persona_or_404,
    get_product_or_404,
)
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/content-items", tags=["content_items"])


@router.get("/", response_model=list[ContentItemRead])
def list_content_items(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[ContentItem]:
    return (
        db.query(ContentItem)
        .filter(ContentItem.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=ContentItemRead, status_code=status.HTTP_201_CREATED)
def create_content_item(
    payload: ContentItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> ContentItem:
    if payload.campaign_id:
        get_campaign_or_404(db, payload.campaign_id, current_user.organization_id)
    if payload.product_id:
        get_product_or_404(db, payload.product_id, current_user.organization_id)
    if payload.persona_id:
        get_persona_or_404(db, payload.persona_id, current_user.organization_id)
    if payload.parent_id:
        get_content_item_or_404(db, payload.parent_id, current_user.organization_id)

    item = ContentItem(**payload.model_dump(), organization_id=current_user.organization_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{content_item_id}", response_model=ContentItemRead)
def read_content_item(
    content_item_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> ContentItem:
    return get_object_or_404(db, ContentItem, content_item_id, current_user.organization_id)


@router.patch("/{content_item_id}", response_model=ContentItemRead)
def update_content_item(
    content_item_id: str,
    payload: ContentItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> ContentItem:
    item = get_object_or_404(db, ContentItem, content_item_id, current_user.organization_id)
    apply_updates(item, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{content_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content_item(
    content_item_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    item = get_object_or_404(db, ContentItem, content_item_id, current_user.organization_id)
    db.delete(item)
    db.commit()
    return None