"""Modelos de publicacao e agendamento."""
from dataclasses import dataclass, field


@dataclass
class PublishResult:
    platform: str
    status: str
    provider: str
    external_id: str = ""
    scheduled_for: str = ""
    content: str = ""
    image_url: str = ""
    hashtags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    error: str = ""


@dataclass
class ScheduledItem:
    platform: str
    content: str
    image: str = ""
    hashtags: list[str] = field(default_factory=list)
    publish_at: str = ""
    retries: int = 0
    status: str = "pending"
    result: dict = field(default_factory=dict)


@dataclass
class ScheduledBatch:
    batch_id: str
    items: list[ScheduledItem] = field(default_factory=list)
    status: str = "pending"
