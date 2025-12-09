"""
Módulo de Estimação do CAPM (Asset 3.1).

Estima o modelo CAPM (Modelo 0) usando OLS com erros-padrão robustos (HC3).
Salva os resultados estatísticos em JSON.

Input:
    - data/processed/returns/returns.parquet

Output:
    - data/outputs/capm_results.json
"""

import json
import pandas as pd
import statsmodels.api as sm
from pathlib import Path
from src.core.config import PROJECT_ROOT

def estimate_capm():
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    input_path = processed_dir / "returns" / "returns.parquet"
    
    output_dir = PROJECT_ROOT / "data" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "capm_results.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo {input_path} não encontrado.")

    print("Carregando retornos...")
    df = pd.read_parquet(input_path)
    
    # Garantir que temos as colunas necessárias
    required_cols = ['excess_ret_petr4', 'excess_ret_ibov']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Colunas necessárias {required_cols} não encontradas.")

    # Remover NaNs
    df_clean = df.dropna(subset=required_cols).copy()
    
    # Definir variáveis
    y = df_clean['excess_ret_petr4']
    X = df_clean['excess_ret_ibov']
    X = sm.add_constant(X) # Adicionar intercepto (Alpha)

    print("Estimando CAPM (OLS com erros robustos HC3)...")
    model = sm.OLS(y, X)
    results = model.fit(cov_type='HC3') # Erros padrão robustos a heterocedasticidade

    # Extrair resultados
    alpha_params = results.params['const']
    alpha_se = results.bse['const']
    alpha_t = results.tvalues['const']
    alpha_p = results.pvalues['const']

    beta_params = results.params['excess_ret_ibov']
    beta_se = results.bse['excess_ret_ibov']
    beta_t = results.tvalues['excess_ret_ibov']
    beta_p = results.pvalues['excess_ret_ibov']
    
    # Durbin-Watson
    dw_stat = sm.stats.stattools.durbin_watson(results.resid)

    # Estruturar output
    output_data = {
        "alpha": {
            "estimate": float(alpha_params),
            "se": float(alpha_se),
            "t_stat": float(alpha_t),
            "p_value": float(alpha_p)
        },
        "beta": {
            "estimate": float(beta_params),
            "se": float(beta_se),
            "t_stat": float(beta_t),
            "p_value": float(beta_p)
        },
        "r_squared": float(results.rsquared),
        "r_squared_adj": float(results.rsquared_adj),
        "n_obs": int(results.nobs),
        "durbin_watson": float(dw_stat),
        "period": {
            "start": str(df_clean['date'].min().date()),
            "end": str(df_clean['date'].max().date())
        }
    }

    print("Salvando resultados...")
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Resultados salvos em {output_path}")
    print("-" * 30)
    print(f"Alpha: {alpha_params:.6f} (p={alpha_p:.4f})")
    print(f"Beta:  {beta_params:.6f} (p={beta_p:.4f})")
    print(f"R2:    {results.rsquared:.4f}")
    print("-" * 30)

if __name__ == "__main__":
    estimate_capm()
