from app.services.semantic_extraction import extract_semantics


def test_extract_semantics_basic():
    text = "Nosso produto tem funcionalidades de automacao. Beneficio: reduz custo. Proposta de valor clara."
    result = extract_semantics(text)
    assert result.value_proposition
    assert len(result.features) > 0
    assert len(result.benefits) > 0