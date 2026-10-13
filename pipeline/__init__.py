"""Funções reutilizáveis do pipeline analítico do projeto RPVMM-Poliedro."""

from .config import PROJECT_ROOT, StageTimeConfig
from .tempo_etapa import (
    build_stage_intervals,
    summarize_stage_time,
    summarize_opportunity_stagnation,
)

__all__ = [
    "PROJECT_ROOT",
    "StageTimeConfig",
    "build_stage_intervals",
    "summarize_stage_time",
    "summarize_opportunity_stagnation",
]