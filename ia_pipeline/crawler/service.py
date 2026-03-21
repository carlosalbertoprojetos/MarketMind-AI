"""Servicos de crawling reutilizaveis."""

from pathlib import Path
from typing import Optional

from ia_pipeline.scraping import CrawlResult, ScrapingResult, crawl_site, scrape_url


def crawl_website(
    url: str,
    *,
    output_dir: Optional[Path] = None,
    login_url: str | None = None,
    login_username: str | None = None,
    login_password: str | None = None,
    max_pages: int = 5,
    max_depth: int = 2,
    max_links_per_page: int = 14,
    wait_seconds: float = 1.5,
    run_ocr: bool = True,
) -> CrawlResult:
    return crawl_site(
        url,
        output_dir=output_dir,
        login_url=login_url,
        login_username=login_username,
        login_password=login_password,
        max_pages=max_pages,
        max_depth=max_depth,
        max_links_per_page=max_links_per_page,
        wait_seconds=wait_seconds,
        run_ocr=run_ocr,
    )


def scrape_website(
    url: str,
    *,
    output_dir: Optional[Path] = None,
    login_url: str | None = None,
    login_username: str | None = None,
    login_password: str | None = None,
    wait_seconds: float = 2.0,
    run_ocr: bool = True,
) -> ScrapingResult:
    return scrape_url(
        url,
        output_dir=output_dir,
        login_url=login_url,
        login_username=login_username,
        login_password=login_password,
        wait_seconds=wait_seconds,
        run_ocr=run_ocr,
    )
