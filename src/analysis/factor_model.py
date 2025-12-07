"""
Análise do Modelo de Fatores (M5) - Fama-French Adaptado.

Estima o modelo M5 que adiciona proxies fundamentalistas (CMA, RMW)
ao modelo Macro (M4).

Input:
    - data/processed/macro_returns.parquet (M4 Data)
    - data/processed/factors/petr4_factors.parquet (M5 Factors)

Output:
    - data/outputs/factor_results.json
    - data/outputs/tables/factor_regression.tex
"""

import json
import pandas as pd
import statsmodels.api as sm
from pathlib import Path
from src.core.config import PROJECT_ROOT

def run_factor_model():
    # 1. Carregar Dados
    macro_path = PROJECT_ROOT / "data" / "processed" / "macro_returns.parquet"
    factors_path = PROJECT_ROOT / "data" / "processed" / "factors" / "petr4_factors.parquet"
    
    df_macro = pd.read_parquet(macro_path)
    df_factors = pd.read_parquet(factors_path)
    
    # 2. Merge (Daily + Quarterly)
    df_macro['date'] = pd.to_datetime(df_macro['date'])
    df_factors['available_date'] = pd.to_datetime(df_factors['available_date'])
    
    df_factors = df_factors.sort_values('available_date')
    df_macro = df_macro.sort_values('date')
    
    df_merged = pd.merge_asof(
        df_macro, 
        df_factors[['available_date', 'cma_proxy', 'rmw_proxy']], 
        left_on='date', 
        right_on='available_date', 
        direction='backward'
    )
    
    # Limpeza
    features = ['excess_ret_ibov', 'ret_brent', 'ret_fx', 'delta_embi', 'cma_proxy', 'rmw_proxy']
    target = 'excess_ret_petr4'
    
    df_model = df_merged.dropna(subset=features + [target]).copy()
    
    print(f"Amostra M5: {len(df_model)} dias.")
    
    # 3. Estimação OLS
    X = sm.add_constant(df_model[features])
    y = df_model[target]
    
    model = sm.OLS(y, X).fit()
    
    print(model.summary())
    
    # 4. Salvar Resultados
    results = {
        "r2": model.rsquared,
        "adj_r2": model.rsquared_adj,
        "aic": model.aic,
        "bic": model.bic,
        "params": model.params.to_dict(),
        "pvalues": model.pvalues.to_dict(),
        "tvalues": model.tvalues.to_dict(),
        "n_obs": int(model.nobs)
    }
    
    output_json = PROJECT_ROOT / "data" / "outputs" / "factor_results.json"
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=4)
        
    # 5. Gerar Tabela LaTeX
    generate_latex_table(model)

def generate_latex_table(model):
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "factor_regression.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Mapeamento de nomes
    names = {
        'const': 'Intercepto',
        'excess_ret_ibov': 'Risco de Mercado (Beta)',
        'ret_brent': 'Retorno Brent',
        'ret_fx': 'Câmbio (USD/BRL)',
        'delta_embi': 'Risco País (EMBI)',
        'cma_proxy': 'Fator Investimento (CMA)',
        'rmw_proxy': 'Fator Lucratividade (RMW)'
    }
    
    latex = [
        "\\begin{table}[h]",
        "\\centering",
        "\\caption{Resultados da Estimação do Modelo de Fatores (M5)}",
        "\\label{tab:factor_regression}",
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        "Fator & Coeficiente & Erro-Padrão & Estatística t & p-valor \\\\",
        "\\midrule"
    ]
    
    for param in model.params.index:
        name = names.get(param, param)
        coef = model.params[param]
        se = model.bse[param]
        t = model.tvalues[param]
        p = model.pvalues[param]
        
        sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
        
        row = f"{name} & {coef:.4f}{sig} & {se:.4f} & {t:.2f} & {p:.4f} \\\\"
        latex.append(row)
        
    latex.extend([
        "\\midrule",
        f"Observações & {int(model.nobs)} & & & \\\\",
        f"$R^2$ Ajustado & {model.rsquared_adj:.4f} & & & \\\\",
        "\\bottomrule",
        "\\multicolumn{5}{l}{\\footnotesize * p$<$0.1; ** p$<$0.05; *** p$<$0.01}",
        "\\end{tabular}",
        "\\end{table}"
    ])
    
    with open(output_path, 'w') as f:
        f.write("\n".join(latex))
    print(f"Tabela salva em {output_path}")

if __name__ == "__main__":
    run_factor_model()
