# Análise de tempo por etapa e estagnação

## Objetivo

Medir a permanência observada em cada etapa do funil e identificar oportunidades abertas cujo tempo desde o último evento excede o comportamento histórico de referência da etapa.

## Entrada

- Arquivo: `suposicoes/base_eventos.csv` durante a etapa exploratória.
- Arquivo oficial futuro: base de eventos produzida pelo pipeline de auditoria semântica.
- Chave de ordenação: `opportunity_id`, `event_date`, `created_at`, `event_id`.
- Data de corte: informada por `--cutoff`; não usar a data atual automaticamente.

## Regra de permanência

Para dois eventos consecutivos A e B da mesma oportunidade:

```text
permanencia_em_A = data(B) - data(A)