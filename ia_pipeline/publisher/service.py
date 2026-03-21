"""Publicacao imediata e agendada em redes sociais."""
import hashlib
import json
import time

try:
    import requests
except ImportError:
    requests = None

from ia_pipeline.publisher.models import PublishResult, ScheduledBatch, ScheduledItem
from ia_pipeline.runtime import ensure_output_path, get_logger, get_pipeline_config, write_json_artifact


def _normalize_platform(platform: str) -> str:
    low = (platform or "").strip().lower()
    return "twitter" if low == "x" else low


def _content_for_platform(platform: str, content: str, hashtags: list[str]) -> str:
    text = " ".join((content or "").split())
    tags = " ".join(hashtags or [])
    final = f"{text}\n\n{tags}".strip()
    limits = {"instagram": 2200, "linkedin": 3000, "twitter": 280}
    limit = limits.get(platform, 2200)
    if len(final) > limit:
        return final[: max(0, limit - 3)].rstrip() + "..."
    return final


def _mock_publish(platform: str, content: str, image: str, hashtags: list[str], scheduled_for: str = "") -> PublishResult:
    external_id = hashlib.md5(f"{platform}:{content}:{image}:{scheduled_for}".encode("utf-8", errors="ignore")).hexdigest()[:12]
    return PublishResult(
        platform=platform,
        status="scheduled" if scheduled_for else "published",
        provider="mock",
        external_id=external_id,
        scheduled_for=scheduled_for,
        content=content,
        image_url=image,
        hashtags=hashtags,
        metadata={"mode": "mock"},
    )


def _publish_instagram(content: str, image: str, hashtags: list[str], scheduled_for: str = "") -> PublishResult:
    config = get_pipeline_config()
    logger = get_logger("marketingai.publisher.instagram")
    if config.publisher_mode == "mock" or not config.instagram_access_token or not config.instagram_account_id or not requests:
        return _mock_publish("instagram", content, image, hashtags, scheduled_for)
    try:
        endpoint = f"https://graph.facebook.com/v20.0/{config.instagram_account_id}/media"
        payload = {
            "image_url": image,
            "caption": _content_for_platform("instagram", content, hashtags),
            "access_token": config.instagram_access_token,
        }
        response = requests.post(endpoint, data=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return PublishResult(
            platform="instagram",
            status="scheduled" if scheduled_for else "published",
            provider="meta_graph",
            external_id=str(data.get("id", "")),
            scheduled_for=scheduled_for,
            content=content,
            image_url=image,
            hashtags=hashtags,
            metadata=data,
        )
    except Exception as exc:
        logger.exception("Instagram publish failed: %s", exc)
        return PublishResult(platform="instagram", status="failed", provider="meta_graph", content=content, image_url=image, hashtags=hashtags, error=str(exc))


def _publish_linkedin(content: str, image: str, hashtags: list[str], scheduled_for: str = "") -> PublishResult:
    config = get_pipeline_config()
    logger = get_logger("marketingai.publisher.linkedin")
    if config.publisher_mode == "mock" or not config.linkedin_access_token or not config.linkedin_organization_id or not requests:
        return _mock_publish("linkedin", content, image, hashtags, scheduled_for)
    try:
        endpoint = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {config.linkedin_access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        payload = {
            "author": f"urn:li:organization:{config.linkedin_organization_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": _content_for_platform("linkedin", content, hashtags)},
                    "shareMediaCategory": "IMAGE" if image else "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=60)
        response.raise_for_status()
        data = response.json() if response.content else {}
        external_id = data.get("id", "") or response.headers.get("x-restli-id", "")
        return PublishResult(
            platform="linkedin",
            status="scheduled" if scheduled_for else "published",
            provider="linkedin",
            external_id=str(external_id),
            scheduled_for=scheduled_for,
            content=content,
            image_url=image,
            hashtags=hashtags,
            metadata=data,
        )
    except Exception as exc:
        logger.exception("LinkedIn publish failed: %s", exc)
        return PublishResult(platform="linkedin", status="failed", provider="linkedin", content=content, image_url=image, hashtags=hashtags, error=str(exc))


def _publish_twitter(content: str, image: str, hashtags: list[str], scheduled_for: str = "") -> PublishResult:
    config = get_pipeline_config()
    logger = get_logger("marketingai.publisher.twitter")
    if config.publisher_mode == "mock" or not config.twitter_access_token or not requests:
        return _mock_publish("twitter", content, image, hashtags, scheduled_for)
    try:
        endpoint = "https://api.twitter.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {config.twitter_access_token}",
            "Content-Type": "application/json",
        }
        payload = {"text": _content_for_platform("twitter", content, hashtags)}
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=60)
        response.raise_for_status()
        data = response.json() if response.content else {}
        return PublishResult(
            platform="twitter",
            status="scheduled" if scheduled_for else "published",
            provider="twitter",
            external_id=str((data.get("data") or {}).get("id", "")),
            scheduled_for=scheduled_for,
            content=content,
            image_url=image,
            hashtags=hashtags,
            metadata=data,
        )
    except Exception as exc:
        logger.exception("Twitter publish failed: %s", exc)
        return PublishResult(platform="twitter", status="failed", provider="twitter", content=content, image_url=image, hashtags=hashtags, error=str(exc))


def publish_post(platform: str, content: str, image: str = "", hashtags: list[str] | None = None, scheduled_for: str = "") -> PublishResult:
    normalized = _normalize_platform(platform)
    hashtags = hashtags or []
    logger = get_logger("marketingai.publisher")
    logger.info("Publishing post platform=%s scheduled_for=%s", normalized, scheduled_for or "now")

    if normalized == "instagram":
        result = _publish_instagram(content, image, hashtags, scheduled_for)
    elif normalized == "linkedin":
        result = _publish_linkedin(content, image, hashtags, scheduled_for)
    elif normalized == "twitter":
        result = _publish_twitter(content, image, hashtags, scheduled_for)
    else:
        result = PublishResult(platform=normalized, status="failed", provider="unsupported", content=content, image_url=image, hashtags=hashtags, error=f"Plataforma nao suportada: {platform}")

    artifact = f"publisher/results/{normalized}_{hashlib.md5((content + image + scheduled_for).encode('utf-8', errors='ignore')).hexdigest()[:12]}.json"
    write_json_artifact(artifact, result)
    return result


def schedule_posts(batch: list[dict]) -> ScheduledBatch:
    config = get_pipeline_config()
    logger = get_logger("marketingai.publisher.scheduler")
    batch_id = hashlib.md5(json.dumps(batch, sort_keys=True).encode("utf-8", errors="ignore")).hexdigest()[:12]
    scheduled_batch = ScheduledBatch(batch_id=batch_id)
    retry_limit = max(1, config.queue_retry_limit)

    for raw_item in batch:
        item = ScheduledItem(
            platform=_normalize_platform(str(raw_item.get("platform", ""))),
            content=str(raw_item.get("content", "")),
            image=str(raw_item.get("image", "")),
            hashtags=list(raw_item.get("hashtags", []) or []),
            publish_at=str(raw_item.get("publish_at", "")),
        )
        scheduled_batch.items.append(item)

        attempts = 0
        result = None
        while attempts < retry_limit:
            attempts += 1
            item.retries = attempts - 1
            result = publish_post(item.platform, item.content, item.image, item.hashtags, item.publish_at)
            if result.status != "failed":
                item.status = result.status
                item.result = result.metadata | {"external_id": result.external_id, "provider": result.provider}
                break
            logger.warning("Publish retry %s/%s failed for platform=%s", attempts, retry_limit, item.platform)
            time.sleep(max(0, config.queue_retry_delay_seconds))

        if result and result.status == "failed":
            item.status = "failed"
            item.result = {"error": result.error, "provider": result.provider}

    scheduled_batch.status = "completed" if all(item.status != "failed" for item in scheduled_batch.items) else "partial_failure"
    write_json_artifact(f"publisher/batches/{batch_id}.json", scheduled_batch)
    return scheduled_batch
