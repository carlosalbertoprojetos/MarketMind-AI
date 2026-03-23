#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
export PYTHONPATH="$PWD"
export MARKETINGAI_LOCAL_CONTROL=1
py -3 -m uvicorn --app-dir "$PWD" marketingai_asgi:app --host 127.0.0.1 --port 8003
