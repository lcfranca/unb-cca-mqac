"""
Análise do Modelo Macro (M4) - Fase 3.

Estima modelo multifatorial:
R_petr4 - Rf = alpha + b1(Rm-Rf) + b2(Brent) + b3(FX) + b4(Delta_EMBI)

Calcula:
1. Coeficientes e Significância (t-stats).
2. R2 e R2 Ajustado.
3. Decomposição de Variância (Contribuição de cada fator para o R2).
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path
from src.core.config import PROJECT_ROOT

def run_macro_model():
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    output_dir = PROJECT_ROOT / "data" / "outputs"
    macro_path = processed_dir / "macro_returns.parquet"
    
    # Outputs
    metrics_path = output_dir / "macro_metrics.json"
    results_path = output_dir / "macro_results.parquet"
    
    print("Carregando dados macro...")
    df = pd.read_parquet(macro_path).dropna()
    
    # Definir Variáveis
    y = df['excess_ret_petr4']
    
    # Fatores (X)
    # M0: Apenas Mercado
    X_m0 = df[['excess_ret_ibov']]
    X_m0 = sm.add_constant(X_m0)
    
    # M4: Mercado + Macro
    X_m4 = df[['excess_ret_ibov', 'ret_brent', 'ret_fx', 'delta_embi']]
    X_m4 = sm.add_constant(X_m4)
    
    # ==========================================================================
    # Estimação M0 (Baseline CAPM)
    # ==========================================================================
    model_m0 = sm.OLS(y, X_m0).fit()
    r2_m0 = model_m0.rsquared
    
    # ==========================================================================
    # Estimação M4 (Macro)
    # ==========================================================================
    model_m4 = sm.OLS(y, X_m4).fit()
    r2_m4 = model_m4.rsquared
    adj_r2_m4 = model_m4.rsquared_adj
    
    print(model_m4.summary())
    
    # ==========================================================================
    # Decomposição de Variância (Covariance Decomposition)
    # ==========================================================================
    # R2 = sum( beta_i * Cov(Xi, Y) ) / Var(Y)
    # Contribuição_i = beta_i * Cov(Xi, Y) / Var(Y)
    
    var_y = y.var()
    contributions = {}
    
    # Iterar sobre colunas (excluindo const)
    factors = ['excess_ret_ibov', 'ret_brent', 'ret_fx', 'delta_embi']
    
    total_explained = 0
    for factor in factors:
        beta = model_m4.params[factor]
        cov = df[factor].cov(y)
        contrib = (beta * cov) / var_y
        contributions[factor] = contrib
        total_explained += contrib
        
    # O resíduo é 1 - R2 (ou próximo disso, total_explained deve ser igual a R2)
    contributions['Residual'] = 1 - total_explained
    
    print("\nDecomposição de Variância (Contribuição para R2):")
    for k, v in contributions.items():
        print(f"{k}: {v:.4f}")
        
    # ==========================================================================
    # Salvar Resultados
    # ==========================================================================
    
    # Métricas para JSON
    metrics = {
        "M0_R2": r2_m0,
        "M4_R2": r2_m4,
        "M4_Adj_R2": adj_r2_m4,
        "Delta_R2": r2_m4 - r2_m0,
        "Coefficients": model_m4.params.to_dict(),
        "PValues": model_m4.pvalues.to_dict(),
        "TValues": model_m4.tvalues.to_dict(),
        "Variance_Decomposition": contributions
    }
    
    import json
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Métricas salvas em {metrics_path}")
    
    # Salvar dados usados (para plotagem se necessário)
    df.to_parquet(results_path)

if __name__ == "__main__":
    run_macro_model()
