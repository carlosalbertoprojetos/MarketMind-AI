from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("/", response_model=list[WorkspaceRead])
def list_workspaces(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[Workspace]:
    return (
        db.query(Workspace)
        .filter(Workspace.organization_id == current_user.organization_id)
        .all()
    )


@router.post("/", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Workspace:
    workspace = Workspace(
        **payload.model_dump(), organization_id=current_user.organization_id
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


@router.get("/{workspace_id}", response_model=WorkspaceRead)
def read_workspace(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Workspace:
    return get_object_or_404(db, Workspace, workspace_id, current_user.organization_id)


@router.patch("/{workspace_id}", response_model=WorkspaceRead)
def update_workspace(
    workspace_id: str,
    payload: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Workspace:
    workspace = get_object_or_404(db, Workspace, workspace_id, current_user.organization_id)
    apply_updates(workspace, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(workspace)
    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    workspace = get_object_or_404(db, Workspace, workspace_id, current_user.organization_id)
    db.delete(workspace)
    db.commit()
    return None