"""Modulo orquestrador do pipeline autonomo."""

from .models import OrchestratedRunResult
from .service import run_pipeline

__all__ = ["OrchestratedRunResult", "run_pipeline"]
