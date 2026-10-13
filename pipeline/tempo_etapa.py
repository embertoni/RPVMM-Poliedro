"""Cálculo de permanência por etapa e indicadores de estagnação.

Regras metodológicas:
- o intervalo é atribuído à etapa do evento de origem;
- etapas puladas não recebem duração artificial;
- o último estágio de uma oportunidade aberta vai até a data de corte
  e é marcado como censurado;
- não há permanência posterior a um estado terminal;
- eventos consecutivos na mesma etapa podem ser consolidados;
- toda execução preserva indicadores de salto e censura.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from .config import StageTimeConfig


REQUIRED_COLUMNS = {
    "opportunity_id",
    "event_id",
    "event_date",
    "stage",
}


def require_event_columns(events: pd.DataFrame) -> None:
    """Falha cedo se a base não tiver o contrato mínimo."""
    missing = sorted(REQUIRED_COLUMNS - set(events.columns))
    if missing:
        raise KeyError(f"Colunas ausentes na base de eventos: {missing}")


def validate_cutoff(events: pd.DataFrame, cutoff_date: pd.Timestamp) -> None:
    """Valida datas antes do cálculo."""
    if pd.isna(cutoff_date):
        raise ValueError("A data de corte não pode ser nula.")
    if events["event_date"].isna().any():
        raise ValueError("Há eventos sem event_date.")
    if (events["event_date"] > cutoff_date).any():
        raise ValueError("Há eventos posteriores à data de corte.")


def _prepare_events(events: pd.DataFrame) -> pd.DataFrame:
    out = events.copy()
    out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")
    if "created_at" in out.columns:
        out["created_at"] = pd.to_datetime(out["created_at"], errors="coerce")

    sort_columns = [
        column
        for column in ("opportunity_id", "event_date", "created_at", "event_id")
        if column in out.columns
    ]
    return out.sort_values(sort_columns, kind="stable").reset_index(drop=True)


def _last_outcome(group: pd.DataFrame) -> str:
    """Obtém o desfecho existente ou deriva um valor conservador."""
    if "outcome" in group.columns and group["outcome"].notna().any():
        return str(group["outcome"].dropna().iloc[-1])

    last_stage = group["stage"].iloc[-1]
    if last_stage == "Contrato assinado":
        return "won"
    if last_stage == "Oportunidade perdida":
        return "lost"
    return "open"


def _optional_value(row: pd.Series, column: str, default=pd.NA):
    return row[column] if column in row.index else default


def build_stage_intervals(
    events: pd.DataFrame,
    config: StageTimeConfig,
) -> pd.DataFrame:
    """Constrói uma linha por permanência observada ou censurada.

    Para um par de eventos A -> B, o intervalo pertence a A. Se B estiver
    mais de uma posição à frente/atrás na sequência oficial, o intervalo
    recebe is_jump=True e as etapas intermediárias permanecem não observadas.
    Para o último evento de uma oportunidade aberta, o intervalo termina na
    data de corte e recebe censored=True.
    """
    require_event_columns(events)
    prepared = _prepare_events(events)
    validate_cutoff(prepared, config.cutoff_date)

    rows: list[dict] = []

    for opportunity_id, group in prepared.groupby("opportunity_id", sort=False):
        group = group.reset_index(drop=True)
        if config.collapse_consecutive_same_stage:
            group = group[group["stage"] != group["stage"].shift()].reset_index(drop=True)
        outcome = _last_outcome(group)

        for index, current in group.iterrows():
            stage = current["stage"]

            if stage in config.terminal_stages:
                continue

            next_row = group.iloc[index + 1] if index + 1 < len(group) else None

            # Eventos consecutivos na mesma etapa são atividade/repetição, não
            # uma saída da etapa. O primeiro evento da sequência continua sendo
            # o início da permanência.
            if (
                config.collapse_consecutive_same_stage
                and next_row is not None
                and next_row["stage"] == stage
            ):
                continue

            if next_row is not None:
                end_date = next_row["event_date"]
                next_stage = next_row["stage"]
                next_event_id = next_row["event_id"]
                censored = False
            elif outcome == "open" and config.include_censored_open_intervals:
                end_date = config.cutoff_date
                next_stage = pd.NA
                next_event_id = pd.NA
                censored = True
            else:
                # Último evento não terminal de uma oportunidade encerrada ou
                # jornada incompleta: não inventar uma data de saída.
                continue

            days = int((end_date - current["event_date"]).days)
            if days < 0:
                raise ValueError(
                    "Intervalo negativo em "
                    f"opportunity_id={opportunity_id}, event_id={current['event_id']}"
                )

            current_order = _optional_value(current, "stage_order", np.nan)
            next_order = (
                _optional_value(next_row, "stage_order", np.nan)
                if next_row is not None
                else np.nan
            )
            is_jump = bool(
                pd.notna(current_order)
                and pd.notna(next_order)
                and abs(float(next_order) - float(current_order)) > 1
            )

            rows.append(
                {
                    "opportunity_id": opportunity_id,
                    "account_id": _optional_value(current, "account_id"),
                    "brand": _optional_value(current, "brand"),
                    "stage": stage,
                    "phase": _optional_value(current, "phase"),
                    "stage_order": current_order,
                    "stage_start_date": current["event_date"],
                    "stage_end_date": end_date,
                    "days_in_stage": days,
                    "censored": censored,
                    "outcome": outcome,
                    "next_stage": next_stage,
                    "next_event_id": next_event_id,
                    "is_jump": is_jump,
                    "intermediate_stages_unobserved": is_jump,
                }
            )

    columns = [
        "opportunity_id",
        "account_id",
        "brand",
        "stage",
        "phase",
        "stage_order",
        "stage_start_date",
        "stage_end_date",
        "days_in_stage",
        "censored",
        "outcome",
        "next_stage",
        "next_event_id",
        "is_jump",
        "intermediate_stages_unobserved",
    ]
    return pd.DataFrame(rows, columns=columns)


def summarize_stage_time(
    intervals: pd.DataFrame,
    min_observations: int = 10,
    group_columns: Iterable[str] = ("stage",),
) -> pd.DataFrame:
    """Agrega mediana, quartis, IQR, censura e saltos."""
    group_columns = tuple(group_columns)
    if intervals.empty:
        return pd.DataFrame()

    missing = set(group_columns) - set(intervals.columns)
    if missing:
        raise KeyError(f"Colunas de agrupamento ausentes: {sorted(missing)}")

    grouped = intervals.groupby(list(group_columns), dropna=False)
    summary = grouped.agg(
        n_intervals=("days_in_stage", "count"),
        median_days=("days_in_stage", "median"),
        mean_days=("days_in_stage", "mean"),
        min_days=("days_in_stage", "min"),
        max_days=("days_in_stage", "max"),
        n_censored=("censored", "sum"),
        n_jumps=("is_jump", "sum"),
    ).reset_index()

    quartiles = grouped["days_in_stage"].quantile([0.25, 0.75]).unstack()
    quartiles = quartiles.rename(columns={0.25: "q1_days", 0.75: "q3_days"})
    summary = summary.merge(
        quartiles.reset_index(),
        on=list(group_columns),
        how="left",
    )
    summary["iqr_days"] = summary["q3_days"] - summary["q1_days"]
    summary["censored_rate"] = summary["n_censored"] / summary["n_intervals"]
    summary["jump_rate"] = summary["n_jumps"] / summary["n_intervals"]
    summary["low_support"] = summary["n_intervals"] < min_observations

    return summary.sort_values(
        list(group_columns) if len(group_columns) > 1 else ["median_days"],
        ascending=False,
    ).reset_index(drop=True)


def summarize_opportunity_stagnation(
    intervals: pd.DataFrame,
    stage_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Marca a permanência atual acima do Q3 de referência da etapa.

    A função só marca intervalos censurados. Intervalos históricos fechados
    são úteis para descrever o funil, mas não representam oportunidades
    atualmente estagnadas.
    """
    required_intervals = {
        "opportunity_id",
        "stage",
        "days_in_stage",
        "censored",
    }
    missing = required_intervals - set(intervals.columns)
    if missing:
        raise KeyError(f"Colunas ausentes nos intervalos: {sorted(missing)}")

    required_summary = {"stage", "q3_days", "median_days", "iqr_days", "n_intervals"}
    missing = required_summary - set(stage_summary.columns)
    if missing:
        raise KeyError(f"Colunas ausentes no resumo: {sorted(missing)}")

    current = intervals[intervals["censored"].astype(bool)].copy()
    if current.empty:
        current["stage_q3_days"] = pd.Series(dtype=float)
        current["is_stalled"] = pd.Series(dtype=bool)
        return current

    reference = stage_summary[
        ["stage", "median_days", "q3_days", "iqr_days", "n_intervals", "low_support"]
    ].rename(
        columns={
            "median_days": "stage_median_days",
            "q3_days": "stage_q3_days",
            "iqr_days": "stage_iqr_days",
            "n_intervals": "stage_n_intervals",
            "low_support": "stage_low_support",
        }
    )
    current = current.merge(reference, on="stage", how="left", validate="many_to_one")
    current["is_stalled"] = (
        current["stage_q3_days"].notna()
        & ~current["stage_low_support"].fillna(True)
        & (current["days_in_stage"] > current["stage_q3_days"])
    )
    return current