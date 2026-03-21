"""
MarketingAI Backend - API FastAPI com autenticacao JWT.
"""
import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

_backend_root = Path(__file__).resolve().parent.parent
load_dotenv(_backend_root / ".env")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.database import Base, SQLALCHEMY_DATABASE_URL, engine
from app.models import Campaign, Credentials, User
from app.routes import auth, campaign, credentials, user
from app.utils.limiter import limiter
from app.utils.security import DEFAULT_SECRET_KEY, SECRET_KEY

DEV_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://localhost:80",
]


def is_production_environment() -> bool:
    return os.environ.get("MARKETINGAI_ENV", "development").strip().lower() == "production"


def get_allowed_origins() -> list[str]:
    raw = os.environ.get("BACKEND_CORS_ORIGINS", "")
    if not raw.strip():
        return DEV_CORS_ORIGINS
    return [item.strip() for item in raw.split(",") if item.strip()]


def validate_runtime_configuration() -> None:
    if not is_production_environment():
        return

    if not SECRET_KEY or SECRET_KEY == DEFAULT_SECRET_KEY:
        raise RuntimeError("SECRET_KEY invalida para producao")
    if not SQLALCHEMY_DATABASE_URL:
        raise RuntimeError("DATABASE_URL obrigatoria em producao")
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        raise RuntimeError("SQLite nao e suportado em producao")
    if os.environ.get("RUN_MIGRATIONS") != "1":
        raise RuntimeError("RUN_MIGRATIONS=1 e obrigatorio em producao")


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def run_migrations() -> None:
    import subprocess

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run(["alembic", "upgrade", "head"], cwd=root, check=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_runtime_configuration()
    if is_production_environment():
        run_migrations()
    elif os.environ.get("RUN_MIGRATIONS") == "1":
        try:
            run_migrations()
        except Exception:
            create_tables()
    else:
        create_tables()
    yield


app = FastAPI(
    title="MarketingAI API",
    description="API para geracao automatica de campanhas de marketing a partir de URL",
    version="0.1.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
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
    return {"status": "ok"}
