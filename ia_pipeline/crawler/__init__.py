"""Modulo de crawler reutilizavel do MarketingAI."""

from .models import CrawlResult, LinkCandidate, PageCapture, ScrapingResult
from .service import crawl_website, scrape_website

__all__ = [
    "CrawlResult",
    "LinkCandidate",
    "PageCapture",
    "ScrapingResult",
    "crawl_website",
    "scrape_website",
]
