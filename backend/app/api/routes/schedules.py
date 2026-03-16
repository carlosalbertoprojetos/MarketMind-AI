from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleRead, ScheduleUpdate
from app.services.validators import get_post_or_404
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("/", response_model=list[ScheduleRead])
def list_schedules(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[Schedule]:
    return (
        db.query(Schedule)
        .filter(Schedule.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Schedule:
    get_post_or_404(db, payload.post_id, current_user.organization_id)
    schedule = Schedule(**payload.model_dump(), organization_id=current_user.organization_id)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.get("/{schedule_id}", response_model=ScheduleRead)
def read_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Schedule:
    return get_object_or_404(db, Schedule, schedule_id, current_user.organization_id)


@router.patch("/{schedule_id}", response_model=ScheduleRead)
def update_schedule(
    schedule_id: str,
    payload: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Schedule:
    schedule = get_object_or_404(db, Schedule, schedule_id, current_user.organization_id)
    apply_updates(schedule, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    schedule = get_object_or_404(db, Schedule, schedule_id, current_user.organization_id)
    db.delete(schedule)
    db.commit()
    return None