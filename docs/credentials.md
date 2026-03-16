# Credenciais e Variaveis de Ambiente

Este documento lista tudo o que deve ser informado pelo desenvolvedor, onde inserir e como usar. Nunca commite segredos no git.

## Backend (local, sem Docker)
Arquivo: `backend/.env`

### Banco de dados
- `DATABASE_URL`: string completa do Postgres.
  - Exemplo: `postgresql+psycopg://usuario:senha@localhost:5432/marketmindai_db`
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
  - Usados pelos scripts de provisionamento (`scripts/create-db.ps1`).

### Redis (fila)
- `REDIS_URL`: URL do Redis (ex.: `redis://localhost:6379/0`)

### Auth (JWT)
- `SECRET_KEY`: chave para assinar tokens.
- `ALGORITHM`: algoritmo JWT (default `HS256`).
- `ACCESS_TOKEN_EXPIRE_MINUTES`: tempo de expiração do access token.
- `REFRESH_TOKEN_EXPIRE_DAYS`: tempo de expiração do refresh token.

### OpenAI
- `OPENAI_API_KEY`: chave da OpenAI (backend e worker).
- `OPENAI_ORG_ID`: opcional.
- `OPENAI_PROJECT_ID`: opcional.
- `OPENAI_EMBEDDING_MODEL`: default `text-embedding-3-small`.
- `OPENAI_EMBEDDING_DIM`: default `1536`.
  - Se mudar o modelo/dimensao, atualize a coluna `embedding` via migration.

### Storage (S3 compatível)
- `S3_ENDPOINT_URL`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `S3_BUCKET`

## Docker Compose
Arquivo: `docker-compose.yml`

### Backend e Worker
Mesmas variaveis do backend local:
- `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `ALGORITHM`,
  `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`,
  `OPENAI_API_KEY`, `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`,
  `OPENAI_EMBEDDING_MODEL`, `OPENAI_EMBEDDING_DIM`,
  `S3_ENDPOINT_URL`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET`.

### Frontend (Docker)
- `NEXT_PUBLIC_API_URL`: URL base do backend para consumo pelo frontend.
  - Exemplo: `http://backend:8000/api/v1`

## Integracoes Sociais (placeholder)
As integracoes reais ainda nao estao implementadas. Quando ativadas, as credenciais devem entrar por tenant e ficar no banco:
- `social_accounts.access_token_encrypted`
- `social_accounts.refresh_token_encrypted`

No estado atual, o payload de criacao aceita `access_token` e `refresh_token` na API e salva no banco.

## Email/SMTP (nao implementado)
Nao ha configuracao de SMTP no sistema atual. Se for adicionar, use:
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`
e documente no backend.

## Onde inserir (resumo rapido)
- Local sem Docker: `backend/.env`
- Docker: `docker-compose.yml` (backend/worker) e `NEXT_PUBLIC_API_URL` (frontend)

## Boas praticas
- Use um gerenciador de segredos em producao.
- Gire `SECRET_KEY` e `OPENAI_API_KEY` caso tenham sido expostas.
