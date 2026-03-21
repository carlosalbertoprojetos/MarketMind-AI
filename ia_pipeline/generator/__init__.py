"""Modulo de geracao de conteudo marketing."""

from .models import CopyVariation, GeneratedContentItem
from .service import generate_marketing_content

__all__ = ["CopyVariation", "GeneratedContentItem", "generate_marketing_content"]
