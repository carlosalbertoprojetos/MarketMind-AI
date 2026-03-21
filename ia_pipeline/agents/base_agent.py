"""Classe base para agentes especializados."""
from dataclasses import dataclass, field
from typing import Any

from ia_pipeline.agent_memory.service import AgentMemoryStore
from ia_pipeline.runtime import get_logger


@dataclass
class BaseAgent:
    name: str
    role: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.logger = get_logger(f"marketingai.agents.{self.name}")

    def think(self, context: dict) -> dict:
        raise NotImplementedError

    def act(self, data: dict) -> dict:
        raise NotImplementedError

    def communicate(self, memory: AgentMemoryStore, recipient: str, message_type: str, payload: dict, cycle_id: str = "") -> dict:
        message = memory.add_message(self.name, recipient, message_type, payload, cycle_id)
        return {
            "from": message.sender,
            "to": message.recipient,
            "type": message.message_type,
            "payload": message.payload,
            "cycle_id": message.cycle_id,
            "timestamp": message.timestamp,
        }

    def record_decision(self, memory: AgentMemoryStore, summary: str, details: dict | None = None, cycle_id: str = "") -> None:
        memory.add_decision(self.name, self.role, summary, details or {}, cycle_id)
