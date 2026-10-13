#!/usr/bin/env python3
"""Executa a análise de tempo por etapa e exporta tabelas/gráficos."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import plotly.express as px

import sys

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from pipeline.config import DEFAULT_EVENTS_PATH, DEFAULT_OUTPUT_DIR, StageTimeConfig, project_path
from pipeline.tempo_etapa import (
    build_stage_intervals,
    summarize_opportunity_stagnation,
    summarize_stage_time,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--events",
        type=Path,
        default=DEFAULT_EVENTS_PATH,
        help="CSV padronizado de eventos.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Diretório de resultados.",
    )
    parser.add_argument(
        "--cutoff",
        required=True,
        help="Data de corte no formato YYYY-MM-DD.",
    )
    parser.add_argument(
        "--min-observations",
        type=int,
        default=10,
        help="Mínimo para não marcar etapa como baixa sustentação.",
    )
    return parser.parse_args()


def save_bar_chart(summary: pd.DataFrame, output_dir: Path) -> None:
    plot_df = summary.loc[~summary["low_support"]].copy()
    if plot_df.empty:
        return

    plot_df = plot_df.sort_values("median_days", ascending=True)
    plot_df["label"] = plot_df.apply(
        lambda row: (
            f"n={int(row['n_intervals'])}; "
            f"Q1={row['q1_days']:.0f}; Q3={row['q3_days']:.0f}"
        ),
        axis=1,
    )

    fig = px.bar(
        plot_df,
        x="median_days",
        y="stage",
        orientation="h",
        text="label",
        title="Tempo mediano observado por etapa",
        labels={
            "median_days": "Mediana de dias",
            "stage": "Etapa",
        },
        hover_data=[
            "q1_days",
            "q3_days",
            "iqr_days",
            "n_intervals",
            "censored_rate",
            "jump_rate",
        ],
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    fig.write_html(output_dir / "mediana_tempo_por_etapa.html")


def save_boxplot(intervals: pd.DataFrame, summary: pd.DataFrame, output_dir: Path) -> None:
    supported = summary.loc[~summary["low_support"], "stage"]
    plot_df = intervals[intervals["stage"].isin(supported)].copy()
    if plot_df.empty:
        return

    fig = px.box(
        plot_df,
        x="days_in_stage",
        y="stage",
        orientation="h",
        points=False,
        title="Distribuição do tempo observado por etapa",
        labels={
            "days_in_stage": "Dias",
            "stage": "Etapa",
        },
    )
    fig.write_html(output_dir / "distribuicao_tempo_por_etapa.html")


def main() -> None:
    args = parse_args()
    events_path = project_path(args.events)
    output_dir = project_path(args.output)
    figures_dir = output_dir / "figuras"
    figures_dir.mkdir(parents=True, exist_ok=True)

    events = pd.read_csv(events_path)
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    if "created_at" in events.columns:
        events["created_at"] = pd.to_datetime(events["created_at"], errors="coerce")

    config = StageTimeConfig(
        cutoff_date=pd.to_datetime(args.cutoff, format="%Y-%m-%d", errors="raise"),
        min_observations=args.min_observations,
    )

    intervals = build_stage_intervals(events, config)
    summary = summarize_stage_time(
        intervals,
        min_observations=config.min_observations,
        group_columns=("stage",),
    )
    summary_by_brand = summarize_stage_time(
        intervals.dropna(subset=["brand"]),
        min_observations=config.min_observations,
        group_columns=("brand", "stage"),
    )
    stagnation = summarize_opportunity_stagnation(intervals, summary)

    output_dir.mkdir(parents=True, exist_ok=True)
    intervals.to_csv(output_dir / "intervalos_por_etapa.csv", index=False)
    summary.to_csv(output_dir / "tempo_por_etapa.csv", index=False)
    summary_by_brand.to_csv(output_dir / "tempo_por_etapa_marca.csv", index=False)
    stagnation.to_csv(output_dir / "estagnacao_por_oportunidade.csv", index=False)
    save_bar_chart(summary, figures_dir)
    save_boxplot(intervals, summary, figures_dir)

    print(f"Eventos lidos: {len(events):,}")
    print(f"Intervalos gerados: {len(intervals):,}")
    print(f"Etapas resumidas: {len(summary):,}")
    print(f"Oportunidades abertas avaliadas: {len(stagnation):,}")
    print(f"Saída: {output_dir}")


if __name__ == "__main__":
    main()