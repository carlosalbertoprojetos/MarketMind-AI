"""
Fixtures compartilhados para testes do backend MarketingAI.
Usa SQLite em memória com StaticPool para que todas as conexões vejam as mesmas tabelas.
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Força uso de banco em memória antes de importar app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.main import app
from app.database import Base, get_db

# Desabilita rate limiting nos testes (evita 429 após vários logins)
if hasattr(app.state, "limiter"):
    app.state.limiter.enabled = False
from app.models import User, Campaign, Credentials
from app.utils.security import hash_password


# Engine em memória com StaticPool: uma única conexão compartilhada (tabelas visíveis em todas as sessões)
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Sessão de banco isolada por teste. Tabelas criadas e dropadas a cada teste."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient com get_db sobrescrito para usar a sessão de teste."""
    def _get_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Cria um usuário de teste e retorna (user, email, password)."""
    email = "teste@marketingai.com"
    password = "senha123"
    user = User(email=email, password_hash=hash_password(password))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user, email, password


@pytest.fixture
def auth_headers(client, test_user):
    """Faz login e retorna headers com Bearer token."""
    _, email, password = test_user
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
