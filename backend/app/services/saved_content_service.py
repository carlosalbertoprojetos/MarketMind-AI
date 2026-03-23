"""Persistencia de conteudos gerados salvos."""
import json
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.saved_content import SavedContent


DEFAULT_RESULT = {"posts": []}
DEFAULT_FINAL_RESULT = {"outputs": [], "ab_test_suggestions": []}
SUPPORTED_SAVED_CONTENT_PLATFORMS = {"instagram", "facebook", "linkedin", "twitter", "tiktok", "youtube"}


def _dump_json(value):
    return json.dumps(value if value is not None else {}, ensure_ascii=True, indent=2)


def _load_json(value, default):
    if not value:
        return default
    try:
        data = json.loads(value)
        if isinstance(data, (dict, list)):
            return data
    except Exception:
        pass
    return default


def _normalize_platform(value: str | None) -> str | None:
    if not value:
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None
    if normalized == "x":
        normalized = "twitter"
    if normalized not in SUPPORTED_SAVED_CONTENT_PLATFORMS:
        return None
    return normalized


def _normalize_platform_filters(platform: str | None = None, platforms: list[str] | None = None) -> list[str]:
    values: list[str] = []
    if platforms:
        values.extend(platforms)
    elif platform:
        values.extend(str(platform).split(","))
    normalized: list[str] = []
    seen: set[str] = set()
    for item in values:
        candidate = _normalize_platform(item)
        if candidate and candidate not in seen:
            seen.add(candidate)
            normalized.append(candidate)
    return normalized


def create_saved_content(
    db: Session,
    *,
    user_id: int,
    source_type: str,
    result_payload: dict,
    request_payload: dict | None = None,
    campaign_id: int | None = None,
    title: str | None = None,
    theme: str | None = None,
    objective: str | None = None,
    audience: str | None = None,
    style: str | None = None,
    platforms: list[str] | None = None,
    publish_results: list[dict] | None = None,
) -> SavedContent:
    record = SavedContent(
        user_id=user_id,
        campaign_id=campaign_id,
        source_type=source_type,
        title=title,
        theme=theme,
        objective=objective,
        audience=audience,
        style=style,
        platforms_json=_dump_json(platforms or []),
        request_payload=_dump_json(request_payload or {}),
        result_payload=_dump_json(result_payload),
        publish_results_payload=_dump_json(publish_results or []),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _parse_datetime_like(value: str | None, *, end_of_day: bool = False) -> datetime | None:
    if not value:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    try:
        if "T" in raw:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        else:
            suffix = "T23:59:59.999999" if end_of_day else "T00:00:00"
            dt = datetime.fromisoformat(raw + suffix)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def list_saved_contents(
    db: Session,
    user_id: int,
    *,
    source_type: str,
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
    platform: str | None = None,
    platforms: list[str] | None = None,
    created_from: str | None = None,
    created_to: str | None = None,
) -> tuple[list[SavedContent], int]:
    q = db.query(SavedContent).filter(SavedContent.user_id == user_id, SavedContent.source_type == source_type)
    if search and search.strip():
        like = f"%{search.strip()}%"
        q = q.filter(or_(SavedContent.title.ilike(like), SavedContent.theme.ilike(like), SavedContent.audience.ilike(like)))
    normalized_platforms = _normalize_platform_filters(platform=platform, platforms=platforms)
    if normalized_platforms:
        q = q.filter(or_(*[SavedContent.platforms_json.ilike(f'%"{item}"%') for item in normalized_platforms]))
    from_dt = _parse_datetime_like(created_from, end_of_day=False)
    if from_dt is not None:
        q = q.filter(SavedContent.created_at >= from_dt)
    to_dt = _parse_datetime_like(created_to, end_of_day=True)
    if to_dt is not None:
        q = q.filter(SavedContent.created_at <= to_dt)
    total = q.count()
    items = q.order_by(SavedContent.created_at.desc(), SavedContent.id.desc()).offset(max(0, offset)).limit(limit).all()
    return items, total


def get_saved_content_by_id(db: Session, saved_content_id: int, user_id: int, *, source_type: str | None = None) -> SavedContent | None:
    q = db.query(SavedContent).filter(SavedContent.id == saved_content_id, SavedContent.user_id == user_id)
    if source_type:
        q = q.filter(SavedContent.source_type == source_type)
    return q.first()


def get_latest_saved_campaign_content(db: Session, user_id: int, campaign_id: int) -> SavedContent | None:
    return (
        db.query(SavedContent)
        .filter(
            SavedContent.user_id == user_id,
            SavedContent.campaign_id == campaign_id,
            SavedContent.source_type == 'campaign',
        )
        .order_by(SavedContent.created_at.desc(), SavedContent.id.desc())
        .first()
    )


def delete_saved_content(db: Session, record: SavedContent) -> None:
    db.delete(record)
    db.commit()


def parse_saved_content_result(record: SavedContent):
    default = DEFAULT_FINAL_RESULT if record.source_type == 'final_content' else DEFAULT_RESULT
    return _load_json(record.result_payload, default)


def parse_saved_content_publish_results(record: SavedContent) -> list[dict]:
    data = _load_json(record.publish_results_payload, [])
    return data if isinstance(data, list) else []


def parse_saved_content_platforms(record: SavedContent) -> list[str]:
    data = _load_json(record.platforms_json, [])
    return [str(item) for item in data] if isinstance(data, list) else []
