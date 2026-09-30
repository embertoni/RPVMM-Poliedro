# Auditoria semântica e preparação da base — versão 1

## 1. Decisões interpretativas adotadas

- **Unidade de análise:** `OpportunityId` representa a negociação observável; a escola é vinculada por `AccountId`. Uma conta pode ter várias oportunidades e isso não é tratado como duplicidade.

- **Evento do funil:** cada linha de `base-funil-2026` é tratada como um registro de estado/movimentação observado na data `Data`. Essa é uma hipótese operacional baseada na presença de `NewValue`, `Data` e `Status Atual`; deve ser confirmada com o responsável pelo CRM antes da produção.

- **Ordem temporal:** a jornada é ordenada por `Data`, depois `CreatedDate` e `Id` para desempate.

- **Desfecho:** o último `NewValue` da jornada define `won` quando é `Contrato assinado`, `lost` quando é `Oportunidade perdida` e `open` nos demais casos. A base de perdas por conta não substitui essa regra, pois não contém `OpportunityId`.

- **Estado absorvente:** assinatura e perda são finais para a modelagem, mas oportunidades com eventos posteriores a esses estados são sinalizadas para investigação de reabertura ou redundância de log.

- **Tempo:** `first_event_date` e `last_event_date` medem o intervalo observado no log. Ainda não são declarados como início/encerramento contratual sem validação do significado das datas.

- **Junções:** a base de escolas é deduplicada por conta somente para permitir uma base analítica; a duplicidade original é reportada. Especialistas, campanhas e perdas são agregados e mantêm sufixo/proveniência auxiliar.


## 2. Resultado dos checks

| check                                          |   value | interpretation                                                                           | severity    |
|:-----------------------------------------------|--------:|:-----------------------------------------------------------------------------------------|:------------|
| linhas_funil                                   |    5900 | Eventos observados na base-funil-2026                                                    | informativo |
| oportunidades                                  |    1610 | OpportunityId distintos com pelo menos um evento                                         | informativo |
| duplicatas_event_id                            |       0 | Mesmo Id de evento repetido                                                              | ok          |
| duplicatas_oportunidade_data_etapa             |       0 | Possíveis eventos repetidos na mesma oportunidade/data/etapa                             | ok          |
| datas_evento_nulas                             |       0 | Impossibilitam ordenar ou calcular duração                                               | ok          |
| datas_fora_ordem_original                      |       0 | Após ordenação, deve ser zero; a ordenação adotada é event_date/created_at/event_id      | informativo |
| estados_sem_sequencia_oficial                  |       0 | Eventos sem correspondência na planilha de sequência                                     | ok          |
| oportunidades_ganhas                           |      56 | Último estado Contrato assinado                                                          | informativo |
| oportunidades_perdidas                         |     897 | Último estado Oportunidade perdida                                                       | informativo |
| oportunidades_abertas                          |     657 | Último estado não absorvente                                                             | informativo |
| oportunidades_multimarcas                      |       0 | OpportunityId com mais de uma marca                                                      | informativo |
| contas_multioportunidades                      |     190 | Contas associadas a várias oportunidades; esperado e não é duplicidade por si só         | informativo |
| contas_multimarcas                             |     183 | Contas negociadas em mais de uma marca                                                   | informativo |
| transicoes_reversao                            |      83 | Retornos a etapas anteriores                                                             | informativo |
| transicoes_salto                               |    1065 | Mudanças que pulam etapas                                                                | informativo |
| mesma_etapa                                    |       0 | Registros consecutivos na mesma etapa                                                    | informativo |
| status_eventos                                 |       3 | Valores distintos de Status Atual                                                        | informativo |
| ultimo_estado_absorvente_com_status_negociacao |      56 | Inconsistência potencial entre estado final e status                                     | atenção     |
| absorvente_com_eventos_posteriores             |      11 | Oportunidades com evento após estado absorvente; investigar reabertura ou log redundante | atenção     |

## 3. Cobertura das junções

| table                     | key            |   opportunities_covered |   opportunities_total |   coverage | key_unique   |
|:--------------------------|:---------------|------------------------:|----------------------:|-----------:|:-------------|
| base-escolas              | account_id     |                    1329 |                  1610 |   0.739566 | False        |
| base-atuação-especialista | opportunity_id |                    1608 |                  1610 |   0.998758 | False        |
| base-campanhas-realizadas | account_id     |                     504 |                  1610 |   0.313043 | False        |
| base-perdas               | account_id     |                    1606 |                  1610 |   0.997516 | False        |

## 4. Regras para a etapa 2

A base para a etapa 2 está pronta em `base_eventos.csv` e `base_oportunidades.csv`. O modelo deve usar `base_oportunidades.csv` para propensão e priorização, e `base_eventos.csv` para transições e tempos. As colunas `loss_date_aux` e `loss_reasons_aux` são auxiliares em nível de conta e não devem entrar como preditores de oportunidades abertas sem uma regra temporal e uma chave de oportunidade confirmada.

Antes da modelagem de produção, devem ser revisados os registros em `possible_reopenings.csv`, `opportunities_multibrand.csv` e as transições classificadas como `forward_jump`, `backward_jump` ou `unmapped_transition`.


## 5. Artefatos

Os CSVs desta pasta constituem a saída reproduzível da auditoria. A interpretação adotada é suficiente para prosseguir tecnicamente para a etapa 2, mas as hipóteses sobre o significado de `Data` e sobre os registros pós-absorção permanecem limitações documentadas.
