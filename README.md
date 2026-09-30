# RPVMM-Poliedro

Projeto da UC **Resolução de Problemas Via Modelagem Matemática** (docente: Horácio Hideki) dedicado à construção de uma metodologia de previsibilidade de assinatura de contratos no funil comercial das marcas analisadas pelo Poliedro.

> **Status atual:** exploração técnica concluída e primeira base analítica produzida sob hipóteses operacionais. A próxima etapa prioritária é confirmar a semântica da jornada e das datas com a empresa antes de tratar as previsões como resultado oficial.

---

## 1. Visão geral

O projeto busca transformar o histórico de movimentações do CRM em uma metodologia que ajude a responder:

- quais oportunidades têm maior probabilidade de chegar à assinatura;

- como o comportamento do funil varia por marca, região, consultor, rede, porte, cluster e outros segmentos;

- quais oportunidades estão avançando, recuando ou permanecendo sem movimentação;

- qual é o tempo observado até os desfechos, quando as datas forem semanticamente confiáveis;

- como combinar probabilidade, receita potencial, prazo e risco em uma priorização comercial interpretável.

A solução final não deve ser apenas uma taxa histórica ou uma classificação isolada. O objetivo é produzir uma visão integrada de **conversão, velocidade, risco e decisão comercial**, usando somente informações disponíveis no momento em que cada previsão seria utilizada.

### Escopo declarado

A documentação do projeto prevê a análise das marcas **Poliedro, Polígono, Conviver e Integrar**. No snapshot de dados atualmente versionado, os resultados observados apresentam registros para **Poliedro, Polígono e Conviver**; a presença e a representação separada de Integrar ainda devem ser confirmadas na fonte oficial.

---

## 2. Ideia geral e abordagem escolhida

A abordagem foi organizada em camadas complementares, com uma ordem deliberadamente conservadora:

1. **Auditar e compreender os dados** antes de modelar.

1. **Reconstruir a jornada** de cada oportunidade a partir dos eventos do funil.

1. Usar uma **cadeia de Markov como baseline**, por ser simples, explicável e útil para medir probabilidades de absorção por etapa.

1. Comparar o baseline com modelos de **propensão individual**, separando:
  - um modelo **estrutural**, baseado no perfil da escola e no contexto da oportunidade;
  - um modelo **operacional**, que também usa a etapa atual e o comportamento observado da negociação.

1. Implementar uma camada de **tempo até o evento** somente depois de validar o significado das datas.

1. Transformar as previsões validadas em uma **priorização comercial**, combinando probabilidade, receita, prazo, risco e confiança.

Essa separação evita que uma interpretação ainda incerta do CRM seja confundida com uma conclusão estatística. Também permite comparar modelos mais sofisticados contra um ponto de referência transparente.

### Unidade de análise adotada provisoriamente

A hipótese operacional atual é que:

- `OpportunityId` representa uma negociação observável;

- `AccountId` representa a escola ou conta associada;

- uma conta pode possuir várias oportunidades, o que não é tratado automaticamente como duplicidade;

- cada linha da base histórica representa um estado ou movimentação observada na oportunidade, registrada na data `Data`.

Essas definições foram usadas para construir os artefatos em `suposicoes/`, mas ainda dependem de confirmação do responsável pelo CRM.

---

## 3. Dados de entrada

O arquivo principal é `dados/Proposta-de-Projeto-Base-Funil.xlsx`. Ele contém as seguintes abas:

| Aba | Papel no projeto |
| --- | --- |
| `base-funil-2026` | Histórico de movimentações do funil; origem dos eventos, etapas, status, datas e receita potencial. |
| `sequência-etapas-funil` | Sequência oficial das etapas e agrupamento em fases. |
| `base-escolas` | Perfil cadastral, geográfico, institucional e comercial das escolas. |
| `base-histórico-etapas` | Tempos médios históricos por fase; material de referência descritiva. |
| `base-atuação-especialista` | Registros de participação ou atuação de especialistas. |
| `base-campanhas-realizadas` | Campanhas associadas às contas. |
| `base-perdas` | Datas e motivos de perda em nível de conta; a chave não é `OpportunityId`, portanto seu uso individual exige cautela. |

### Dimensões do snapshot analisado

- `base-funil-2026`: **5.900 eventos**;

- `OpportunityId` distintos: **1.610 oportunidades**;

- sequência oficial: **14 etapas**;

- base de escolas: **34.642 linhas**, com duplicidade de contas;

- atuação de especialista: **1.623 registros**;

- campanhas: **1.077 registros**;

- perdas: **1.605 registros**, incluindo duplicidades de linha.

Os notebooks renomeiam os campos de origem para nomes analíticos mais consistentes, como `opportunity_id`, `account_id`, `event_date`, `stage`, `brand` e `potential_revenue`.

---

## 4. Estrutura do repositório

```
.
├── dados/
│   └── Proposta-de-Projeto-Base-Funil.xlsx
├── propostas_iniciais/
│   ├── Poliedro.ipynb
│   ├── Cadeias_de_Markov.ipynb
│   └── resultados/
├── suposicoes/
│   ├── relatorio_auditoria_semantica.md
│   ├── base_eventos.csv
│   ├── base_oportunidades.csv
│   ├── cardinality_summary.csv
│   ├── checks.csv
│   ├── join_coverage.csv
│   ├── opportunities_multibrand.csv
│   ├── possible_reopenings.csv
│   ├── sequence_official.csv
│   └── transition_counts.csv
├── versao1_pipeline/
│   ├── modelo_previsibilidade_v1.ipynb
│   ├── dicionario_base_analitica.md
│   ├── objetivo_final_projeto_v1.md
│   └── resultados_v1/
└── README.md
```

### Papel de cada diretório

#### `propostas_iniciais/`

Contém a primeira exploração do Excel e a implementação inicial da cadeia de Markov. Essa etapa ajudou a entender as colunas, padronizar as planilhas, visualizar a distribuição geográfica e gerar as primeiras matrizes de transição e previsões por etapa.

#### `suposicoes/`

Contém a saída de uma auditoria semântica e temporal construída sob uma **interpretação provisória** do dataset. Esses arquivos não são uma resposta oficial da empresa; servem como base de testes das etapas seguintes enquanto a confirmação não está disponível.

O diretório inclui duas tabelas analíticas centrais:

- `base_eventos.csv`: uma linha por movimentação observada, com etapa anterior, intervalo desde o evento anterior e tipo de transição;

- `base_oportunidades.csv`: uma linha por oportunidade, com características agregadas da jornada, desfecho, duração observada e atributos auxiliares.

#### `versao1_pipeline/`

Contém o notebook que integra auditoria estrutural, reconstrução da jornada, baseline Markov, enriquecimento, propensão exploratória, estatísticas temporais e uma demonstração de priorização.

O arquivo `dicionario_base_analitica.md` documenta as colunas construídas e as regras de uso. O arquivo `objetivo_final_projeto_v1.md` descreve o resultado esperado e os critérios de completude.

---

## 5. O que já foi feito

### 5.1 Exploração inicial e padronização

O notebook `propostas_iniciais/Poliedro.ipynb`:

- carrega as abas do Excel;

- renomeia colunas para um padrão analítico;

- converte datas e valores numéricos;

- inspeciona as tabelas auxiliares;

- realiza explorações geográficas e descritivas;

- registra possibilidades de modelos, incluindo regressão logística, Random Forest, modelos de tempo e Markov.

O notebook `propostas_iniciais/Cadeias_de_Markov.ipynb` concentra a primeira implementação da cadeia de Markov e seus resultados em `propostas_iniciais/resultados/`.

### 5.2 Auditoria semântica hipotética

A auditoria versionada em `suposicoes/relatorio_auditoria_semantica.md` adotou as seguintes regras provisórias:

- ordenar eventos por `Data`, depois `CreatedDate` e `Id`;

- definir o desfecho pelo último `NewValue` observado;

- considerar `Contrato assinado` como `won`;

- considerar `Oportunidade perdida` como `lost`;

- considerar os demais estados como `open`;

- tratar assinatura e perda como estados absorventes para o baseline;

- manter registros posteriores a estados absorventes como casos a investigar, e não descartá-los silenciosamente;

- usar a base de perdas apenas como contexto auxiliar, pois ela está no nível de conta.

### 5.3 Resultado da auditoria provisória

| Indicador | Resultado | Leitura atual |
| --- | --- | --- |
| Eventos observados | 5.900 | Linhas da base histórica do funil. |
| Oportunidades | 1.610 | `OpportunityId` distintos. |
| Ganhas | 56 | Último estado igual a `Contrato assinado`. |
| Perdidas | 897 | Último estado igual a `Oportunidade perdida`. |
| Abertas | 657 | Último estado não absorvente. |
| Duplicatas de evento por `Id` | 0 | Nenhuma encontrada. |
| Duplicatas por oportunidade/data/etapa | 0 | Nenhuma encontrada sob essa regra. |
| Oportunidades com múltiplas marcas | 0 | Nenhuma encontrada no snapshot. |
| Contas com múltiplas oportunidades | 190 | Comportamento esperado, não duplicidade automática. |
| Recuos | 83 | Inclui transições classificadas como reversão/salto para trás. |
| Saltos entre etapas | 1.065 | Deve ser validado antes de assumir que toda transição é literal. |
| Eventos posteriores a estado absorvente | 11 oportunidades | Possíveis reaberturas ou redundâncias do log. |

A distribuição de desfechos é fortemente desbalanceada: poucas oportunidades são classificadas como ganhas em comparação com as perdidas. Portanto, métricas, calibração e incerteza são tão importantes quanto a capacidade de ordenar oportunidades.

### 5.4 Cobertura das junções

| Fonte | Chave | Cobertura das 1.610 oportunidades | Observação |
| --- | --- | --- | --- |
| `base-escolas` | `account_id` | 73,96% | A chave não é única na fonte; foi deduplicada provisoriamente para enriquecer a base. |
| `base-atuação-especialista` | `opportunity_id` | 99,88% | Agregada por oportunidade. |
| `base-campanhas-realizadas` | `account_id` | 31,30% | Cobertura parcial; agregada por conta. |
| `base-perdas` | `account_id` | 99,75% | Não deve ser usada como rótulo individual sem chave de oportunidade e regra temporal. |

### 5.5 Base analítica construída

#### Base de eventos

`suposicoes/base_eventos.csv` possui 5.900 linhas e inclui:

- identificação da oportunidade, conta e evento;

- data do evento e data de criação;

- etapa e fase;

- status registrado;

- receita potencial;

- ordem oficial da etapa;

- evento anterior e intervalo em dias;

- tipo de transição (`initial`, `advance`, `forward_jump`, `reversal` ou `backward_jump`);

- indicador de estado absorvente;

- indicador técnico de disponibilidade após o evento.

#### Base de oportunidades

`suposicoes/base_oportunidades.csv` possui 1.610 linhas e inclui:

- identificação, conta e marca;

- receita potencial;

- primeiro e último evento observado;

- etapa atual e desfecho;

- quantidade de eventos e etapas distintas;

- duração observada;

- avanços, recuos, repetições e transições não mapeadas;

- intervalo desde o último evento;

- atributos da escola, quando disponíveis;

- agregações de especialistas, campanhas e perdas;

- `target_won`, preenchido apenas para oportunidades encerradas.

### 5.6 Cadeia de Markov como baseline

A primeira versão do pipeline estima a cadeia usando oportunidades finalizadas, com as etapas intermediárias como estados transitórios e assinatura/perda como estados absorventes. A matriz fundamental permite estimar:

- probabilidade final de assinatura por etapa;

- probabilidade final de perda por etapa;

- número esperado de transições até absorção;

- uma referência de probabilidade para oportunidades abertas.

Alguns resultados do baseline produzido em `versao1_pipeline/resultados_v1/`:

- oportunidades finalizadas utilizadas: **953**;

- oportunidades abertas: **657**;

- pares de transição observados: **2.838**;

- probabilidade estimada de assinatura a partir de `Solicitação de material`: **5,46%**;

- probabilidade estimada de assinatura a partir de `Validação pedagógica`: **10,14%**;

- probabilidade estimada de assinatura a partir de `Negociação e ajuste financeiro`: **62,30%**;

- probabilidade estimada de assinatura a partir de `Enviado para a assinatura`: **94,92%**.

Esses números são **referências empíricas do snapshot**, não previsões oficiais. O baseline é homogêneo: oportunidades na mesma etapa recebem a mesma probabilidade, sem incorporar perfil individual, tempo na etapa ou comportamento recente.

### 5.7 Propensão individual exploratória

O notebook `versao1_pipeline/modelo_previsibilidade_v1.ipynb` também testa uma regressão logística regularizada com:

- imputação de valores ausentes;

- padronização de variáveis numéricas;

- codificação one-hot de categóricas;

- divisão temporal, usando oportunidades mais antigas para treino e posteriores para teste.

Foram comparados:

- **Modelo estrutural:** perfil da escola, marca, região, porte, cluster, score, receita e características semelhantes;

- **Modelo operacional:** variáveis estruturais mais etapa atual, duração observada, quantidade de eventos, etapas distintas, transições e indicadores de atividade.

No output atualmente versionado, o corte temporal foi `2026-04-17`, com 708 observações no treino e 245 no teste:

| Modelo | AUC | Average Precision | Brier |
| --- | --- | --- | --- |
| Estrutural | 0,8380 | 0,3011 | 0,1277 |
| Operacional | 1,0000 | 1,0000 | 0,0027 |

A performance perfeita do modelo operacional deve ser tratada como **sinal de investigação**, não como validação definitiva. Ela pode refletir separação muito forte por estágio, composição temporal da amostra, baixa quantidade de ganhos ou alguma variável muito próxima do desfecho. É obrigatório repetir a validação com vários cortes temporais, revisar vazamento e avaliar calibração antes de qualquer uso comercial.

### 5.8 Camada temporal e priorização

A versão atual calcula apenas duração observada entre o primeiro e o último evento e apresenta estatísticas exploratórias. Ela ainda não implementa um modelo temporal final.

A priorização também é uma demonstração: o notebook calcula valor esperado simples como `receita potencial × probabilidade`, mas ainda não define horizonte, penalização de prazo, confiança, capacidade dos consultores ou faixas comerciais. Portanto, o resultado não deve ser usado como regra oficial.

---

## 6. Limitações e cuidados metodológicos

1. **Semântica não confirmada:** ainda é necessário confirmar se cada linha é uma movimentação válida e qual é o significado exato de `Data`, `CreatedDate`, `NewValue` e `Status Atual`.

1. **Datas:** `first_event_date` e `last_event_date` são intervalos observados no log; não são automaticamente a data real de abertura, assinatura, perda ou censura.

1. **Censura:** oportunidades abertas precisam de uma data de corte formal para que o componente temporal seja válido.

1. **Reaberturas:** 11 oportunidades possuem eventos posteriores a estados tratados como absorventes e devem ser revisadas.

1. **Saltos e recuos:** saltos entre etapas e retornos podem ser reais ou consequência da forma como o CRM registra alterações.

1. **Chaves auxiliares:** escola, campanhas e perdas usam `account_id`, enquanto a unidade analítica é a oportunidade; isso limita a interpretação individual.

1. **Cobertura:** a base de escolas tem cobertura parcial e duplicidades; a deduplicação atual é uma decisão técnica provisória.

1. **Desbalanceamento:** existem 56 ganhos, 897 perdas e 657 oportunidades abertas. A avaliação não pode depender apenas de acurácia ou AUC.

1. **Vazamento temporal:** campos como data/motivo de perda, assinatura futura e informações posteriores ao corte não podem entrar nos preditores.

1. **Associação não é causalidade:** visitas, campanhas, consultores e especialistas podem estar associados ao resultado sem provar que causaram conversão.

1. **Volume por segmento:** modelos por marca, região ou cluster só devem ser interpretados quando houver observações suficientes e estabilidade.

1. **Reprodutibilidade:** cada execução deve registrar versão do dataset, data de corte, regras de tratamento, features disponíveis e artefatos gerados.

---

## 7. Próximas etapas

A ordem abaixo segue o plano definido em `proximas_etapas.md`. As caixas devem ser atualizadas conforme o projeto avance.

### Etapa 1 — Auditoria semântica e temporal

- [ ] Confirmar se `OpportunityId` corresponde a uma única negociação.

- [ ] Confirmar se uma oportunidade pode ter mais de uma marca.

- [ ] Verificar oportunidades simultâneas da mesma escola e marca.

- [ ] Verificar se reaberturas reutilizam o mesmo identificador.

- [ ] Verificar mudanças de escola, conta, consultor ou marca ao longo da jornada.

- [ ] Documentar duplicidades reais e diferenciá-las de contas com múltiplas oportunidades.

- [ ] Confirmar se `CreatedDate` é a criação do registro ou da oportunidade.

- [ ] Confirmar se `Data` é a data efetiva da movimentação.

- [ ] Confirmar o evento que define assinatura.

- [ ] Confirmar o evento que define perda.

- [ ] Definir a data de corte das oportunidades abertas.

- [ ] Verificar eventos fora de ordem e registros posteriores a estados finais.

- [ ] Confirmar se a data de perda está no nível da conta ou da oportunidade.

- [ ] Gerar relatório de cardinalidade das chaves.

- [ ] Gerar relatório de duplicidades.

- [ ] Gerar relação de oportunidades com múltiplas marcas.

- [ ] Gerar relação de oportunidades reabertas.

- [ ] Gerar diagnóstico de eventos fora de ordem.

- [ ] Gerar distribuição dos intervalos entre eventos.

- [ ] Comparar estados finais com os status registrados.

- [ ] Medir a cobertura das junções com escolas, campanhas, especialistas e perdas.

**Critério para prosseguir:** documentar a unidade analítica válida, o tratamento de duplicidades e reaberturas, a regra para múltiplas oportunidades por escola e as definições temporais oficiais.

### Etapa 2 — Base analítica oficial

- [ ] Formalizar o dicionário de dados após a confirmação semântica.

- [ ] Construir a tabela de eventos oficial, com uma linha por movimentação válida.

- [ ] Construir a tabela de oportunidades oficial, com uma linha por oportunidade.

- [ ] Definir quais atributos são históricos, atuais ou disponíveis no momento da previsão.

- [ ] Versionar a base, o corte temporal e as regras de tratamento.

- [ ] Salvar tabela de oportunidades com desfecho.

- [ ] Salvar tabela de eventos com transições validadas.

### Etapa 3 — Jornada validada

- [ ] Confirmar a sequência oficial de etapas.

- [ ] Revisar transições de avanço, salto, recuo, repetição e não mapeadas.

- [ ] Definir o tratamento das oportunidades reabertas.

- [ ] Definir como `Contrato Ativo`, assinatura e perda participam do estado final.

- [ ] Validar a reconstrução da jornada em amostras com a empresa.

### Etapa 4 — Baselines

- [ ] Produzir taxas históricas de avanço, conversão e perda.

- [ ] Manter a cadeia de Markov global como baseline.

- [ ] Testar cadeia por marca somente com volume suficiente.

- [ ] Calcular probabilidades empíricas por etapa.

- [ ] Quantificar a incerteza das transições, considerando o número de observações.

- [ ] Comparar probabilidades previstas com frequências observadas.

### Etapa 5 — Propensão individual

- [ ] Definir formalmente a previsão desde a abertura e/ou a previsão a partir de uma data de corte.

- [ ] Treinar o modelo estrutural com variáveis disponíveis no início.

- [ ] Treinar o modelo operacional com etapa e comportamento disponíveis na data de corte.

- [ ] Repetir a validação em múltiplos cortes temporais.

- [ ] Avaliar AUC, Average Precision, Brier Score e calibração.

- [ ] Avaliar precisão e conversão no grupo prioritário.

- [ ] Verificar vazamento temporal e estabilidade dos coeficientes/previsões.

- [ ] Comparar todos os modelos na mesma amostra de teste.

### Etapa 6 — Tempo até o evento

- [ ] Confirmar que as datas permitem calcular permanência e encerramento.

- [ ] Definir assinatura, perda e oportunidade aberta censurada.

- [ ] Expandir oportunidades em períodos semanais ou mensais.

- [ ] Implementar modelo de tempo discreto com riscos competitivos, se viável.

- [ ] Estimar probabilidades de assinatura e perda em 30, 60 e 90 dias.

- [ ] Estimar prazo provável até assinatura.

- [ ] Se a granularidade não for confiável, manter apenas a análise descritiva e registrar a inviabilidade temporal.

### Etapa 7 — Priorização comercial

- [ ] Definir o horizonte de previsão `τ`.

- [ ] Definir como penalizar prazos longos.

- [ ] Incorporar confiança ou incerteza da previsão.

- [ ] Definir o peso da receita potencial.

- [ ] Definir tratamento de valores ausentes.

- [ ] Definir faixas de prioridade interpretáveis.

- [ ] Considerar capacidade operacional dos consultores.

- [ ] Relacionar cada faixa a uma ação comercial recomendada.

- [ ] Manter o índice como demonstração até sua validação e aprovação comercial.

Uma formulação inicial possível é:

```
VP_i = Receita_i × P(assinatura até τ) × Desconto_de_prazo_i(τ) × Confiança_i
```

Essa expressão é apenas um ponto de partida; os fatores e seus pesos ainda precisam ser definidos.

### Etapa 8 — Relatório comparativo e entrega

- [ ] Comparar Markov global, Markov por marca, propensão estrutural, propensão operacional e modelo temporal.

- [ ] Comparar desempenho estatístico.

- [ ] Comparar interpretabilidade.

- [ ] Comparar requisitos e cobertura de dados.

- [ ] Comparar estabilidade temporal e por segmento.

- [ ] Comparar utilidade comercial.

- [ ] Documentar limitações e segmentos sem volume suficiente.

- [ ] Produzir relatório final reproduzível.

- [ ] Definir rotina de atualização e monitoramento após a entrega.

---

## 8. Como reproduzir a análise atual

### Pré-requisitos

- Python com `pandas`, `numpy`, `scikit-learn`, `openpyxl` e Jupyter;

- arquivo Excel disponível em `dados/Proposta-de-Projeto-Base-Funil.xlsx`;

- execução a partir do diretório do notebook ou ajuste do caminho `DATASET`.

### Notebooks

1. Abrir `propostas_iniciais/Poliedro.ipynb` para a exploração inicial e a padronização das abas.

1. Abrir `propostas_iniciais/Cadeias_de_Markov.ipynb` para a implementação inicial da cadeia.

1. Abrir `versao1_pipeline/modelo_previsibilidade_v1.ipynb` para a versão integrada do pipeline.

O notebook da versão 1 exporta matrizes, probabilidades, oportunidades enriquecidas, previsões Markov e arquivos de validação da propensão. Os artefatos já versionados estão em `versao1_pipeline/resultados_v1/`.

> **Atenção ao diretório de saída:** o notebook define `OUTPUT_DIR = Path('resultados-v1')`, enquanto o repositório versiona `resultados_v1`. Ao executar novamente, verifique o diretório gerado e compare explicitamente os artefatos antes de substituir resultados versionados.

### Ordem recomendada de execução

1. Validar o arquivo de entrada e suas abas.

1. Executar a auditoria semântica/temporal.

1. Revisar as hipóteses e os relatórios produzidos.

1. Gerar ou atualizar as bases analíticas oficiais.

1. Executar os baselines.

1. Somente então treinar e validar propensões e modelos temporais.

1. Gerar a priorização apenas após a validação dos modelos.

---

## 9. Critérios para considerar o projeto completo

O projeto estará completo quando:

1. a unidade de análise e as chaves de junção estiverem documentadas e auditadas;

1. a jornada for reconstruída de forma reproduzível;

1. houver tratamento documentado para ausências, duplicidades, reaberturas e inconsistências;

1. a data de corte e as informações disponíveis no momento da previsão estiverem definidas;

1. o vazamento de informação tiver sido prevenido e verificado;

1. as marcas forem analisadas em conjunto e separadamente quando houver volume suficiente;

1. existir baseline, modelo individual e componente temporal comparáveis;

1. a validação respeitar a ordem temporal, usando dados posteriores ao treinamento;

1. forem avaliadas discriminação, calibração, erro temporal, estabilidade e utilidade comercial;

1. associações forem distinguidas de efeitos causais;

1. as previsões forem convertidas em uma regra operacional de priorização;

1. limitações, incertezas e segmentos sem volume suficiente forem apresentados explicitamente.

---

## 10. Referências internas

- Plano de próximas etapas: arquivo `proximas_etapas.md` fornecido para orientar a evolução do projeto.

- Auditoria provisória: `suposicoes/relatorio_auditoria_semantica.md`.

- Dicionário da base analítica: `versao1_pipeline/dicionario_base_analitica.md`.

- Objetivo e critérios de completude: `versao1_pipeline/objetivo_final_projeto_v1.md`.

