import pandas as pd
import pytest

from pipeline.config import StageTimeConfig
from pipeline.tempo_etapa import (
    build_stage_intervals,
    summarize_opportunity_stagnation,
    summarize_stage_time,
    validate_cutoff,
)


CUTOFF = pd.Timestamp("2026-04-17")


def test_rejeita_evento_posterior_ao_corte():
    events = pd.DataFrame({
        "event_date": pd.to_datetime(["2026-04-01", "2026-05-01"]),
    })
    with pytest.raises(ValueError, match="posteriores"):
        validate_cutoff(events, CUTOFF)


def test_intervalo_e_atribuido_a_etapa_de_origem():
    events = pd.DataFrame({
        "opportunity_id": ["O1", "O1"],
        "event_id": ["E1", "E2"],
        "event_date": pd.to_datetime(["2026-04-01", "2026-04-11"]),
        "stage": ["Etapa 1", "Etapa 2"],
        "stage_order": [1, 2],
        "outcome": ["won", "won"],
    })
    result = build_stage_intervals(
        events,
        StageTimeConfig(cutoff_date=CUTOFF, terminal_stages=("Etapa 9",)),
    )
    assert len(result) == 1
    assert result.loc[0, "stage"] == "Etapa 1"
    assert result.loc[0, "days_in_stage"] == 10
    assert bool(result.loc[0, "censored"]) is False


def test_aberta_usa_data_de_corte_e_marca_censura():
    events = pd.DataFrame({
        "opportunity_id": ["O1"],
        "event_id": ["E1"],
        "event_date": pd.to_datetime(["2026-04-01"]),
        "stage": ["Etapa 1"],
        "stage_order": [1],
        "outcome": ["open"],
    })
    result = build_stage_intervals(
        events,
        StageTimeConfig(cutoff_date=CUTOFF, terminal_stages=("Etapa 9",)),
    )
    assert len(result) == 1
    assert result.loc[0, "days_in_stage"] == 16
    assert bool(result.loc[0, "censored"]) is True
    assert result.loc[0, "stage_end_date"] == CUTOFF


def test_salto_nao_cria_tempo_para_etapas_intermediarias():
    events = pd.DataFrame({
        "opportunity_id": ["O1", "O1"],
        "event_id": ["E1", "E2"],
        "event_date": pd.to_datetime(["2026-04-01", "2026-04-11"]),
        "stage": ["Etapa 1", "Etapa 4"],
        "stage_order": [1, 4],
        "outcome": ["open", "open"],
    })
    result = build_stage_intervals(
        events,
        StageTimeConfig(cutoff_date=CUTOFF, terminal_stages=("Etapa 9",)),
    )
    assert len(result) == 2
    assert result.loc[0, "days_in_stage"] == 10
    assert bool(result.loc[0, "is_jump"]) is True
    assert set(result["stage"]) == {"Etapa 1", "Etapa 4"}


def test_repeticao_na_mesma_etapa_nao_cria_saida_falsa():
    events = pd.DataFrame({
        "opportunity_id": ["O1", "O1", "O1"],
        "event_id": ["E1", "E2", "E3"],
        "event_date": pd.to_datetime([
            "2026-04-01",
            "2026-04-03",
            "2026-04-11",
        ]),
        "stage": ["Etapa 1", "Etapa 1", "Etapa 2"],
        "stage_order": [1, 1, 2],
        "outcome": ["won", "won", "won"],
    })
    result = build_stage_intervals(
        events,
        StageTimeConfig(cutoff_date=CUTOFF, terminal_stages=("Etapa 9",)),
    )
    assert len(result) == 1
    assert result.loc[0, "stage"] == "Etapa 1"
    assert result.loc[0, "days_in_stage"] == 10


def test_terminal_nao_gera_permanencia_posterior():
    events = pd.DataFrame({
        "opportunity_id": ["O1", "O1"],
        "event_id": ["E1", "E2"],
        "event_date": pd.to_datetime(["2026-04-01", "2026-04-11"]),
        "stage": ["Etapa 1", "Contrato assinado"],
        "stage_order": [1, 12],
        "outcome": ["won", "won"],
    })
    result = build_stage_intervals(
        events,
        StageTimeConfig(cutoff_date=CUTOFF),
    )
    assert len(result) == 1
    assert "Contrato assinado" not in set(result["stage"])


def test_resumo_calcula_mediana_quartis_iqr_e_suporte():
    intervals = pd.DataFrame({
        "stage": ["A"] * 4,
        "days_in_stage": [1, 2, 3, 4],
        "censored": [False, False, False, True],
        "is_jump": [False, False, True, False],
    })
    result = summarize_stage_time(intervals, min_observations=5)
    row = result.iloc[0]
    assert row["median_days"] == 2.5
    assert row["q1_days"] == 1.75
    assert row["q3_days"] == 3.25
    assert row["iqr_days"] == 1.5
    assert bool(row["low_support"]) is True


def test_estagnacao_usa_q3_e_ignora_baixa_amostra():
    intervals = pd.DataFrame({
        "opportunity_id": ["O1", "O2"],
        "stage": ["A", "A"],
        "days_in_stage": [10, 20],
        "censored": [True, True],
        "is_jump": [False, False],
    })
    summary = pd.DataFrame({
        "stage": ["A"],
        "median_days": [10],
        "q3_days": [15],
        "iqr_days": [5],
        "n_intervals": [20],
        "low_support": [False],
    })
    result = summarize_opportunity_stagnation(intervals, summary)
    assert bool(result.loc[result["opportunity_id"] == "O1", "is_stalled"].iloc[0]) is False
    assert bool(result.loc[result["opportunity_id"] == "O2", "is_stalled"].iloc[0]) is True