# Objetivo final do projeto e critérios de completude

## 1. Definição do objetivo final

O projeto deve desenvolver uma metodologia analítica de previsibilidade de assinatura de contratos para as marcas Poliedro, Polígono e Conviver e Integrar. A metodologia deverá relacionar o perfil das escolas, as características da oportunidade e o histórico de movimentações no funil comercial para estimar, para cada oportunidade aberta, a probabilidade de assinatura e, quando tecnicamente viável, o horizonte provável de fechamento.

A solução final deve apoiar a priorização de oportunidades, a gestão da carteira comercial e a projeção de resultados. Ela deve permitir comparar o comportamento do funil entre marcas, regiões, consultores, redes, portes, clusters, origens e demais segmentos relevantes, levando em conta que as marcas possuem níveis de maturidade e volumes históricos diferentes.

O projeto não se completa com uma taxa histórica de conversão ou com uma única classificação de oportunidades. Deve produzir uma visão integrada de **conversão, velocidade, risco e decisão comercial**, sempre com informações disponíveis no momento em que a previsão seria utilizada.

## 2. Perguntas que a solução completa deve responder

A solução deve permitir investigar quais perfis de escola apresentam maior probabilidade de assinatura para cada marca, quais perfis avançam mais lentamente, em quais segmentos há maior assertividade e conversão, e quais características estão associadas à estagnação, perda ou alongamento da negociação.

Também deve permitir comparar o comportamento do funil entre Poliedro, Polígono e Conviver e Integrar, identificar em que momento uma oportunidade passa a apresentar sinais de maior ou menor probabilidade de conversão e produzir previsões por oportunidade, perfil de escola, marca, consultor, região e período do ano, quando houver dados e volume suficientes.

## 3. Escopo analítico mínimo

A metodologia deve incluir, no mínimo:

1. Caracterização dos perfis de escolas por variáveis institucionais, geográficas, de porte, rede, etapas de ensino, mensalidade, sistema atual, vencimento de contrato e aderência à marca.
2. Reconstrução da jornada das oportunidades, com datas de entrada e saída das etapas, permanência, avanços, recuos, perdas, conversões e movimentações.
3. Análise descritiva do funil, incluindo volume, taxas de avanço, conversão, perdas, motivos de perda, tempo por etapa e ciclo total.
4. Estimativa do tempo típico de avanço e de assinatura por perfil e marca.
5. Identificação dos fatores associados à conversão, ao avanço, à velocidade, à perda e à estagnação.
6. Estimativa da probabilidade de assinatura para oportunidades abertas.
7. Estimativa do prazo provável de assinatura, quando os dados permitirem uma previsão temporal confiável.
8. Criação de indicadores de assertividade e velocidade comercial.
9. Construção de faixas de prioridade que combinem probabilidade, valor potencial, estágio e tempo esperado de fechamento.
10. Disponibilização dos resultados em formato aplicável à rotina comercial.

## 4. Arquitetura metodológica esperada

A solução deve ser organizada em camadas complementares:

### Camada 1 — Reconstrução e auditoria

A base deve ser auditada antes da modelagem. É necessário confirmar a unidade de análise, o significado de cada linha, as chaves de junção, a granularidade temporal, os estados do funil, os valores ausentes, as duplicidades, as oportunidades reabertas e a proporção de oportunidades assinadas, perdidas e abertas.

A unidade analítica recomendada é a oportunidade escola–marca. Quando a base não permitir confirmar essa unidade ou quando uma junção usar uma chave apenas aproximada, a limitação deve ser explicitamente registrada.

### Camada 2 — Modelo de jornada e transições

A dinâmica do funil deve ser representada por estados e transições. Uma cadeia de Markov pode ser usada como baseline descritivo e explicável, com as etapas intermediárias como estados transientes e assinatura e perda como estados absorventes.

A solução deve estimar taxas de avanço, permanência, recuo e saída, além das probabilidades de absorção e do número esperado de transições. Se houver dados suficientes, a transição deve ser condicionada a variáveis como marca, perfil, região, valor, tempo na etapa e comportamento recente, para evitar que todas as oportunidades em uma mesma etapa recebam a mesma previsão.

### Camada 3 — Propensão individual

A solução deve atribuir uma probabilidade de assinatura a cada oportunidade, comparando pelo menos um modelo estrutural, baseado no fit da escola, com um modelo operacional, que inclua o estado e o comportamento recente da negociação.

As variáveis devem ser calculadas apenas com informações disponíveis até a data de previsão. Dados posteriores, como motivo da perda, data de perda ou assinatura futura, não podem entrar como preditores para oportunidades que estavam abertas.

### Camada 4 — Tempo até o evento

A solução deve considerar assinatura e perda como desfechos e oportunidades ainda abertas como observações censuradas. Deve estimar o tempo até assinatura ou perda por análise de sobrevivência, riscos competitivos ou modelo de tempo discreto, conforme a granularidade e a qualidade dos dados.

O resultado temporal esperado é uma probabilidade acumulada em um horizonte definido ou um prazo provável, e não apenas um número de transições entre etapas.

### Camada 5 — Prioridade comercial

A decisão comercial deve combinar probabilidade de assinatura, receita potencial, estágio, risco de estagnação, tempo esperado e confiança da previsão. O resultado deve produzir faixas de prioridade interpretáveis e uma ação ou uso recomendado para cada faixa.

## 5. Respostas e indicadores esperados

A solução deve produzir, quando suportado pelos dados:

- Taxa de avanço entre cada etapa e taxa de chegada às etapas críticas;
- Taxa de conversão final em contrato assinado;
- Taxa de perda geral, por etapa e por motivo;
- Tempo médio e mediano por etapa e até assinatura ou perda;
- Probabilidade de avanço, conversão ou perda de oportunidades abertas;
- Prazo ou probabilidade de assinatura em horizontes definidos;
- Variáveis mais associadas a avanço, conversão, velocidade, perda e estagnação;
- Comparações por marca, região, consultor, rede, porte, cluster, origem e demais segmentos com volume adequado;
- Indicadores de receita convertida, valor esperado e assertividade das prioridades.

## 6. Critérios de validade e completude

A solução será considerada completa somente quando:

1. A unidade de análise e as chaves de junção forem documentadas e auditadas.
2. A jornada for reconstruída de forma reproduzível.
3. Houver tratamento documentado para valores ausentes, duplicidades, oportunidades reabertas e registros inconsistentes.
4. A data de corte e o conjunto de informações disponíveis no momento da previsão forem definidos.
5. O vazamento de informação for prevenido e verificado.
6. As marcas forem analisadas em conjunto e separadamente quando houver volume suficiente.
7. Houver baseline, modelo individual e componente temporal comparáveis.
8. O desempenho for validado respeitando a ordem temporal, com dados posteriores ao treinamento.
9. Forem avaliadas discriminação, calibração, erro temporal, estabilidade e utilidade nas oportunidades prioritárias.
10. As associações forem distinguidas de efeitos causais, especialmente para visitas, consultores e especialistas.
11. As previsões forem convertidas em uma regra operacional de priorização.
12. Limitações, incertezas e segmentos sem volume suficiente forem apresentados explicitamente.

## 7. Limites desta definição

A descrição acima define o resultado esperado do projeto com base no arquivo `prop_proj_poli.txt`. Ela não afirma que todos os campos necessários, a qualidade temporal ou o volume estatístico já estejam disponíveis no Excel atual. A viabilidade de cada componente deve ser confirmada pela auditoria e pelos testes do notebook.
