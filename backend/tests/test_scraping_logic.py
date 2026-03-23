"""Testes de classificacao, priorizacao e selecao explicita de URLs."""
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ia_pipeline.scraping import LinkCandidate, build_requested_url_list, build_screen_label, infer_screen_type, rank_internal_links


def test_infer_screen_type_identifies_pricing_page():
    screen_type = infer_screen_type(
        "https://acme.com/precos",
        page_title="Planos e precos | Acme",
        primary_heading="Escolha o plano ideal",
        meta_description="Veja planos e compare beneficios",
        link_texts=["Produto", "FAQ", "Contato"],
    )
    assert screen_type == "pricing"


def test_infer_screen_type_identifies_article_page():
    screen_type = infer_screen_type(
        "https://acme.com/blog/como-reduzir-cac",
        page_title="Como reduzir CAC",
        primary_heading="Como reduzir CAC em SaaS",
        meta_description="Artigo com estrategias de crescimento",
        link_texts=["Blog", "Pricing"],
    )
    assert screen_type == "blog" or screen_type == "article"


def test_build_screen_label_prefers_heading():
    label = build_screen_label(
        "features",
        page_title="Funcionalidades | Acme",
        primary_heading="Automatize campanhas com IA",
        url="https://acme.com/funcionalidades",
    )
    assert label == "Automatize campanhas com IA"


def test_build_requested_url_list_keeps_only_explicit_unique_urls():
    urls = build_requested_url_list(
        "https://acme.com",
        [
            "https://acme.com/precos",
            "https://acme.com/precos#faq",
            "https://acme.com/blog",
            "",
        ],
        max_urls=5,
    )
    assert urls == [
        "https://acme.com",
        "https://acme.com/precos",
        "https://acme.com/blog",
    ]


def test_rank_internal_links_prioritizes_strategic_pages():
    candidates = [
        LinkCandidate(
            url="https://acme.com/precos",
            text="Precos",
            source_url="https://acme.com",
            source_zone="nav",
        ),
        LinkCandidate(
            url="https://acme.com/solucoes",
            text="Solucoes",
            source_url="https://acme.com",
            source_zone="nav",
        ),
        LinkCandidate(
            url="https://acme.com/login",
            text="Entrar",
            source_url="https://acme.com",
            source_zone="header",
        ),
        LinkCandidate(
            url="https://acme.com/privacy",
            text="Privacidade",
            source_url="https://acme.com",
            source_zone="footer",
        ),
    ]

    ranked = rank_internal_links(candidates, "https://acme.com", 4)
    urls = [item.url for item in ranked]

    assert urls.index("https://acme.com/precos") < urls.index("https://acme.com/login")
    assert urls.index("https://acme.com/solucoes") < urls.index("https://acme.com/privacy")
