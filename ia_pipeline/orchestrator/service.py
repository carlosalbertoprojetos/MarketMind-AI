"""Orquestrador principal do sistema autonomo."""
from dataclasses import asdict

from ia_pipeline.ai_image.service import generate_image_variations, prompt_builder
from ia_pipeline.analyzer.service import analyze_business
from ia_pipeline.autonomous.service import run_autonomous_cycle
from ia_pipeline.crawler.service import crawl_website
from ia_pipeline.generator.service import generate_marketing_content
from ia_pipeline.orchestrator.models import OrchestratedRunResult
from ia_pipeline.parser.service import parse_crawl_result
from ia_pipeline.publisher.service import publish_post
from ia_pipeline.runtime import get_logger, get_pipeline_config, write_json_artifact


def run_pipeline(
    url: str,
    platform: str,
    *,
    objective: str = "branding",
    campaign_title: str = "",
    login_url: str | None = None,
    login_username: str | None = None,
    login_password: str | None = None,
    auto_publish: bool = False,
    performance_data: list[dict] | None = None,
) -> OrchestratedRunResult:
    logger = get_logger("marketingai.orchestrator")
    config = get_pipeline_config()
    normalized_platform = "twitter" if (platform or "").lower() == "x" else (platform or "").lower()
    result = OrchestratedRunResult(url=url, platform=normalized_platform, objective=objective)

    try:
        crawl = crawl_website(
            url,
            login_url=login_url,
            login_username=login_username,
            login_password=login_password,
            max_pages=config.max_crawl_pages,
            max_depth=config.max_crawl_depth,
            run_ocr=True,
        )
        if crawl.error:
            result.status = "failed"
            result.error = crawl.error
            return result

        parsed_site = parse_crawl_result(crawl)
        business_summary = analyze_business(parsed_site)
        result.business_summary = asdict(business_summary)

        generated_contents = generate_marketing_content(
            parsed_site,
            business_summary,
            target_platform=normalized_platform,
            objective=objective,
            campaign_title=campaign_title or url,
        )
        result.generated_contents = [
            {
                "platform": item.platform,
                "objective": item.objective,
                "source_page_url": item.source_page_url,
                "screen_type": item.screen_type,
                "screen_label": item.screen_label,
                "headlines": item.headlines,
                "persuasive_text": item.persuasive_text,
                "copy_variations": [asdict(variation) for variation in item.copy_variations],
                "hashtags": item.hashtags,
                "visual_suggestions": item.visual_suggestions,
            }
            for item in generated_contents
        ]

        image_assets = []
        publish_results = []
        for item in generated_contents:
            content_for_image = " ".join(
                [
                    item.persuasive_text,
                    business_summary.summary,
                    " ".join(item.visual_suggestions[:2]),
                ]
            ).strip()
            prompt = prompt_builder(content_for_image, item.platform, config.image_style)
            variations = generate_image_variations(content_for_image, item.platform, config.image_style)
            image_assets.extend(asdict(asset) for asset in variations)

            if auto_publish:
                primary_image = next((asset.path or asset.url for asset in variations if asset.path or asset.url), "")
                publish_result = publish_post(
                    platform=item.platform,
                    content=item.persuasive_text,
                    image=primary_image,
                    hashtags=item.hashtags,
                )
                publish_results.append(asdict(publish_result))

        result.image_assets = image_assets
        result.publish_results = publish_results

        autonomous_cycle = run_autonomous_cycle(result.generated_contents, performance_data=performance_data)
        result.autonomous_cycle = asdict(autonomous_cycle)
        write_json_artifact(f"orchestrator/runs/{normalized_platform}_{hash(url) & 0xfffffff}.json", result)
        logger.info("Orchestrated pipeline finished for url=%s platform=%s", url, normalized_platform)
        return result
    except Exception as exc:
        logger.exception("Orchestrated pipeline failed: %s", exc)
        result.status = "failed"
        result.error = str(exc)
        return result
