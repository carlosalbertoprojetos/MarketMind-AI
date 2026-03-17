from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.analytics_agent import AnalyticsAgent
from app.agents.audience_agent import AudienceAgent
from app.agents.campaign_agent import CampaignAgent
from app.agents.content_agent import ContentAgent
from app.agents.market_agent import MarketAgent
from app.agents.narrative_agent import NarrativeAgent
from app.agents.product_agent import ProductAgent
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.persona import Persona
from app.models.product import Product
from app.models.workspace import Workspace
from app.schemas.ai import (
    AnalyticsSummaryResponse,
    AudienceRequest,
    CampaignPlanRequest,
    CampaignPlanResponse,
    ContentGenerationRequest,
    MarketAnalysisRequest,
    MarketAnalysisResponse,
    NarrativeRequest,
    NarrativeResponse,
    ProductAnalysisRequest,
    ProductAnalysisResponse,
)
from app.schemas.ai_run import AiRunRead, PipelineRunRequest, PipelineRunResponse
from app.schemas.content_item import ContentItemRead
from app.schemas.persona import PersonaRead
from app.services.pipeline_engine import run_pipeline
from app.models.ai_run import AiRun
from app.utils.db import get_object_or_404
from app.services.validators import (
    get_persona_or_404,
    get_product_or_404,
    get_workspace_or_404,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/product/analyze", response_model=ProductAnalysisResponse)
def analyze_product(
    payload: ProductAnalysisRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> ProductAnalysisResponse:
    product: Product = get_product_or_404(db, payload.product_id, current_user.organization_id)
    result = ProductAgent(db).run(product, payload.sources)
    return ProductAnalysisResponse(
        product_id=payload.product_id, extracted_data=result.extracted_data
    )


@router.post("/market/analyze", response_model=MarketAnalysisResponse)
def analyze_market(
    payload: MarketAnalysisRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> MarketAnalysisResponse:
    product: Product = get_product_or_404(db, payload.product_id, current_user.organization_id)
    result = MarketAgent(db).run(product, payload.competitors)
    return MarketAnalysisResponse(
        product_id=payload.product_id, competitive_map=result.competitive_map
    )


@router.post("/audience/generate", response_model=list[PersonaRead])
def generate_audience(
    payload: AudienceRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> list[Persona]:
    product = get_product_or_404(db, payload.product_id, current_user.organization_id)
    result = AudienceAgent(db).run(product, payload.count)
    return result.personas


@router.post("/narrative/generate", response_model=NarrativeResponse)
def generate_narrative(
    payload: NarrativeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> NarrativeResponse:
    product = get_product_or_404(db, payload.product_id, current_user.organization_id)
    persona = None
    if payload.persona_id:
        persona = get_persona_or_404(db, payload.persona_id, current_user.organization_id)
    result = NarrativeAgent().run(product, persona)
    return NarrativeResponse(**asdict(result))


@router.post("/content/generate", response_model=ContentItemRead)
def generate_content(
    payload: ContentGenerationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> ContentItemRead:
    product = get_product_or_404(db, payload.product_id, current_user.organization_id)
    persona = None
    if payload.persona_id:
        persona = get_persona_or_404(db, payload.persona_id, current_user.organization_id)
    narrative = NarrativeAgent().run(product, persona)
    result = ContentAgent(db).run(
        product, payload.content_type, persona, narrative, payload.brief
    )
    return result.content_item


@router.post("/campaign/plan", response_model=CampaignPlanResponse)
def plan_campaign(
    payload: CampaignPlanRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> CampaignPlanResponse:
    workspace: Workspace = get_workspace_or_404(
        db, payload.workspace_id, current_user.organization_id
    )
    product: Product = get_product_or_404(db, payload.product_id, current_user.organization_id)
    result = CampaignAgent(db).run(workspace, product, payload.name, payload.objective)
    return CampaignPlanResponse(
        campaign_id=result.campaign.id,
        content_item_ids=[item.id for item in result.content_items],
    )


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
def analytics_summary(
    db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
) -> AnalyticsSummaryResponse:
    summary = AnalyticsAgent(db).run(current_user.organization_id)
    return AnalyticsSummaryResponse(
        engagement_rate=summary.engagement_rate, ctr=summary.ctr, growth=summary.growth
    )


@router.post("/pipeline/run", response_model=PipelineRunResponse)
def run_full_pipeline(
    payload: PipelineRunRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> PipelineRunResponse:
    product = get_product_or_404(db, payload.product_id, current_user.organization_id)
    result = run_pipeline(
        db,
        product,
        payload.sources,
        payload.content_types,
        payload.persona_count,
        payload.brief,
    )
    return PipelineRunResponse(
        run_id=result.run.id,
        status=result.run.status,
        content_item_ids=[item_id for item_id in result.content_item_ids],
        steps=result.steps,
        output=result.output,
    )


@router.get("/pipeline/runs", response_model=list[AiRunRead])
def list_pipeline_runs(
    product_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> list[AiRunRead]:
    product = get_product_or_404(db, product_id, current_user.organization_id)
    runs = (
        db.query(AiRun)
        .filter(AiRun.organization_id == current_user.organization_id, AiRun.product_id == product.id)
        .order_by(AiRun.created_at.desc())
        .limit(20)
        .all()
    )
    return runs


@router.get("/pipeline/runs/{run_id}", response_model=AiRunRead)
def read_pipeline_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> AiRunRead:
    return get_object_or_404(db, AiRun, run_id, current_user.organization_id)
