"""
MarketingAI - Pipeline NLP (Etapa 5).

- Extrai funcionalidades, diferenciais e público-alvo do produto.
- Gera headlines, descrições, CTAs e roteiros de vídeo.
- Adapta conteúdo por rede social (formatos, tamanho, hashtags).
"""
import json
import os
import re
import collections
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# Prompts
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# Limites e regras por plataforma (caracteres e sugestão de hashtags)
PLATFORM_SPECS = {
    "instagram": {
        "caption_max": 2200,
        "rules": "Máximo 2200 caracteres na legenda. Até 30 hashtags no final. Tom visual e direto.",
        "hashtag_suggestion_count": 10,
    },
    "facebook": {
        "caption_max": 50000,
        "rules": "Texto pode ser longo. Foco em benefícios e storytelling. CTA claro.",
        "hashtag_suggestion_count": 5,
    },
    "linkedin": {
        "caption_max": 3000,
        "rules": "Tom profissional. Sem emojis em excesso. Foco em valor e credibilidade.",
        "hashtag_suggestion_count": 5,
    },
    "twitter": {
        "caption_max": 280,
        "rules": "Máximo 280 caracteres. Objetivo e impactante. Hashtags 2-3.",
        "hashtag_suggestion_count": 3,
    },
    "tiktok": {
        "caption_max": 150,
        "rules": "Legenda curta, até 150 caracteres. Tom jovem e dinâmico.",
        "hashtag_suggestion_count": 5,
    },
    "youtube": {
        "caption_max": 5000,
        "rules": "Descricao mais completa, com promessa clara, contexto, CTA e foco em retencao.",
        "hashtag_suggestion_count": 5,
    },
    "x": {
        "caption_max": 280,
        "rules": "Maximo 280 caracteres. Objetivo e impactante. Hashtags 2-3.",
        "hashtag_suggestion_count": 3,
    },
}


@dataclass
class MarketingInsights:
    """Resultado da análise de marketing."""
    funcionalidades: list[str] = field(default_factory=list)
    diferenciais: list[str] = field(default_factory=list)
    publico_alvo: str = ""
    headlines: list[str] = field(default_factory=list)
    descricoes_curtas: list[str] = field(default_factory=list)
    ctas: list[str] = field(default_factory=list)
    roteiro_video: str = ""


def _load_prompt(name: str) -> str:
    p = PROMPTS_DIR / name
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


def _call_llm(prompt: str, content: str = "") -> str:
    """
    Chama modelo de linguagem. Sem API key retorna string vazia (usa análise heurística).
    """
    message = prompt.format(content=content) if "{content}" in prompt else prompt
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return ""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        r = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": message}],
            max_tokens=2000,
        )
        return r.choices[0].message.content
    except Exception:
        pass
    return ""


_PT_STOPWORDS = frozenset(
    """
    a o os as um uma uns umas de do da dos das em no na nos nas por para com sem sob sobre
    ao à aos às pelo pela pelos pelas quando que onde qual quais como mas ou se já então
    este essa estes essas esse essa esses essas isto isso aquilo ele ela eles elas eu tu nós
    vos me te nos vos lhe lhes mais menos muito pouco todo toda todos todas ser estar ter
    foi são era eram será seja sejam há ho havia teria poder deve pode faz fez fazem diz
    também apenas assim bem como tal onde mesmo outros outras outro outra um uma the and or
    of to in for on at by from with is are was were be been being it its this that these
    those not no yes all any both each few most other some such than too very can will just
    don should now d com br www html http https
    """.split()
)


def _clip_text(s: str, max_len: int, ellipsis: str = "…") -> str:
    s = " ".join(s.split())
    if not s:
        return ""
    if len(s) <= max_len:
        return s
    return s[: max(0, max_len - len(ellipsis))].rstrip(",.;: ") + ellipsis


def _heuristic_marketing_insights(content: str) -> MarketingInsights:
    """
    Gera headlines, descrições e bullets a partir do texto real capturado do site (OCR / página),
    sem depender de placeholders genéricos.
    """
    raw = (content or "").strip()
    if not raw:
        return MarketingInsights(
            funcionalidades=[
                "Não houve texto capturado do site (OCR vazio ou página sem conteúdo legível na captura).",
            ],
            diferenciais=["Tente gerar de novo ou confira se a URL está acessível e o Playwright capturou a página."],
            publico_alvo="Público interessado no produto ou serviço divulgado no site informado.",
            headlines=[
                "Refaça a geração após uma captura com texto legível",
                "Conteúdo de marketing precisa de texto extraído do site",
                "Confirme a URL e o scraping antes de publicar",
            ],
            descricoes_curtas=[
                "Não há texto suficiente extraído do site nesta execução. Gere de novo após confirmar que a página foi capturada (screenshot + OCR).",
                "Sites muito visuais ou com bloqueios podem retornar pouco texto; valide a URL e, se precisar, credenciais de acesso.",
            ],
            ctas=["Saiba mais no site", "Confira agora", "Acesse e conheça"],
            roteiro_video="[0-5s] Gancho com o principal benefício. [5-20s] Problema e como o site resolve. [20-30s] CTA para conversão.",
        )

    flat = " ".join(raw.split())
    snippet = flat[:12000]
    # Frases por pontuação; se monolítico, fatias por tamanho
    parts = re.split(r"(?<=[.!?…])\s+", snippet)
    parts = [p.strip() for p in parts if len(p.strip()) > 12]
    if len(parts) < 2:
        chunk = 180
        parts = [snippet[i : i + chunk] for i in range(0, min(len(snippet), chunk * 4), chunk)]
        parts = [p.strip() for p in parts if len(p.strip()) > 12]
    if not parts:
        parts = [_clip_text(snippet, 300)]

    h1 = _clip_text(parts[0], 60)
    h2 = _clip_text(parts[1], 60) if len(parts) > 1 else _clip_text(h1[:55] + " — oferta", 60)
    h3 = _clip_text(parts[2], 60) if len(parts) > 2 else _clip_text("Destaques que seu público precisa ver", 60)
    d1 = _clip_text(parts[0], 125)
    d2 = _clip_text(parts[1], 125) if len(parts) > 1 else _clip_text(parts[0][len(d1) :] or parts[0], 125)

    funcs = [_clip_text(p, 90) for p in parts[:3]]
    difs = [_clip_text(p, 90) for p in parts[1:4]] if len(parts) > 1 else ["Proposta alinhada ao tom do site capturado."]
    publico = _clip_text(
        f"Pessoas e empresas buscando soluções ligadas a: {parts[0][:100]}",
        200,
    )

    return MarketingInsights(
        funcionalidades=funcs or [_clip_text(snippet, 120)],
        diferenciais=difs,
        publico_alvo=publico,
        headlines=[h1, h2, h3],
        descricoes_curtas=[d1, d2],
        ctas=["Conheça no site", "Garanta sua vantagem", "Fale com a equipe"],
        roteiro_video=f"[0-5s] {h1} [5-15s] {d1} [15-25s] {d2} [25-30s] CTA: acesse o site.",
    )


def _parse_insights_from_llm_raw(raw: str) -> MarketingInsights | None:
    if not raw or not raw.strip():
        return None
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return MarketingInsights(
        funcionalidades=data.get("funcionalidades", []),
        diferenciais=data.get("diferenciais", []),
        publico_alvo=data.get("publico_alvo", ""),
        headlines=data.get("headlines", []),
        descricoes_curtas=data.get("descricoes_curtas", []),
        ctas=data.get("ctas", []),
        roteiro_video=data.get("roteiro_video", ""),
    )


def _is_placeholder_insights(insights: MarketingInsights) -> bool:
    blob = " ".join(
        (insights.headlines or [])
        + (insights.descricoes_curtas or [])
        + [insights.publico_alvo or ""]
    ).lower()
    bad = ("headline impactante", "descrição curta para anúncio", "diferencial 1", "recursos extraídos do conteúdo")
    return any(b in blob for b in bad)


def _call_llm_raw(full_message: str) -> str:
    """Chama o LLM com uma única mensagem (sem template). Para adaptação de texto."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return ""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        r = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": full_message}],
            max_tokens=500,
        )
        return (r.choices[0].message.content or "").strip()
    except Exception:
        pass
    return ""


def extract_marketing_insights(content: str) -> MarketingInsights:
    """
    Extrai insights de marketing: LLM quando OPENAI_API_KEY está definida;
    caso contrário (ou JSON inválido), usa análise heurística do texto capturado do site.
    """
    content = (content or "").strip()
    if not content:
        return _heuristic_marketing_insights("")

    prompt = _load_prompt("marketing.txt")
    if not prompt:
        prompt = "Analise o seguinte conteúdo e retorne um JSON com: funcionalidades (lista), diferenciais (lista), publico_alvo (string), headlines (lista de 3), descricoes_curtas (lista de 2), ctas (lista de 3), roteiro_video (string). Conteúdo:\n\n{content}"

    raw = _call_llm(prompt, content[:12000])
    if raw.strip():
        llm_insights = _parse_insights_from_llm_raw(raw)
        if llm_insights and llm_insights.headlines and llm_insights.descricoes_curtas and not _is_placeholder_insights(llm_insights):
            return llm_insights
        if llm_insights and _is_placeholder_insights(llm_insights):
            base = _heuristic_marketing_insights(content)
            # Mescla: prefira campos úteis do LLM
            if llm_insights.ctas:
                base.ctas = llm_insights.ctas[:3]
            if llm_insights.roteiro_video and "gancho" not in llm_insights.roteiro_video.lower():
                base.roteiro_video = llm_insights.roteiro_video
            return base

    return _heuristic_marketing_insights(content)


def adapt_for_platform(text: str, platform: str) -> str:
    """
    Adapta o texto para a rede social (limite de caracteres e regras de estilo).
    Se platform não estiver em PLATFORM_SPECS, retorna o texto truncado em 280 chars.
    """
    spec = PLATFORM_SPECS.get(platform.lower(), {"caption_max": 280, "rules": "Seja objetivo."})
    max_len = spec["caption_max"]
    rules = spec.get("rules", "")
    prompt_tpl = _load_prompt("social_adapt.txt")
    if prompt_tpl:
        full_prompt = prompt_tpl.format(platform=platform, rules=rules, text=text)
        adapted = _call_llm_raw(full_prompt)
        if not adapted:
            adapted = text
        adapted = adapted.strip().strip('"')
        if len(adapted) > max_len:
            adapted = adapted[: max_len - 3] + "..."
        return adapted
    # Sem prompt/LLM: apenas truncar
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def _hashtags_from_llm(
    platform: str,
    count: int,
    insights: MarketingInsights,
    content_snippet: str,
    campaign_hint: str,
) -> list[str]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return []
    ctx = "\n".join(
        [
            f"Público-alvo: {insights.publico_alvo}",
            f"Headlines: {insights.headlines}",
            f"Funcionalidades: {insights.funcionalidades[:5]}",
            f"Diferenciais: {insights.diferenciais[:5]}",
            f"Trecho do site: {content_snippet[:2500]}",
            f"Campanha / URL: {campaign_hint[:500]}",
        ]
    )
    msg = f"""Você é especialista em social media no Brasil.
Plataforma: {platform}.
Com base no contexto abaixo, sugira {count} hashtags em português ou inglês (conforme o nicho), SEM repetição,
altamente relevantes ao nicho, público, intenção de busca e conversão. Evite hashtags genéricas (#love, #insta),
fragmentos de URL (#https, #www, #com), e palavras vazias.
Retorne APENAS uma linha: hashtags separadas por espaço, cada uma começando com #.

Contexto:
{ctx}
"""
    try:
        import openai
        client = getattr(openai, "OpenAI", None) or openai
        r = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": msg}],
            max_tokens=400,
        )
        line = r.choices[0].message.content.strip()
        tags = [t.strip() for t in line.split() if t.strip().startswith("#")]
        # filtra lixo
        clean = []
        for t in tags:
            low = t.lower()
            if any(x in low for x in ("#http", "#www", "#com", "#html", "#br")):
                continue
            if len(low) < 4 or not any(c.isalpha() for c in t):
                continue
            clean.append(t)
        return clean[:count]
    except Exception:
        return []


def _hashtags_heuristic(
    theme: str,
    platform: str,
    count: int,
    insights: Optional[MarketingInsights] = None,
    content_snippet: str = "",
) -> list[str]:
    blob = " ".join(
        [
            theme,
            content_snippet or "",
            " ".join(insights.headlines) if insights else "",
            " ".join(insights.funcionalidades) if insights else "",
            " ".join(insights.diferenciais) if insights else "",
            insights.publico_alvo if insights else "",
        ]
    )
    blob = re.sub(r"https?://\S+", " ", blob, flags=re.I)
    blob = re.sub(r"[^\w\sáàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ-]", " ", blob)
    words = blob.lower().split()
    filtered = []
    for w in words:
        w = w.strip("-_")
        if len(w) < 3 or w in _PT_STOPWORDS:
            continue
        if w.isdigit():
            continue
        filtered.append(w)
    freq = collections.Counter(filtered)
    # prioriza termos mais longos (costumam ser mais específicos)
    candidates = sorted(freq.keys(), key=lambda x: (freq[x], len(x)), reverse=True)
    seen = set()
    tags = []
    for w in candidates:
        if w in seen:
            continue
        tag = "#" + re.sub(r"[^a-z0-9áàâãéêíóôõúüç]", "", w, flags=re.I)
        if len(tag) < 4 or tag.lower() in ("#com", "#para", "#como"):
            continue
        seen.add(w)
        tags.append(tag)
        if len(tags) >= count:
            break
    # variação por plataforma: twitter menos tags
    return tags[:count]


def suggest_hashtags(
    theme: str,
    platform: str,
    count: int | None = None,
    *,
    insights: Optional[MarketingInsights] = None,
    content_snippet: str = "",
) -> list[str]:
    """
    Hashtags por contexto (LLM se houver API key; senão heurística sobre conteúdo + insights).
    """
    n = count or PLATFORM_SPECS.get(platform.lower(), {}).get("hashtag_suggestion_count", 5)
    ins = insights or MarketingInsights()
    ctx = content_snippet or theme
    llm_tags = _hashtags_from_llm(platform, n, ins, ctx, theme)
    if len(llm_tags) >= max(3, min(n, 4)):
        return llm_tags[:n]
    base = _hashtags_heuristic(theme, platform, n, ins, ctx)
    if llm_tags:
        merged = []
        seen = set(x.lower() for x in base)
        for t in llm_tags + base:
            if t.lower() not in seen:
                seen.add(t.lower())
                merged.append(t)
            if len(merged) >= n:
                break
        return merged[:n]
    return base[:n]


if __name__ == "__main__":
    sample = "App de gestão financeira para PMEs. Controle de fluxo de caixa, relatórios e integração com bancos."
    insights = extract_marketing_insights(sample)
    print("Headlines:", insights.headlines)
    print("CTAs:", insights.ctas)
    print("Adaptado Twitter:", adapt_for_platform(insights.descricoes_curtas[0] if insights.descricoes_curtas else sample, "twitter"))
    print("Hashtags:", suggest_hashtags("gestão financeira PME", "instagram"))
