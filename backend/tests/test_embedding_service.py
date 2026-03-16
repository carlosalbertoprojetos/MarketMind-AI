from app.services.embedding_service import generate_embedding


def test_embedding_fallback_is_deterministic():
    vec1 = generate_embedding("MarketMind", use_openai=False)
    vec2 = generate_embedding("MarketMind", use_openai=False)
    assert vec1 == vec2
    assert len(vec1) == 1536


def test_embedding_respects_dimensions():
    vec = generate_embedding("MarketMind", dims=64, use_openai=False)
    assert len(vec) == 64