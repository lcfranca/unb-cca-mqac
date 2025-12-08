# Análise de Decaimento Informacional e Eficiência de Mercado

## Objetivo
Investigar empiricamente a "meia-vida" da informação fundamentalista para as ações da Petrobras (PETR4). A análise busca responder: *Quão rapidamente o mercado incorpora o sinal de um resultado trimestral e quando o ruído macro/técnico passa a dominar a formação de preço?*

## Metodologia

### 1. Definição de Tempo Relativo ($\Delta t$)
Para medir o decaimento, transformamos o eixo temporal de datas de calendário para "dias de negociação desde a última divulgação de resultados" (`days_since_release`). Isso permite alinhar todos os trimestres em uma escala comparável (0 a ~65 dias).

### 2. Modelagem de Importância Dinâmica (SHAP)
Utilizamos um modelo XGBoost treinado com horizonte de previsão de 5 dias (identificado como o de maior sinal-ruído, $R^2 \approx 0.13$). Calculamos os valores SHAP (SHapley Additive exPlanations) para cada dia e cada feature, agregando-os em três categorias:
*   **Fundamentos**: Métricas de Valor, Qualidade e Risco (ex: `score_valor`, `z_earnings_yield`).
*   **Macro**: Variáveis de contexto econômico (ex: `ret_brent`, `delta_embi`, `mkt_vol_regime`).
*   **Técnico**: Momentum e Volatilidade de preço (ex: `ret_lag`, `vol_20d`).

A "Curva de Decaimento Informacional" plota a média absoluta do valor SHAP (|SHAP|) para cada categoria em função de $\Delta t$.

## Resultados

### Dinâmica de Eficiência e Ciclos de Relevância
A visualização consolidada (ver `data/outputs/figures/master_efficiency_dynamics.pdf`) apresenta a síntese do comportamento informacional do mercado para PETR4:

1.  **Janelas de Eficiência (Painel Superior)**:
    *   As áreas sombreadas em azul marcam os 15 dias subsequentes a cada divulgação de resultados.
    *   Observa-se que os movimentos de preço mais expressivos e direcionais tendem a ocorrer dentro dessas janelas, onde o mercado está ativamente precificando a nova realidade fundamentalista.

2.  **Decaimento da Dominância Fundamentalista (Painel Inferior)**:
    *   A curva de "Dominância Fundamentalista" (proporção da importância do modelo atribuída a métricas de Valor/Qualidade) exibe um padrão cíclico claro.
    *   **Picos**: Coincidem com as datas de divulgação, onde a importância relativa dos fundamentos chega a superar 60-70%.
    *   **Vales**: Nos períodos "inter-safra" (entre divulgações), a dominância cai abaixo da média histórica, indicando que o preço passa a ser governado por ruído de mercado e variáveis macroeconômicas (Brent, Risco País).

### Quantificação do Decaimento (Tabela)
A Tabela \ref{tab:decaimento_info} (ver `data/outputs/tables/tab_decaimento_informacional.tex`) quantifica a degradação do poder preditivo do modelo ao longo do ciclo trimestral:

*   **Janela 0-5 dias**: O modelo atinge seu pico de performance, com Information Coefficient (IC) de 61.0% e $R^2$ de 27.3%. Isso confirma que a informação fundamentalista é extremamente valiosa imediatamente após sua liberação.
*   **Janela 16-20 dias**: Observa-se o colapso da eficiência preditiva. O IC cai para 25.1% e o $R^2$ para apenas 6.0%. Este ponto marca o fim da "Janela de Eficiência", onde o mercado já absorveu a maior parte do sinal.
*   **Recuperação Tardia (21-40 dias)**: Curiosamente, há uma recuperação parcial da previsibilidade (IC ~48%), possivelmente associada a movimentos de *momentum* ou ajustes macroeconômicos de médio prazo, mas desconectados do choque informacional inicial.

## Conclusão e Validação de Hipóteses
Os resultados oferecem suporte empírico à **Hipótese dos Mercados Adaptativos (AMH)**:
*   **Eficiência Cíclica**: O mercado exibe janelas de ineficiência relativa (alta previsibilidade fundamentalista) imediatamente após choques informacionais.
*   **Adaptação Rápida**: A vantagem informacional decai rapidamente (meia-vida de ~15 dias), conforme evidenciado pela queda na curva de dominância.
*   **Mudança de Regime**: O ativo transita estruturalmente entre um regime "driven by fundamentals" e um regime "driven by macro".
