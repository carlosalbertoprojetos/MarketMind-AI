"""
Rotas de campanhas: criar, listar (via /user/campaigns), obter, atualizar, remover, preview.
"""
import os
import sys
import re
import json
from dataclasses import asdict
from pathlib import Path
from urllib.parse import quote
from datetime import datetime, timezone

import io
import mimetypes
import zipfile
import tempfile
import shutil
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.limiter import limiter
from app.models.user import User
from app.models.campaign import Campaign
from app.utils.deps import get_current_user
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse
from app.schemas.preview import CampaignPreviewRequest, CampaignPreviewResponse, PostPreviewResponse
from app.schemas.media import CampaignAssetsResponse, CampaignAssetItem, CampaignAssetsExportSelectedRequest
from app.schemas.generation import CampaignGenerationHistoryResponse, CampaignGenerationItem
from app.schemas.final_pipeline import (
    FinalContentPipelineRequest,
    FinalContentPipelineResponse,
    FinalContentPublishResponse,
    SavedFinalContentItemResponse,
    SavedFinalContentListResponse,
    SavedFinalContentResponse,
)
from app.services.campaign_service import (
    create_campaign,
    get_campaign_platforms,
    get_campaigns_by_user,
    get_campaigns_by_user_paginated,
    get_campaign_by_id,
    update_campaign,
    delete_campaign,
)
from app.services.saved_content_service import (
    create_saved_content,
    delete_saved_content,
    get_latest_saved_campaign_content,
    get_saved_content_by_id,
    list_saved_contents,
    parse_saved_content_platforms,
    parse_saved_content_publish_results,
    parse_saved_content_result,
)

router = APIRouter(prefix="/campaign", tags=["campaign"])


def _serialize_campaign(campaign: Campaign) -> CampaignResponse:
    return CampaignResponse.model_validate(
        {
            "id": campaign.id,
            "user_id": campaign.user_id,
            "title": campaign.title,
            "content": campaign.content,
            "platform": campaign.platform,
            "platforms": get_campaign_platforms(campaign),
            "schedule": campaign.schedule,
            "reminder_sent_at": campaign.reminder_sent_at,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
        }
    )


def _model_dump(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    if hasattr(model, "dict"):
        return model.dict()
    return dict(model)


def _saved_at_value(record) -> datetime | None:
    return getattr(record, "created_at", None)


def _serialize_saved_preview_response(response: CampaignPreviewResponse, record) -> CampaignPreviewResponse:
    response.saved_content_id = record.id
    response.saved_at = _saved_at_value(record)
    return response


def _build_saved_final_content_item(record) -> SavedFinalContentItemResponse:
    payload = parse_saved_content_result(record)
    outputs = payload.get("outputs") if isinstance(payload, dict) else []
    return SavedFinalContentItemResponse(
        id=record.id,
        title=record.title,
        theme=record.theme,
        objective=record.objective,
        audience=record.audience,
        style=record.style,
        platforms=parse_saved_content_platforms(record),
        post_count=len(outputs or []),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _build_saved_final_content_response(record) -> SavedFinalContentResponse:
    payload = parse_saved_content_result(record)
    payload["saved_content_id"] = record.id
    payload["saved_at"] = _saved_at_value(record)
    payload["id"] = record.id
    payload["title"] = record.title
    payload["style"] = record.style
    payload["platforms"] = parse_saved_content_platforms(record)
    payload["source_type"] = record.source_type
    payload["publish_results"] = parse_saved_content_publish_results(record)
    payload["updated_at"] = record.updated_at
    return SavedFinalContentResponse(**payload)


def _save_campaign_preview(db: Session, current_user: User, campaign: Campaign, response: CampaignPreviewResponse) -> CampaignPreviewResponse:
    record = create_saved_content(
        db,
        user_id=current_user.id,
        source_type="campaign",
        campaign_id=campaign.id,
        title=campaign.title,
        objective=campaign.platform,
        result_payload=_model_dump(response),
        platforms=sorted({post.platform for post in response.posts}),
    )
    return _serialize_saved_preview_response(response, record)


def _save_final_content_result(db: Session, current_user: User, data: FinalContentPipelineRequest, payload: dict, publish_results: list[dict] | None = None):
    return create_saved_content(
        db,
        user_id=current_user.id,
        source_type="final_content",
        title=data.theme,
        theme=data.theme,
        objective=data.objective,
        audience=data.audience,
        style=data.style,
        platforms=data.platforms,
        request_payload={
            "theme": data.theme,
            "objective": data.objective,
            "audience": data.audience,
            "platforms": data.platforms,
            "style": data.style,
        },
        result_payload=payload,
        publish_results=publish_results or [],
    )


def _run_final_content_pipeline_or_422(data: FinalContentPipelineRequest):
    root = Path(__file__).resolve().parent.parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from ia_pipeline.pipelines.final_content_pipeline import run_final_content_pipeline
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pipeline final de conteudo nao disponivel.",
        )

    try:
        return run_final_content_pipeline(
            theme=data.theme,
            objective=data.objective,
            audience=data.audience,
            platforms=data.platforms,
            style=data.style,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Falha ao executar o pipeline final: {exc}",
        )


def _extract_url_from_campaign_content(content: str | None) -> str | None:
    if not content:
        return None
    s = str(content).strip()
    if s.upper().startswith("URL:"):
        first_line = s.splitlines()[0]
        candidate = first_line[4:].strip()
        return candidate if re.match(r"^https?://", candidate, re.IGNORECASE) else None
    if re.match(r"^https?://", s, re.IGNORECASE):
        return s
    m = re.search(r"URL:\s*(https?://\S+)", s, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def _extract_additional_urls_from_campaign_content(content: str | None) -> list[str]:
    if not content:
        return []
    s = str(content)
    block = re.search(r"(?:^|\n)ADDITIONAL_URLS:\s*\n([\s\S]*?)\nEND_ADDITIONAL_URLS(?:\n|$)", s, re.IGNORECASE)
    if not block:
        return []
    urls: list[str] = []
    for line in block.group(1).splitlines():
        candidate = line.strip()
        if re.match(r"^https?://", candidate, re.IGNORECASE):
            urls.append(candidate)
    return urls


def _extract_credentials_id_from_campaign_content(content: str | None) -> int | None:
    if not content:
        return None
    s = str(content)
    match = re.search(r"(?:^|\n)CREDENTIALS_ID:\s*(\d+)(?:\n|$)", s, re.IGNORECASE)
    if not match:
        return None
    try:
        return int(match.group(1))
    except (TypeError, ValueError):
        return None


def _extract_platforms_from_campaign_content(content: str | None) -> list[str]:
    if not content:
        return []
    s = str(content)
    block = re.search(r"(?:^|\n)PLATFORMS:\s*\n([\s\S]*?)\nEND_PLATFORMS(?:\n|$)", s, re.IGNORECASE)
    if not block:
        return []
    platforms: list[str] = []
    seen: set[str] = set()
    for line in block.group(1).splitlines():
        candidate = line.strip().lower()
        if not candidate:
            continue
        if candidate == "x":
            candidate = "twitter"
        if candidate not in ("instagram", "facebook", "linkedin", "twitter", "tiktok", "youtube"):
            continue
        if candidate not in seen:
            seen.add(candidate)
            platforms.append(candidate)
    return platforms


def _normalize_compare_url(value: str | None) -> str:
    if not value:
        return ""
    normalized = str(value).strip().rstrip("/")
    return normalized.lower()


def _validate_analysis_target(url: str, login_url: str | None = None) -> None:
    normalized_url = _normalize_compare_url(url)
    normalized_login_url = _normalize_compare_url(login_url)
    if normalized_url and normalized_login_url and normalized_url == normalized_login_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A URL principal de analise nao pode ser a mesma URL de login. Use a tela de login apenas em 'URL de login' e informe uma tela interna como URL principal.",
        )


def _preview_image_query_urls(output_base: Path, image_paths: list[str]) -> list[str]:
    """Paths absolutos salvos pelo pipeline → query segura para GET /campaign/preview/image."""
    try:
        base = output_base.resolve()
    except OSError:
        base = output_base
    urls: list[str] = []
    for abs_path in image_paths or []:
        if not abs_path:
            continue
        try:
            p = Path(abs_path).resolve()
            rel = p.relative_to(base)
            urls.append("campaign/preview/image?path=" + quote(rel.as_posix()))
        except (ValueError, TypeError, OSError, RuntimeError):
            continue
    return urls


def _build_preview_response(root: Path, out: object, url: str, *, saved_content_id: int | None = None, saved_at: datetime | None = None) -> CampaignPreviewResponse:
    output_base = root / "ia_pipeline" / "output"
    posts = []
    for p in out.posts:
        image_urls = _preview_image_query_urls(output_base, p.image_paths)
        posts.append(
            PostPreviewResponse(
                platform=p.platform,
                title=p.title,
                text=p.text,
                image_paths=p.image_paths,
                image_urls=image_urls,
                hashtags=p.hashtags,
                suggested_times=p.suggested_times,
                steps=p.steps,
                source_page_url=getattr(p, "source_page_url", "") or "",
                page_title=getattr(p, "page_title", "") or "",
                screen_type=getattr(p, "screen_type", "generic") or "generic",
                screen_label=getattr(p, "screen_label", "") or "",
                strategy_summary=getattr(p, "strategy_summary", "") or "",
                content_format=getattr(p, "content_format", "") or "",
                primary_cta=getattr(p, "primary_cta", "") or "",
                platform_rules=getattr(p, "platform_rules", {}) or {},
                structured_output=getattr(p, "structured_output", {}) or {},
                hooks=getattr(p, "hooks", []) or [],
                narrative_structure=getattr(p, "narrative_structure", {}) or {},
                cta_options=getattr(p, "cta_options", []) or [],
                ab_variations=getattr(p, "ab_variations", []) or [],
                visual_decision=getattr(p, "visual_decision", {}) or {},
            )
        )
    return CampaignPreviewResponse(
        url=url,
        posts=posts,
        business_summary=getattr(out, "business_summary", {}) or {},
        generated_contents=getattr(out, "generated_contents", []) or [],
        copy_variations=getattr(out, "copy_variations", []) or [],
        visual_suggestions=getattr(out, "visual_suggestions", []) or [],
        error=None,
        saved_content_id=saved_content_id,
        saved_at=saved_at,
    )


def _campaign_output_dir(root: Path, user_id: int, campaign_id: int) -> Path:
    return root / "ia_pipeline" / "output" / f"campaign_{user_id}_{campaign_id}"


def _preview_output_dir(root: Path, user_id: int) -> Path:
    output_base = root / "ia_pipeline" / "output"
    output_base.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=f"preview_{user_id}_", dir=output_base))


def _path_belongs_to_user(current_user: User, relative_path: str) -> bool:
    normalized = str(relative_path).lstrip("/").replace("\\", "/")
    return normalized.startswith(f"preview_{current_user.id}_") or normalized.startswith(f"campaign_{current_user.id}_")


def _generation_history_path(root: Path, user_id: int, campaign_id: int) -> Path:
    return _campaign_output_dir(root, user_id, campaign_id) / "generation-history.json"


def _load_generation_history(root: Path, user_id: int, campaign_id: int) -> list[dict]:
    history_path = _generation_history_path(root, user_id, campaign_id)
    if not history_path.is_file():
        return []
    try:
        data = json.loads(history_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def _append_generation_history(root: Path, user_id: int, campaign_id: int, source_url: str, out: object) -> None:
    asset_count = 0
    platforms: list[str] = []
    seen_platforms: set[str] = set()
    for p in out.posts:
        asset_count += len(p.image_paths or [])
        platform_name = str(getattr(p, "platform", "") or "").strip().lower()
        if platform_name and platform_name not in seen_platforms:
            seen_platforms.add(platform_name)
            platforms.append(platform_name)
    item = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_url": source_url,
        "post_count": len(out.posts or []),
        "asset_count": asset_count,
        "platforms": platforms,
    }
    history = _load_generation_history(root, user_id, campaign_id)
    history.insert(0, item)
    history = history[:50]
    history_path = _generation_history_path(root, user_id, campaign_id)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, ensure_ascii=True, indent=2), encoding="utf-8")


def _collect_campaign_assets(
    root: Path,
    user_id: int,
    campaign_id: int,
    *,
    kind: str | None = None,
    platform: str | None = None,
    generated_from: str | None = None,
    generated_to: str | None = None,
) -> list[CampaignAssetItem]:
    def _parse_date_like(value: str | None, end_of_day: bool = False) -> datetime | None:
        if not value:
            return None
        s = str(value).strip()
        if not s:
            return None
        try:
            if "T" in s:
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
            d = datetime.fromisoformat(s + ("T23:59:59.999999" if end_of_day else "T00:00:00"))
            return d
        except Exception:
            return None

    from_dt = _parse_date_like(generated_from, end_of_day=False)
    to_dt = _parse_date_like(generated_to, end_of_day=True)
    output_dir = _campaign_output_dir(root, user_id, campaign_id)
    assets: list[CampaignAssetItem] = []
    if output_dir.exists():
        for full in output_dir.rglob("*"):
            if not full.is_file():
                continue
            ext = full.suffix.lower()
            if ext not in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
                continue
            rel = os.path.relpath(full, root / "ia_pipeline" / "output").replace("\\", "/")
            asset_kind = "screenshot" if "/screenshots/" in f"/{rel}/" else "generated"
            asset_platform = None
            name = full.stem.lower()
            for p_name in ("instagram", "facebook", "linkedin", "twitter", "tiktok", "youtube"):
                if f"_{p_name}_" in name or name.endswith(f"_{p_name}"):
                    asset_platform = p_name
                    break
            if kind and asset_kind != kind:
                continue
            if platform and asset_platform != platform.lower():
                continue
            modified_at = datetime.fromtimestamp(full.stat().st_mtime, tz=timezone.utc)
            if from_dt:
                cmp_from = from_dt if from_dt.tzinfo else from_dt.replace(tzinfo=timezone.utc)
                if modified_at < cmp_from:
                    continue
            if to_dt:
                cmp_to = to_dt if to_dt.tzinfo else to_dt.replace(tzinfo=timezone.utc)
                if modified_at > cmp_to:
                    continue
            assets.append(
                CampaignAssetItem(
                    path=rel,
                    url="campaign/preview/image?path=" + quote(rel),
                    kind=asset_kind,
                    platform=asset_platform,
                    generated_at=modified_at.isoformat(),
                )
            )
    assets.sort(key=lambda a: a.path)
    return assets


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria nova campanha para o usuário logado."""
    return _serialize_campaign(create_campaign(db, current_user.id, data))


@router.get("/upcoming", response_model=list[CampaignResponse])
def list_upcoming_campaigns(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista campanhas agendadas nas próximas N horas (para lembretes/notificações)."""
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    end = now + timedelta(hours=hours)
    campaigns = (
        db.query(Campaign)
        .filter(
            Campaign.user_id == current_user.id,
            Campaign.schedule.isnot(None),
            Campaign.schedule >= now,
            Campaign.schedule <= end,
        )
        .order_by(Campaign.schedule)
        .all()
    )
    return [_serialize_campaign(item) for item in campaigns]


@router.post("/{campaign_id}/remind", response_model=CampaignResponse)
def mark_reminder_sent(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marca que um lembrete foi enviado para esta campanha (chamado por cron/script)."""
    campaign = get_campaign_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campanha não encontrada")
    from datetime import datetime
    campaign.reminder_sent_at = datetime.utcnow()
    db.commit()
    db.refresh(campaign)
    return _serialize_campaign(campaign)


@router.get("", response_model=CampaignListResponse)
def list_campaigns(
    limit: int = 50,
    offset: int = 0,
    platform: str | None = None,
    search: str | None = None,
    sort: str = "created_at_desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista campanhas do usuário com paginação e filtros (platform, search, sort)."""
    limit = min(max(1, limit), 100)
    offset = max(0, offset)
    if sort not in ("created_at_desc", "created_at_asc", "schedule_desc", "schedule_asc"):
        sort = "created_at_desc"
    items, total = get_campaigns_by_user_paginated(
        db, current_user.id, limit=limit, offset=offset, platform=platform, search=search, sort=sort
    )
    return CampaignListResponse(items=[_serialize_campaign(item) for item in items], total=total, limit=limit, offset=offset)


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna uma campanha por id (apenas se for do usuário)."""
    campaign = get_campaign_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campanha não encontrada")
    return _serialize_campaign(campaign)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
def patch_campaign(
    campaign_id: int,
    data: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza campanha parcialmente."""
    campaign = get_campaign_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campanha não encontrada")
    return _serialize_campaign(update_campaign(db, campaign, data))


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove campanha."""
    campaign = get_campaign_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campanha não encontrada")
    delete_campaign(db, campaign)


@router.post("/preview", response_model=CampaignPreviewResponse)
@limiter.limit("20/minute")
def preview_from_url(
    request: Request,
    data: CampaignPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gera pré-visualização a partir da URL. Aceita credentials_id ou login manual."""
    login_url, login_user, login_pass = None, None, None
    if data.credentials_id:
        from app.services.credentials_service import get_plain_credentials
        login_url, login_user, login_pass = get_plain_credentials(db, data.credentials_id, current_user.id)
    if not login_url and (data.login_url or data.login_username or data.login_password):
        login_url, login_user, login_pass = data.login_url, data.login_username, data.login_password

    _validate_analysis_target(data.url, login_url)

    root = Path(__file__).resolve().parent.parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from ia_pipeline.pipeline import run_pipeline
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pipeline de IA não disponível. Verifique o ambiente ia_pipeline.",
        )
    try:
        out = run_pipeline(
            url=data.url,
            campaign_title=data.campaign_title,
            platforms=[data.target_platform] if data.target_platform else (data.platforms or ["instagram", "facebook", "linkedin", "twitter", "tiktok", "youtube"]),
            login_url=login_url,
            login_user=login_user,
            login_pass=login_pass,
            output_dir=_preview_output_dir(root, current_user.id),
            source_urls=data.source_urls,
            max_crawl_pages=data.max_crawl_pages,
            max_crawl_depth=data.max_crawl_depth,
            objective=data.objective,
            follow_internal_links=data.follow_internal_links,
            capture_scroll_sections=data.capture_scroll_sections,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Falha ao executar o pipeline: {e}",
        )
    if out.error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=out.error)
    return _build_preview_response(root, out, out.url)


@router.post("/marketing-content", response_model=CampaignPreviewResponse)
@limiter.limit("20/minute")
def marketing_content_from_url(
    request: Request,
    data: CampaignPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Alias semantico para o modulo automatizado de geracao de marketing por URL."""
    return preview_from_url(request=request, data=data, db=db, current_user=current_user)


@router.post("/orchestrate")
@limiter.limit("10/minute")
def orchestrate_marketing_pipeline(
    request: Request,
    data: CampaignPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Executa o pipeline autonomo completo: gerar copy, imagem, publicacao e ciclo evolutivo."""
    root = Path(__file__).resolve().parent.parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from ia_pipeline.orchestrator.service import run_pipeline as run_orchestrator
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Orquestrador autonomo nao disponivel.",
        )

    target_platform = data.target_platform or ((data.platforms or ["instagram"])[0])
    result = run_orchestrator(
        url=data.url,
        platform=target_platform,
        objective=data.objective,
        campaign_title=data.campaign_title,
        login_url=data.login_url,
        login_username=data.login_username,
        login_password=data.login_password,
        source_urls=data.source_urls,
        auto_publish=os.environ.get("MARKETINGAI_AUTO_PUBLISH_DEFAULT", "false").lower() in ("1", "true", "yes"),
        follow_internal_links=data.follow_internal_links,
        capture_scroll_sections=data.capture_scroll_sections,
    )
    return asdict(result)


@router.post("/multi-agent")
@limiter.limit("10/minute")
def run_multi_agent_marketing_pipeline(
    request: Request,
    data: CampaignPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Executa o ciclo coordenado por agentes especializados."""
    root = Path(__file__).resolve().parent.parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from ia_pipeline.agents.orchestrator_agent import run_multi_agent_pipeline
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema multi-agente nao disponivel.",
        )

    target_platform = data.target_platform or ((data.platforms or ["instagram"])[0])
    result = run_multi_agent_pipeline(
        url=data.url,
        platform=target_platform,
        objective=data.objective,
        campaign_title=data.campaign_title,
        login_url=data.login_url,
        login_username=data.login_username,
        login_password=data.login_password,
        auto_publish=os.environ.get("MARKETINGAI_AUTO_PUBLISH_DEFAULT", "false").lower() in ("1", "true", "yes"),
        max_cycles=int(os.environ.get("MARKETINGAI_AGENT_MAX_CYCLES", "2")),
        debug=os.environ.get("MARKETINGAI_AGENT_DEBUG", "false").lower() in ("1", "true", "yes"),
        source_urls=data.source_urls,
        follow_internal_links=data.follow_internal_links,
        capture_scroll_sections=data.capture_scroll_sections,
    )
    return result


@router.post("/final-content", response_model=FinalContentPipelineResponse)
@limiter.limit("20/minute")
def run_final_content_pipeline_route(
    request: Request,
    data: FinalContentPipelineRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gera conteudo multiplataforma a partir de tema, objetivo e publico."""
    result = _run_final_content_pipeline_or_422(data)
    payload = asdict(result)
    record = _save_final_content_result(db, current_user, data, payload)
    return {**payload, "saved_content_id": record.id, "saved_at": _saved_at_value(record)}


@router.post("/final-content/export")
@limiter.limit("10/minute")
def export_final_content_pipeline_route(
    request: Request,
    data: FinalContentPipelineRequest,
    current_user: User = Depends(get_current_user),
):
    """Exporta o resultado do pipeline final em ZIP com JSON e TXT por plataforma."""
    result = _run_final_content_pipeline_or_422(data)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        payload = asdict(result)
        zf.writestr("manifest.json", json.dumps(payload, ensure_ascii=True, indent=2).encode("utf-8"))
        for item in result.outputs:
            prefix = item.platform.replace(" ", "_")
            zf.writestr(f"{prefix}/content.txt", item.full_content.encode("utf-8"))
            zf.writestr(f"{prefix}/image_prompt.txt", item.image_prompt.encode("utf-8"))
            zf.writestr(
                f"{prefix}/metadata.json",
                json.dumps(asdict(item), ensure_ascii=True, indent=2).encode("utf-8"),
            )
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=marketingai-final-content.zip"},
    )


@router.post("/final-content/publish", response_model=FinalContentPublishResponse)
@limiter.limit("10/minute")
def publish_final_content_pipeline_route(
    request: Request,
    data: FinalContentPipelineRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Executa o pipeline final e publica os conteudos gerados nas plataformas selecionadas."""
    result = _run_final_content_pipeline_or_422(data)
    root = Path(__file__).resolve().parent.parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from ia_pipeline.publisher.service import publish_post
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modulo de publicacao nao disponivel.",
        )

    publish_results = []
    for item in result.outputs:
        publish_result = publish_post(
            platform=item.platform,
            content=item.full_content,
            image="",
            hashtags=item.hashtags,
        )
        publish_results.append(asdict(publish_result))

    payload = asdict(result)
    record = _save_final_content_result(db, current_user, data, payload, publish_results=publish_results)
    return {
        **payload,
        "publish_results": publish_results,
        "saved_content_id": record.id,
        "saved_at": _saved_at_value(record),
    }


@router.get("/final-content/saved", response_model=SavedFinalContentListResponse)
def list_saved_final_content_route(
    limit: int = 20,
    offset: int = 0,
    search: str | None = None,
    platform: str | None = None,
    platforms: str | None = None,
    created_from: str | None = None,
    created_to: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    limit = min(max(1, limit), 100)
    offset = max(0, offset)
    requested_platforms = [item.strip() for item in str(platforms or '').split(',') if item.strip()]
    records, total = list_saved_contents(
        db,
        current_user.id,
        source_type="final_content",
        limit=limit,
        offset=offset,
        search=search,
        platform=platform,
        platforms=requested_platforms,
        created_from=created_from,
        created_to=created_to,
    )
    items = [_build_saved_final_content_item(record) for record in records]
    return SavedFinalContentListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/final-content/saved/{saved_content_id}", response_model=SavedFinalContentResponse)
def get_saved_final_content_route(
    saved_content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = get_saved_content_by_id(db, saved_content_id, current_user.id, source_type="final_content")
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conteudo salvo nao encontrado")
    return _build_saved_final_content_response(record)


@router.delete("/final-content/saved/{saved_content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_final_content_route(
    saved_content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = get_saved_content_by_id(db, saved_content_id, current_user.id, source_type="final_content")
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conteudo salvo nao encontrado")
    delete_saved_content(db, record)


@router.get("/{campaign_id}/saved-posts/latest", response_model=CampaignPreviewResponse)
def get_latest_saved_campaign_preview(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    campaign = get_campaign_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campanha nao encontrada")
    record = get_latest_saved_campaign_content(db, current_user.id, campaign_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum post salvo para esta campanha")
    payload = parse_saved_content_result(record)
    payload["saved_content_id"] = record.id
    payload["saved_at"] = _saved_at_value(record)
    return CampaignPreviewResponse(**payload)


@router.post("/{campaign_id}/generate", response_model=CampaignPreviewResponse)
@limiter.limit("20/minute")
def generate_campaign_content_from_saved_url(
    request: Request,
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Gera posts da campanha usando EXCLUSIVAMENTE a URL salva na campanha.
    A URL é lida de campaign.content no formato "URL: https://..." (ou URL pura).
    """
    campaign = get_campaign_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campanha não encontrada")
    source_url = _extract_url_from_campaign_content(campaign.content)
    source_urls = _extract_additional_urls_from_campaign_content(campaign.content)
    credentials_id = _extract_credentials_id_from_campaign_content(campaign.content)
    requested_platforms = _extract_platforms_from_campaign_content(campaign.content)
    if not requested_platforms:
        requested_platforms = [campaign.platform] if campaign.platform else ["instagram", "facebook", "linkedin", "twitter", "tiktok", "youtube"]
    if not source_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Campanha sem URL válida. Salve a campanha com o campo URL do site/produto preenchido.",
        )
    login_url, login_user, login_pass = None, None, None
    if credentials_id:
        from app.services.credentials_service import get_plain_credentials
        login_url, login_user, login_pass = get_plain_credentials(db, credentials_id, current_user.id)

    root = Path(__file__).resolve().parent.parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from ia_pipeline.pipeline import run_pipeline
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pipeline de IA não disponível. Verifique o ambiente ia_pipeline.",
        )

    output_dir = _campaign_output_dir(root, current_user.id, campaign.id)
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        out = run_pipeline(
            url=source_url,
            campaign_title=campaign.title,
            platforms=requested_platforms,
            login_url=login_url,
            login_user=login_user,
            login_pass=login_pass,
            output_dir=output_dir,
            source_urls=source_urls,
            max_crawl_pages=max(int(os.environ.get("MARKETINGAI_MAX_CRAWL_PAGES", "5")), 1 + len(source_urls)),
            max_crawl_depth=0,
            follow_internal_links=False,
            capture_scroll_sections=True,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Falha ao executar o pipeline: {e}",
        )
    if out.error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=out.error)
    _append_generation_history(root, current_user.id, campaign.id, source_url, out)
    response = _build_preview_response(root, out, source_url)
    return _save_campaign_preview(db, current_user, campaign, response)


@router.get("/{campaign_id}/assets", response_model=CampaignAssetsResponse)
def list_campaign_generated_assets(
    campaign_id: int,
    kind: str | None = None,
    platform: str | None = None,
    generated_from: str | None = None,
    generated_to: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista ativos de mídia gerados da campanha em forma de galeria.
    """
    campaign = get_campaign_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campanha não encontrada")

    source_url = _extract_url_from_campaign_content(campaign.content)
    root = Path(__file__).resolve().parent.parent.parent.parent
    assets = _collect_campaign_assets(
        root,
        current_user.id,
        campaign.id,
        kind=kind,
        platform=platform,
        generated_from=generated_from,
        generated_to=generated_to,
    )
    return CampaignAssetsResponse(campaign_id=campaign.id, source_url=source_url, assets=assets)


@router.get("/{campaign_id}/assets/export")
def export_campaign_assets_filtered(
    campaign_id: int,
    kind: str | None = None,
    platform: str | None = None,
    generated_from: str | None = None,
    generated_to: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    campaign = get_campaign_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campanha não encontrada")
    root = Path(__file__).resolve().parent.parent.parent.parent
    assets = _collect_campaign_assets(
        root,
        current_user.id,
        campaign.id,
        kind=kind,
        platform=platform,
        generated_from=generated_from,
        generated_to=generated_to,
    )
    if not assets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum ativo encontrado para exportar com os filtros selecionados")

    output_base = root / "ia_pipeline" / "output"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, asset in enumerate(assets, start=1):
            full = (output_base / asset.path).resolve()
            if full.is_file() and str(full).startswith(str(output_base.resolve())):
                ext = full.suffix.lower() or ".png"
                safe_platform = asset.platform or "geral"
                zf.write(full, f"{asset.kind}/{safe_platform}/asset_{i}{ext}")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=marketingai-assets-filtrados.zip"},
    )


@router.post("/{campaign_id}/assets/export-selected")
def export_campaign_assets_selected(
    campaign_id: int,
    data: CampaignAssetsExportSelectedRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    campaign = get_campaign_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campanha não encontrada")
    if not data.paths:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Selecione ao menos um ativo para exportar")

    root = Path(__file__).resolve().parent.parent.parent.parent
    output_base = (root / "ia_pipeline" / "output").resolve()
    output_dir = _campaign_output_dir(root, current_user.id, campaign.id).resolve()
    buf = io.BytesIO()
    selected_count = 0
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, rel in enumerate(data.paths, start=1):
            safe_rel = str(rel).lstrip("/").replace("\\", "/")
            full = (output_base / safe_rel).resolve()
            if not str(full).startswith(str(output_dir)):
                continue
            if not full.is_file():
                continue
            ext = full.suffix.lower() or ".png"
            zf.write(full, f"selecionados/asset_{i}{ext}")
            selected_count += 1
    if selected_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum ativo válido selecionado para exportação")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=marketingai-assets-selecionados.zip"},
    )


@router.post("/{campaign_id}/assets/delete-selected")
def delete_campaign_assets_selected(
    campaign_id: int,
    data: CampaignAssetsExportSelectedRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    campaign = get_campaign_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campanha nao encontrada")
    if not data.paths:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Selecione ao menos um ativo para excluir")

    root = Path(__file__).resolve().parent.parent.parent.parent
    output_base = (root / "ia_pipeline" / "output").resolve()
    output_dir = _campaign_output_dir(root, current_user.id, campaign.id).resolve()
    deleted_count = 0

    for rel in data.paths:
        safe_rel = str(rel).lstrip("/").replace("\\", "/")
        full = (output_base / safe_rel).resolve()
        if not str(full).startswith(str(output_dir)):
            continue
        if not full.is_file():
            continue
        try:
            full.unlink()
            deleted_count += 1
            parent = full.parent
            while parent != output_dir and parent.exists():
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent
        except OSError:
            continue

    if deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum ativo valido selecionado para exclusao")

    return {
        "deleted_count": deleted_count,
        "campaign_id": campaign.id,
    }


@router.get("/{campaign_id}/generations", response_model=CampaignGenerationHistoryResponse)
def get_campaign_generation_history(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    campaign = get_campaign_by_id(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campanha não encontrada")
    root = Path(__file__).resolve().parent.parent.parent.parent
    raw = _load_generation_history(root, current_user.id, campaign.id)
    items = []
    for row in raw:
        try:
            items.append(
                CampaignGenerationItem(
                    generated_at=str(row.get("generated_at", "")),
                    source_url=str(row.get("source_url", "")),
                    post_count=int(row.get("post_count", 0)),
                    asset_count=int(row.get("asset_count", 0)),
                    platforms=[str(item) for item in (row.get("platforms") or []) if str(item).strip()],
                )
            )
        except Exception:
            continue
    return CampaignGenerationHistoryResponse(campaign_id=campaign.id, generations=items)


@router.post("/export")
@limiter.limit("10/minute")
def export_campaign_package(
    request: Request,
    data: CampaignPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Gera pacote ZIP com imagens e textos por plataforma (para download e publicação).
    Mesmo corpo do preview; executa o pipeline e retorna um arquivo ZIP.
    """
    login_url, login_user, login_pass = None, None, None
    if data.credentials_id:
        from app.services.credentials_service import get_plain_credentials
        login_url, login_user, login_pass = get_plain_credentials(db, data.credentials_id, current_user.id)
    if not login_url and (data.login_url or data.login_username or data.login_password):
        login_url, login_user, login_pass = data.login_url, data.login_username, data.login_password

    _validate_analysis_target(data.url, login_url)

    root = Path(__file__).resolve().parent.parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from ia_pipeline.pipeline import run_pipeline
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pipeline de IA não disponível.",
        )
    export_dir = root / "ia_pipeline" / "output" / f"export_{current_user.id}_{id(data)}"
    try:
        try:
            out = run_pipeline(
                url=data.url,
                campaign_title=data.campaign_title,
                platforms=[data.target_platform] if data.target_platform else (data.platforms or ["instagram", "facebook", "linkedin", "twitter", "tiktok", "youtube"]),
                login_url=login_url,
                login_user=login_user,
                login_pass=login_pass,
                output_dir=export_dir,
                source_urls=data.source_urls,
                max_crawl_pages=data.max_crawl_pages,
                max_crawl_depth=data.max_crawl_depth,
                objective=data.objective,
                follow_internal_links=data.follow_internal_links,
                capture_scroll_sections=data.capture_scroll_sections,
            )
            if out.error:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=out.error)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Falha ao executar o pipeline: {e}",
            )
        requested_platforms = sorted({str(p.platform).lower() for p in out.posts if getattr(p, "platform", None)})
        manifest = {
            "campaign_title": data.campaign_title,
            "source_url": data.url,
            "source_urls": data.source_urls or [],
            "platforms": requested_platforms,
            "post_count": len(out.posts or []),
        }
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
            zf.writestr("platforms.txt", "\n".join(requested_platforms).encode("utf-8"))
            for idx, p in enumerate(out.posts):
                prefix = f"{p.platform.lower().replace(' ', '_')}_{idx + 1:03d}"
                src = getattr(p, "source_page_url", "") or ""
                ptitle = getattr(p, "page_title", "") or ""
                caption_lines = [f"Pagina: {src}", f"Titulo site: {ptitle}", f"Plataformas do pacote: {', '.join(requested_platforms)}", "", p.title, "", p.text, "", " ".join(p.hashtags), ""]
                caption_lines.extend(f"{i+1}. {s}" for i, s in enumerate(p.steps))
                zf.writestr(f"{prefix}/caption.txt", "\n".join(caption_lines).encode("utf-8"))
                for i, img_path in enumerate(p.image_paths):
                    if Path(img_path).is_file():
                        zf.write(img_path, f"{prefix}/imagem_{i+1}.png")
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=marketingai-pacote.zip"},
        )
    finally:
        if export_dir.exists():
            shutil.rmtree(export_dir, ignore_errors=True)


@router.get("/preview/image")
def serve_preview_image(
    path: str,
    current_user: User = Depends(get_current_user),
):
    """Serve uma imagem gerada pelo pipeline (path relativo ao ia_pipeline/output)."""
    root = Path(__file__).resolve().parent.parent.parent.parent
    output_base = root / "ia_pipeline" / "output"
    path = path.lstrip("/")
    if ".." in path or path.startswith("/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path inv?lido")
    if not _path_belongs_to_user(current_user, path):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    full = (output_base / path).resolve()
    if not str(full).startswith(str(output_base.resolve())):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    if not full.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo n?o encontrado")
    guessed, _ = mimetypes.guess_type(str(full))
    media_type = guessed or "application/octet-stream"
    try:
        with full.open("rb") as handle:
            head = handle.read(256).lstrip()
        if head.startswith(b"<?xml") or head.startswith(b"<svg"):
            media_type = "image/svg+xml"
    except OSError:
        pass
    return FileResponse(full, media_type=media_type)
