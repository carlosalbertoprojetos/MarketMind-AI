from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.analytics_event import AnalyticsEvent
from app.models.brand import Brand
from app.models.campaign import Campaign
from app.models.content_item import ContentItem
from app.models.enums import (
    AnalyticsEventType,
    CampaignStage,
    CampaignStatus,
    ContentType,
)
from app.models.organization import Organization
from app.models.product import Product
from app.models.user import User
from app.models.workspace import Workspace
from app.services.auth_service import hash_password


def seed_demo(db: Session) -> dict[str, str]:
    existing = db.query(Organization).filter(Organization.slug == "marketmind").first()
    status = "created"
    if existing:
        org = existing
        status = "exists"
    else:
        org = Organization(name="MarketMind", slug="marketmind", status="active")
        db.add(org)
        db.flush()

    user = (
        db.query(User)
        .filter(User.organization_id == org.id, User.email == "admin@marketmind.ai")
        .first()
    )
    if not user:
        user = User(
            organization_id=org.id,
            email="admin@marketmind.ai",
            full_name="Admin",
            hashed_password=hash_password("secret"),
            is_active=True,
            is_superuser=True,
        )
        db.add(user)
        db.flush()

    workspace = (
        db.query(Workspace)
        .filter(Workspace.organization_id == org.id, Workspace.slug == "main")
        .first()
    )
    if not workspace:
        workspace = Workspace(
            organization_id=org.id,
            name="Main Workspace",
            slug="main",
            description="Workspace principal de marketing.",
        )
        db.add(workspace)
        db.flush()

    brand = (
        db.query(Brand)
        .filter(Brand.organization_id == org.id, Brand.name == "MarketMind")
        .first()
    )
    if not brand:
        brand = Brand(
            organization_id=org.id,
            workspace_id=workspace.id,
            name="MarketMind",
            description="Marca principal de produtos AI.",
            website_url="https://marketmind.ai",
        )
        db.add(brand)
        db.flush()

    product = (
        db.query(Product)
        .filter(Product.organization_id == org.id, Product.name == "MarketMind AI")
        .first()
    )
    if not product:
        product = Product(
            organization_id=org.id,
            brand_id=brand.id,
            name="MarketMind AI",
            description="Plataforma de inteligencia de marketing orientada por IA.",
            website_url="https://marketmind.ai",
            status="active",
        )
        db.add(product)
        db.flush()

    campaign = (
        db.query(Campaign)
        .filter(Campaign.organization_id == org.id, Campaign.name == "Launch Q2")
        .first()
    )
    if not campaign:
        campaign = Campaign(
            organization_id=org.id,
            workspace_id=workspace.id,
            product_id=product.id,
            name="Launch Q2",
            objective="Gerar pipeline para o novo modulo de IA.",
            stage=CampaignStage.awareness,
            status=CampaignStatus.active,
        )
        db.add(campaign)
        db.flush()

    content_item = (
        db.query(ContentItem)
        .filter(ContentItem.organization_id == org.id, ContentItem.title == "Post LinkedIn Q2")
        .first()
    )
    if not content_item:
        content_item = ContentItem(
            organization_id=org.id,
            campaign_id=campaign.id,
            product_id=product.id,
            content_type=ContentType.linkedin_post,
            title="Post LinkedIn Q2",
            brief="Resumo do lancamento do modulo de IA.",
            short_version="Resumo curto do lancamento do modulo de IA.",
            medium_version="Versao media sobre resultados e beneficios.",
            long_version="Versao longa com storytelling e prova social.",
            technical_version="Detalhe tecnico do modulo e arquitetura.",
            sales_version="Versao comercial com CTA de demo.",
            meta={"persona": "Marketing Leaders"},
        )
        db.add(content_item)
        db.flush()

    existing_events = (
        db.query(AnalyticsEvent)
        .filter(AnalyticsEvent.organization_id == org.id)
        .count()
    )
    if existing_events == 0:
        now = datetime.utcnow()
        events: list[AnalyticsEvent] = []
        for days_ago in range(7):
            day = now - timedelta(days=days_ago)
            events.append(
                AnalyticsEvent(
                    organization_id=org.id,
                    post_id=None,
                    event_type=AnalyticsEventType.post_viewed,
                    occurred_at=day,
                    meta={"source": "seed"},
                )
            )
            events.append(
                AnalyticsEvent(
                    organization_id=org.id,
                    post_id=None,
                    event_type=AnalyticsEventType.post_engaged,
                    occurred_at=day,
                    meta={"source": "seed"},
                )
            )
            if days_ago % 2 == 0:
                events.append(
                    AnalyticsEvent(
                        organization_id=org.id,
                        post_id=None,
                        event_type=AnalyticsEventType.post_clicked,
                        occurred_at=day,
                        meta={"source": "seed"},
                    )
                )
        db.add_all(events)

    db.commit()
    db.refresh(org)
    db.refresh(user)
    return {
        "status": status,
        "organization_id": str(org.id),
        "user_id": str(user.id),
        "workspace_id": str(workspace.id),
        "product_id": str(product.id),
        "campaign_id": str(campaign.id),
    }
