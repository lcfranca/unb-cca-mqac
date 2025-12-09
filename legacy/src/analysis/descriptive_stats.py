"""
Módulo de Estatísticas Descritivas (Asset 4.1).

Calcula estatísticas descritivas para retornos e métricas fundamentalistas.
Gera matriz de correlação e estatísticas de distribuição (assimetria, curtose).

Input:
    - data/processed/returns/returns.parquet
    - data/processed/metrics/metrics.parquet

Output:
    - data/outputs/descriptive_stats.json
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from src.core.config import PROJECT_ROOT

def calc_descriptive_stats():
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    returns_path = processed_dir / "returns" / "returns.parquet"
    metrics_path = processed_dir / "metrics" / "metrics.parquet"
    
    output_dir = PROJECT_ROOT / "data" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "descriptive_stats.json"

    # 1. Carregar Dados
    print("Carregando dados...")
    df_ret = pd.read_parquet(returns_path)
    
    # Tentar carregar métricas se existir, senão usar apenas retornos
    has_metrics = False
    if metrics_path.exists():
        df_metrics = pd.read_parquet(metrics_path)
        has_metrics = True
    else:
        print("Aviso: Arquivo de métricas não encontrado. Gerando estatísticas apenas para retornos.")

    stats_data = {}

    # 2. Estatísticas de Retornos
    print("Calculando estatísticas de retornos...")
    ret_cols = ['ret_petr4', 'ret_ibov', 'excess_ret_petr4', 'excess_ret_ibov']
    
    returns_stats = {}
    for col in ret_cols:
        if col not in df_ret.columns: continue
        
        series = df_ret[col].dropna()
        stats = {
            "mean": float(series.mean()),
            "median": float(series.median()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
            "skew": float(series.skew()),
            "kurt": float(series.kurtosis()),
            "annualized_vol": float(series.std() * np.sqrt(252)),
            "n_obs": int(len(series))
        }
        returns_stats[col] = stats
    
    stats_data["returns"] = returns_stats
    
    # Correlação PETR4 vs IBOV
    corr_petr4_ibov = df_ret['ret_petr4'].corr(df_ret['ret_ibov'])
    stats_data["correlations"] = {"petr4_ibov": float(corr_petr4_ibov)}

    # 3. Estatísticas de Métricas Fundamentalistas
    if has_metrics:
        print("Calculando estatísticas de métricas fundamentalistas...")
        # Selecionar colunas numéricas relevantes
        metric_cols = [c for c in df_metrics.columns if c not in ['quarter_end', 'ticker']]
        
        metrics_stats = {}
        for col in metric_cols:
            series = df_metrics[col].dropna()
            if len(series) == 0: continue
            
            stats = {
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(series.std()),
                "min": float(series.min()),
                "max": float(series.max()),
                "skew": float(series.skew()),
                "kurt": float(series.kurtosis()),
                "n_obs": int(len(series))
            }
            metrics_stats[col] = stats
            
        stats_data["metrics"] = metrics_stats
        
        # Matriz de Correlação de Métricas
        corr_matrix = df_metrics[metric_cols].corr().to_dict()
        # Converter para float puro para JSON
        clean_corr = {}
        for k, v in corr_matrix.items():
            clean_corr[k] = {k2: float(v2) for k2, v2 in v.items() if not np.isnan(v2)}
            
        stats_data["metrics_correlation"] = clean_corr

    # 4. Salvar
    print("Salvando estatísticas descritivas...")
    with open(output_path, 'w') as f:
        json.dump(stats_data, f, indent=2)
        
    print(f"Resultados salvos em {output_path}")

if __name__ == "__main__":
    calc_descriptive_stats()
