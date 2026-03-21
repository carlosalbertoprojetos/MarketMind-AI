"""Modelos da memoria dos agentes."""
from dataclasses import dataclass, field


@dataclass
class AgentMessage:
    sender: str
    recipient: str
    message_type: str
    payload: dict = field(default_factory=dict)
    cycle_id: str = ""
    timestamp: str = ""


@dataclass
class AgentDecision:
    agent_name: str
    role: str
    summary: str
    details: dict = field(default_factory=dict)
    cycle_id: str = ""
    timestamp: str = ""
