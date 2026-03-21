# Production Checklist

## Infraestrutura
- Configurar `DATABASE_URL` para PostgreSQL em produ??o.
- Definir `SECRET_KEY` forte e exclusiva por ambiente.
- Desativar `DEBUG`/modo desenvolvimento no ambiente final.
- Publicar backend atr?s de reverse proxy com HTTPS.
- Garantir storage persistente para `ia_pipeline/output` ou mover artefatos para S3/objeto equivalente.

## Backend
- Executar `alembic upgrade head`.
- Definir `RUN_MIGRATIONS=1` apenas se a estrat?gia de deploy suportar migra??o autom?tica.
- Configurar CORS apenas com os dom?nios reais do frontend.
- Revisar limites de rate limit por ambiente.
- Habilitar monitoramento de logs e healthcheck em `/health`.

## Frontend
- Definir `VITE_API_URL` para o backend p?blico em builds de produ??o.
- Em desenvolvimento local, usar `VITE_API_PROXY_TARGET=http://127.0.0.1:8003`.
- Validar fluxo de login, cria??o de campanha, preview e export antes do go-live.

## IA e Pipeline
- Definir `OPENAI_API_KEY` se quiser gera??o enriquecida por LLM/DALL-E.
- Configurar `MARKETINGAI_IMAGE_PROVIDER` e, se aplic?vel, `STABLE_DIFFUSION_API_URL` / `STABLE_DIFFUSION_API_KEY`.
- Instalar Playwright Chromium no servidor que executa scraping.
- Validar sites protegidos por login usando credenciais salvas em `/credentials`.

## Publica??o Social
- Instagram: `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID`.
- Facebook: `FACEBOOK_PAGE_ACCESS_TOKEN`, `FACEBOOK_PAGE_ID`.
- LinkedIn: `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_ORGANIZATION_ID`.
- X/Twitter: `TWITTER_ACCESS_TOKEN` e segredos relacionados.
- TikTok: `TIKTOK_ACCESS_TOKEN`, `TIKTOK_ACCOUNT_ID`, `TIKTOK_PRIVACY_LEVEL`.
- Se n?o houver credenciais reais, manter `MARKETINGAI_PUBLISHER_MODE=mock`.

## Seguran?a
- Nunca commitar `.env`, `.env.local`, bancos SQLite, logs ou artefatos do pipeline.
- Rotacionar tokens e chaves periodicamente.
- Revisar permiss?es de usu?rios e credenciais armazenadas.
- Proteger endpoints autenticados com HTTPS e cabe?alhos seguros no proxy.

## Qualidade
- Backend: `py -3 -m pytest -q`
- Frontend: `npm test`
- Frontend build: `npm run build`
- Smoke manual m?nimo:
  - login
  - salvar credencial
  - gerar preview por uma plataforma
  - exportar ZIP
  - abrir biblioteca de m?dia

## Status desta entrega
- Backend validado: 48 testes passando.
- Frontend validado: 21 testes passando.
- Build do frontend: OK.
- Preview/export respeitando plataforma selecionada: OK.
- TikTok fim a fim no pipeline: OK.
