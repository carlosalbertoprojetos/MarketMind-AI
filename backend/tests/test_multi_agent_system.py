"""Testes do sistema multi-agente."""
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["MARKETINGAI_OUTPUT_DIR"] = str(ROOT / "ia_pipeline" / "output_test")
os.environ["MARKETINGAI_AGENT_MAX_CYCLES"] = "2"
os.environ["MARKETINGAI_AGENT_DEBUG"] = "true"

from ia_pipeline.agent_memory.service import AgentMemoryStore
from ia_pipeline.agents.architect_agent import ArchitectAgent
from ia_pipeline.agents.growth_agent import GrowthAgent
from ia_pipeline.agents.orchestrator_agent import run_multi_agent_pipeline
from ia_pipeline.agents.qa_agent import QAAgent


def test_architect_agent_generates_structured_plan():
    agent = ArchitectAgent()
    plan = agent.think({"url": "https://acme.com", "platform": "instagram", "cycle_index": 1})
    assert plan["target_url"] == "https://acme.com"
    assert "crawler" in plan["modules"]
    assert plan["validation_criteria"]


def test_base_communication_records_message():
    agent = ArchitectAgent()
    memory = AgentMemoryStore(run_id="test-run")
    message = agent.communicate(memory, "dev_agent", "task", {"foo": "bar"}, "cycle-1")
    assert message["from"] == "architect_agent"
    assert len(memory.messages) == 1
    assert memory.messages[0].payload["foo"] == "bar"


def test_qa_agent_detects_missing_outputs():
    qa = QAAgent()
    report = qa.act({"status": "completed", "business_summary": {}, "generated_contents": [], "image_assets": []})
    assert report["approved"] is False
    assert "business_summary ausente" in report["issues"]


def test_growth_agent_returns_optimized_contents():
    growth = GrowthAgent()
    output = growth.act(
        {
            "generated_contents": [
                {
                    "platform": "instagram",
                    "source_page_url": "https://acme.com/precos",
                    "screen_type": "pricing",
                    "headlines": ["ROI para equipes de growth"],
                    "persuasive_text": "Ganhe eficiencia e previsibilidade.",
                    "visual_suggestions": ["Dashboard em notebook"],
                }
            ],
            "performance_data": [],
        }
    )
    assert output["optimized_contents"]
    assert output["next_objective"] in {"branding", "engajamento", "conversao"}


def test_run_multi_agent_pipeline_success(monkeypatch):
    from ia_pipeline.agents import dev_agent as dev_agent_module

    def fake_act(self, data):
        return {
            "status": "completed",
            "business_summary": {"summary": "Produto SaaS para marketing."},
            "generated_contents": [
                {
                    "platform": "instagram",
                    "source_page_url": "https://acme.com",
                    "screen_type": "product",
                    "headlines": ["Automatize seu marketing"],
                    "persuasive_text": "Ganhe previsibilidade com IA.",
                    "visual_suggestions": ["Tela do produto em destaque"],
                }
            ],
            "image_assets": [{"provider": "mock"}],
            "publish_results": [],
            "autonomous_cycle": {},
        }

    monkeypatch.setattr(dev_agent_module.DevAgent, "act", fake_act)
    result = run_multi_agent_pipeline("https://acme.com", "instagram", max_cycles=2)
    assert result["status"] == "completed"
    assert result["qa_output"]["approved"] is True
    assert result["growth_output"]["optimized_contents"]
    assert result["memory"]["messages"]


def test_run_multi_agent_pipeline_stops_after_cycle_limit(monkeypatch):
    from ia_pipeline.agents import dev_agent as dev_agent_module

    def failing_act(self, data):
        return {
            "status": "failed",
            "error": "falha simulada",
            "business_summary": {},
            "generated_contents": [],
            "image_assets": [],
        }

    monkeypatch.setattr(dev_agent_module.DevAgent, "act", failing_act)
    result = run_multi_agent_pipeline("https://acme.com", "instagram", max_cycles=1)
    assert result["status"] == "failed"
    assert "QA nao aprovou" in result["error"]
