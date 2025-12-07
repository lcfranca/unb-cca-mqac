"""
Análise de Benchmarks Naïve (Fase 1).

Calcula métricas de erro (MSE, MAE) e R2 Out-of-Sample (R2_OOS) para modelos de referência:
1. Random Walk (RW): Previsão = 0
2. Média Histórica (HM): Previsão = Média Expansiva (Benchmark para R2_OOS)
3. CAPM (Baseline): Previsão = Alpha + Beta * Rm (Parâmetros fixos no treino)

Gera dados para tabelas e figuras comparativas.
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
    
    # Evitar divisão por zero (improvável)
    if mse_benchmark == 0:
        return np.nan
        
    return 1 - (mse_model / mse_benchmark)

def run_naive_benchmarks():
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    output_dir = PROJECT_ROOT / "data" / "outputs"
    returns_path = processed_dir / "returns" / "returns.parquet"
    
    # Outputs
    metrics_path = output_dir / "naive_metrics.json"
    errors_path = output_dir / "naive_errors.parquet"
    
    print("Carregando dados...")
    df = pd.read_parquet(returns_path).sort_values('date')
    
    # Definir Split (Treino: 2016-2022, Teste: 2023-2025)
    train_mask = df['date'] < '2023-01-01'
    test_mask = df['date'] >= '2023-01-01'
    
    df_train = df[train_mask].copy()
    df_test = df[test_mask].copy()
    
    print(f"Treino: {len(df_train)} obs | Teste: {len(df_test)} obs")
    
    # Variáveis
    y_train = df_train['excess_ret_petr4']
    X_train = sm.add_constant(df_train['excess_ret_ibov'])
    
    y_test = df_test['excess_ret_petr4']
    X_test = sm.add_constant(df_test['excess_ret_ibov'])
    
    # ==========================================================================
    # 1. Random Walk (RW)
    # ==========================================================================
    # Previsão = 0 (para retornos excedentes)
    pred_rw = np.zeros(len(y_test))
    
    # ==========================================================================
    # 2. Média Histórica (HM) - Expanding Window (Benchmark)
    # ==========================================================================
    full_y = pd.concat([y_train, y_test])
    expanding_mean = full_y.expanding().mean().shift(1)
    pred_hm = expanding_mean.loc[y_test.index].values
    
    # ==========================================================================
    # 3. CAPM (Fixed Parameters)
    # ==========================================================================
    model_capm = sm.OLS(y_train, X_train).fit()
    pred_capm = model_capm.predict(X_test).values
    
    # ==========================================================================
    # Cálculo de Erros
    # ==========================================================================
    errors = pd.DataFrame(index=y_test.index)
    errors['date'] = df_test['date']
    errors['y_true'] = y_test
    
    # Erros simples
    errors['e_rw'] = y_test - pred_rw
    errors['e_hm'] = y_test - pred_hm
    errors['e_capm'] = y_test - pred_capm
    
    # Erros quadráticos
    errors['se_rw'] = errors['e_rw'] ** 2
    errors['se_hm'] = errors['e_hm'] ** 2
    errors['se_capm'] = errors['e_capm'] ** 2
    
    # Erros acumulados (Cumulative Squared Error)
    errors['cse_rw'] = errors['se_rw'].cumsum()
    errors['cse_hm'] = errors['se_hm'].cumsum()
    errors['cse_capm'] = errors['se_capm'].cumsum()
    
    # Diferença acumulada (HM - CAPM) -> Se positivo, CAPM é melhor
    errors['diff_cse_hm_capm'] = errors['cse_hm'] - errors['cse_capm']
    
    # Salvar erros
    errors.to_parquet(errors_path)
    print(f"Erros salvos em {errors_path}")
    
    # ==========================================================================
    # Métricas Agregadas (incluindo R2 OOS)
    # ==========================================================================
    # Benchmark para R2 OOS é a Média Histórica (HM)
    
    metrics = {
        "RW": {
            "MSE": mean_squared_error(y_test, pred_rw),
            "MAE": mean_absolute_error(y_test, pred_rw),
            "RMSE": np.sqrt(mean_squared_error(y_test, pred_rw)),
            "R2_OOS": calculate_r2_oos(y_test, pred_rw, pred_hm)
        },
        "HM": {
            "MSE": mean_squared_error(y_test, pred_hm),
            "MAE": mean_absolute_error(y_test, pred_hm),
            "RMSE": np.sqrt(mean_squared_error(y_test, pred_hm)),
            "R2_OOS": 0.0 # Por definição
        },
        "CAPM": {
            "MSE": mean_squared_error(y_test, pred_capm),
            "MAE": mean_absolute_error(y_test, pred_capm),
            "RMSE": np.sqrt(mean_squared_error(y_test, pred_capm)),
            "R2_OOS": calculate_r2_oos(y_test, pred_capm, pred_hm)
        }
    }
    
    # Salvar métricas
    import json
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Métricas salvas em {metrics_path}")

if __name__ == "__main__":
    run_naive_benchmarks()
