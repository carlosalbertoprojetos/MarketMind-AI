from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.competitor import Competitor
from app.schemas.competitor import CompetitorCreate, CompetitorRead, CompetitorUpdate
from app.services.validators import get_product_or_404
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/competitors", tags=["competitors"])


@router.get("/", response_model=list[CompetitorRead])
def list_competitors(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[Competitor]:
    return (
        db.query(Competitor)
        .filter(Competitor.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=CompetitorRead, status_code=status.HTTP_201_CREATED)
def create_competitor(
    payload: CompetitorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Competitor:
    get_product_or_404(db, payload.product_id, current_user.organization_id)
    competitor = Competitor(
        **payload.model_dump(), organization_id=current_user.organization_id
    )
    db.add(competitor)
    db.commit()
    db.refresh(competitor)
    return competitor


@router.get("/{competitor_id}", response_model=CompetitorRead)
def read_competitor(
    competitor_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Competitor:
    return get_object_or_404(db, Competitor, competitor_id, current_user.organization_id)


@router.patch("/{competitor_id}", response_model=CompetitorRead)
def update_competitor(
    competitor_id: str,
    payload: CompetitorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Competitor:
    competitor = get_object_or_404(db, Competitor, competitor_id, current_user.organization_id)
    apply_updates(competitor, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(competitor)
    return competitor


@router.delete("/{competitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_competitor(
    competitor_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    competitor = get_object_or_404(db, Competitor, competitor_id, current_user.organization_id)
    db.delete(competitor)
    db.commit()
    return None