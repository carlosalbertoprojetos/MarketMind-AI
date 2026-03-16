from __future__ import annotations

from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup


@dataclass(slots=True)
class CrawlResult:
    url: str
    status_code: int | None
    title: str | None
    text: str
    error: str | None = None


def fetch_url(url: str, timeout: float = 15.0) -> CrawlResult:
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
        html = response.text
        text, title = parse_html(html)
        return CrawlResult(
            url=url,
            status_code=response.status_code,
            title=title,
            text=text,
        )
    except Exception as exc:  # pragma: no cover - network errors vary
        return CrawlResult(url=url, status_code=None, title=None, text="", error=str(exc))


def parse_html(html: str) -> tuple[str, str | None]:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else None
    text = " ".join(chunk.strip() for chunk in soup.get_text(separator=" ").split())
    return text, title