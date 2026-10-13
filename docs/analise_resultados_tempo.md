# Análise dos resultados dos testes de tempo por etapa

### 1. Novas capacidades

Foram adicionados:

- `pipeline/config.py`: configuração centralizada, incluindo data de corte explícita, etapas terminais e limite mínimo de observações;
- `pipeline/tempo_etapa.py`: módulo reutilizável para reconstruir intervalos de permanência e identificar estagnação;
- `scripts/run_tempo_etapa.py`: execução por linha de comando com entrada, saída, corte e suporte mínimo configuráveis;
- `tests/test_tempo_etapa.py`: oito testes unitários cobrindo corte, censura, saltos, repetição de etapa, terminais, resumos e estagnação;
- `modelo_previsibilidade_v2.ipynb`: notebook integrado com auditoria, reconstrução da jornada, tempo por etapa, Markov, propensão e camadas exploratórias de priorização;
- `requirements.txt`: dependências explícitas para execução e testes;
- `resultados_oficiais/`: tabelas, previsões e gráficos HTML gerados a partir da execução da análise.

### 2. Reorganização dos arquivos existentes

Os artefatos que estavam na raiz em `main` foram movidos para `parcial1/`, incluindo `suposicoes/`, `versao1_pipeline/`, `propostas_iniciais/` e resultados da primeira versão.

A alteração é principalmente estrutural, mas impacta a reprodutibilidade: o script novo mantém como default `suposicoes/base_eventos.csv`, enquanto a base foi movida para `parcial1/suposicoes/base_eventos.csv`. Portanto, o comando sem `--events` falha na branch analisada.


### 3. Processo implementado

#### 3.1 Entrada e ordenação

A execução utiliza a base padronizada de eventos. Para cada oportunidade, os eventos são ordenados por `opportunity_id`, `event_date`, `created_at` (quando presente) e `event_id`.

A função `validate_cutoff` rejeita eventos posteriores à data de corte. Isso impede que a análise use informação futura de forma silenciosa.

#### 3.2 Construção da permanência

Para dois eventos consecutivos A e B da mesma oportunidade:

```text
permanência na etapa de A = data(B) - data(A)
```

As regras observadas no código são:

- o intervalo pertence à etapa de origem, não à etapa de destino;
- eventos consecutivos na mesma etapa são consolidados;
- etapas intermediárias de um salto não recebem duração artificial;
- o intervalo final de uma oportunidade aberta vai até `2026-08-14` e é marcado como censurado;
- estados terminais (`Contrato assinado` e `Oportunidade perdida`) não geram permanência posterior;
- cada intervalo preserva indicadores de censura e salto.

A estagnação é definida como `dias_na_etapa > Q3 histórico da etapa`. A regra só é aplicada a intervalos censurados e a etapas com pelo menos 10 observações.

### 3.3 Artefatos produzidos

O script produz `intervalos_por_etapa.csv`, `tempo_por_etapa.csv`, `tempo_por_etapa_marca.csv`, `estagnacao_por_oportunidade.csv` e dois gráficos HTML. O notebook v2 também preserva os resultados das camadas anteriores: baseline de Markov, previsões de oportunidades abertas, enriquecimento exploratório e validações de propensão.

## 4. Validação técnica realizada

A suíte foi executada com:

```bash
PYTHONPATH=. pytest -q
```

Resultado: **8 testes aprovados** (`8 passed in 1.19s`).

Também foi feita uma reexecução independente:

```bash
python3 scripts/run_tempo_etapa.py
  --events parcial1/suposicoes/base_eventos.csv
  --cutoff 2026-08-14
  --output /tmp/rerun-results
```

Resultado da execução:

- 5.900 eventos lidos;
- 4.936 intervalos gerados;
- 12 etapas resumidas;
- 657 oportunidades abertas avaliadas.

Os hashes de `tempo_por_etapa.csv` e `intervalos_por_etapa.csv` gerados na reexecução coincidiram exatamente com os arquivos versionados em `resultados_oficiais/`. Isso confirma a consistência do cálculo e dos artefatos principais para esse corte e essa entrada.


## 5. Resultados quantitativos

### 5.1 Cobertura da base

| Indicador | Resultado |
|---|---:|
| Eventos | 5.900 |
| Oportunidades | 1.610 |
| Período dos eventos | 2025-09-19 a 2026-08-14 |
| Marcas identificadas | Poliedro: 2.179 eventos; Polígono: 2.157; Conviver: 1.546 |
| Eventos sem marca | 18 |
| Intervalos calculados | 4.936 |
| Intervalos censurados | 657 (13,31%) |
| Intervalos com salto | 1.054 (21,35%) |
| Intervalos com duração zero | 1.625 (32,92%) |

As durações zero não são necessariamente um erro, mas a proporção é alta o suficiente para justificar uma análise de granularidade de timestamp e das regras de registro do CRM antes de interpretar médias de etapas curtas.

### 5.2 Tempo por etapa

| Etapa | Intervalos | Mediana (dias) | Q1–Q3 (dias) | Censura | Saltos | Suporte |
|---|---:|---:|---:|---:|---:|---|
| Solicitação de material | 1.604 | 34,0 | 10,0–61,0 | 11,22% | 24,63% | adequado |
| Validação pedagógica | 959 | 22,0 | 0,0–52,0 | 22,00% | 28,47% | adequado |
| Proposta personalizada | 317 | 17,0 | 1,0–43,0 | 23,34% | 27,44% | adequado |
| Proposta tabela | 477 | 11,0 | 0,0–36,0 | 18,45% | 14,88% | adequado |
| Negociação e ajuste financeiro | 156 | 8,0 | 0,0–45,25 | 33,97% | 13,46% | adequado |
| Enviado para a assinatura | 71 | 6,0 | 0,0–20,5 | 15,49% | 4,23% | adequado |
| Análise de operações comerciais | 80 | 0,0 | 0,0–2,25 | 1,25% | 98,75% | muitos saltos |
| Análise do Jurídico | 77 | 0,0 | 0,0–0,0 | 5,19% | 1,30% | duração concentrada em zero |
| Análise do Financeiro | 72 | 0,0 | 0,0–0,0 | 0,00% | 100,00% | todos são saltos |
| Material entregue | 1.040 | 0,0 | 0,0–9,0 | 3,08% | 5,00% | adequado |
| Documentação enviada | 82 | 0,0 | 0,0–1,75 | 2,44% | 0,00% | adequado |
| Contrato Ativo | 1 | 149,0 | 149,0–149,0 | 100,00% | 0,00% | **baixo** |

A leitura mais robusta está nas etapas com suporte alto e distribuição não degenerada. `Solicitação de material` é a etapa com maior mediana (34 dias), seguida de `Validação pedagógica` (22 dias) e `Proposta personalizada` (17 dias). Isso sugere concentração do tempo observado no início e no meio do funil, mas não permite concluir causalidade ou definir SLA sem controlar censura, saltos e composição por marca.

As etapas com mediana zero não devem ser interpretadas como “nenhum trabalho realizado”: o resultado pode refletir mudanças no mesmo dia, eventos em lote ou saltos no histórico.

### 5.3 Estagnação das oportunidades abertas

Foram avaliadas 657 oportunidades abertas. Destas, 320 (48,71%) ultrapassaram o terceiro quartil histórico da própria etapa e foram marcadas como estagnadas.

| Etapa atual | Oportunidades abertas | Estagnadas | Taxa |
|---|---:|---:|---:|
| Validação pedagógica | 211 | 118 | 55,92% |
| Solicitação de material | 180 | 64 | 35,56% |
| Proposta tabela | 88 | 44 | 50,00% |
| Proposta personalizada | 74 | 36 | 48,65% |
| Negociação e ajuste financeiro | 53 | 27 | 50,94% |
| Material entregue | 32 | 22 | 68,75% |

O resultado é útil para priorização operacional, mas deve ser tratado como **sinal de aging**, não como previsão de perda. A regra compara cada oportunidade com o histórico agregado da etapa; ela ainda não controla marca, perfil, valor, sazonalidade ou número de interações. Como o intervalo aberto é censurado na data de corte, a taxa depende diretamente do snapshot escolhido.

### 5.4 Relação com os modelos existentes

Os artefatos de validação de propensão têm 245 observações de teste e 12 positivos. O Brier score calculado sobre os CSVs versionados foi:

| Modelo | Média prevista | Brier score |
|---|---:|---:|
| Estrutural | 0,2392 | 0,1272 |
| Operacional | 0,0554 | 0,0027 |

A diferença é expressiva, mas não prova superioridade definitiva: há apenas 12 positivos, o corte temporal precisa ser repetido e o próprio projeto alerta para possível separação forte por estágio, composição amostral ou vazamento. O componente de tempo por etapa, nesta branch, é principalmente descritivo e de priorização; ainda não é um modelo de sobrevivência ou risco competitivo validado.

## 6. Limitações e riscos interpretativos

1. **Censura:** oportunidades abertas são interrompidas no corte; o tempo observado é limite inferior para o tempo total.
2. **Saltos:** 21,35% dos intervalos têm salto. Não é válido distribuir automaticamente esse tempo entre etapas intermediárias.
3. **Granularidade:** 32,92% dos intervalos têm zero dias. Isso pode refletir eventos no mesmo dia, ausência de hora ou atualização em lote.
4. **Dependência do corte:** alterar `2026-08-14` altera permanências abertas e estagnação.
5. **Baixa amostra:** `Contrato Ativo` tem uma observação e deve ser excluído de decisões ou referências.
6. **Viés de seleção:** o resumo mistura marcas e perfis; ainda não há validação de estabilidade ou intervalos de confiança.
7. **Desfecho:** a camada não estima diretamente probabilidade de assinatura nem prazo até assinatura/perda.
8. **Reprodutibilidade operacional:** o caminho default da entrada está incompatível com a reorganização para `parcial1/`.
9. **Duplicação:** há duas árvores de saída, o que pode gerar consumo de arquivos de execuções diferentes.

## 7. Recomendações

### Prioridade alta

1. Reexecutar o pipeline em múltiplos cortes e comparar medianas, Q3, censura e estagnação.

### Prioridade média

5. Reportar contagens e intervalos de confiança por etapa e marca.
6. Investigar eventos no mesmo dia e a semântica de `event_date` antes de transformar duração em SLA.
7. Separar saltos reais de atualizações agregadas do CRM.
8. Criar uma validação que impeça divergência entre CSVs versionados e resultados produzidos pelo script.

### Evolução do modelo

9. Expandir oportunidades em intervalos temporais e modelar assinatura e perda como riscos competitivos, se a qualidade temporal for confirmada.
10. Comparar Markov, propensão estrutural, propensão operacional e componente temporal em cortes futuros, avaliando discriminação, calibração, erro temporal, estabilidade e utilidade comercial.
11. Usar estagnação como variável explicativa ou regra de fila apenas após validar que acrescenta informação além da etapa atual e do tempo desde o último evento.

## 8. Conclusão

Os novos testes transformam a camada temporal, antes exploratória, em um módulo reutilizável com regras explícitas, corte temporal e saídas reproduzíveis. O cálculo identifica a permanência da etapa de origem, preserva censura e não inventa duração para etapas puladas.

Os resultados apontam para gargalos em `Solicitação de material` e `Validação pedagógica`, além de 320 oportunidades abertas acima do Q3 histórico. Esses achados são adequados para investigação e priorização inicial, mas ainda não sustentam, isoladamente, metas de prazo, probabilidade de conversão ou decisões comerciais automatizadas.

Antes da integração, os pontos mais importantes são corrigir o caminho default da entrada, eliminar caches versionados, escolher uma saída canônica e repetir a validação em diferentes cortes temporais. Com esses ajustes, a branch fornece uma base sólida para evoluir de uma análise descritiva de aging para um modelo temporal validado.
