"""Modelos do orquestrador."""
from dataclasses import dataclass, field


@dataclass
class OrchestratedRunResult:
    url: str
    platform: str
    objective: str
    business_summary: dict = field(default_factory=dict)
    generated_contents: list[dict] = field(default_factory=list)
    image_assets: list[dict] = field(default_factory=list)
    publish_results: list[dict] = field(default_factory=list)
    autonomous_cycle: dict = field(default_factory=dict)
    status: str = "completed"
    error: str = ""
