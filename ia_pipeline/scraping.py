"""
MarketingAI - Coleta visual e textual de URLs explicitas.

Usa Playwright (headless) para:
- abrir uma URL com login opcional
- capturar a tela informada, incluindo secoes de landing pages longas
- extrair imagens e metadados da propria pagina
- opcionalmente processar uma lista explicita de URLs, sem navegar por links internos
"""
import asyncio
import hashlib
import os
import re
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "screenshots"


@dataclass
class ScrapingResult:
    """Resultado de uma sessao de scraping de uma unica pagina."""
    url: str
    screenshot_paths: list[str] = field(default_factory=list)
    extracted_image_paths: list[str] = field(default_factory=list)
    full_page_path: Optional[str] = None
    ocr_texts: list[str] = field(default_factory=list)
    body_text: str = ""
    page_title: str = ""
    error: Optional[str] = None


@dataclass
class LinkCandidate:
    """Link interno descoberto em uma tela."""
    url: str
    text: str = ""
    title: str = ""
    aria_label: str = ""
    source_url: str = ""
    source_zone: str = ""
    score: int = 0
    reason: str = ""


@dataclass
class PageCapture:
    """Uma pagina visitada no crawl com metadados de marketing."""
    url: str
    page_title: str = ""
    primary_heading: str = ""
    meta_description: str = ""
    screen_type: str = "generic"
    screen_label: str = ""
    raw_html: str = ""
    body_text: str = ""
    screenshot_paths: list[str] = field(default_factory=list)
    extracted_image_paths: list[str] = field(default_factory=list)
    ocr_texts: list[str] = field(default_factory=list)
    discovered_from_url: str = ""
    discovered_from_text: str = ""
    internal_links: list[dict] = field(default_factory=list)


@dataclass
class CrawlResult:
    """Navegacao por varias telas do mesmo site."""
    start_url: str
    pages: list[PageCapture] = field(default_factory=list)
    error: Optional[str] = None


def _ensure_output_dir(output_dir: Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _sanitize_filename(url: str) -> str:
    safe = re.sub(r"https?://", "", url)
    safe = re.sub(r"[^\w\-.]", "_", safe)[:80]
    return safe or "page"


def _normalize_url(url: str) -> str:
    if not url or not isinstance(url, str):
        return ""
    normalized = url.split("#", 1)[0].strip()
    if normalized.endswith("/") and len(normalized) > len(urlparse(normalized).scheme) + 3:
        normalized = normalized.rstrip("/")
    return normalized


def build_requested_url_list(start_url: str, source_urls: list[str] | None = None, max_urls: int | None = None) -> list[str]:
    urls: list[str] = []
    candidates = [start_url, *(source_urls or [])]
    for raw in candidates:
        normalized = _normalize_url(raw)
        if not normalized or normalized in urls:
            continue
        urls.append(normalized)
        if max_urls and len(urls) >= max_urls:
            break
    return urls


def _goto_resilient(page, url: str, timeout_ms: int = 60000) -> None:
    last_err: Exception | None = None
    for wait_until in ("domcontentloaded", "load"):
        try:
            page.goto(url, wait_until=wait_until, timeout=timeout_ms)
            return
        except Exception as exc:
            last_err = exc
    if last_err:
        raise last_err


def _normalize_netloc(netloc: str) -> str:
    low = (netloc or "").lower()
    return low[4:] if low.startswith("www.") else low


def _same_site(page_url: str, base_url: str) -> bool:
    try:
        current = urlparse(page_url)
        base = urlparse(base_url)
        if current.scheme not in ("http", "https") or base.scheme not in ("http", "https"):
            return False
        return _normalize_netloc(current.netloc) == _normalize_netloc(base.netloc)
    except Exception:
        return False


def _page_title_text(page) -> str:
    try:
        return (page.title() or "").strip()
    except Exception:
        return ""


def _extract_primary_heading(page) -> str:
    for selector in ("main h1", "h1", "[role='heading'][aria-level='1']"):
        try:
            el = page.query_selector(selector)
            if not el:
                continue
            text = " ".join((el.inner_text() or "").split())
            if text:
                return text[:300]
        except Exception:
            continue
    return ""


def _extract_meta_description(page) -> str:
    for selector in (
        'meta[name="description"]',
        'meta[property="og:description"]',
        'meta[name="twitter:description"]',
    ):
        try:
            el = page.query_selector(selector)
            if not el:
                continue
            content = " ".join(((el.get_attribute("content") or "").split()))
            if content:
                return content[:500]
        except Exception:
            continue
    return ""


def _page_body_text(page, max_chars: int = 20000) -> str:
    try:
        raw = page.inner_text("body", timeout=15000)
        text = " ".join(raw.split())
        return text[:max_chars] if text else ""
    except Exception:
        return ""


def _capture_scroll_sections(page, output_dir: Path, base_name: str, *, run_ocr: bool, max_sections: int = 6) -> tuple[list[str], list[str]]:
    output_dir = Path(output_dir)
    section_paths: list[str] = []
    ocr_texts: list[str] = []
    try:
        metrics = page.evaluate(
            """() => ({
                scrollHeight: Math.max(document.body?.scrollHeight || 0, document.documentElement?.scrollHeight || 0),
                viewportHeight: window.innerHeight || document.documentElement?.clientHeight || 0
            })"""
        )
        scroll_height = int((metrics or {}).get("scrollHeight") or 0)
        viewport_height = int((metrics or {}).get("viewportHeight") or 0)
    except Exception:
        return section_paths, ocr_texts

    if scroll_height <= 0 or viewport_height <= 0:
        return section_paths, ocr_texts

    max_offset = max(scroll_height - viewport_height, 0)
    if max_offset <= 0:
        return section_paths, ocr_texts

    step = max(viewport_height - 120, 240)
    positions: list[int] = []
    current = 0
    while current < max_offset and len(positions) < max_sections:
        positions.append(current)
        current += step
    if len(positions) < max_sections and (not positions or positions[-1] != max_offset):
        positions.append(max_offset)

    seen: set[int] = set()
    for index, top in enumerate(positions, start=1):
        top = max(0, min(int(top), max_offset))
        if top in seen:
            continue
        seen.add(top)
        try:
            page.evaluate("y => window.scrollTo(0, y)", top)
            time.sleep(0.35)
            section_path = (output_dir / f"{base_name}_section_{index}.png").resolve()
            page.screenshot(path=str(section_path))
            if not section_path.is_file() or section_path.stat().st_size < 24:
                continue
            section_paths.append(str(section_path))
            if run_ocr:
                ocr_texts.append(run_ocr_on_image(str(section_path)))
        except Exception:
            continue

    try:
        page.evaluate("window.scrollTo(0, 0)")
    except Exception:
        pass
    return section_paths, ocr_texts


def _screen_keywords() -> dict[str, tuple[str, ...]]:
    return {
        "home": ("home", "inicio", "inicial"),
        "product": ("product", "produto", "platform", "plataforma", "app", "software"),
        "features": ("feature", "features", "funcionalidade", "funcionalidades", "recurso", "recursos"),
        "solutions": ("solution", "solutions", "solucao", "solucoes", "segmento", "industria"),
        "pricing": ("pricing", "price", "prices", "plan", "plans", "preco", "precos", "planos"),
        "docs": ("docs", "doc", "documentation", "documentacao", "guia", "help", "knowledge"),
        "faq": ("faq", "perguntas", "duvidas", "questions", "support"),
        "blog": ("blog", "artigo", "artigos", "post", "posts", "news", "conteudo"),
        "case_study": ("case", "cases", "depoimento", "depoimentos", "resultado", "clientes"),
        "about": ("about", "sobre", "empresa", "company", "quem-somos"),
        "contact": ("contact", "contato", "fale", "sales", "demo", "trial", "orcamento"),
        "login": ("login", "entrar", "signin", "sign-in", "auth"),
        "signup": ("signup", "register", "cadastro", "criar-conta"),
    }


def infer_screen_type(
    url: str,
    page_title: str = "",
    primary_heading: str = "",
    meta_description: str = "",
    link_texts: list[str] | None = None,
) -> str:
    parsed = urlparse(url or "")
    path = (parsed.path or "/").lower().strip("/")
    if not path:
        return "home"

    own_signals = [
        path.replace("/", " "),
        (page_title or "").lower(),
        (primary_heading or "").lower(),
        (meta_description or "").lower(),
    ]
    support_signals = [" ".join((link_texts or [])).lower()]
    scores: dict[str, int] = {}

    for screen_type, terms in _screen_keywords().items():
        score = 0
        for signal in own_signals:
            if any(term in signal for term in terms):
                score += 4
        for signal in support_signals:
            if any(term in signal for term in terms):
                score += 1
        if score:
            scores[screen_type] = score

    if scores:
        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_type, top_score = ordered[0]
        if top_score > 0:
            return top_type

    if "/blog/" in parsed.path.lower() or "/artigo/" in parsed.path.lower():
        return "article"
    return "generic"


def build_screen_label(screen_type: str, page_title: str = "", primary_heading: str = "", url: str = "") -> str:
    preferred = " ".join((primary_heading or "").split()).strip() or " ".join((page_title or "").split()).strip()
    if preferred:
        return preferred[:120]
    fallback_labels = {
        "home": "Pagina inicial",
        "product": "Tela de produto",
        "features": "Tela de funcionalidades",
        "solutions": "Tela de solucoes",
        "pricing": "Tela de precos",
        "docs": "Tela de documentacao",
        "faq": "Tela de FAQ",
        "blog": "Tela de blog",
        "article": "Tela de artigo",
        "case_study": "Tela de prova social",
        "about": "Tela institucional",
        "contact": "Tela de contato",
        "login": "Tela de login",
        "signup": "Tela de cadastro",
        "generic": "Tela do site",
    }
    path = (urlparse(url or "").path or "").strip("/")
    base = fallback_labels.get(screen_type, "Tela do site")
    return f"{base}: {path}" if path else base


def _extract_internal_link_candidates(page, current_url: str, base_url: str) -> list[LinkCandidate]:
    try:
        items = page.eval_on_selector_all(
            "a[href]",
            """
            els => els.map(a => {
              const text = (a.innerText || a.textContent || '').replace(/\\s+/g, ' ').trim();
              const title = (a.getAttribute('title') || '').trim();
              const aria = (a.getAttribute('aria-label') || '').trim();
              const zoneEl = a.closest('nav, header, footer, aside, main');
              const zone = zoneEl ? zoneEl.tagName.toLowerCase() : '';
              return {
                href: a.href || '',
                text,
                title,
                aria_label: aria,
                source_zone: zone
              };
            }).filter(item => Boolean(item.href))
            """,
        )
    except Exception:
        return []

    out: list[LinkCandidate] = []
    seen: set[str] = set()
    for item in items or []:
        href = _normalize_url((item or {}).get("href", ""))
        if not href or href in seen:
            continue
        if not _same_site(href, base_url):
            continue
        low = href.lower()
        if any(low.split("?")[0].endswith(ext) for ext in (".pdf", ".zip", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".css", ".js")):
            continue
        seen.add(href)
        out.append(
            LinkCandidate(
                url=href,
                text=((item or {}).get("text") or "")[:160],
                title=((item or {}).get("title") or "")[:160],
                aria_label=((item or {}).get("aria_label") or "")[:160],
                source_url=current_url,
                source_zone=((item or {}).get("source_zone") or "")[:40],
            )
        )
    return out


def _score_internal_link(candidate: LinkCandidate, base_url: str) -> LinkCandidate:
    parsed = urlparse(candidate.url or "")
    path = (parsed.path or "/").lower()
    text_blob = " ".join(
        [
            candidate.text.lower(),
            candidate.title.lower(),
            candidate.aria_label.lower(),
            path.replace("/", " "),
        ]
    )
    score = 0
    reasons: list[str] = []

    strategic_weights = {
        "pricing": 16,
        "solutions": 15,
        "product": 14,
        "features": 13,
        "faq": 11,
        "docs": 10,
        "case_study": 10,
        "blog": 8,
        "about": 7,
        "contact": 9,
        "home": 6,
    }
    for screen_type, terms in _screen_keywords().items():
        if any(term in text_blob for term in terms):
            if screen_type in ("login", "signup"):
                score -= 12
                reasons.append(screen_type)
            else:
                score += strategic_weights.get(screen_type, 4)
                reasons.append(screen_type)
            break

    if candidate.source_zone in ("nav", "header", "main"):
        score += 4
        reasons.append(candidate.source_zone)
    elif candidate.source_zone == "footer":
        score -= 2

    blocked_terms = (
        "logout", "sair", "account", "conta", "admin", "wp-admin", "cart", "checkout",
        "privacy", "privacidade", "termos", "terms", "cookie", "cookies", "feed",
        "tag", "category", "categoria", "javascript:", "mailto:", "tel:",
    )
    if any(term in text_blob for term in blocked_terms):
        score -= 20
        reasons.append("blocked")

    if parsed.query:
        score -= 2
    if candidate.url == _normalize_url(base_url):
        score -= 1

    candidate.score = score
    candidate.reason = ",".join(reasons[:4])
    return candidate


def rank_internal_links(candidates: list[LinkCandidate], base_url: str, max_links: int) -> list[LinkCandidate]:
    ranked = [_score_internal_link(candidate, base_url) for candidate in candidates]
    ranked.sort(
        key=lambda item: (
            item.score,
            len(item.text or ""),
            -len(urlparse(item.url or "").path or ""),
        ),
        reverse=True,
    )
    return ranked[:max_links]


def _collect_internal_links(page, current_url: str, base_url: str, max_links: int) -> list[LinkCandidate]:
    return rank_internal_links(
        _extract_internal_link_candidates(page, current_url, base_url),
        base_url,
        max_links,
    )


def _capture_page_assets(
    page,
    context,
    output_dir: Path,
    base_name: str,
    *,
    run_ocr: bool,
    grab_extra_elements: bool = True,
    capture_scroll_sections: bool = True,
    max_scroll_sections: int = 6,
) -> tuple[list[str], list[str], list[str]]:
    """Captura viewport, secoes da pagina, elementos destacados e imagens embutidas."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot_paths: list[str] = []
    extracted_image_paths: list[str] = []
    ocr_texts: list[str] = []

    viewport_path = (output_dir / f"{base_name}_viewport.png").resolve()
    page.screenshot(path=str(viewport_path))
    if not viewport_path.is_file() or viewport_path.stat().st_size < 24:
        raise RuntimeError("Screenshot da viewport nao foi salvo ou esta vazio.")
    screenshot_paths.append(str(viewport_path))
    if run_ocr:
        ocr_texts.append(run_ocr_on_image(str(viewport_path)))

    if capture_scroll_sections:
        section_paths, section_ocr = _capture_scroll_sections(
            page,
            output_dir,
            base_name,
            run_ocr=run_ocr,
            max_sections=max_scroll_sections,
        )
        screenshot_paths.extend(section_paths)
        ocr_texts.extend(section_ocr)

    if grab_extra_elements:
        for selector, suffix in [
            ("header", "header"),
            ("main", "main"),
            ("[class*='hero']", "hero"),
            ("h1", "h1"),
        ]:
            el = page.query_selector(selector)
            if not el:
                continue
            try:
                el_path = output_dir / f"{base_name}_{suffix}.png"
                el.screenshot(path=str(el_path))
                screenshot_paths.append(str(el_path.resolve()))
                if run_ocr:
                    ocr_texts.append(run_ocr_on_image(str(el_path)))
            except Exception:
                continue

    try:
        image_srcs = page.eval_on_selector_all(
            "img",
            "els => els.map(e => e.currentSrc || e.src).filter(Boolean)",
        )
        image_dir = output_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        seen_src: set[str] = set()
        for idx, src in enumerate((image_srcs or [])[:12]):
            if not src or src in seen_src:
                continue
            seen_src.add(src)
            try:
                resp = context.request.get(src, timeout=10000)
                if not resp.ok:
                    continue
                content_type = (resp.headers.get("content-type") or "").lower()
                if not content_type.startswith("image/"):
                    continue
                ext = os.path.splitext(urlparse(src).path)[1].lower()
                if content_type == "image/svg+xml":
                    ext = ".svg"
                elif ext not in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"):
                    ext = ".png"
                img_path = image_dir / f"{base_name}_asset_{idx + 1}{ext}"
                img_path.write_bytes(resp.body())
                extracted_image_paths.append(str(img_path.resolve()))
                if run_ocr:
                    ocr_texts.append(run_ocr_on_image(str(img_path)))
            except Exception:
                continue
    except Exception:
        pass

    return screenshot_paths, extracted_image_paths, ocr_texts


def run_ocr_on_image(image_path: str) -> str:
    if not pytesseract or not Image:
        return ""
    try:
        img = Image.open(image_path)
        return pytesseract.image_to_string(img, lang="por+eng").strip()
    except Exception:
        return ""


def _maybe_login(page, login_url: str | None, login_username: str | None, login_password: str | None) -> Optional[str]:
    if not login_url or not (login_username or login_password):
        return None
    try:
        _goto_resilient(page, login_url, timeout_ms=60000)
        time.sleep(1)
        email_sel = 'input[type="email"], input[name="email"], input[type="text"]'
        if page.query_selector(email_sel) and login_username:
            page.fill(email_sel, login_username)
        pass_sel = 'input[type="password"]'
        if page.query_selector(pass_sel) and login_password:
            page.fill(pass_sel, login_password)
        page.click('button[type="submit"], input[type="submit"], [type="submit"]')
        time.sleep(2)
    except Exception as exc:
        return f"Login falhou: {exc}"
    return None


def scrape_url(
    url: str,
    *,
    login_url: Optional[str] = None,
    login_username: Optional[str] = None,
    login_password: Optional[str] = None,
    wait_seconds: float = 2.0,
    full_page_screenshot: bool = False,
    viewport_width: int = 1280,
    viewport_height: int = 720,
    output_dir: Optional[Path] = None,
    run_ocr: bool = True,
    capture_scroll_sections: bool = True,
) -> ScrapingResult:
    output_dir = _ensure_output_dir(output_dir or DEFAULT_OUTPUT_DIR)
    base_name = _sanitize_filename(url)
    result = ScrapingResult(url=url)

    if not sync_playwright:
        result.error = "Playwright nao instalado. Execute: pip install playwright && playwright install chromium"
        return result

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            page = context.new_page()

            login_error = _maybe_login(page, login_url, login_username, login_password)
            if login_error:
                result.error = login_error
                browser.close()
                return result

            _goto_resilient(page, url, timeout_ms=60000)
            time.sleep(max(wait_seconds, 1.5))

            result.page_title = _page_title_text(page)
            result.body_text = _page_body_text(page)
            shots, extracted, ocr_texts = _capture_page_assets(
                page,
                context,
                output_dir,
                base_name,
                run_ocr=run_ocr,
                grab_extra_elements=True,
                capture_scroll_sections=capture_scroll_sections,
            )
            result.screenshot_paths.extend(shots)
            result.extracted_image_paths.extend(extracted)
            result.ocr_texts.extend(ocr_texts)

            if full_page_screenshot:
                full_path = output_dir / f"{base_name}_full.png"
                page.screenshot(path=str(full_path), full_page=True)
                result.screenshot_paths.append(str(full_path.resolve()))
                result.full_page_path = str(full_path.resolve())
                if run_ocr:
                    result.ocr_texts.append(run_ocr_on_image(str(full_path)))

            browser.close()
    except Exception as exc:
        result.error = str(exc)

    return result


def crawl_site(
    start_url: str,
    *,
    output_dir: Optional[Path] = None,
    login_url: Optional[str] = None,
    login_username: Optional[str] = None,
    login_password: Optional[str] = None,
    source_urls: list[str] | None = None,
    max_pages: int = 5,
    max_depth: int = 0,
    max_links_per_page: int = 14,
    wait_seconds: float = 1.5,
    run_ocr: bool = True,
    viewport_width: int = 1280,
    viewport_height: int = 720,
    follow_internal_links: bool = False,
    capture_scroll_sections: bool = True,
) -> CrawlResult:
    """
    Coleta apenas as URLs explicitamente informadas por padrao.
    A navegacao automatica por links internos fica desativada, mas pode ser habilitada explicitamente.
    """
    out = CrawlResult(start_url=start_url)
    output_root = _ensure_output_dir(output_dir or DEFAULT_OUTPUT_DIR)

    if not sync_playwright:
        out.error = "Playwright nao instalado. Execute: pip install playwright && playwright install chromium"
        return out

    max_pages = max(1, min(int(max_pages), 20))
    max_depth = max(0, min(int(max_depth), 5))
    requested_urls = build_requested_url_list(start_url, source_urls, max_pages)
    if not requested_urls:
        out.error = "Nenhuma URL valida foi informada para coleta."
        return out

    discovered_by: dict[str, LinkCandidate] = {}

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            page = context.new_page()

            login_error = _maybe_login(page, login_url, login_username, login_password)
            if login_error:
                out.error = login_error
                browser.close()
                return out

            page_index = 0

            def capture_page(current: str, discovered: LinkCandidate | None = None) -> list[LinkCandidate]:
                nonlocal page_index
                _goto_resilient(page, current, timeout_ms=60000)
                time.sleep(max(wait_seconds, 1.0))
                page_title = _page_title_text(page)
                primary_heading = _extract_primary_heading(page)
                meta_description = _extract_meta_description(page)
                try:
                    raw_html = page.content() or ""
                except Exception:
                    raw_html = ""
                body_text = _page_body_text(page)
                ranked_links = _collect_internal_links(page, current, start_url, max_links_per_page)
                screen_type = infer_screen_type(
                    current,
                    page_title=page_title,
                    primary_heading=primary_heading,
                    meta_description=meta_description,
                    link_texts=[link.text for link in ranked_links[:6]],
                )
                screen_label = build_screen_label(screen_type, page_title, primary_heading, current)

                stem = f"{page_index:02d}_{hashlib.md5(current.encode('utf-8', errors='ignore')).hexdigest()[:10]}"
                page_dir = output_root / f"page_{stem}"
                shots, extracted, ocr_list = _capture_page_assets(
                    page,
                    context,
                    page_dir,
                    stem,
                    run_ocr=run_ocr,
                    grab_extra_elements=False,
                    capture_scroll_sections=capture_scroll_sections,
                )
                out.pages.append(
                    PageCapture(
                        url=current,
                        page_title=page_title,
                        primary_heading=primary_heading,
                        meta_description=meta_description,
                        screen_type=screen_type,
                        screen_label=screen_label,
                        raw_html=raw_html,
                        body_text=body_text,
                        screenshot_paths=shots,
                        extracted_image_paths=extracted,
                        ocr_texts=ocr_list,
                        discovered_from_url=discovered.source_url if discovered else "",
                        discovered_from_text=(discovered.text or discovered.title or discovered.aria_label) if discovered else "",
                        internal_links=[
                            {
                                "url": link.url,
                                "text": link.text,
                                "title": link.title,
                                "aria_label": link.aria_label,
                                "score": link.score,
                                "reason": link.reason,
                                "source_zone": link.source_zone,
                            }
                            for link in ranked_links
                        ],
                    )
                )
                page_index += 1
                return ranked_links

            if follow_internal_links:
                queue: deque[tuple[str, int]] = deque((requested_url, 0) for requested_url in requested_urls)
                visited: set[str] = set()
                while queue and len(out.pages) < max_pages:
                    current, depth = queue.popleft()
                    current = _normalize_url(current)
                    if not current or current in visited:
                        continue
                    visited.add(current)
                    try:
                        ranked_links = capture_page(current, discovered_by.get(current))
                    except Exception as exc:
                        if not out.pages:
                            out.error = f"Falha ao abrir {current}: {exc}"
                            browser.close()
                            return out
                        continue
                    if depth >= max_depth:
                        continue
                    queued_urls = {item[0] for item in queue}
                    for link in ranked_links:
                        if link.url not in visited and link.url not in queued_urls:
                            queue.append((link.url, depth + 1))
                            discovered_by.setdefault(link.url, link)
            else:
                for current in requested_urls:
                    try:
                        capture_page(current)
                    except Exception as exc:
                        if not out.pages:
                            out.error = f"Falha ao abrir {current}: {exc}"
                            browser.close()
                            return out
                        continue
                    if len(out.pages) >= max_pages:
                        break

            browser.close()
    except Exception as exc:
        out.error = str(exc)

    if not out.error and not out.pages:
        out.error = "Nenhuma pagina foi capturada."
    return out


def upload_to_s3(local_path: str, bucket: str, key: str) -> Optional[str]:
    """Placeholder para upload em storage externo."""
    return None


if __name__ == "__main__":
    import sys as _sys

    sample_url = _sys.argv[1] if len(_sys.argv) > 1 else "https://example.com"
    result = scrape_url(sample_url, run_ocr=False)
    print("URL:", result.url)
    print("Screenshots:", result.screenshot_paths)
    if result.error:
        print("Erro:", result.error)
    if result.ocr_texts:
        print("OCR:", result.ocr_texts[0][:200] if result.ocr_texts[0] else "(vazio)")
