"""
Script para comparação completa dos modelos M0 a M4.
Gera métricas In-Sample e Out-of-Sample para avaliar a evolução informacional.

Modelos:
- M0: CAPM (Market Beta)
- M1: CAPM + Value Score (Componente de Valor do Q-VAL)
- M2: CAPM + Quality Score (Componente de Qualidade do Q-VAL)
- M3: CAPM + Q-VAL Score (Score Agregado)
- M4: CAPM + Macro Factors (Brent, FX, EMBI)

Output:
- data/outputs/full_model_comparison.json
- data/outputs/tables/tabela_evolucao_r2.tex
"""

import json
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
from src.core.config import PROJECT_ROOT

def run():
    # 1. Carregar Dados
    print("Carregando dados...")
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # Retornos (PETR4, IBOV)
    df_ret = pd.read_parquet(processed_dir / "returns" / "returns.parquet")
    
    # Q-VAL (Scores)
    df_qval = pd.read_parquet(processed_dir / "qval" / "qval_timeseries.parquet")
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    df_qval = df_qval[['available_date', 'score_valor', 'score_qualidade', 'qval_scaled']].sort_values('available_date')
    
    # Macro (Brent, FX, EMBI)
    # Note: macro_returns.parquet already contains returns data (merged in macro_model.py)
    df_macro = pd.read_parquet(processed_dir / "macro_returns.parquet")
    
    # Factors (CMA, RMW)
    df_factors = pd.read_parquet(processed_dir / "factors" / "petr4_factors.parquet")
    df_factors['available_date'] = pd.to_datetime(df_factors['available_date'])
    
    # 2. Merge de Dados
    # Use df_macro as base since it has daily returns + macro
    df_daily = df_macro.copy()
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    
    # Merge com Q-VAL (Low freq to High freq)
    df_daily = df_daily.sort_values('date')
    df_full = pd.merge_asof(df_daily, df_qval, left_on='date', right_on='available_date', direction='backward')
    
    # Merge com Factors (Low freq to High freq)
    df_factors = df_factors.sort_values('available_date')
    df_full = pd.merge_asof(df_full, df_factors[['available_date', 'cma_proxy', 'rmw_proxy']], left_on='date', right_on='available_date', direction='backward')
    
    # Limpeza
    cols_needed = [
        'excess_ret_petr4', 'excess_ret_ibov', 
        'score_valor', 'score_qualidade', 'qval_scaled',
        'ret_brent', 'ret_fx', 'delta_embi',
        'cma_proxy', 'rmw_proxy'
    ]
    df_model = df_full.dropna(subset=cols_needed).copy()
    
    # 3. Definição de Split
    split_date = "2023-01-01"
    train = df_model[df_model['date'] < split_date].copy()
    test = df_model[df_model['date'] >= split_date].copy()
    
    print(f"Treino: {len(train)} obs")
    print(f"Teste: {len(test)} obs")
    
    # 4. Definição dos Modelos
    models = {
        "M0 (CAPM)": ['excess_ret_ibov'],
        "M1 (CAPM + Value)": ['excess_ret_ibov', 'score_valor'],
        "M2 (CAPM + Quality)": ['excess_ret_ibov', 'score_qualidade'],
        "M3 (CAPM + Q-VAL)": ['excess_ret_ibov', 'qval_scaled'],
        "M4 (Macro)": ['excess_ret_ibov', 'ret_brent', 'ret_fx', 'delta_embi'],
        "M5 (Fatores)": ['excess_ret_ibov', 'ret_brent', 'ret_fx', 'delta_embi', 'cma_proxy', 'rmw_proxy']
    }
    
    results = {}
    
    for name, features in models.items():
        # In-Sample
        X_train = sm.add_constant(train[features])
        y_train = train['excess_ret_petr4']
        model = sm.OLS(y_train, X_train).fit()
        
        # Out-of-Sample
        X_test = sm.add_constant(test[features], has_constant='add')
        y_test = test['excess_ret_petr4']
        y_pred = model.predict(X_test)
        
        # Métricas
        mse = np.mean((y_test - y_pred)**2)
        # MSE Naive (Historical Mean of Train)
        y_train_mean = y_train.mean()
        mse_naive = np.mean((y_test - y_train_mean)**2)
        r2_oos = 1 - (mse / mse_naive)
        
        results[name] = {
            "R2_Adj": model.rsquared_adj,
            "AIC": model.aic,
            "BIC": model.bic,
            "R2_OOS": r2_oos,
            "MSE": mse,
            "Num_Params": len(model.params)
        }
        
    # 5. Salvar JSON
    output_json = PROJECT_ROOT / "data" / "outputs" / "full_model_comparison.json"
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=4)
        
    # 6. Gerar Tabela LaTeX
    generate_latex_table(results)
    
def generate_latex_table(results):
    output_tex = PROJECT_ROOT / "data" / "outputs" / "tables" / "tabela_evolucao_r2.tex"
    output_tex.parent.mkdir(parents=True, exist_ok=True)
    
    latex = [
        "\\begin{table}[h]",
        "\\centering",
        "\\caption{Evolução da Eficiência Informacional (M0 a M4)}",
        "\\label{tab:evolucao_r2}",
        "\\begin{tabular}{lccccc}",
        "\\toprule",
        "Modelo & $R^2$ Adj. & $\\Delta R^2$ (vs M0) & AIC & $R^2_{OOS}$ & Info. Adicional \\\\",
        "\\midrule"
    ]
    
    base_r2 = results["M0 (CAPM)"]["R2_Adj"]
    
    for name, metrics in results.items():
        r2_adj = metrics["R2_Adj"]
        delta_r2 = r2_adj - base_r2
        aic = metrics["AIC"]
        r2_oos = metrics["R2_OOS"]
        
        # Descrição curta
        if "M0" in name: info = "Risco de Mercado"
        elif "M1" in name: info = "+ Valor (P/L, etc)"
        elif "M2" in name: info = "+ Qualidade (ROE, etc)"
        elif "M3" in name: info = "+ Score Agregado"
        elif "M4" in name: info = "+ Macro (Oil, FX, Risk)"
        elif "M5" in name: info = "+ Fatores (RMW, CMA)"
        else: info = ""
        
        row = f"{name.split(' ')[0]} & {r2_adj:.4f} & {delta_r2:+.4f} & {aic:.1f} & {r2_oos:.4f} & {info} \\\\"
        latex.append(row)
        
    latex.extend([
        "\\bottomrule",
        "\\multicolumn{6}{l}{\\footnotesize $\\Delta R^2$: Ganho sobre o CAPM. $R^2_{OOS}$: Performance fora da amostra (2023-2025).}",
        "\\end{tabular}",
        "\\end{table}"
    ])
    
    with open(output_tex, 'w') as f:
        f.write("\n".join(latex))
    print(f"Tabela salva em {output_tex}")

if __name__ == "__main__":
    run()
