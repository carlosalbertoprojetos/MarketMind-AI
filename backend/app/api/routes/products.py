from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.validators import get_brand_or_404
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductRead])
def list_products(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[Product]:
    return (
        db.query(Product)
        .filter(Product.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Product:
    get_brand_or_404(db, payload.brand_id, current_user.organization_id)
    product = Product(**payload.model_dump(), organization_id=current_user.organization_id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductRead)
def read_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Product:
    return get_object_or_404(db, Product, product_id, current_user.organization_id)


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: str,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Product:
    product = get_object_or_404(db, Product, product_id, current_user.organization_id)
    apply_updates(product, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    product = get_object_or_404(db, Product, product_id, current_user.organization_id)
    db.delete(product)
    db.commit()
    return None