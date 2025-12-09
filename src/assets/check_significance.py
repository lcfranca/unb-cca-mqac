import pandas as pd
import numpy as np
from scipy import stats
from src.core.config import PROJECT_ROOT

def run_significance_test():
    # Load equity curves
    curves_path = PROJECT_ROOT / "data" / "outputs" / "backtest_equity_curves.parquet"
    if not curves_path.exists():
        print("Equity curves file not found.")
        return

    df_curves = pd.read_parquet(curves_path)
    
    # Calculate daily returns from equity curves
    # Equity curve is cumulative product of (1+r). So r_t = E_t / E_{t-1} - 1
    df_returns = df_curves.pct_change().dropna()
    
    # Extract series
    if 'M5b_ML' not in df_returns.columns or 'Buy & Hold' not in df_returns.columns:
        print("Required columns not found.")
        return

    r_m5b = df_returns['M5b_ML']
    r_bh = df_returns['Buy & Hold']
    
    # 1. Paired T-Test (Daily Returns)
    # H0: Mean(r_m5b) = Mean(r_bh)
    t_stat, p_val = stats.ttest_rel(r_m5b, r_bh)
    
    print(f"Paired T-Test (Daily Returns): t={t_stat:.4f}, p={p_val:.4f}")
    
    # 2. Welch's T-Test (Independent samples assumption, unequal variance)
    t_stat_ind, p_val_ind = stats.ttest_ind(r_m5b, r_bh, equal_var=False)
    print(f"Welch's T-Test (Daily Returns): t={t_stat_ind:.4f}, p={p_val_ind:.4f}")
    
    # 3. Excess Return Analysis
    excess_ret = r_m5b - r_bh
    t_stat_excess, p_val_excess = stats.ttest_1samp(excess_ret, 0)
    print(f"One-Sample T-Test on Excess Returns (Alpha): t={t_stat_excess:.4f}, p={p_val_excess:.4f}")
    
    # Stats
    mean_excess = excess_ret.mean() * 252
    std_excess = excess_ret.std() * np.sqrt(252)
    ir = mean_excess / std_excess
    print(f"Annualized Excess Return: {mean_excess:.2%}")
    print(f"Tracking Error: {std_excess:.2%}")
    print(f"Information Ratio: {ir:.2f}")

if __name__ == "__main__":
    run_significance_test()
