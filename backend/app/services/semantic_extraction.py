from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class SemanticExtraction:
    features: list[str]
    benefits: list[str]
    value_proposition: str
    target_audience: list[str]
    differentiators: list[str]
    use_cases: list[str]


def _extract_lines(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text)
    parts = re.split(r"[\n\r\t]+", cleaned)
    lines = [part.strip() for part in parts if part.strip()]
    if not lines:
        lines = [chunk.strip() for chunk in cleaned.split(".") if chunk.strip()]
    return lines


def _find_by_keywords(lines: list[str], keywords: list[str], limit: int = 5) -> list[str]:
    matches: list[str] = []
    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in keywords):
            matches.append(line)
        if len(matches) >= limit:
            break
    return matches


def extract_semantics(text: str) -> SemanticExtraction:
    lines = _extract_lines(text)

    features = _find_by_keywords(lines, ["feature", "funcional", "capability", "capacidade"]) or lines[:3]
    benefits = _find_by_keywords(lines, ["benefit", "beneficio", "resultado", "impacto"]) or lines[3:6]
    value_candidates = _find_by_keywords(lines, ["value", "proposta", "valor"]) or lines[:1]
    value_proposition = value_candidates[0] if value_candidates else "Plataforma de inteligencia de marketing."

    target_audience = _find_by_keywords(lines, ["audience", "target", "publico", "clientes"]) or [
        "SaaS B2B",
        "Marketing teams",
    ]
    differentiators = _find_by_keywords(lines, ["differentiator", "diferencial", "unique", "exclusivo"]) or [
        "Automacao ponta a ponta",
        "IA multi-agente",
    ]
    use_cases = _find_by_keywords(lines, ["use case", "caso de uso", "aplicacao"]) or [
        "Lancar campanhas",
        "Gerar conteudo multiformato",
    ]

    return SemanticExtraction(
        features=features,
        benefits=benefits,
        value_proposition=value_proposition,
        target_audience=target_audience,
        differentiators=differentiators,
        use_cases=use_cases,
    )