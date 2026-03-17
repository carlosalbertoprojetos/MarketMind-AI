# Deployment

## Prerequisitos
- Docker + Docker Compose
- Python 3.10 (para execucao local sem Docker)

## Subir ambiente (manual)
1. Ajuste as variaveis de ambiente em `docker-compose.yml` se necessario.
2. Suba os containers:
   - `docker-compose up --build`

## Execucao local (sem Docker)
- Start: `scripts/start-local.ps1`
- Stop: `scripts/stop-local.ps1`
- Smoke test: `scripts/smoke-local.ps1`
- Smoke auth (requer Postgres local): `scripts/smoke-auth.ps1`
- Credenciais: veja `docs/credentials.md`

## Migrations
1. Gere a revisao inicial:
   - `alembic revision --autogenerate -m "initial"`
2. Aplique as migrations:
   - `alembic upgrade head`

## Seed (opcional)
- `py -3.10 -m app.scripts.seed_demo`
- `scripts/seed-demo.ps1`

## Servicos
- Backend: `http://localhost:8003`
- Frontend: `http://localhost:3000`
- Postgres: `localhost:5432`
- Redis: `localhost:6379`

## Observacoes
- Alembic esta configurado.
- Seeds iniciais podem ser adicionadas para demo.
- Chaves de API devem ficar no servidor (nunca no frontend).

## Producao
- Recomenda-se separar as imagens e usar secrets para `SECRET_KEY` e credenciais S3.
- Configure TLS, CORS e rate limits.
- Sempre rode `alembic upgrade head` apos novas migrations (ex.: reset de senha).

## OpenAI Key
- Defina `OPENAI_API_KEY` no ambiente do backend/worker (ex.: `docker-compose.yml`).
- Opcional: `OPENAI_ORG_ID` e `OPENAI_PROJECT_ID` quando usar multiplas orgs/projetos.
 - Embeddings: `OPENAI_EMBEDDING_MODEL` (default `text-embedding-3-small`) e `OPENAI_EMBEDDING_DIM` (default `1536`).
 - Se mudar para um modelo com dimensao diferente, atualize as colunas `embedding` e as migrations do banco.
