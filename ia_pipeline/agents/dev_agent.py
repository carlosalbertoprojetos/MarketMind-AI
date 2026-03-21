"""Agente desenvolvedor: executa o pipeline e materializa a entrega."""

from dataclasses import asdict

from ia_pipeline.agents.base_agent import BaseAgent
from ia_pipeline.orchestrator.service import run_pipeline as run_orchestrated_pipeline


class DevAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="dev_agent",
            role="Implementar e executar a solucao tecnica definida pelo architect",
            input_schema={"technical_plan": "plano do architect"},
            output_schema={"run_result": "resultado funcional do pipeline"},
        )

    def think(self, context: dict) -> dict:
        return {
            "execution_summary": "Executar pipeline autonomo com foco na plataforma alvo e criterios do architect.",
            "platform": context.get("target_platform", "instagram"),
            "objective": context.get("objective", "branding"),
        }

    def act(self, data: dict) -> dict:
        result = run_orchestrated_pipeline(
            url=data.get("target_url", ""),
            platform=data.get("target_platform", "instagram"),
            objective=data.get("objective", "branding"),
            campaign_title=data.get("campaign_title", "") or data.get("target_url", ""),
            login_url=data.get("login_url"),
            login_username=data.get("login_username"),
            login_password=data.get("login_password"),
            auto_publish=bool(data.get("auto_publish", False)),
            performance_data=data.get("performance_data"),
        )
        return asdict(result)
