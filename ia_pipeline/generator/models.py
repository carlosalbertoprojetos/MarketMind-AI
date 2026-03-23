"""Modelos de geracao de conteudo."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CopyVariation:
    label: str
    text: str


@dataclass
class GeneratedContentItem:
    platform: str
    objective: str
    source_page_url: str
    screen_type: str
    screen_label: str
    headlines: list[str] = field(default_factory=list)
    persuasive_text: str = ""
    copy_variations: list[CopyVariation] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    visual_suggestions: list[str] = field(default_factory=list)
    content_format: str = ""
    primary_cta: str = ""
    platform_rules: dict[str, Any] = field(default_factory=dict)
    structured_output: dict[str, Any] = field(default_factory=dict)
    hooks: list[str] = field(default_factory=list)
    narrative_structure: dict[str, str] = field(default_factory=dict)
    cta_options: list[str] = field(default_factory=list)
    ab_variations: list[CopyVariation] = field(default_factory=list)
