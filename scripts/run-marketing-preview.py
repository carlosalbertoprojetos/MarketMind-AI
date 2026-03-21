"""CLI para gerar conteudo de marketing a partir de uma URL."""
import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ia_pipeline.pipeline import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Gerar marketing a partir de uma URL")
    parser.add_argument("url", help="URL inicial do site")
    parser.add_argument("--title", default="", help="Titulo da campanha")
    parser.add_argument("--platform", default="instagram", help="Rede social alvo: instagram, linkedin, x")
    parser.add_argument("--objective", default="branding", help="branding, engajamento ou conversao")
    parser.add_argument("--max-pages", type=int, default=5, help="Numero maximo de paginas")
    parser.add_argument("--max-depth", type=int, default=2, help="Profundidade maxima do crawl")
    args = parser.parse_args()

    platform = "twitter" if args.platform.lower() == "x" else args.platform.lower()
    output = run_pipeline(
        url=args.url,
        campaign_title=args.title or args.url,
        platforms=[platform],
        max_crawl_pages=args.max_pages,
        max_crawl_depth=args.max_depth,
        objective=args.objective,
    )
    print(json.dumps(asdict(output), ensure_ascii=True, indent=2))
    return 0 if not output.error else 1


if __name__ == "__main__":
    raise SystemExit(main())
