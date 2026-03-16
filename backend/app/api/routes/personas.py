from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.persona import Persona
from app.schemas.persona import PersonaCreate, PersonaRead, PersonaUpdate
from app.services.validators import get_product_or_404
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("/", response_model=list[PersonaRead])
def list_personas(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[Persona]:
    return (
        db.query(Persona)
        .filter(Persona.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=PersonaRead, status_code=status.HTTP_201_CREATED)
def create_persona(
    payload: PersonaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Persona:
    get_product_or_404(db, payload.product_id, current_user.organization_id)
    persona = Persona(**payload.model_dump(), organization_id=current_user.organization_id)
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona


@router.get("/{persona_id}", response_model=PersonaRead)
def read_persona(
    persona_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Persona:
    return get_object_or_404(db, Persona, persona_id, current_user.organization_id)


@router.patch("/{persona_id}", response_model=PersonaRead)
def update_persona(
    persona_id: str,
    payload: PersonaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Persona:
    persona = get_object_or_404(db, Persona, persona_id, current_user.organization_id)
    apply_updates(persona, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(persona)
    return persona


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(
    persona_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    persona = get_object_or_404(db, Persona, persona_id, current_user.organization_id)
    db.delete(persona)
    db.commit()
    return None