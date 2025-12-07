"""
Módulo de Análise Rolling R2 (Asset 4.2).

Calcula o R2 e R2 Ajustado em janelas móveis para avaliar a estabilidade temporal
da eficiência informacional e a contribuição do modelo Q-VAL.

Input:
    - data/processed/returns/returns.parquet
    - data/processed/qval/qval_timeseries.parquet

Output:
    - data/outputs/rolling_r2.parquet
"""

import pandas as pd
import statsmodels.api as sm
import numpy as np
from pathlib import Path
from src.core.config import PROJECT_ROOT

def calc_rolling_r2():
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    returns_path = processed_dir / "returns" / "returns.parquet"
    qval_path = processed_dir / "qval" / "qval_timeseries.parquet"
    
    output_dir = PROJECT_ROOT / "data" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "rolling_r2.parquet"

    # 1. Preparar Dados (Mesma lógica de estimate_models.py)
    print("Carregando e preparando dados...")
    df_ret = pd.read_parquet(returns_path)
    df_qval = pd.read_parquet(qval_path)
    
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    qval_cols = ['available_date', 'qval_scaled']
    df_qval_ready = df_qval[qval_cols].sort_values('available_date')
    
    df_ret = df_ret.sort_values('date')
    df_merged = pd.merge_asof(df_ret, df_qval_ready, left_on='date', right_on='available_date', direction='backward')
    
    required_cols = ['excess_ret_petr4', 'excess_ret_ibov', 'qval_scaled']
    df_model = df_merged.dropna(subset=required_cols).copy()
    
    # 2. Configuração Rolling
    window_size = 252 # 1 ano de dias úteis
    step_size = 5     # Calcular a cada 5 dias para suavizar e acelerar
    
    results = []
    
    print(f"Calculando Rolling R2 (Janela: {window_size}, Step: {step_size})...")
    
    total_obs = len(df_model)
    
    for i in range(window_size, total_obs, step_size):
        subset = df_model.iloc[i-window_size:i]
        
        # Data de referência (fim da janela)
        ref_date = subset['date'].iloc[-1]
        
        y = subset['excess_ret_petr4']
        
        # Modelo 0 (CAPM)
        X0 = sm.add_constant(subset[['excess_ret_ibov']])
        model0 = sm.OLS(y, X0).fit()
        
        # Modelo 3 (Q-VAL)
        X3 = sm.add_constant(subset[['excess_ret_ibov', 'qval_scaled']])
        model3 = sm.OLS(y, X3).fit()
        
        res_dict = {
            'date': ref_date,
            'window_start': subset['date'].iloc[0],
            'r2_m0': model0.rsquared,
            'adj_r2_m0': model0.rsquared_adj,
            'beta_m0': model0.params['excess_ret_ibov'],
            
            'r2_m3': model3.rsquared,
            'adj_r2_m3': model3.rsquared_adj,
            'beta_m3': model3.params['excess_ret_ibov'],
            'qval_coef': model3.params['qval_scaled'],
            'qval_pvalue': model3.pvalues['qval_scaled'],
            
            'delta_r2': model3.rsquared - model0.rsquared,
            'delta_adj_r2': model3.rsquared_adj - model0.rsquared_adj
        }
        results.append(res_dict)
        
    # 3. Salvar
    df_results = pd.DataFrame(results)
    df_results.to_parquet(output_path)
    
    print(f"Resultados salvos em {output_path}")
    print(f"Total de janelas calculadas: {len(df_results)}")
    print(f"Média Delta Adj R2: {df_results['delta_adj_r2'].mean():.6f}")

if __name__ == "__main__":
    calc_rolling_r2()
