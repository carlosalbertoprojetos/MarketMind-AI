"""Agente de growth: otimiza copy e cria variantes de crescimento."""

from ia_pipeline.agents.base_agent import BaseAgent
from ia_pipeline.autonomous.service import run_autonomous_cycle


class GrowthAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="growth_agent",
            role="Otimizar conversao, copy e estrategia de conteudo",
            input_schema={"run_result": "resultado aprovado do dev", "performance": "metricas e sinais"},
            output_schema={"growth_output": "conteudos otimizados e aprendizados"},
        )

    def think(self, context: dict) -> dict:
        return {
            "focus": "otimizar engajamento e conversao com base em sinais de performance",
            "platforms": sorted({item.get("platform", "") for item in context.get("generated_contents", []) if item.get("platform")}),
        }

    def act(self, data: dict) -> dict:
        cycle = run_autonomous_cycle(data.get("generated_contents", []), performance_data=data.get("performance_data"))
        optimized_contents = []
        for item in data.get("generated_contents", []):
            improved_headlines = list(item.get("headlines", []))
            if cycle.evolved_copy_hints:
                hint = cycle.evolved_copy_hints[0]
                improved_headlines = improved_headlines[:2] + [hint[:110]]
            ab_tests = [
                {
                    "variant": "A",
                    "headline": improved_headlines[0] if improved_headlines else item.get("persuasive_text", "")[:110],
                    "angle": "controle",
                },
                {
                    "variant": "B",
                    "headline": (improved_headlines[1] if len(improved_headlines) > 1 else item.get("persuasive_text", ""))[:110],
                    "angle": cycle.evolved_copy_hints[0] if cycle.evolved_copy_hints else "otimizacao",
                },
            ]
            optimized_contents.append(
                {
                    "platform": item.get("platform", ""),
                    "source_page_url": item.get("source_page_url", ""),
                    "optimized_headlines": improved_headlines,
                    "ab_tests": ab_tests,
                    "prompt_hints": cycle.evolved_prompt_hints,
                }
            )
        return {
            "autonomous_cycle": cycle.__dict__,
            "optimized_contents": optimized_contents,
            "next_objective": cycle.next_objective,
        }
