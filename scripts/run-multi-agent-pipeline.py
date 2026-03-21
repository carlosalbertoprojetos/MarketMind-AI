"""CLI para executar o sistema multi-agente."""
import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ia_pipeline.agents.orchestrator_agent import run_multi_agent_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Executar pipeline multi-agente")
    parser.add_argument("url", help="URL principal do site")
    parser.add_argument("platform", help="instagram, linkedin ou x")
    parser.add_argument("--objective", default="branding", help="branding, engajamento ou conversao")
    parser.add_argument("--title", default="", help="Titulo da campanha")
    parser.add_argument("--publish", action="store_true", help="Publicar automaticamente")
    parser.add_argument("--max-cycles", type=int, default=2, help="Numero maximo de ciclos multi-agente")
    parser.add_argument("--debug", action="store_true", help="Ativar modo debug")
    args = parser.parse_args()

    result = run_multi_agent_pipeline(
        url=args.url,
        platform=args.platform,
        objective=args.objective,
        campaign_title=args.title,
        auto_publish=args.publish,
        max_cycles=args.max_cycles,
        debug=args.debug,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result.get("status") == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
