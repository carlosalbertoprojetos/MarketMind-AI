from celery import shared_task

from app.workers.celery_app import celery_app


@celery_app.task(name="tasks.generate_content")
def generate_content_task(content_item_id: str) -> dict:
    return {"status": "queued", "content_item_id": content_item_id}


@celery_app.task(name="tasks.generate_image")
def generate_image_task(prompt: str) -> dict:
    return {"status": "queued", "prompt": prompt}


@celery_app.task(name="tasks.market_analysis")
def market_analysis_task(product_id: str) -> dict:
    return {"status": "queued", "product_id": product_id}


@celery_app.task(name="tasks.scheduled_post")
def scheduled_post_task(post_id: str) -> dict:
    return {"status": "queued", "post_id": post_id}