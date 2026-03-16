from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.models.persona import Persona
from app.models.product import Product


@dataclass(slots=True)
class NarrativeResult:
    problem: str
    diagnosis: str
    solution: str
    demonstration: str
    social_proof: str
    cta: str
    angles: list[str]


def build_narrative(product: Product, persona: Persona | None = None) -> NarrativeResult:
    audience = persona.profile if persona else "times de marketing B2B"
    return NarrativeResult(
        problem=f"{audience} sofrem com falta de previsibilidade em campanhas.",
        diagnosis="Dados fragmentados e processos manuais atrasam o time.",
        solution=f"{product.name} orquestra agentes de IA para acelerar planejamento e execucao.",
        demonstration="Pipeline inteligente gera conteudo, agenda e otimiza com analytics.",
        social_proof="Times SaaS reduziram o ciclo de campanha em 40%.",
        cta="Agende uma demo e veja a automacao em acao.",
        angles=["eficiencia", "crescimento", "previsibilidade"],
    )