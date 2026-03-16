import uuid

from app.models.product import Product
from app.services.narrative_engine import build_narrative


def test_build_narrative():
    product = Product(
        name="MarketMind",
        organization_id=uuid.uuid4(),
        brand_id=uuid.uuid4(),
    )
    narrative = build_narrative(product)
    assert narrative.problem
    assert narrative.solution
    assert narrative.cta
