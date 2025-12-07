"""
Análise de CAPM Dinâmico (Fase 2).

Implementa CAPM com Beta Variável no Tempo (Rolling Window).
Janela de estimação: 252 dias (aprox. 1 ano de negociação).

Calcula:
1. Série temporal de Betas e Alphas.
2. Previsões Out-of-Sample (OOS).
3. Métricas de erro (MSE, MAE, R2_OOS).
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error, mean_absolute_error
from pathlib import Path
from src.core.config import PROJECT_ROOT

def calculate_r2_oos(y_true, y_pred, y_benchmark):
    """
    Calcula R2 Out-of-Sample conforme Campbell & Thompson (2008).
    R2_OOS = 1 - (MSE_model / MSE_benchmark)
    """
    mse_model = mean_squared_error(y_true, y_pred)
    mse_benchmark = mean_squared_error(y_true, y_benchmark)
    
    if mse_benchmark == 0:
        return np.nan
        
    return 1 - (mse_model / mse_benchmark)

def rolling_capm(y, x, window=252):
    """
    Calcula Beta e Alpha rolantes.
    Retorna séries alinhadas com o índice original (com NaNs no início).
    """
    betas = []
    alphas = []
    
    # Adicionar constante para Alpha
    X = sm.add_constant(x)
    
    # Rolling regression
    # Nota: RollingOLS do statsmodels é eficiente
    from statsmodels.regression.rolling import RollingOLS
    
    model = RollingOLS(y, X, window=window)
    results = model.fit()
    
    params = results.params
    
    # params columns: const (alpha), excess_ret_ibov (beta)
    return params['const'], params['excess_ret_ibov']

def run_dynamic_capm():
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    output_dir = PROJECT_ROOT / "data" / "outputs"
    returns_path = processed_dir / "returns" / "returns.parquet"
    
    # Outputs
    metrics_path = output_dir / "dynamic_metrics.json"
    results_path = output_dir / "dynamic_results.parquet"
    
    print("Carregando dados...")
    df = pd.read_parquet(returns_path).sort_values('date')
    
    # Definir Split (Mesmo do Naive: Teste >= 2023-01-01)
    test_start_date = '2023-01-01'
    
    # Variáveis
    y = df['excess_ret_petr4']
    x = df['excess_ret_ibov']
    
    # ==========================================================================
    # Estimação Rolling (Janela de 1 ano = 252 dias úteis)
    # ==========================================================================
    print("Estimando Rolling CAPM (Window=252)...")
    alphas, betas = rolling_capm(y, x, window=252)
    
    df['rolling_alpha'] = alphas
    df['rolling_beta'] = betas
    
    # ==========================================================================
    # Previsão OOS
    # ==========================================================================
    # Para prever t, usamos parâmetros estimados com dados até t-1.
    # Portanto, shiftamos os parâmetros em 1 período.
    
    df['pred_alpha'] = df['rolling_alpha'].shift(1)
    df['pred_beta'] = df['rolling_beta'].shift(1)
    
    # Predição: R_hat_t = alpha_{t-1} + beta_{t-1} * Rm_t
    # Nota: Usamos Rm_t realizado. Isso é "Conditional" prediction no sentido de que
    # condicionamos ao fator de mercado contemporâneo, mas usamos parâmetros passados.
    # É o padrão para avaliar fit do modelo de fatores.
    
    df['pred_dynamic_capm'] = df['pred_alpha'] + df['pred_beta'] * df['excess_ret_ibov']
    
    # Filtrar apenas período de teste para avaliação
    df_test = df[df['date'] >= test_start_date].copy()
    
    # Remover NaNs (se houver, devido ao shift ou window)
    df_test = df_test.dropna(subset=['pred_dynamic_capm'])
    
    print(f"Teste: {len(df_test)} observações")
    
    # ==========================================================================
    # Benchmarks (Recalcular ou carregar para comparar R2 OOS)
    # ==========================================================================
    # Precisamos do HM (Historical Mean) para o R2 OOS
    # HM Expanding Window
    
    # Recriando HM para o conjunto de teste exato
    # Expanding mean até t-1
    full_y = df['excess_ret_petr4']
    expanding_mean = full_y.expanding().mean().shift(1)
    df_test['pred_hm'] = expanding_mean.loc[df_test.index]
    
    # ==========================================================================
    # Métricas
    # ==========================================================================
    y_true = df_test['excess_ret_petr4']
    y_pred = df_test['pred_dynamic_capm']
    y_bench = df_test['pred_hm']
    
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2_oos = calculate_r2_oos(y_true, y_pred, y_bench)
    
    metrics = {
        "Dynamic CAPM": {
            "MSE": mse,
            "MAE": mae,
            "RMSE": rmse,
            "R2_OOS": r2_oos
        }
    }
    
    # Salvar métricas
    import json
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Métricas salvas em {metrics_path}")
    
    # Salvar resultados (séries temporais)
    # Salvar tudo (treino e teste) para plotar evolução do Beta
    output_cols = ['date', 'excess_ret_petr4', 'excess_ret_ibov', 
                   'rolling_alpha', 'rolling_beta', 'pred_dynamic_capm']
    df[output_cols].to_parquet(results_path)
    print(f"Resultados salvos em {results_path}")

if __name__ == "__main__":
    run_dynamic_capm()
