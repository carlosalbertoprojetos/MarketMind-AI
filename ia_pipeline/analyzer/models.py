"""Modelos para entendimento de negocio."""

from dataclasses import dataclass, field


@dataclass
class BusinessSummary:
    source_url: str
    product_type: str = ""
    value_proposition: str = ""
    target_audience: str = ""
    differentiators: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    ctas: list[str] = field(default_factory=list)
    summary: str = ""
    screen_inventory: list[dict] = field(default_factory=list)
