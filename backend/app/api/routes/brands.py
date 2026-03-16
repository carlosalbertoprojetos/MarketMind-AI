from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandRead, BrandUpdate
from app.services.validators import get_workspace_or_404
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/brands", tags=["brands"])


@router.get("/", response_model=list[BrandRead])
def list_brands(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[Brand]:
    return (
        db.query(Brand)
        .filter(Brand.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=BrandRead, status_code=status.HTTP_201_CREATED)
def create_brand(
    payload: BrandCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Brand:
    get_workspace_or_404(db, payload.workspace_id, current_user.organization_id)
    brand = Brand(
        **payload.model_dump(), organization_id=current_user.organization_id
    )
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


@router.get("/{brand_id}", response_model=BrandRead)
def read_brand(
    brand_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Brand:
    return get_object_or_404(db, Brand, brand_id, current_user.organization_id)


@router.patch("/{brand_id}", response_model=BrandRead)
def update_brand(
    brand_id: str,
    payload: BrandUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Brand:
    brand = get_object_or_404(db, Brand, brand_id, current_user.organization_id)
    apply_updates(brand, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(brand)
    return brand


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
    brand_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    brand = get_object_or_404(db, Brand, brand_id, current_user.organization_id)
    db.delete(brand)
    db.commit()
    return None