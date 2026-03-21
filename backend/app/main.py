"""
MarketingAI Backend - API FastAPI com autenticação JWT.

Rotas:
  POST /auth/register  - Registrar usuário
  POST /auth/login     - Login (retorna JWT)
  GET  /user/campaigns - Listar campanhas do usuário (requer JWT)
  POST /campaign       - Criar campanha (requer JWT)
  GET  /campaign       - Listar campanhas (requer JWT)
  GET  /campaign/{id}  - Obter campanha (requer JWT)
  PATCH /campaign/{id} - Atualizar campanha (requer JWT)
  DELETE /campaign/{id}- Remover campanha (requer JWT)

Variáveis opcionais (ex.: MarketingAI/backend/.env): OPENAI_API_KEY, MARKETINGAI_IMAGE_SOURCE, MARKETINGAI_MAX_CRAWL_PAGES.
"""
import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

_backend_root = Path(__file__).resolve().parent.parent
load_dotenv(_backend_root / ".env")

# Playwright (scraping): no Windows, SelectorEventLoop não implementa subprocessos async do Chromium.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import engine
from app.models import Base, User, Credentials, Campaign  # import para registrar tabelas
from app.routes import auth, user, campaign, credentials
from app.utils.limiter import limiter


def create_tables():
    """Cria tabelas no banco (fallback quando não usa Alembic)."""
    Base.metadata.create_all(bind=engine)


def run_migrations():
    """Executa Alembic upgrade head (use RUN_MIGRATIONS=1 em produção)."""
    import os
    import subprocess
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run(["alembic", "upgrade", "head"], cwd=root, check=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialização ao subir a aplicação."""
    if os.environ.get("RUN_MIGRATIONS") == "1":
        try:
            run_migrations()
        except Exception:
            create_tables()  # fallback se alembic falhar
    else:
        create_tables()
    yield
    # cleanup se necessário


app = FastAPI(
    title="MarketingAI API",
    description="API para geração automática de campanhas de marketing a partir de URL",
    version="0.1.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS para o frontend (ajuste origins em produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(campaign.router)
app.include_router(credentials.router)


@app.get("/health")
def health():
    """Health check para deploy e load balancers."""
    return {"status": "ok"}
