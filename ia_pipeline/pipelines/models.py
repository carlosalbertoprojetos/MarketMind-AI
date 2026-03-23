"""Modelos do pipeline final de conteudo."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FinalPlatformContent:
    platform: str
    objective: str
    audience: str
    content_format: str
    full_content: str
    hooks: list[str] = field(default_factory=list)
    narrative_structure: dict[str, str] = field(default_factory=dict)
    cta_options: list[str] = field(default_factory=list)
    ab_variations: list[dict[str, str]] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    structured_output: dict[str, Any] = field(default_factory=dict)
    image_prompt: str = ""
    visual_decision: dict[str, Any] = field(default_factory=dict)


@dataclass
class FinalABTestSuggestion:
    platform: str
    hypothesis: str
    variant_a: str
    variant_b: str
    success_metric: str


@dataclass
class FinalContentPipelineResult:
    theme: str
    objective: str
    audience: str
    outputs: list[FinalPlatformContent] = field(default_factory=list)
    ab_test_suggestions: list[FinalABTestSuggestion] = field(default_factory=list)
