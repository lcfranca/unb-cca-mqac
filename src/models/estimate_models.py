"""
Módulo de Estimação de Modelos Comparativos (Asset 3.2).

Estima quatro modelos aninhados para testar a eficiência informacional:
- M0: CAPM (Baseline)
- M1: CAPM + Fator Único (Earnings Yield)
- M2: CAPM + Fatores Q-VAL (Valor, Qualidade, Risco)
- M3: CAPM + Score Q-VAL (Sintético)

Realiza alinhamento temporal com lag conservador de 3 meses para evitar look-ahead bias.
Salva resultados comparativos em JSON.
"""

import json
import pandas as pd
import statsmodels.api as sm
import numpy as np
from pathlib import Path
from src.core.config import PROJECT_ROOT

def estimate_models():
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    returns_path = processed_dir / "returns" / "returns.parquet"
    qval_path = processed_dir / "qval" / "qval_timeseries.parquet"
    
    output_dir = PROJECT_ROOT / "data" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "model_comparison.json"

    # 1. Carregar Dados
    print("Carregando dados...")
    df_ret = pd.read_parquet(returns_path)
    df_qval = pd.read_parquet(qval_path)

    # 2. Preparar Q-VAL (Lag de 3 meses para disponibilidade da informação)
    # Assumimos que a informação do trimestre T só está disponível em T + 3 meses
    print("Processando lags e merge...")
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    
    # Selecionar colunas relevantes e renomear para merge
    qval_cols = [
        'available_date', 
        'z_earnings_yield', # Para M1
        'score_valor', 'score_qualidade', 'score_risco', # Para M2
        'qval_scaled' # Para M3
    ]
    df_qval_ready = df_qval[qval_cols].sort_values('available_date')

    # Merge asof (para propagar o último valor disponível)
    df_ret = df_ret.sort_values('date')
    df_merged = pd.merge_asof(
        df_ret, 
        df_qval_ready, 
        left_on='date', 
        right_on='available_date', 
        direction='backward'
    )

    # Filtrar dados válidos (remover períodos sem Q-VAL ou sem retornos)
    # Precisamos de todas as colunas preenchidas para comparar os modelos no mesmo sample
    required_cols = ['excess_ret_petr4', 'excess_ret_ibov', 'z_earnings_yield', 
                     'score_valor', 'score_qualidade', 'score_risco', 'qval_scaled']
    
    df_model = df_merged.dropna(subset=required_cols).copy()
    
    print(f"Amostra final: {len(df_model)} observações ({df_model['date'].min().date()} a {df_model['date'].max().date()})")

    # 3. Definir Modelos
    models_config = {
        "M0_CAPM": {
            "y": "excess_ret_petr4",
            "X": ["excess_ret_ibov"]
        },
        "M1_SingleFactor": {
            "y": "excess_ret_petr4",
            "X": ["excess_ret_ibov", "z_earnings_yield"]
        },
        "M2_MultiFactor": {
            "y": "excess_ret_petr4",
            "X": ["excess_ret_ibov", "score_valor", "score_qualidade", "score_risco"]
        },
        "M3_QVAL": {
            "y": "excess_ret_petr4",
            "X": ["excess_ret_ibov", "qval_scaled"]
        }
    }

    results_store = {}

    # 4. Estimar Modelos
    for model_name, config in models_config.items():
        print(f"Estimando {model_name}...")
        y = df_model[config["y"]]
        X = df_model[config["X"]]
        X = sm.add_constant(X)

        model = sm.OLS(y, X)
        res = model.fit(cov_type='HC3')

        # Armazenar métricas
        results_store[model_name] = {
            "r_squared": res.rsquared,
            "adj_r_squared": res.rsquared_adj,
            "aic": res.aic,
            "bic": res.bic,
            "f_pvalue": res.f_pvalue,
            "params": res.params.to_dict(),
            "pvalues": res.pvalues.to_dict(),
            "n_obs": int(res.nobs)
        }

    # 5. Calcular Delta R2 (vs M0)
    r2_m0 = results_store["M0_CAPM"]["adj_r_squared"]
    for name in results_store:
        results_store[name]["delta_adj_r2"] = results_store[name]["adj_r_squared"] - r2_m0

    # 6. Salvar
    print("Salvando comparação de modelos...")
    with open(output_path, 'w') as f:
        json.dump(results_store, f, indent=2)

    print(f"Resultados salvos em {output_path}")
    
    # Exibir resumo
    summary_df = pd.DataFrame(results_store).T[['adj_r_squared', 'delta_adj_r2', 'aic', 'bic']]
    print("\nResumo Comparativo:")
    print(summary_df)

if __name__ == "__main__":
    estimate_models()
