from sqlalchemy.orm import Session

from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.content_item import ContentItem
from app.models.persona import Persona
from app.models.post import Post
from app.models.product import Product
from app.models.social_account import SocialAccount
from app.models.user import User
from app.models.workspace import Workspace
from app.utils.db import get_object_or_404


def get_workspace_or_404(db: Session, workspace_id, organization_id):
    return get_object_or_404(db, Workspace, workspace_id, organization_id)


def get_brand_or_404(db: Session, brand_id, organization_id):
    return get_object_or_404(db, Brand, brand_id, organization_id)


def get_product_or_404(db: Session, product_id, organization_id):
    return get_object_or_404(db, Product, product_id, organization_id)


def get_campaign_or_404(db: Session, campaign_id, organization_id):
    return get_object_or_404(db, Campaign, campaign_id, organization_id)


def get_persona_or_404(db: Session, persona_id, organization_id):
    return get_object_or_404(db, Persona, persona_id, organization_id)


def get_content_item_or_404(db: Session, content_item_id, organization_id):
    return get_object_or_404(db, ContentItem, content_item_id, organization_id)


def get_post_or_404(db: Session, post_id, organization_id):
    return get_object_or_404(db, Post, post_id, organization_id)


def get_social_account_or_404(db: Session, social_account_id, organization_id):
    return get_object_or_404(db, SocialAccount, social_account_id, organization_id)


def get_user_or_404(db: Session, user_id, organization_id):
    return get_object_or_404(db, User, user_id, organization_id)