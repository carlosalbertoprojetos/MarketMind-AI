#!/usr/bin/env bash
# MarketingAI - Inicia backend e frontend em desenvolvimento local (sem Docker)
# Uso: ./scripts/start-local.sh (ou bash scripts/start-local.sh)

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== MarketingAI - Ambiente local ==="

# Backend
if ! [ -f backend/venv/bin/activate ] 2>/dev/null && ! [ -f backend/.venv/Scripts/activate ] 2>/dev/null; then
  echo "Criando venv no backend..."
  python3 -m venv backend/venv 2>/dev/null || py -3 -m venv backend/venv
fi
if [ -f backend/venv/bin/activate ]; then
  source backend/venv/bin/activate
elif [ -f backend/.venv/Scripts/activate ]; then
  source backend/.venv/Scripts/activate
fi
cd backend
pip install -q -r requirements.txt
echo "Iniciando backend em http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$ROOT"

# Frontend
cd frontend
if ! [ -d node_modules ]; then
  echo "Instalando dependências do frontend..."
  npm install
fi
echo "Iniciando frontend em http://localhost:5173"
npm run dev &
FRONTEND_PID=$!
cd "$ROOT"

echo "Backend PID: $BACKEND_PID | Frontend PID: $FRONTEND_PID"
echo "Para parar: kill $BACKEND_PID $FRONTEND_PID"
wait
