from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.media_asset import MediaAsset
from app.schemas.media_asset import MediaAssetCreate, MediaAssetRead, MediaAssetUpdate
from app.services.validators import get_content_item_or_404
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/media-assets", tags=["media_assets"])


@router.get("/", response_model=list[MediaAssetRead])
def list_media_assets(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[MediaAsset]:
    return (
        db.query(MediaAsset)
        .filter(MediaAsset.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=MediaAssetRead, status_code=status.HTTP_201_CREATED)
def create_media_asset(
    payload: MediaAssetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> MediaAsset:
    if payload.content_item_id:
        get_content_item_or_404(db, payload.content_item_id, current_user.organization_id)
    asset = MediaAsset(
        **payload.model_dump(), organization_id=current_user.organization_id
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/{media_asset_id}", response_model=MediaAssetRead)
def read_media_asset(
    media_asset_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> MediaAsset:
    return get_object_or_404(db, MediaAsset, media_asset_id, current_user.organization_id)


@router.patch("/{media_asset_id}", response_model=MediaAssetRead)
def update_media_asset(
    media_asset_id: str,
    payload: MediaAssetUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> MediaAsset:
    asset = get_object_or_404(db, MediaAsset, media_asset_id, current_user.organization_id)
    apply_updates(asset, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{media_asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media_asset(
    media_asset_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    asset = get_object_or_404(db, MediaAsset, media_asset_id, current_user.organization_id)
    db.delete(asset)
    db.commit()
    return None