"""Agente arquiteto: define plano tecnico e revisa modularizacao."""

from ia_pipeline.agents.base_agent import BaseAgent


class ArchitectAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="architect_agent",
            role="Definir estrutura do sistema e sugerir melhorias arquiteturais",
            input_schema={"context": "estado do projeto, url, plataforma, historico"},
            output_schema={"technical_plan": "plano estruturado com modulos, riscos e validacoes"},
        )

    def think(self, context: dict) -> dict:
        target_platform = context.get("platform", "instagram")
        cycle = int(context.get("cycle_index", 1))
        risks = [
            "timeouts no crawl",
            "falta de imagens geradas",
            "publicacao sem credenciais reais",
        ]
        technical_plan = {
            "target_url": context.get("url", ""),
            "target_platform": target_platform,
            "cycle_index": cycle,
            "modules": [
                "crawler",
                "parser",
                "analyzer",
                "generator",
                "ai_image",
                "publisher",
            ],
            "execution_focus": "robustez do pipeline e qualidade do conteudo" if cycle == 1 else "otimizacao incremental guiada por QA e growth",
            "validation_criteria": [
                "business_summary preenchido",
                "conteudos gerados para a plataforma alvo",
                "imagem ou variacao visual retornada",
                "resultado publicavel ou agendavel",
            ],
            "risks": risks,
            "feedback_context": context.get("qa_feedback", []),
        }
        return technical_plan

    def act(self, data: dict) -> dict:
        return self.think(data)
