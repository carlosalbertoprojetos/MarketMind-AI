"""Coordenador do sistema multi-agente."""
import hashlib
from dataclasses import dataclass, field

from ia_pipeline.agent_memory.service import AgentMemoryStore
from ia_pipeline.agents.architect_agent import ArchitectAgent
from ia_pipeline.agents.dev_agent import DevAgent
from ia_pipeline.agents.growth_agent import GrowthAgent
from ia_pipeline.agents.qa_agent import QAAgent
from ia_pipeline.runtime import get_logger, get_pipeline_config, write_json_artifact


@dataclass
class MultiAgentRunResult:
    run_id: str
    status: str
    url: str
    platform: str
    cycles_executed: int = 0
    architect_output: dict = field(default_factory=dict)
    dev_output: dict = field(default_factory=dict)
    qa_output: dict = field(default_factory=dict)
    growth_output: dict = field(default_factory=dict)
    memory: dict = field(default_factory=dict)
    error: str = ""


class OrchestratorAgent:
    def __init__(self) -> None:
        self.logger = get_logger("marketingai.agents.orchestrator")
        self.config = get_pipeline_config()
        self.architect = ArchitectAgent()
        self.dev = DevAgent()
        self.qa = QAAgent()
        self.growth = GrowthAgent()

    def run_cycle(self, context: dict, memory: AgentMemoryStore, cycle_id: str) -> dict:
        architect_output = self.architect.think(context)
        self.architect.record_decision(memory, "Plano tecnico gerado", architect_output, cycle_id)
        self.architect.communicate(memory, "dev_agent", "task", architect_output, cycle_id)

        dev_output = self.dev.act({**architect_output, **context})
        self.dev.record_decision(memory, "Execucao do pipeline concluida", {"status": dev_output.get("status", "")}, cycle_id)
        self.dev.communicate(memory, "qa_agent", "task", {"status": dev_output.get("status", "")}, cycle_id)

        qa_output = self.qa.act(dev_output)
        self.qa.record_decision(memory, "QA validou a execucao", qa_output, cycle_id)

        growth_output = {}
        if qa_output.get("approved"):
            self.qa.communicate(memory, "growth_agent", "feedback", {"approved": True}, cycle_id)
            growth_output = self.growth.act(dev_output | {"performance_data": context.get("performance_data")})
            self.growth.record_decision(memory, "Growth gerou otimizacoes", {"next_objective": growth_output.get("next_objective", "")}, cycle_id)
            if growth_output.get("autonomous_cycle"):
                memory.add_learning("growth_agent", growth_output.get("autonomous_cycle", {}), cycle_id)
        else:
            self.qa.communicate(memory, "dev_agent", "error", {"issues": qa_output.get("issues", []), "suggestions": qa_output.get("suggestions", [])}, cycle_id)

        cycle_result = {
            "cycle_id": cycle_id,
            "architect_output": architect_output,
            "dev_output": dev_output,
            "qa_output": qa_output,
            "growth_output": growth_output,
        }
        memory.add_cycle(cycle_result)
        memory.persist()
        return cycle_result


def run_multi_agent_pipeline(
    url: str,
    platform: str = "instagram",
    *,
    objective: str = "branding",
    campaign_title: str = "",
    login_url: str | None = None,
    login_username: str | None = None,
    login_password: str | None = None,
    source_urls: list[str] | None = None,
    performance_data: list[dict] | None = None,
    auto_publish: bool = False,
    max_cycles: int | None = None,
    debug: bool = False,
    follow_internal_links: bool = False,
    capture_scroll_sections: bool = True,
) -> dict:
    config = get_pipeline_config()
    logger = get_logger("marketingai.agents.orchestrator")
    safe_max_cycles = max(1, min(int(max_cycles or getattr(config, "agent_max_cycles", 2) or 2), 5))
    run_id = hashlib.md5(f"{url}:{platform}:{objective}:{campaign_title}".encode("utf-8", errors="ignore")).hexdigest()[:12]
    memory = AgentMemoryStore(run_id=run_id, tenant_id=config.tenant_id)
    orchestrator = OrchestratorAgent()
    result = MultiAgentRunResult(run_id=run_id, status="running", url=url, platform=platform)

    context = {
        "url": url,
        "platform": "twitter" if (platform or "").lower() == "x" else (platform or "").lower(),
        "objective": objective,
        "campaign_title": campaign_title,
        "login_url": login_url,
        "login_username": login_username,
        "login_password": login_password,
        "source_urls": source_urls or [],
        "performance_data": performance_data or [],
        "auto_publish": auto_publish,
        "debug": debug,
        "follow_internal_links": follow_internal_links,
        "capture_scroll_sections": capture_scroll_sections,
    }

    try:
        for cycle_index in range(1, safe_max_cycles + 1):
            cycle_id = f"{run_id}-cycle-{cycle_index}"
            context["cycle_index"] = cycle_index
            cycle_output = orchestrator.run_cycle(context, memory, cycle_id)
            result.cycles_executed = cycle_index
            result.architect_output = cycle_output["architect_output"]
            result.dev_output = cycle_output["dev_output"]
            result.qa_output = cycle_output["qa_output"]
            result.growth_output = cycle_output["growth_output"]

            if cycle_output["qa_output"].get("approved"):
                result.status = "completed"
                break

            context["qa_feedback"] = cycle_output["qa_output"].get("issues", [])
            if cycle_index >= safe_max_cycles:
                result.status = "failed"
                result.error = "QA nao aprovou dentro do limite de ciclos."
                break

        if result.status == "running":
            result.status = "completed"
        result.memory = memory.snapshot()
        write_json_artifact(f"agents/runs/{run_id}.json", result)
        logger.info("Multi-agent pipeline finished run_id=%s status=%s", run_id, result.status)
        return result.__dict__
    except Exception as exc:
        logger.exception("Multi-agent pipeline failed: %s", exc)
        result.status = "failed"
        result.error = str(exc)
        result.memory = memory.snapshot()
        write_json_artifact(f"agents/runs/{run_id}.json", result)
        return result.__dict__
