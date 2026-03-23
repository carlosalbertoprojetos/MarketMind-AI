"""Modulo de copywriting orientado por objetivo, publico e plataforma."""

from dataclasses import dataclass, field

from ia_pipeline import nlp
from ia_pipeline.analyzer.models import BusinessSummary
from ia_pipeline.generator.models import CopyVariation


@dataclass
class CopywritingOutput:
    hooks: list[str] = field(default_factory=list)
    narrative_structure: dict[str, str] = field(default_factory=dict)
    cta_options: list[str] = field(default_factory=list)
    ab_variations: list[CopyVariation] = field(default_factory=list)
    primary_copy: str = ""


PLATFORM_BLUEPRINTS = {
    "instagram": {
        "hook_templates": [
            "{value_prop} em uma tela: {screen_label}",
            "Como {audience} pode ganhar velocidade com {value_prop}",
            "O detalhe que transforma {screen_label} em conversao",
        ],
        "narrative_order": ["hook", "context", "proof", "cta"],
        "cta_templates": [
            "Salve este post e veja {cta}",
            "Envie para quem precisa de {keyword}",
            "Comente '{keyword}' para receber o proximo passo",
        ],
    },
    "tiktok": {
        "hook_templates": [
            "Se voce trabalha com {keyword}, precisa ver isso",
            "A tela que corta etapas para {audience}",
            "3 segundos para entender por que {value_prop} chama atencao",
        ],
        "narrative_order": ["hook", "problem", "solution", "cta"],
        "cta_templates": [
            "Comente 'quero' e veja {cta}",
            "Manda para o time que cuida de {keyword}",
            "Abre o link e testa antes do proximo concorrente",
        ],
    },
    "linkedin": {
        "hook_templates": [
            "{value_prop}: um caso claro para times de {audience}",
            "O que esta tela revela sobre eficiencia operacional",
            "Menos friccao, mais previsibilidade para {audience}",
        ],
        "narrative_order": ["hook", "context", "insight", "proof", "cta"],
        "cta_templates": [
            "Vale uma conversa com o time para avaliar {cta}",
            "Se fizer sentido para sua operacao, avance para {cta}",
            "Use este insight como criterio na sua proxima decisao",
        ],
    },
    "twitter": {
        "hook_templates": [
            "{value_prop} sem enrolacao.",
            "Uma tela. Um ganho claro para {audience}.",
            "Se {keyword} importa, isso aqui merece atencao.",
        ],
        "narrative_order": ["hook", "point", "proof", "cta"],
        "cta_templates": [
            "Quer ver {cta}? Abra o link.",
            "Se isso ajuda sua operacao, salve este post.",
            "Teste agora antes da proxima sprint.",
        ],
    },
    "youtube": {
        "hook_templates": [
            "Como {value_prop} muda a operacao de {audience}",
            "Analise completa da tela {screen_label}",
            "O que esta pagina mostra sobre {keyword}",
        ],
        "narrative_order": ["hook", "problem", "solution", "proof", "cta"],
        "cta_templates": [
            "Veja a demonstracao completa e avance para {cta}",
            "Use os pontos deste video para avaliar sua proxima compra",
            "Se quiser a estrutura aplicada no seu caso, parta para {cta}",
        ],
    },
    "facebook": {
        "hook_templates": [
            "Para quem busca {keyword}, esta tela chama atencao",
            "Uma historia simples sobre {value_prop}",
            "Como {audience} pode reduzir atrito com esta solucao",
        ],
        "narrative_order": ["hook", "story", "proof", "cta"],
        "cta_templates": [
            "Fale com a equipe e veja {cta}",
            "Compartilhe com quem esta avaliando {keyword}",
            "Se fizer sentido, avance para {cta}",
        ],
    },
}

OBJECTIVE_EMPHASIS = {
    "branding": {
        "context": "Reforce percepcao de marca e clareza de proposta de valor.",
        "cta": "Saiba mais e conheca a solucao.",
    },
    "engajamento": {
        "context": "Abra conversa com uma dor concreta e gere resposta imediata.",
        "cta": "Interaja com o conteudo e compartilhe com o time.",
    },
    "conversao": {
        "context": "Reduza friccao e explicite o proximo passo comercial.",
        "cta": "Avance para demonstracao, contato ou cadastro.",
    },
}


def _first(items: list[str], fallback: str = "") -> str:
    for item in items:
        text = (item or "").strip()
        if text:
            return text
    return fallback


def _compact(text: str) -> str:
    return " ".join((text or "").split())


def _limit(text: str, size: int) -> str:
    clean = _compact(text)
    if len(clean) <= size:
        return clean
    return clean[: max(0, size - 3)].rstrip(' ,.;:') + '...'


def _context_payload(platform: str, objective: str, page, business_summary: BusinessSummary) -> dict[str, str]:
    keyword = _first(page.keywords, _first(business_summary.keywords, business_summary.product_type or "resultado"))
    return {
        "platform": platform,
        "objective": objective,
        "audience": business_summary.target_audience or "equipes que precisam executar melhor",
        "value_prop": business_summary.value_proposition or page.primary_heading or page.page_title or "uma proposta clara de valor",
        "screen_label": page.screen_label or page.page_title or page.url,
        "keyword": keyword,
        "cta": _first(page.ctas, _first(business_summary.ctas, OBJECTIVE_EMPHASIS[objective]["cta"])),
        "differentiator": _first(business_summary.differentiators, _first(page.paragraphs, business_summary.summary)),
        "problem": _first(page.paragraphs, business_summary.summary),
        "proof": _first(business_summary.differentiators, _first(page.headings_h2, page.primary_heading)),
        "summary": business_summary.summary or _first(page.paragraphs),
    }


def _render(template: str, context: dict[str, str]) -> str:
    return _compact(template.format(**context))


def _build_hooks(platform: str, context: dict[str, str]) -> list[str]:
    hooks: list[str] = []
    for template in PLATFORM_BLUEPRINTS[platform]["hook_templates"]:
        hook = _render(template, context)
        if hook and hook not in hooks:
            hooks.append(hook)
    return hooks[:3]


def _build_narrative(platform: str, objective: str, page, business_summary: BusinessSummary, context: dict[str, str], hooks: list[str]) -> dict[str, str]:
    emphasis = OBJECTIVE_EMPHASIS[objective]
    sections = {
        "hook": hooks[0] if hooks else context["value_prop"],
        "problem": _limit(context["problem"], 180),
        "context": _limit(f"{context['summary']} {emphasis['context']}", 220),
        "story": _limit(f"{context['summary']} O diferencial aparece quando {context['differentiator'].lower()}.", 220),
        "insight": _limit(f"Para {context['audience']}, o ganho esta em {context['differentiator'].lower()}.", 200),
        "point": _limit(f"{context['value_prop']} com foco em {context['keyword']}.", 160),
        "solution": _limit(f"A resposta esta em {context['value_prop']}.", 180),
        "proof": _limit(context["proof"], 160),
        "cta": _limit(context["cta"], 140),
    }
    ordered = {}
    for key in PLATFORM_BLUEPRINTS[platform]["narrative_order"]:
        ordered[key] = sections[key]
    return ordered


def _build_ctas(platform: str, context: dict[str, str]) -> list[str]:
    ctas: list[str] = []
    for template in PLATFORM_BLUEPRINTS[platform]["cta_templates"]:
        cta = _render(template, context)
        if cta and cta not in ctas:
            ctas.append(cta)
    return ctas[:3]


def _join_narrative(narrative_structure: dict[str, str]) -> str:
    return " ".join(value for value in narrative_structure.values() if value).strip()


def _build_ab_variations(platform: str, narrative_structure: dict[str, str], cta_options: list[str]) -> list[CopyVariation]:
    ordered_values = [value for value in narrative_structure.values() if value]
    variation_a = nlp.adapt_for_platform(" ".join(ordered_values), platform)
    variation_b = nlp.adapt_for_platform(" ".join(reversed(ordered_values[:-1])) + (f" {cta_options[1]}" if len(cta_options) > 1 else f" {cta_options[0]}"), platform)
    return [
        CopyVariation(label="A", text=variation_a),
        CopyVariation(label="B", text=variation_b.strip()),
    ]


def generate_copywriting_output(platform: str, objective: str, page, business_summary: BusinessSummary) -> CopywritingOutput:
    normalized_platform = (platform or "").strip().lower()
    if normalized_platform == "x":
        normalized_platform = "twitter"
    if normalized_platform not in PLATFORM_BLUEPRINTS:
        raise ValueError(f"Plataforma de copywriting nao suportada: {platform}")
    normalized_objective = objective if objective in OBJECTIVE_EMPHASIS else "branding"

    context = _context_payload(normalized_platform, normalized_objective, page, business_summary)
    hooks = _build_hooks(normalized_platform, context)
    narrative_structure = _build_narrative(normalized_platform, normalized_objective, page, business_summary, context, hooks)
    cta_options = _build_ctas(normalized_platform, context)
    ab_variations = _build_ab_variations(normalized_platform, narrative_structure, cta_options)
    primary_copy = nlp.adapt_for_platform(_join_narrative(narrative_structure), normalized_platform)

    return CopywritingOutput(
        hooks=hooks,
        narrative_structure=narrative_structure,
        cta_options=cta_options,
        ab_variations=ab_variations,
        primary_copy=primary_copy,
    )
