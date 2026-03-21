"""Modulo de parsing de paginas crawleadas."""

from .models import ParsedPageContent, ParsedSiteContent
from .service import parse_crawl_result, parse_page_capture

__all__ = ["ParsedPageContent", "ParsedSiteContent", "parse_crawl_result", "parse_page_capture"]
