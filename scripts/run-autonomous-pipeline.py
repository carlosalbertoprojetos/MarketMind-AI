"""CLI para executar o pipeline autonomo completo."""
import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ia_pipeline.orchestrator.service import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Executar pipeline autonomo de marketing")
    parser.add_argument("url", help="URL principal do site")
    parser.add_argument("platform", help="instagram, linkedin ou x")
    parser.add_argument("--objective", default="branding", help="branding, engajamento ou conversao")
    parser.add_argument("--title", default="", help="Titulo da campanha")
    parser.add_argument("--publish", action="store_true", help="Publicar automaticamente")
    args = parser.parse_args()

    result = run_pipeline(
        url=args.url,
        platform=args.platform,
        objective=args.objective,
        campaign_title=args.title,
        auto_publish=args.publish,
    )
    print(json.dumps(asdict(result), ensure_ascii=True, indent=2))
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
