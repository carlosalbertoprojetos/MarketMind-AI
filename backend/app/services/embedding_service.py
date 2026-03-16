from __future__ import annotations

import hashlib
import random

from app.core.config import settings
from app.services.openai_client import get_openai_client


def generate_embedding(text: str, dims: int | None = None, use_openai: bool = True) -> list[float]:
    if use_openai and settings.OPENAI_API_KEY:
        client = get_openai_client()
        payload = {
            "model": settings.OPENAI_EMBEDDING_MODEL,
            "input": text,
            "encoding_format": "float",
        }
        if dims or settings.OPENAI_EMBEDDING_DIM:
            payload["dimensions"] = dims or settings.OPENAI_EMBEDDING_DIM
        response = client.embeddings.create(**payload)
        return response.data[0].embedding

    dims = dims or settings.OPENAI_EMBEDDING_DIM
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(dims)]
