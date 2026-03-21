"""
Configuração do banco de dados SQLAlchemy.
Usa SQLite por padrão; use DATABASE_URL para PostgreSQL em produção.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./marketingai.db")
# SQLite exige check_same_thread=False; PostgreSQL não usa
connect_args = {} if SQLALCHEMY_DATABASE_URL.startswith("postgresql") else {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency: fornece sessão do banco e fecha ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
