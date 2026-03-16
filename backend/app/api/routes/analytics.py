from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.analytics_event import AnalyticsEvent
from app.schemas.analytics_event import AnalyticsEventCreate, AnalyticsEventRead
from app.services.validators import get_post_or_404
from app.utils.db import get_object_or_404

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/events", response_model=list[AnalyticsEventRead])
def list_events(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[AnalyticsEvent]:
    return (
        db.query(AnalyticsEvent)
        .filter(AnalyticsEvent.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/events", response_model=AnalyticsEventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: AnalyticsEventCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> AnalyticsEvent:
    if payload.post_id:
        get_post_or_404(db, payload.post_id, current_user.organization_id)
    event = AnalyticsEvent(
        **payload.model_dump(), organization_id=current_user.organization_id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/events/{event_id}", response_model=AnalyticsEventRead)
def read_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> AnalyticsEvent:
    return get_object_or_404(db, AnalyticsEvent, event_id, current_user.organization_id)