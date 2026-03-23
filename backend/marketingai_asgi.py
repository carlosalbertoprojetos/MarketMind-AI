"""Uvicorn entrypoint unico para evitar conflito com outros pacotes app.* no ambiente local."""

from app.main import app

__all__ = ["app"]
