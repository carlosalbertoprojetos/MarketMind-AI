from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.post import Post
from app.schemas.post import PostCreate, PostRead, PostUpdate
from app.services.validators import get_content_item_or_404, get_social_account_or_404
from app.utils.db import apply_updates, get_object_or_404

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostRead])
def list_posts(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> list[Post]:
    return db.query(Post).filter(Post.organization_id == current_user.organization_id).all()


@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Post:
    get_content_item_or_404(db, payload.content_item_id, current_user.organization_id)
    if payload.social_account_id:
        get_social_account_or_404(db, payload.social_account_id, current_user.organization_id)
    post = Post(**payload.model_dump(), organization_id=current_user.organization_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostRead)
def read_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Post:
    return get_object_or_404(db, Post, post_id, current_user.organization_id)


@router.patch("/{post_id}", response_model=PostRead)
def update_post(
    post_id: str,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> Post:
    post = get_object_or_404(db, Post, post_id, current_user.organization_id)
    apply_updates(post, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> None:
    post = get_object_or_404(db, Post, post_id, current_user.organization_id)
    db.delete(post)
    db.commit()
    return None