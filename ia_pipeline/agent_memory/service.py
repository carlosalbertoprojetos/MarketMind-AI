"""Persistencia de mensagens, decisoes e aprendizados dos agentes."""
from dataclasses import asdict
from datetime import datetime, timezone

from ia_pipeline.agent_memory.models import AgentDecision, AgentMessage
from ia_pipeline.runtime import get_logger, write_json_artifact


class AgentMemoryStore:
    def __init__(self, run_id: str, tenant_id: str = "default"):
        self.run_id = run_id
        self.tenant_id = tenant_id
        self.messages: list[AgentMessage] = []
        self.decisions: list[AgentDecision] = []
        self.learnings: list[dict] = []
        self.cycles: list[dict] = []
        self.logger = get_logger("marketingai.agent_memory")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def add_message(self, sender: str, recipient: str, message_type: str, payload: dict | None = None, cycle_id: str = "") -> AgentMessage:
        message = AgentMessage(
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            payload=payload or {},
            cycle_id=cycle_id,
            timestamp=self._now(),
        )
        self.messages.append(message)
        self.logger.info("Message %s -> %s (%s)", sender, recipient, message_type)
        return message

    def add_decision(self, agent_name: str, role: str, summary: str, details: dict | None = None, cycle_id: str = "") -> AgentDecision:
        decision = AgentDecision(
            agent_name=agent_name,
            role=role,
            summary=summary,
            details=details or {},
            cycle_id=cycle_id,
            timestamp=self._now(),
        )
        self.decisions.append(decision)
        self.logger.info("Decision from %s: %s", agent_name, summary)
        return decision

    def add_learning(self, source: str, content: dict, cycle_id: str = "") -> dict:
        item = {
            "source": source,
            "content": content,
            "cycle_id": cycle_id,
            "timestamp": self._now(),
        }
        self.learnings.append(item)
        return item

    def add_cycle(self, cycle_data: dict) -> None:
        self.cycles.append(cycle_data)

    def snapshot(self) -> dict:
        return {
            "run_id": self.run_id,
            "tenant_id": self.tenant_id,
            "messages": [asdict(item) for item in self.messages],
            "decisions": [asdict(item) for item in self.decisions],
            "learnings": self.learnings,
            "cycles": self.cycles,
        }

    def persist(self) -> None:
        write_json_artifact(f"agent_memory/{self.run_id}.json", self.snapshot())
