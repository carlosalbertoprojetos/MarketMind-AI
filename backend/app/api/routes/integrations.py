from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.integration import Integration
from app.schemas.integration import IntegrationCreate, IntegrationRead, IntegrationUpdate
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/", response_model=list[IntegrationRead])
def list_integrations(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[Integration]:
    return (
        db.query(Integration)
        .filter(Integration.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=IntegrationRead, status_code=status.HTTP_201_CREATED)
def create_integration(
    payload: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Integration:
    integration = Integration(
        **payload.model_dump(), organization_id=current_user.organization_id
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


@router.get("/{integration_id}", response_model=IntegrationRead)
def read_integration(
    integration_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Integration:
    return get_object_or_404(db, Integration, integration_id, current_user.organization_id)


@router.patch("/{integration_id}", response_model=IntegrationRead)
def update_integration(
    integration_id: str,
    payload: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Integration:
    integration = get_object_or_404(db, Integration, integration_id, current_user.organization_id)
    apply_updates(integration, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(integration)
    return integration


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_integration(
    integration_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    integration = get_object_or_404(db, Integration, integration_id, current_user.organization_id)
    db.delete(integration)
    db.commit()
    return None