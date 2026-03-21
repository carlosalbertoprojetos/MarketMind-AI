#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
exec py -3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8003
