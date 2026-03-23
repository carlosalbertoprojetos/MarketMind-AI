"""Orquestrador principal do sistema autonomo."""
from dataclasses import asdict

from ia_pipeline.ai_image.models import ImageAsset
from ia_pipeline.ai_image.service import generate_image_variations
from ia_pipeline.analyzer.service import analyze_business
from ia_pipeline.autonomous.service import run_autonomous_cycle
from ia_pipeline.crawler.service import crawl_website
from ia_pipeline.generator.service import generate_marketing_content
from ia_pipeline.orchestrator.models import OrchestratedRunResult
from ia_pipeline.parser.service import parse_crawl_result
from ia_pipeline.publisher.service import publish_post
from ia_pipeline.runtime import get_logger, get_pipeline_config, write_json_artifact
from ia_pipeline.services.visual_service import decide_visual_source, serialize_visual_decision


def run_pipeline(
    url: str,
    platform: str,
    *,
    objective: str = "branding",
    campaign_title: str = "",
    login_url: str | None = None,
    login_username: str | None = None,
    login_password: str | None = None,
    source_urls: list[str] | None = None,
    auto_publish: bool = False,
    performance_data: list[dict] | None = None,
    follow_internal_links: bool = False,
    capture_scroll_sections: bool = True,
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
            source_urls=source_urls,
            max_pages=config.max_crawl_pages,
            max_depth=config.max_crawl_depth,
            run_ocr=True,
            follow_internal_links=follow_internal_links,
            capture_scroll_sections=capture_scroll_sections,
        )
        if crawl.error:
            result.status = "failed"
            result.error = crawl.error
            return result

        parsed_site = parse_crawl_result(crawl)
        business_summary = analyze_business(parsed_site)
        result.business_summary = asdict(business_summary)
        crawl_page_map = {page.url: page for page in crawl.pages}

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
            source_page = crawl_page_map.get(item.source_page_url)
            source_images = []
            if source_page:
                source_images = list(source_page.screenshot_paths) + list(source_page.extracted_image_paths)
            visual_decision = decide_visual_source(
                platform=item.platform,
                objective=objective,
                screen_type=item.screen_type,
                screen_label=item.screen_label,
                headline=(item.headlines[0] if item.headlines else business_summary.value_proposition),
                caption=item.persuasive_text,
                audience=business_summary.target_audience,
                value_proposition=business_summary.value_proposition,
                differentiator=(business_summary.differentiators[0] if business_summary.differentiators else ""),
                source_images=source_images,
                style=config.image_style,
            )
            if visual_decision.selected_mode == "real" and source_images:
                primary_image = visual_decision.recommended_source_path or source_images[0]
                real_asset = ImageAsset(
                    platform=item.platform,
                    provider="real",
                    style=config.image_style,
                    prompt=visual_decision.prompt,
                    path=primary_image,
                    metadata=serialize_visual_decision(visual_decision, applied_mode="real"),
                )
                image_assets.append(asdict(real_asset))
            else:
                variations = generate_image_variations(visual_decision.prompt, item.platform, config.image_style)
                image_assets.extend(asdict(asset) for asset in variations)
                primary_image = next((asset.path or asset.url for asset in variations if asset.path or asset.url), "")

            if auto_publish:
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
