"""Reexporta os modelos do crawler legado para manter compatibilidade."""

from ia_pipeline.scraping import CrawlResult, LinkCandidate, PageCapture, ScrapingResult

__all__ = ["CrawlResult", "LinkCandidate", "PageCapture", "ScrapingResult"]
