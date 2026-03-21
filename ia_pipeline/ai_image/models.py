"""Modelos de ativos de imagem."""
from dataclasses import dataclass, field


@dataclass
class ImageAsset:
    platform: str
    provider: str
    style: str
    prompt: str
    path: str = ""
    url: str = ""
    metadata: dict = field(default_factory=dict)
