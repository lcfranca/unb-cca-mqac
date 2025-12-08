# Roteiro de Implementação: Estratégia de Valor Justo Dinâmico (M5-FairValue)

Este documento detalha o plano de implementação para uma nova estratégia de backtest dos modelos M5a e M5b, abandonando a lógica de *day-trade* direcional em favor de uma abordagem de **Valuation Quantitativo Dinâmico**.

## 1. Fundamentação Teórica e Conceitual

### O Problema do Backtest Ingênuo
O backtest atual opera sob a premissa de que $Signal_t = \text{sinal}(\hat{r}_{t+1})$. Se o modelo prevê retorno positivo, compra-se. Isso ignora:
1.  **Magnitude do Retorno:** Um retorno previsto de +0.01% gera o mesmo sinal que +2.0%, embora o risco/retorno seja distinto.
2.  **Custo de Oportunidade:** Com o CDI brasileiro em patamares elevados, o *hurdle rate* (taxa de corte) para assumir risco de renda variável é alto.
3.  **Ruído de Alta Frequência:** Previsões diárias são ruidosas. O conceito de "Valor Justo" pressupõe uma convergência em horizonte mais longo.

### A Nova Abordagem: Expected Present Value (EPV)
A estratégia derivará um **Preço Justo Implícito ($P^*_{t}$)** a partir das predições do modelo para um horizonte de projeção $H$.

$$ P^*_{t} = \frac{E_t[P_{t+H}]}{(1 + CDI_t)^{\frac{H}{252}}} $$

Onde $E_t[P_{t+H}]$ é o preço esperado no futuro dado pelo modelo M5 (que utiliza fundamentos e macro).

**Regra de Decisão (Mispricing Spread):**
Definimos o *Spread de Valor* ($\Delta V_t$) como:
$$ \Delta V_t = \ln(P^*_{t}) - \ln(P_t) $$

*   **Compra (Long):** Se $\Delta V_t > \delta_{entry}$ (O ativo está descontado frente ao valor justo ajustado pelo risco livre).
*   **Venda/Caixa (Neutral):** Se $\Delta V_t < \delta_{exit}$ (O ativo convergiu ou está caro).
*   **Gestão de Caixa:** O capital não alocado é remunerado a $100\%$ do CDI diário.

---

## 2. Checklist de Implementação

### Fase 1: Engenharia de Features e Targets (Horizonte Estendido)
Para calcular um preço justo robusto, precisamos prever o retorno acumulado em um horizonte $H$ (ex: 21 dias úteis / 1 mês), não apenas 1 dia.

- [ ] **Criar Target de Retorno Acumulado:**
    - Calcular $R_{t \to t+21} = \prod_{i=1}^{21} (1 + r_{t+i}) - 1$.
    - Atualizar `src/analysis/train_m5_models.py` para treinar modelos focados neste horizonte ou usar a soma das predições diárias (abordagem *bootstrapping*).
    - *Decisão:* Manter predição diária e acumular (mais flexível) ou treinar direto no alvo mensal?
    - *Recomendação:* Treinar direto no alvo mensal ($H=21$) reduz ruído.

### Fase 2: Desenvolvimento da Estratégia (`src/analysis/backtest_fair_value.py`)
Criar um novo script dedicado a esta lógica.

- [ ] **Cálculo do Preço Justo ($P^*$):**
    - $P^*_{t} = P_t \times (1 + \hat{y}_{t, H}) \times \text{FatorDescontoCDI}$.
- [ ] **Lógica de Alocação:**
    - Implementar máquina de estados: `OUT -> LONG` se Upside > X%; `LONG -> OUT` se Upside < Y%.
- [ ] **Contabilização Rigorosa:**
    - NAV (Net Asset Value) diário.
    - Acrual de CDI sobre saldo em caixa.
    - Custos de transação (corretagem + slippage).

### Fase 3: Integração e Comparação
- [ ] **Executar Backtest:** Rodar para M5a e M5b.
- [ ] **Gerar Métricas:** Sharpe, Sortino, Alpha vs CDI, Beta vs Ibovespa.
- [ ] **Visualização:** Plotar Preço de Mercado vs. Preço Justo Estimado (Banda de Valor).

### Fase 4: Atualização da Nota Técnica
- [ ] **Escrever Seção Metodológica:** Explicar a mudança de paradigma (Trading -> Valuation).
- [ ] **Inserir Resultados:** Substituir ou complementar o backtest antigo.

---

## 3. Estrutura de Arquivos Necessária

### `src/analysis/train_m5_horizon.py` (Novo)
Script para treinar o modelo especificamente para prever retornos em janelas de 21 dias (mensal), capturando tendências fundamentais melhor que o ruído diário.

### `src/analysis/backtest_fair_value.py` (Novo)
```python
def calculate_fair_value_strategy(df_predictions, cdi_series, threshold=0.02):
    """
    Executa estratégia baseada em Preço Justo.
    
    1. Fair Price = Current Price * (1 + Predicted_21d_Return) / (1 + CDI_21d)
    2. Upside = Fair Price / Current Price - 1
    3. Se Upside > threshold: Aloca em PETR4
    4. Se Upside <= 0: Aloca em CDI
    """
    pass
```

---

## 4. Roteiro de Execução (Passo a Passo)

1.  **Preparação dos Dados:**
    *   Verificar se `data/processed/returns.parquet` e `data/processed/macro_returns.parquet` estão atualizados.
    *   Garantir que temos a série do CDI diário disponível e alinhada.

2.  **Treinamento do Modelo de Horizonte (M5-H):**
    *   Modificar o target para `ret_21d`.
    *   Treinar XGBoost (M5b) e Huber (M5a) neste novo target.
    *   Salvar predições em `data/outputs/m5_horizon_predictions.parquet`.

3.  **Backtest da Estratégia:**
    *   Implementar a lógica de *switching* (PETR4 <-> CDI).
    *   Calcular métricas de performance.

4.  **Documentação:**
    *   Adicionar a seção "Estratégia de Valor Justo e Custo de Oportunidade" no `nota-tecnica.md`.

## 5. Rigor Científico e Justificativa

Esta abordagem é superior porque:
1.  **Incorpora a Taxa Livre de Risco Endogenamente:** O modelo só recomenda compra se o retorno esperado superar o CDI *ex-ante*.
2.  **Reduz Turnover:** Ao focar em horizonte mensal/semanal e usar thresholds, evita-se o *churn* excessivo do day-trade.
3.  **Alinhamento Teórico:** Aproxima-se de modelos de *Asset Pricing* onde o preço converge para o valor fundamental. O M5b atua como o "descobridor" do valor fundamental.

---

**Próximo Passo Sugerido:** Iniciar pela criação do script de treinamento com horizonte expandido (`src/analysis/train_m5_horizon.py`).
