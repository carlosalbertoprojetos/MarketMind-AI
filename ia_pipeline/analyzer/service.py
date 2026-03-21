"""Analisa o conteudo extraido e gera entendimento estruturado do negocio."""

from .models import BusinessSummary
from ia_pipeline import nlp
from ia_pipeline.parser.models import ParsedSiteContent


def _infer_product_type(text: str) -> str:
    low = (text or "").lower()
    if any(term in low for term in ("saas", "software", "plataforma", "app", "aplicativo")):
        return "software"
    if any(term in low for term in ("curso", "treinamento", "mentoria", "aula")):
        return "educacao"
    if any(term in low for term in ("loja", "e-commerce", "ecommerce", "comprar", "produto fisico")):
        return "ecommerce"
    if any(term in low for term in ("agencia", "consultoria", "servico", "solucao")):
        return "servicos"
    return "negocio digital"


def analyze_business(parsed_site: ParsedSiteContent) -> BusinessSummary:
    all_text = " ".join(page.clean_text for page in parsed_site.pages if page.clean_text).strip()
    insights = nlp.extract_marketing_insights(all_text[:12000])
    product_type = _infer_product_type(all_text)

    value_proposition = ""
    for candidate in [
        *(page.primary_heading for page in parsed_site.pages if page.primary_heading),
        *(page.meta_description for page in parsed_site.pages if page.meta_description),
        *(insights.headlines or []),
        *(insights.descricoes_curtas or []),
    ]:
        if candidate and len(candidate.strip()) >= 12:
            value_proposition = candidate.strip()[:240]
            break

    target_audience = (insights.publico_alvo or "").strip()
    if not target_audience:
        top_keywords = ", ".join(parsed_site.global_keywords[:5])
        target_audience = f"Publico interessado em {top_keywords}" if top_keywords else "Publico com interesse no produto ou servico"

    differentiators = [item.strip() for item in (insights.diferenciais or []) if item and item.strip()]
    if not differentiators:
        differentiators = [item.strip() for item in parsed_site.global_ctas[:3] if item.strip()]
    if not differentiators:
        differentiators = [item.strip() for item in parsed_site.global_keywords[:3] if item.strip()]

    screen_inventory = [
        {
            "url": page.url,
            "screen_type": page.screen_type,
            "screen_label": page.screen_label,
            "keywords": page.keywords[:5],
            "ctas": page.ctas[:3],
        }
        for page in parsed_site.pages
    ]

    summary_parts = [
        f"Tipo de negocio: {product_type}.",
        f"Proposta de valor: {value_proposition or 'Nao identificada com clareza.'}",
        f"Publico-alvo: {target_audience}.",
    ]
    if differentiators:
        summary_parts.append(f"Diferenciais: {'; '.join(differentiators[:4])}.")

    return BusinessSummary(
        source_url=parsed_site.source_url,
        product_type=product_type,
        value_proposition=value_proposition,
        target_audience=target_audience,
        differentiators=differentiators[:6],
        keywords=parsed_site.global_keywords[:15],
        ctas=parsed_site.global_ctas[:8],
        summary=" ".join(summary_parts).strip(),
        screen_inventory=screen_inventory,
    )
