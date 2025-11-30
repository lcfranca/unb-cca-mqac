"""
Análise CAPM — Estimação de Beta e Alfa
=======================================

Executa regressão OLS dos retornos em excesso de PETR4 sobre IBOV.
Salva resultados em data/processed/capm_results.json
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

def main():
    base_path = Path(__file__).resolve().parents[2]
    
    returns_path = base_path / "data" / "processed" / "returns.csv"
    output_path = base_path / "data" / "processed" / "capm_results.json"
    
    df = pd.read_csv(returns_path, parse_dates=["date"])
    
    df = df.dropna(subset=["r_petr4_excess", "r_ibov_excess"])
    
    X = df["r_ibov_excess"].values
    y = df["r_petr4_excess"].values
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
    
    n = len(X)
    r_squared = r_value ** 2
    adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - 2)
    
    rf_mean = df["rf"].mean()
    rm_mean = df["r_ibov"].mean()
    r_petr4_mean = df["r_petr4"].mean()
    
    rf_annual = (1 + rf_mean) ** 252 - 1
    rm_annual = (1 + rm_mean) ** 252 - 1
    r_petr4_annual = (1 + r_petr4_mean) ** 252 - 1
    
    market_premium = rm_annual - rf_annual
    ke_capm = rf_annual + slope * market_premium
    
    alpha_annual = (1 + intercept) ** 252 - 1
    
    residuals = y - (intercept + slope * X)
    idiosyncratic_vol = np.std(residuals) * np.sqrt(252)
    
    results = {
        "beta": round(slope, 4),
        "alpha_daily": round(intercept, 6),
        "alpha_annual": round(alpha_annual, 4),
        "r_squared": round(r_squared, 4),
        "adj_r_squared": round(adj_r_squared, 4),
        "std_err_beta": round(std_err, 4),
        "p_value_beta": round(p_value, 6),
        "n_observations": n,
        "rf_annual": round(rf_annual, 4),
        "rm_annual": round(rm_annual, 4),
        "r_petr4_annual": round(r_petr4_annual, 4),
        "market_premium": round(market_premium, 4),
        "ke_capm": round(ke_capm, 4),
        "idiosyncratic_volatility": round(idiosyncratic_vol, 4),
        "period_start": df["date"].min().strftime("%Y-%m-%d"),
        "period_end": df["date"].max().strftime("%Y-%m-%d")
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Análise CAPM salva em: {output_path}")
    print(f"  Beta: {results['beta']}")
    print(f"  Alfa (anual): {results['alpha_annual']:.2%}")
    print(f"  R²: {results['r_squared']:.2%}")
    print(f"  Ke (CAPM): {results['ke_capm']:.2%}")

if __name__ == "__main__":
    main()
