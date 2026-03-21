# MarketingAI

Sistema SaaS de geração automática de campanhas de marketing a partir de qualquer URL, pronto para múltiplas redes sociais.

## Estrutura do Projeto

```
MarketingAI/
├─ backend/           # API FastAPI + autenticação JWT
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ routes/
│  │  ├─ models/
│  │  ├─ services/
│  │  ├─ schemas/
│  │  └─ utils/
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/          # React + TailwindCSS (Vite)
│  ├─ src/
│  │  ├─ components/
│  │  ├─ pages/
│  │  ├─ api/
│  │  └─ context/
│  ├─ package.json
│  └─ Dockerfile
├─ ia_pipeline/       # Scraping, NLP e geração de imagens
│  ├─ scraping.py
│  ├─ nlp.py
│  ├─ image_generation.py
│  ├─ pipeline.py
│  └─ prompts/
├─ database/
│  └─ migrations/
├─ scripts/           # start-local.sh, init-pipeline.sh, run-backend.bat
├─ run.bat            # Executar sistema (backend + frontend) no Windows
├─ docker-compose.yml
└─ README.md
```

## Pré-requisitos

- Python 3.11+
- Node.js 18+
- Docker e Docker Compose (para deploy em container)

## Início Rápido

### Opção 1: Docker Compose (recomendado para testes completos)

```bash
cd MarketingAI
docker compose up --build
```

- **Backend:** http://localhost:8000  
- **Frontend:** http://localhost:80  
- **Docs da API:** http://localhost:8000/docs  

Variáveis opcionais: `SECRET_KEY`, `DATABASE_URL`.

### Opção 2: Desenvolvimento local

**Backend** (obrigatório rodar de dentro de `MarketingAI/backend`, onde está o módulo `app`):
```bash
cd MarketingAI/backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd MarketingAI/frontend
npm install
npm run dev
```

Acesse http://localhost:5173. O proxy do Vite encaminha `/api` para o backend na porta 8000.

**Script único (backend + frontend)**  
- **Windows:** duplo-clique em `MarketingAI/run.bat` (abre duas janelas: backend e frontend).  
- **Linux/Mac:** `cd MarketingAI && bash scripts/start-local.sh`

### Pipeline IA (scraping + NLP + imagens)

Para usar **Pré-visualizar posts** (botão na tela "Nova campanha") a partir de uma URL, o backend precisa ter acesso ao diretório `ia_pipeline` (por exemplo, rodando o backend **localmente**, não apenas em Docker). Em Docker, o preview pode retornar 503; use o ambiente local para essa função.

```bash
cd MarketingAI
bash scripts/init-pipeline.sh
```

Isso instala dependências do `ia_pipeline` e o browser Chromium do Playwright.

**Chave OpenAI (opcional):** crie `backend/.env` a partir de `backend/.env.example` e defina `OPENAI_API_KEY`. Com a chave, o pipeline tende a gerar **arte DALL·E** a partir do copy de marketing (`MARKETINGAI_IMAGE_SOURCE`: `marketing_dalle` padrão, `screenshot` só print do site, `both` os dois). **Nunca** coloque a chave no frontend.

**Crawl multi-página:** o scraper segue links **do mesmo domínio** (BFS), até `max_crawl_pages` (UI em Nova campanha ou `MARKETINGAI_MAX_CRAWL_PAGES` na geração da campanha salva). Por página: texto visível + OCR + imagens; marketing e imagem de IA por combinação página × rede.

Teste o scraping:
```bash
cd MarketingAI/ia_pipeline
python scraping.py https://example.com
```

**Windows – `NotImplementedError` / Playwright:** o backend e o `scraping.py` forçam `WindowsProactorEventLoopPolicy()` para o Chromium conseguir abrir subprocesso. Reinicie o servidor após atualizar.

**Timeout no scraping / posts vazios:** a navegação usa `domcontentloaded` + `load` (não `networkidle`), pois muitos sites nunca ficam ociosos na rede e o Playwright estourava o tempo antes do screenshot.

**Browsers Playwright:** use *o mesmo Python do backend* (ex.: após `backend\venv\Scripts\activate`):

```bash
python -m playwright install chromium
```

Ou no Windows: `scripts\install-playwright-chromium.bat` (usa `backend\venv` se existir; senão `py -m playwright`).

**Reiniciar o backend:** na janela do uvicorn, `Ctrl+C`; suba de novo com `run.bat` ou `cd backend && py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

## Funcionalidades por Etapa

1. **Estrutura** – Pastas e organização
2. **Backend** – FastAPI, JWT, modelos User/Credentials/Campaign, rotas de auth e campanhas
3. **Frontend** – Login, Registro, Dashboard, Nova campanha, Calendário (React + Tailwind)
4. **Webscraping** – Playwright headless, screenshots, login opcional, OCR (Tesseract)
5. **Pipeline IA** – NLP (insights, headlines, CTAs, roteiros), adaptação por rede, imagens por tamanho
6. **Output** – Pacote por rede (texto, hashtags, horários sugeridos, passo a passo), preview na UI
7. **Agenda** – Calendário tipo Google Calendar, drag-and-drop, filtro por rede
8. **Deploy** – Docker Compose, scripts, variáveis de ambiente  
9. **Credentials** – CRUD de credenciais (login em URLs), uso no preview e export; criptografia Fernet
10. **Imagens no preview** – Endpoint para servir imagens do pipeline; cards com miniatura no frontend
11. **Lembretes** – GET /campaign/upcoming?hours=24, POST /campaign/{id}/remind, script `scripts/check-reminders.py`
12. **Export ZIP** – POST /campaign/export gera pacote por plataforma (imagens + caption.txt); botão "Baixar pacote (ZIP)"
13. **Testes** – pytest no backend (auth, campanhas, credenciais, health, upcoming, remind); SQLite em memória com StaticPool; Vitest + React Testing Library no frontend (Login, Register, Dashboard, Credenciais, 404)
14. **Migrações** – Alembic no backend (alembic upgrade head); RUN_MIGRATIONS=1 no startup opcional
15. **Dashboard e detalhe** – GET /user/summary (total, por plataforma, próximas 24h); cards de resumo no Dashboard; página de detalhe da campanha (/campaign/:id) com Editar e Excluir
16. **Rate limiting e paginação** – SlowAPI por IP; limites em auth (register/login), preview e export; listagem de campanhas com `limit`/`offset` e resposta `{ items, total, limit, offset }`
17. **Paginação no Dashboard** – Controles Anterior/Próxima e texto "Mostrando X–Y de Z" na listagem de campanhas
18. **Filtros e busca na listagem** – Backend: query params `platform`, `search`, `sort` em GET /user/campaigns e GET /campaign; frontend: filtro por plataforma, busca por título (com debounce) e ordenação (mais recentes, mais antigas, agendamento) no Dashboard
19. **Página de Credenciais** – Página dedicada em /credentials para listar, criar e excluir credenciais (login em URLs); link "Credenciais" na Navbar
20. **Página 404** – Para URLs inexistentes, exibir página "Página não encontrada" (404) com link para Dashboard ou Login, em vez de redirecionar para /
21. **Tamanho de página no Dashboard** – Seletor "Itens por página" (12, 24 ou 50); preferência salva em localStorage
22. **Testes frontend** – Vitest + React Testing Library; testes para Login, Register, Dashboard, Credenciais, 404 (API mockada)
23. **Toasts de feedback** – Notificações visuais (sucesso/erro) após login, cadastro, criar/editar/excluir campanha, salvar/remover credencial; ToastContext + componente fixo no canto da tela
24. **Duplicar campanha** – Botão "Duplicar" na página de detalhe e no card do Dashboard; cria cópia com título "(cópia)", mesmo conteúdo e plataforma, sem agendamento
25. **Página Sobre** – Rota pública /sobre com descrição do produto, funcionalidades e tecnologias; link "Sobre" na Navbar (logado e não logado)
26. **Modo escuro** – Toggle "Modo escuro" / "Modo claro" na Navbar; preferência salva em localStorage; Tailwind dark: em páginas principais (Dashboard, Login, Register, Sobre, 404, cards)
27. **Toasts no modo escuro** – Notificações visuais (sucesso/erro) respeitam `dark:` (cores e contraste)
28. **Persistência e polimento final** – Correção do campo "URL do site/produto" ao editar campanha; revisão geral de dark mode nas telas (Nova campanha, Calendário, Credenciais) e ajustes de UI
29. **Ícone-only no toggle e parsing robusto** – Toggle de tema apenas com ícone (sem texto/emoji) e parsing mais tolerante do campo URL ao editar
30. **Correção do dev server (IPv4/localhost) + varredura final dark** – Ajuste do Vite para evitar `ERR_CONNECTION_REFUSED` no `localhost` e checagem final de dark mode nos componentes auxiliares das telas principais
31. **UI responsiva + geração estrita por URL + biblioteca de mídia** – Navbar com menu hambúrguer no mobile (sem link "Nova campanha"), geração de posts por campanha a partir da URL salva e nova tela de galeria de ativos gerados
32. **Filtros de mídia + histórico de gerações** – Biblioteca de mídia com filtros por tipo/plataforma e histórico auditável de execuções do pipeline por campanha
33. **Exportação em lote da galeria filtrada** – Download de ZIP dos ativos visíveis na biblioteca de mídia, respeitando filtros por tipo e plataforma
34. **Seleção manual de ativos para exportação** – Checkboxes por item na galeria e ZIP customizado com apenas os ativos escolhidos pelo usuário
35. **Filtro por período de geração** – Biblioteca e exportação por filtros passam a aceitar intervalo de datas de geração dos ativos

## API (resumo)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | /auth/register | Registrar usuário |
| POST | /auth/login | Login (retorna JWT) |
| GET | /user/summary | Resumo do dashboard: total, por plataforma, próximas 24h (JWT) |
| GET | /user/campaigns?limit=50&offset=0&platform=&search=&sort= | Listar campanhas paginadas com filtros (JWT). Params opcionais: platform, search (título), sort (created_at_desc, created_at_asc, schedule_desc, schedule_asc). Resposta: `{ items, total, limit, offset }` |
| GET | /credentials | Listar credenciais (JWT) |
| POST | /credentials | Criar credencial (JWT) |
| DELETE | /credentials/{id} | Remover credencial (JWT) |
| POST | /campaign | Criar campanha (JWT) |
| GET | /campaign?limit=50&offset=0 | Listar campanhas paginadas (JWT). Resposta: `{ items, total, limit, offset }` |
| GET | /campaign/upcoming?hours=24 | Campanhas agendadas nas próximas N h (JWT) |
| POST | /campaign/{id}/remind | Marcar lembrete enviado (JWT) |
| GET | /campaign/{id} | Obter campanha (JWT) |
| PATCH | /campaign/{id} | Atualizar campanha (JWT) |
| DELETE | /campaign/{id} | Remover campanha (JWT) |
| POST | /campaign/preview | Gerar preview a partir de URL (JWT) |
| POST | /campaign/{id}/generate | Gerar posts da campanha usando a URL salva na própria campanha (JWT) |
| GET | /campaign/{id}/assets | Listar ativos de mídia gerados da campanha (JWT). Filtros: `kind`, `platform`, `generated_from`, `generated_to` |
| GET | /campaign/{id}/assets/export | Exportar ZIP dos ativos filtrados por `kind`, `platform`, `generated_from`, `generated_to` (JWT) |
| POST | /campaign/{id}/assets/export-selected | Exportar ZIP dos ativos selecionados manualmente (JWT) |
| GET | /campaign/{id}/generations | Histórico de gerações da campanha (data, URL fonte, total de posts e ativos) (JWT) |
| GET | /campaign/preview/image?path=... | Servir imagem do pipeline (JWT) |
| POST | /campaign/export | Gerar e baixar ZIP do pacote (JWT) |
| GET | /health | Health check |

**Rate limits (por IP):** registro 10/min; login 15/min; preview 20/min; export 10/min. Em caso de excesso: 429 Too Many Requests.

## Testes (backend)

```bash
cd MarketingAI/backend
pip install -r requirements.txt   # inclui pytest, pytest-cov, httpx
pytest tests/ -v
# Com cobertura:
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Testes (frontend)

O frontend usa **Vitest** e **React Testing Library** (jsdom). Testes em `frontend/src/test/`: rotas/páginas públicas (Login, Register, 404), Login e Register com API mockada, Dashboard e Credenciais com API mockada.

```bash
cd MarketingAI/frontend
npm install
npm run test        # executa uma vez
npm run test:watch  # modo watch
```

## Migrações (Alembic)

O backend usa **Alembic** para versionar o schema do banco. A URL é lida de `app.database` (env `DATABASE_URL`).

```bash
cd MarketingAI/backend
pip install -r requirements.txt
# Aplicar todas as migrações
alembic upgrade head
# Criar nova migração após alterar modelos
alembic revision --autogenerate -m "descrição"
# Ver revisão atual / histórico
alembic current
alembic history
```

Em produção, defina `RUN_MIGRATIONS=1` para a aplicação rodar `alembic upgrade head` ao subir (senão usa `create_all` como fallback).

**Se o banco já existia (criado com `create_all` antes do Alembic):** rode uma vez `alembic stamp head` para marcar a revisão atual sem executar a migração, evitando erro "table already exists". Depois use `alembic upgrade head` normalmente para novas migrações.

## Deploy em nuvem (opcional)

- **Backend:** defina `DATABASE_URL` (PostgreSQL recomendado), `SECRET_KEY` e opcionalmente `OPENAI_API_KEY`.
- **Frontend:** build com `VITE_API_URL` apontando para a URL pública do backend.
- **Pipeline:** em servidor com Playwright, use o mesmo `OPENAI_API_KEY` para NLP/imagens.
- **Notificações de lembrete:** implementar job (cron ou Celery) que consulta campanhas agendadas e envia e-mail/push (ex.: SendGrid, OneSignal).

## Licença

Projeto interno – SocialOne / MarketMind AI.
