"""Configurações centralizadas do pipeline de tempo por etapa."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS_PATH = PROJECT_ROOT / "suposicoes" / "base_eventos.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "resultados_oficiais"


@dataclass(frozen=True)
class StageTimeConfig:
    """Contrato de cálculo da permanência nas etapas."""

    cutoff_date: pd.Timestamp
    min_observations: int = 10
    terminal_stages: tuple[str, ...] = (
        "Contrato assinado",
        "Oportunidade perdida",
    )
    collapse_consecutive_same_stage: bool = True
    include_censored_open_intervals: bool = True

    @classmethod
    def from_environment(cls) -> "StageTimeConfig":
        """Lê o corte do ambiente para tornar a execução reproduzível.

        A variável STAGE_TIME_CUTOFF deve estar no formato YYYY-MM-DD.
        Não usar a data atual automaticamente: isso mudaria o resultado
        sem alterar a versão do código ou da fonte.
        """
        raw_cutoff = os.getenv("STAGE_TIME_CUTOFF")
        if not raw_cutoff:
            raise ValueError(
                "Defina STAGE_TIME_CUTOFF no formato YYYY-MM-DD. "
                "Exemplo: export STAGE_TIME_CUTOFF=2026-04-17"
            )
        cutoff = pd.to_datetime(raw_cutoff, format="%Y-%m-%d", errors="raise")
        return cls(cutoff_date=cutoff)


def project_path(value: str | Path) -> Path:
    """Converte caminho relativo ao projeto em caminho absoluto."""
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path