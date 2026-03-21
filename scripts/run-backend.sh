#!/usr/bin/env bash
# Inicia o backend a partir de qualquer lugar (entra em MarketingAI/backend e roda uvicorn)
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
