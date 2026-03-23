"""Infraestrutura comum para o pipeline autonomo."""
import json
import logging
import os
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any


@dataclass
class PipelineConfig:
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    openai_model: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    image_provider: str = os.environ.get("MARKETINGAI_IMAGE_PROVIDER", "auto")
    image_style: str = os.environ.get("MARKETINGAI_IMAGE_STYLE", "modern")
    image_variations: int = int(os.environ.get("MARKETINGAI_IMAGE_VARIATIONS", "2"))
    stable_diffusion_url: str = os.environ.get("STABLE_DIFFUSION_API_URL", "")
    stable_diffusion_api_key: str = os.environ.get("STABLE_DIFFUSION_API_KEY", "")
    publisher_mode: str = os.environ.get("MARKETINGAI_PUBLISHER_MODE", "mock")
    instagram_access_token: str = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    instagram_account_id: str = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
    facebook_page_access_token: str = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    facebook_page_id: str = os.environ.get("FACEBOOK_PAGE_ID", "")
    linkedin_access_token: str = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    linkedin_organization_id: str = os.environ.get("LINKEDIN_ORGANIZATION_ID", "")
    twitter_api_key: str = os.environ.get("TWITTER_API_KEY", "")
    twitter_api_secret: str = os.environ.get("TWITTER_API_SECRET", "")
    twitter_access_token: str = os.environ.get("TWITTER_ACCESS_TOKEN", "")
    twitter_access_token_secret: str = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "")
    tiktok_access_token: str = os.environ.get("TIKTOK_ACCESS_TOKEN", "")
    tiktok_account_id: str = os.environ.get("TIKTOK_ACCOUNT_ID", "")
    tiktok_privacy_level: str = os.environ.get("TIKTOK_PRIVACY_LEVEL", "PUBLIC_TO_EVERYONE")
    youtube_access_token: str = os.environ.get("YOUTUBE_ACCESS_TOKEN", "")
    youtube_channel_id: str = os.environ.get("YOUTUBE_CHANNEL_ID", "")
    queue_retry_limit: int = int(os.environ.get("MARKETINGAI_QUEUE_RETRY_LIMIT", "3"))
    queue_retry_delay_seconds: int = int(os.environ.get("MARKETINGAI_QUEUE_RETRY_DELAY_SECONDS", "5"))
    max_crawl_pages: int = int(os.environ.get("MARKETINGAI_MAX_CRAWL_PAGES", "5"))
    max_crawl_depth: int = int(os.environ.get("MARKETINGAI_MAX_CRAWL_DEPTH", "2"))
    agent_max_cycles: int = int(os.environ.get("MARKETINGAI_AGENT_MAX_CYCLES", "2"))
    agent_debug: bool = os.environ.get("MARKETINGAI_AGENT_DEBUG", "false").lower() in ("1", "true", "yes")
    auto_publish_default: bool = os.environ.get("MARKETINGAI_AUTO_PUBLISH_DEFAULT", "false").lower() in ("1", "true", "yes")
    output_dir: Path = Path(os.environ.get("MARKETINGAI_OUTPUT_DIR", str(Path(__file__).resolve().parent / "output")))
    log_level: str = os.environ.get("MARKETINGAI_LOG_LEVEL", "INFO")
    tenant_id: str = os.environ.get("MARKETINGAI_TENANT_ID", "default")


def get_pipeline_config() -> PipelineConfig:
    return PipelineConfig()


def get_logger(name: str = "marketingai") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    config = get_pipeline_config()
    logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    log_dir = config.output_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "pipeline.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger


def ensure_output_path(*parts: str) -> Path:
    config = get_pipeline_config()
    path = config.output_dir.joinpath(*parts)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _normalize_payload(payload: Any) -> Any:
    if is_dataclass(payload):
        return asdict(payload)
    if isinstance(payload, Path):
        return str(payload)
    if isinstance(payload, dict):
        return {str(key): _normalize_payload(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_normalize_payload(item) for item in payload]
    return payload


def write_json_artifact(relative_path: str, payload: Any) -> Path:
    config = get_pipeline_config()
    path = config.output_dir / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_normalize_payload(payload), ensure_ascii=True, indent=2), encoding="utf-8")
    return path


def is_production_environment() -> bool:
    return os.environ.get("MARKETINGAI_ENV", "development").strip().lower() == "production"


def mocks_allowed_in_runtime() -> bool:
    return os.environ.get("MARKETINGAI_ALLOW_MOCKS", "false").strip().lower() in ("1", "true", "yes")
