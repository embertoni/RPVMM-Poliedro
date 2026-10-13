# Dicionário da base analítica — etapa 2

## Base de eventos: `base_eventos.csv`

Cada linha representa um registro observado na base `base-funil-2026`, ordenado dentro da oportunidade por `event_date`, `created_at` e `event_id`.

| Campo | Origem ou construção | Uso previsto |
|---|---|---|
| `event_id` | Id do registro histórico | Rastreabilidade do evento |
| `opportunity_id` | OpportunityId do CRM | Chave da oportunidade |
| `account_id` | AccountId da oportunidade | Ligação com a escola/conta |
| `brand` | Tipo de sistema da oportunidade | Comparação entre marcas |
| `created_at` | CreatedDate | Ordenação auxiliar e auditoria |
| `event_date` | Data do registro | Ordenação e cálculo de intervalos |
| `stage` | NewValue | Estado observado do funil |
| `event_status` | Status Atual | Contexto do registro; não define sozinho o desfecho |
| `potential_revenue` | Receita potencial do funil | Valor econômico |
| `stage_order` | Sequência oficial das etapas | Classificação de avanços e recuos |
| `phase` | Fase oficial agregada | Análises por fase |
| `event_seq` | Ordem do evento dentro da oportunidade | Reconstrução da jornada |
| `prev_stage` | Etapa anterior após ordenação | Transição |
| `prev_event_date` | Data do evento anterior | Intervalo temporal |
| `days_since_previous_event` | Diferença entre datas | Velocidade e estagnação |
| `transition_type` | Construção baseada na ordem oficial | Avanço, recuo, salto, repetição ou evento inicial |
| `is_absorbing` | Etapa é assinatura ou perda | Estado final para o modelo |
| `available_after_event` | Indicador técnico | Controle de disponibilidade temporal |

## Base de oportunidades: `base_oportunidades.csv`

Cada linha representa uma oportunidade distinta. O desfecho é determinado pelo último `stage` observado e não pela base de perdas em nível de conta.

| Campo | Origem ou construção | Uso previsto |
|---|---|---|
| `opportunity_id` | Chave da oportunidade | Unidade de análise |
| `account_id` | Conta associada | Ligação com perfil |
| `brand` | Marca da oportunidade | Segmentação |
| `potential_revenue` | Máximo observado no histórico | Receita potencial, sujeito à validação |
| `first_event_date` | Primeiro evento observado | Início observado no log |
| `last_event_date` | Último evento observado | Última observação no log |
| `created_at` | Menor CreatedDate observado | Auditoria temporal |
| `event_count` | Número de eventos | Intensidade do registro |
| `unique_stage_count` | Número de etapas distintas | Complexidade da jornada |
| `current_stage` | Último estágio observado | Estado atual |
| `outcome` | `won`, `lost` ou `open` | Rótulo para propensão e censura |
| `duration_days` | Última data menos primeira data | Duração observada, não necessariamente ciclo contratual |
| `advance_count` | Transições de avanço ou salto à frente | Evolução |
| `reversal_count` | Recuos ou saltos para trás | Instabilidade |
| `same_stage_count` | Registros consecutivos na mesma etapa | Repetição de estado |
| `unmapped_transition_count` | Transições sem ordem oficial | Qualidade da jornada |
| `days_since_previous_event_last` | Intervalo até o último evento | Recência da movimentação |
| Campos de `base-escolas` | Perfil da conta, quando há correspondência | Fit estrutural |
| `specialist_record_count` e `specialist_actions` | Agregação por oportunidade | Participação de especialista; associação, não causalidade |
| `campaign_record_count` e `campaign_names` | Agregação por conta | Origem/relacionamento, com cobertura parcial |
| `loss_record_count`, `loss_date_aux`, `loss_reasons_aux` | Agregação por conta | Contexto auxiliar; não usar como alvo individual sem chave de oportunidade |
| `target_won` | `won=1`, `lost=0`, aberto nulo | Treino supervisionado somente em encerradas |

## Regras de uso

1. Para oportunidades abertas, não utilizar informações produzidas depois da data de corte.
2. Não utilizar `loss_date_aux` ou `loss_reasons_aux` como preditores individuais sem confirmar a ligação entre conta e oportunidade.
3. Não tratar uma conta com várias oportunidades como duplicidade automaticamente.
4. Investigar oportunidades com eventos posteriores a assinatura ou perda antes de tratá-las como estados absorventes definitivos.
5. Avaliar `forward_jump`, `backward_jump` e `unmapped_transition` antes de estimar transições condicionadas.
6. Manter a versão do dataset, o corte temporal e as regras de tratamento junto de cada execução.
