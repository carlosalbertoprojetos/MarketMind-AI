"""Modelos estruturados para conteudo extraido do site."""

from dataclasses import dataclass, field


@dataclass
class ParsedPageContent:
    url: str
    page_title: str = ""
    screen_type: str = "generic"
    screen_label: str = ""
    primary_heading: str = ""
    headings_h2: list[str] = field(default_factory=list)
    headings_h3: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    ctas: list[str] = field(default_factory=list)
    clean_text: str = ""
    meta_description: str = ""
    discovered_from_url: str = ""
    discovered_from_text: str = ""


@dataclass
class ParsedSiteContent:
    source_url: str
    pages: list[ParsedPageContent] = field(default_factory=list)
    global_keywords: list[str] = field(default_factory=list)
    global_ctas: list[str] = field(default_factory=list)
