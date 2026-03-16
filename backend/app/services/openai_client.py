from __future__ import annotations

from functools import lru_cache

from openai import OpenAI

from app.core.config import settings


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    return OpenAI(
        api_key=settings.OPENAI_API_KEY,
        organization=settings.OPENAI_ORG_ID,
        project=settings.OPENAI_PROJECT_ID,
        max_retries=2,
        timeout=20.0,
    )