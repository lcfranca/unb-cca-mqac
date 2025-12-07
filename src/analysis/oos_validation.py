"""
Módulo de Validação Out-of-Sample (Asset 4.3).

Realiza validação cruzada temporal (Time Series Split) e teste OOS fixo
para avaliar a capacidade preditiva real do modelo Q-VAL.

Input:
    - data/processed/returns/returns.parquet
    - data/processed/qval/qval_timeseries.parquet

Output:
    - data/outputs/oos_results.json
"""

import json
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pathlib import Path
from src.core.config import PROJECT_ROOT

def calc_oos_r2(y_true, y_pred, y_train_mean):
    """
    Calcula R2 Out-of-Sample.
    R2_OOS = 1 - (MSE_model / MSE_naive)
    Onde MSE_naive usa a média do treino como predição.
    """
    mse_model = mean_squared_error(y_true, y_pred)
    mse_naive = mean_squared_error(y_true, np.full_like(y_true, y_train_mean))
    return 1 - (mse_model / mse_naive)

def run_oos_validation():
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    returns_path = processed_dir / "returns" / "returns.parquet"
    qval_path = processed_dir / "qval" / "qval_timeseries.parquet"
    
    output_dir = PROJECT_ROOT / "data" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "oos_results.json"

    # 1. Preparar Dados
    print("Carregando dados...")
    df_ret = pd.read_parquet(returns_path)
    df_qval = pd.read_parquet(qval_path)
    
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    qval_cols = ['available_date', 'qval_scaled']
    df_qval_ready = df_qval[qval_cols].sort_values('available_date')
    
    df_ret = df_ret.sort_values('date')
    df_merged = pd.merge_asof(df_ret, df_qval_ready, left_on='date', right_on='available_date', direction='backward')
    
    required_cols = ['excess_ret_petr4', 'excess_ret_ibov', 'qval_scaled']
    df_model = df_merged.dropna(subset=required_cols).copy()

    # 2. Definição de Split (Treino vs Teste)
    # Treino: 2016-2022
    # Teste: 2023-Presente
    split_date = "2023-01-01"
    
    train = df_model[df_model['date'] < split_date].copy()
    test = df_model[df_model['date'] >= split_date].copy()
    
    print(f"Treino: {len(train)} obs ({train['date'].min().date()} a {train['date'].max().date()})")
    print(f"Teste:  {len(test)} obs ({test['date'].min().date()} a {test['date'].max().date()})")

    results = {
        "train_period": {"start": str(train['date'].min().date()), "end": str(train['date'].max().date()), "n_obs": int(len(train))},
        "test_period": {"start": str(test['date'].min().date()), "end": str(test['date'].max().date()), "n_obs": int(len(test))},
        "in_sample": {},
        "out_of_sample": {}
    }

    # 3. Estimação In-Sample (Treino)
    y_train = train['excess_ret_petr4']
    
    # M0 (CAPM)
    X0_train = sm.add_constant(train[['excess_ret_ibov']])
    m0 = sm.OLS(y_train, X0_train).fit()
    
    # M3 (Q-VAL)
    X3_train = sm.add_constant(train[['excess_ret_ibov', 'qval_scaled']])
    m3 = sm.OLS(y_train, X3_train).fit()
    
    results["in_sample"]["M0"] = {"r2": m0.rsquared, "adj_r2": m0.rsquared_adj}
    results["in_sample"]["M3"] = {"r2": m3.rsquared, "adj_r2": m3.rsquared_adj}

    # 4. Predição Out-of-Sample (Teste)
    y_test = test['excess_ret_petr4']
    y_train_mean = y_train.mean() # Para cálculo do R2 OOS
    
    # M0 Pred
    X0_test = sm.add_constant(test[['excess_ret_ibov']], has_constant='add')
    y_pred_m0 = m0.predict(X0_test)
    
    # M3 Pred
    X3_test = sm.add_constant(test[['excess_ret_ibov', 'qval_scaled']], has_constant='add')
    y_pred_m3 = m3.predict(X3_test)
    
    # Métricas OOS
    def calc_metrics(y_true, y_pred, label):
        r2_oos = calc_oos_r2(y_true, y_pred, y_train_mean)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        
        # Direction Accuracy (Acerto de sinal)
        direction_match = np.sign(y_pred) == np.sign(y_true)
        dir_acc = direction_match.mean()
        
        return {
            "r2_oos": float(r2_oos),
            "rmse": float(rmse),
            "mae": float(mae),
            "direction_accuracy": float(dir_acc)
        }

    results["out_of_sample"]["M0"] = calc_metrics(y_test, y_pred_m0, "M0")
    results["out_of_sample"]["M3"] = calc_metrics(y_test, y_pred_m3, "M3")
    
    # 5. Salvar
    print("Salvando resultados OOS...")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Resultados salvos em {output_path}")
    print("-" * 30)
    print(f"M0 R2 OOS: {results['out_of_sample']['M0']['r2_oos']:.4f}")
    print(f"M3 R2 OOS: {results['out_of_sample']['M3']['r2_oos']:.4f}")
    print("-" * 30)

if __name__ == "__main__":
    run_oos_validation()
