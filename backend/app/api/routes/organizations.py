from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_superuser
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationUpdate
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/me", response_model=OrganizationRead)
def read_my_org(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> Organization:
    return get_object_or_404(db, Organization, current_user.organization_id)


@router.get("/", response_model=list[OrganizationRead])
def list_organizations(
    db: Session = Depends(get_db), _: User = Depends(require_superuser)
) -> list[Organization]:
    return db.query(Organization).all()


@router.post("/", response_model=OrganizationRead)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
) -> Organization:
    existing_org = db.query(Organization).filter(Organization.slug == payload.slug).first()
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization slug already exists")
    org = Organization(**payload.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/{organization_id}", response_model=OrganizationRead)
def read_organization(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Organization:
    if not current_user.is_superuser and str(current_user.organization_id) != organization_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return get_object_or_404(db, Organization, organization_id)


@router.patch("/{organization_id}", response_model=OrganizationRead)
def update_organization(
    organization_id: str,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Organization:
    if not current_user.is_superuser and str(current_user.organization_id) != organization_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    org = get_object_or_404(db, Organization, organization_id)
    apply_updates(org, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(org)
    return org
