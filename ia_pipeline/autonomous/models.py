"""Modelos do ciclo autonomo."""
from dataclasses import dataclass, field


@dataclass
class PerformanceSignal:
    platform: str
    source_page_url: str
    engagement_rate: float = 0.0
    click_rate: float = 0.0
    conversion_rate: float = 0.0
    score: float = 0.0
    winning_elements: list[str] = field(default_factory=list)


@dataclass
class AutonomousCycleResult:
    cycle_id: str
    status: str
    performance_signals: list[PerformanceSignal] = field(default_factory=list)
    improvement_actions: list[str] = field(default_factory=list)
    next_objective: str = "branding"
    evolved_prompt_hints: list[str] = field(default_factory=list)
    evolved_copy_hints: list[str] = field(default_factory=list)
