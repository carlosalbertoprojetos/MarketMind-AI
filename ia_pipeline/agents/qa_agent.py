"""Agente de QA: valida o resultado do pipeline e aponta falhas."""

from ia_pipeline.agents.base_agent import BaseAgent


class QAAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="qa_agent",
            role="Validar o pipeline e identificar falhas",
            input_schema={"run_result": "saida do dev agent"},
            output_schema={"qa_report": "aprovacao, erros e sugestoes"},
        )

    def think(self, context: dict) -> dict:
        return self.act(context)

    def act(self, data: dict) -> dict:
        issues: list[str] = []
        suggestions: list[str] = []

        if data.get("status") != "completed":
            issues.append(data.get("error") or "pipeline falhou")

        if not data.get("business_summary"):
            issues.append("business_summary ausente")
        if not data.get("generated_contents"):
            issues.append("nenhum conteudo gerado")
        if not data.get("image_assets"):
            issues.append("nenhum ativo visual gerado")

        if issues:
            suggestions.append("Reexecutar com mais paginas e verificar contexto extraido do site.")
            if "nenhum ativo visual gerado" in issues:
                suggestions.append("Ativar provider de imagem ou conferir fallback de screenshot.")
            if "nenhum conteudo gerado" in issues:
                suggestions.append("Revisar input da URL e profundidade do crawl.")

        return {
            "approved": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "score": max(0.0, 1.0 - (0.2 * len(issues))),
        }
