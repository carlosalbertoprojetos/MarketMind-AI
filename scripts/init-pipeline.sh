#!/usr/bin/env bash
# Instala dependências e browsers do pipeline IA (Playwright)
# Uso: ./scripts/init-pipeline.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/ia_pipeline"

echo "=== MarketingAI - Inicializando pipeline IA ==="
pip install -q -r requirements.txt
if command -v playwright &>/dev/null; then
  playwright install chromium
else
  python -m playwright install chromium
fi
echo "Pipeline pronto. Teste com: python scraping.py https://example.com"
