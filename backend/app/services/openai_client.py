from __future__ import annotations

from functools import lru_cache

from app.core.config import settings


@lru_cache(maxsize=1)
def get_openai_client():
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError(
            "OpenAI SDK not installed. Add 'openai' to your environment."
        ) from exc

    return OpenAI(
        api_key=settings.OPENAI_API_KEY,
        organization=settings.OPENAI_ORG_ID,
        project=settings.OPENAI_PROJECT_ID,
        max_retries=2,
        timeout=20.0,
    )
