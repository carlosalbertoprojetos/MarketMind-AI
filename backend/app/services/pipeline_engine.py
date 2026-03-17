from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.agents.audience_agent import AudienceAgent
from app.agents.content_agent import ContentAgent
from app.agents.narrative_agent import NarrativeAgent
from app.agents.product_agent import ProductAgent
from app.models.ai_run import AiRun
from app.models.enums import AiRunStatus, ContentType
from app.models.product import Product


@dataclass(slots=True)
class PipelineResult:
    run: AiRun
    content_item_ids: list[str]
    steps: dict
    output: dict


def run_pipeline(
    db: Session,
    product: Product,
    sources: list[str],
    content_types: list[str] | None = None,
    persona_count: int = 3,
    brief: str | None = None,
) -> PipelineResult:
    run = AiRun(
        organization_id=product.organization_id,
        product_id=product.id,
        run_type="pipeline",
        status=AiRunStatus.running,
        input_payload={
            "sources": sources,
            "content_types": content_types,
            "persona_count": persona_count,
            "brief": brief,
        },
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    steps = {
        "analyze": "pending",
        "audience": "pending",
        "narrative": "pending",
        "content": "pending",
    }
    output: dict = {}
    content_item_ids: list[str] = []

    try:
        steps["analyze"] = "running"
        analysis = ProductAgent(db).run(product, sources)
        output["analysis"] = analysis.extracted_data
        steps["analyze"] = "done"

        steps["audience"] = "running"
        audience = AudienceAgent(db).run(product, persona_count)
        output["personas"] = [persona.id for persona in audience.personas]
        steps["audience"] = "done"

        persona = audience.personas[0] if audience.personas else None

        steps["narrative"] = "running"
        narrative = NarrativeAgent().run(product, persona)
        output["narrative"] = narrative.__dict__
        steps["narrative"] = "done"

        steps["content"] = "running"
        types = content_types or [item.value for item in ContentType]
        for content_type in types:
            item = ContentAgent(db).run(
                product,
                ContentType(content_type),
                persona,
                narrative,
                brief,
            )
            content_item_ids.append(str(item.content_item.id))
        steps["content"] = "done"

        run.status = AiRunStatus.completed
        run.output_payload = {
            "steps": steps,
            "content_item_ids": content_item_ids,
            **output,
        }
        db.commit()
        db.refresh(run)
    except Exception as exc:
        run.status = AiRunStatus.failed
        run.error_message = str(exc)
        run.output_payload = {"steps": steps, "error": str(exc)}
        db.commit()
        db.refresh(run)
        raise

    return PipelineResult(run=run, content_item_ids=content_item_ids, steps=steps, output=output)
