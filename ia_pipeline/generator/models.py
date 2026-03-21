"""Modelos de geracao de conteudo."""

from dataclasses import dataclass, field


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
