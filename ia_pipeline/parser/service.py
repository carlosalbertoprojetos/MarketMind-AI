"""Extrai informacoes estruturadas das paginas capturadas pelo crawler."""
import collections
import html
import re

from ia_pipeline.crawler.models import CrawlResult, PageCapture
from ia_pipeline.nlp import _PT_STOPWORDS

from .models import ParsedPageContent, ParsedSiteContent


CTA_PATTERNS = (
    "fale conosco",
    "agende uma demo",
    "agendar demo",
    "solicite uma demo",
    "compre agora",
    "saiba mais",
    "entre em contato",
    "teste gratis",
    "assine agora",
    "comece agora",
    "solicitar orcamento",
    "request a demo",
    "book a demo",
    "learn more",
    "get started",
    "contact sales",
    "buy now",
    "sign up",
)


def _strip_html(raw_html: str) -> str:
    cleaned = re.sub(r"(?is)<script.*?>.*?</script>", " ", raw_html or "")
    cleaned = re.sub(r"(?is)<style.*?>.*?</style>", " ", cleaned)
    cleaned = re.sub(r"(?is)<noscript.*?>.*?</noscript>", " ", cleaned)
    cleaned = re.sub(r"(?s)<[^>]+>", " ", cleaned)
    return " ".join(html.unescape(cleaned).split())


def _extract_tag_texts(raw_html: str, tag: str, limit: int = 12) -> list[str]:
    pattern = re.compile(rf"(?is)<{tag}\b[^>]*>(.*?)</{tag}>")
    matches = pattern.findall(raw_html or "")
    out: list[str] = []
    for match in matches:
        text = _strip_html(match)
        if text and text not in out:
            out.append(text[:240])
        if len(out) >= limit:
            break
    return out


def _extract_keywords(text: str, limit: int = 12) -> list[str]:
    normalized = re.sub(r"https?://\S+", " ", text or "", flags=re.I)
    normalized = re.sub(r"[^\w\s-]", " ", normalized)
    words = [token.lower().strip("-_") for token in normalized.split()]
    valid = [
        token for token in words
        if len(token) >= 4 and token not in _PT_STOPWORDS and not token.isdigit()
    ]
    freq = collections.Counter(valid)
    return [word for word, _count in freq.most_common(limit)]


def _extract_ctas(page: PageCapture, paragraphs: list[str]) -> list[str]:
    candidates = []
    for paragraph in paragraphs[:10]:
        candidates.append(paragraph)
    for link in page.internal_links or []:
        candidates.append(str(link.get("text") or "").strip())
        candidates.append(str(link.get("title") or "").strip())
        candidates.append(str(link.get("aria_label") or "").strip())
    out: list[str] = []
    for candidate in candidates:
        text = " ".join(candidate.split()).strip()
        if not text:
            continue
        low = text.lower()
        if any(pattern in low for pattern in CTA_PATTERNS) and text not in out:
            out.append(text[:180])
    return out[:8]


def parse_page_capture(page: PageCapture) -> ParsedPageContent:
    h2 = _extract_tag_texts(page.raw_html, "h2", limit=10)
    h3 = _extract_tag_texts(page.raw_html, "h3", limit=10)
    paragraphs = _extract_tag_texts(page.raw_html, "p", limit=24)
    clean_text = " ".join(
        part for part in [
            page.page_title,
            page.primary_heading,
            page.meta_description,
            " ".join(h2),
            " ".join(h3),
            " ".join(paragraphs),
            page.body_text,
        ]
        if part
    ).strip()
    clean_text = " ".join(clean_text.split()) or _strip_html(page.raw_html)
    keywords = _extract_keywords(clean_text)
    ctas = _extract_ctas(page, paragraphs)
    return ParsedPageContent(
        url=page.url,
        page_title=page.page_title,
        screen_type=page.screen_type,
        screen_label=page.screen_label,
        primary_heading=page.primary_heading,
        headings_h2=h2,
        headings_h3=h3,
        paragraphs=paragraphs,
        keywords=keywords,
        ctas=ctas,
        clean_text=clean_text,
        meta_description=page.meta_description,
        discovered_from_url=page.discovered_from_url,
        discovered_from_text=page.discovered_from_text,
    )


def parse_crawl_result(crawl: CrawlResult) -> ParsedSiteContent:
    parsed_pages = [parse_page_capture(page) for page in (crawl.pages or [])]
    keyword_counter = collections.Counter()
    cta_seen: list[str] = []
    for page in parsed_pages:
        keyword_counter.update(page.keywords)
        for cta in page.ctas:
            if cta not in cta_seen:
                cta_seen.append(cta)
    return ParsedSiteContent(
        source_url=crawl.start_url,
        pages=parsed_pages,
        global_keywords=[word for word, _count in keyword_counter.most_common(20)],
        global_ctas=cta_seen[:12],
    )
