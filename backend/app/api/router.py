from fastapi import APIRouter

from app.api.routes.analytics import router as analytics_router
from app.api.routes.ai import router as ai_router
from app.api.routes.auth import router as auth_router
from app.api.routes.brands import router as brands_router
from app.api.routes.campaigns import router as campaigns_router
from app.api.routes.competitors import router as competitors_router
from app.api.routes.content_items import router as content_items_router
from app.api.routes.health import router as health_router
from app.api.routes.integrations import router as integrations_router
from app.api.routes.media_assets import router as media_assets_router
from app.api.routes.memberships import router as memberships_router
from app.api.routes.organizations import router as organizations_router
from app.api.routes.personas import router as personas_router
from app.api.routes.posts import router as posts_router
from app.api.routes.products import router as products_router
from app.api.routes.schedules import router as schedules_router
from app.api.routes.social_accounts import router as social_accounts_router
from app.api.routes.users import router as users_router
from app.api.routes.workspaces import router as workspaces_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(ai_router)
api_router.include_router(auth_router)
api_router.include_router(organizations_router)
api_router.include_router(users_router)
api_router.include_router(workspaces_router)
api_router.include_router(brands_router)
api_router.include_router(products_router)
api_router.include_router(competitors_router)
api_router.include_router(personas_router)
api_router.include_router(campaigns_router)
api_router.include_router(content_items_router)
api_router.include_router(posts_router)
api_router.include_router(media_assets_router)
api_router.include_router(schedules_router)
api_router.include_router(analytics_router)
api_router.include_router(social_accounts_router)
api_router.include_router(integrations_router)
api_router.include_router(memberships_router)
