from app.integrations.crawler import parse_html


def test_parse_html_extracts_text_and_title():
    html = "<html><head><title>Teste</title></head><body><h1>Ola</h1><p>Mundo</p></body></html>"
    text, title = parse_html(html)
    assert title == "Teste"
    assert "Ola" in text
    assert "Mundo" in text