"""Executa ciclos autonomos de evolucao de conteudo."""
import hashlib
from dataclasses import asdict

from ia_pipeline.autonomous.models import AutonomousCycleResult, PerformanceSignal
from ia_pipeline.runtime import get_logger, write_json_artifact


def _score_metrics(metrics: dict) -> float:
    engagement = float(metrics.get("engagement_rate", 0.0) or 0.0)
    click_rate = float(metrics.get("click_rate", 0.0) or 0.0)
    conversion_rate = float(metrics.get("conversion_rate", 0.0) or 0.0)
    return round((engagement * 0.45) + (click_rate * 0.30) + (conversion_rate * 0.25), 4)


def run_autonomous_cycle(generated_contents: list[dict], performance_data: list[dict] | None = None) -> AutonomousCycleResult:
    logger = get_logger("marketingai.autonomous")
    performance_data = performance_data or []
    metrics_by_key = {
        (str(item.get("platform", "")), str(item.get("source_page_url", ""))): item
        for item in performance_data
    }

    signals: list[PerformanceSignal] = []
    for content in generated_contents or []:
        key = (str(content.get("platform", "")), str(content.get("source_page_url", "")))
        metrics = metrics_by_key.get(
            key,
            {
                "engagement_rate": 0.18 if "instagram" in key[0] else 0.12,
                "click_rate": 0.07 if "linkedin" in key[0] else 0.05,
                "conversion_rate": 0.04 if "pricing" in str(content.get("screen_type", "")) else 0.02,
            },
        )
        winning_elements = []
        if content.get("screen_type") in ("pricing", "case_study"):
            winning_elements.append("prova de valor")
        if content.get("headlines"):
            winning_elements.append("headline forte")
        if content.get("visual_suggestions"):
            winning_elements.append("criativo contextual")
        signals.append(
            PerformanceSignal(
                platform=key[0],
                source_page_url=key[1],
                engagement_rate=float(metrics.get("engagement_rate", 0.0) or 0.0),
                click_rate=float(metrics.get("click_rate", 0.0) or 0.0),
                conversion_rate=float(metrics.get("conversion_rate", 0.0) or 0.0),
                score=_score_metrics(metrics),
                winning_elements=winning_elements,
            )
        )

    signals.sort(key=lambda item: item.score, reverse=True)
    top_signals = signals[:3]
    improvement_actions: list[str] = []
    evolved_prompt_hints: list[str] = []
    evolved_copy_hints: list[str] = []

    if top_signals:
        best = top_signals[0]
        improvement_actions.append(f"Priorizar paginas e angulos parecidos com {best.source_page_url} em {best.platform}.")
        if best.engagement_rate >= 0.15:
            evolved_copy_hints.append("Manter abertura forte e gancho nos dois primeiros periodos.")
        if best.click_rate >= 0.05:
            evolved_copy_hints.append("Reforcar CTA de proximo passo com urgencia moderada.")
        if best.conversion_rate >= 0.03:
            evolved_prompt_hints.append("Usar criativos com contexto de produto e prova de valor.")

    low_signals = [signal for signal in signals if signal.score < 0.08]
    if low_signals:
        improvement_actions.append("Reduzir posts excessivamente genericos e aumentar alinhamento com dores especificas.")
        evolved_copy_hints.append("Trocar descricoes vagas por beneficios concretos e numericos sempre que houver.")
        evolved_prompt_hints.append("Incluir cenas mais especificas do ambiente do cliente ideal.")

    next_objective = "conversao" if any(signal.conversion_rate >= 0.03 for signal in top_signals) else "engajamento"
    if not top_signals:
        next_objective = "branding"

    cycle_id = hashlib.md5(str([(signal.platform, signal.source_page_url, signal.score) for signal in signals]).encode("utf-8", errors="ignore")).hexdigest()[:12]
    result = AutonomousCycleResult(
        cycle_id=cycle_id,
        status="completed",
        performance_signals=signals,
        improvement_actions=improvement_actions or ["Coletar mais dados para detectar padroes confiaveis."],
        next_objective=next_objective,
        evolved_prompt_hints=evolved_prompt_hints or ["Explorar mais contexto visual das paginas com melhor fit."],
        evolved_copy_hints=evolved_copy_hints or ["Testar variacoes de copy com CTA mais claro e tom mais especifico."],
    )
    logger.info("Autonomous cycle completed with %s signals", len(signals))
    write_json_artifact(f"autonomous/cycles/{cycle_id}.json", result)
    return result
