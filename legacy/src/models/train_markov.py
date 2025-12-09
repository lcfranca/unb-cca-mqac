import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

# Config
DATA_PATH = PROJECT_ROOT / "data/processed/ml_dataset.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data/outputs/models"
FIGURES_DIR = PROJECT_ROOT / "data/outputs/figures"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

set_style()

def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    
    df = pd.read_parquet(DATA_PATH)
    if 'date' in df.columns:
        df = df.set_index('date')
    df = df.sort_index()
    return df

def train_markov_model():
    print("🚀 Iniciando Treinamento Markov Switching Model...")
    
    df = load_data()
    
    # We want to model the regimes of PETR4 returns
    # Using 'ret_petr4' (Daily Returns)
    # Drop NaNs
    series = df['ret_petr4'].dropna() * 100 # Scale to percentage for numerical stability
    
    print(f"   Série Temporal: {len(series)} observações")
    
    # Specification: 2 Regimes, Switching Mean and Switching Variance
    # regime 0: Low Volatility / Bull?
    # regime 1: High Volatility / Bear?
    
    print("   Ajustando Modelo (2 Regimes, Switching Variance)...")
    # MarkovRegression(endog, k_regimes, trend='c', switching_variance=True)
    # trend='c' means a constant (intercept) is estimated for each regime (switching mean)
    # switching_variance=True means variance is estimated for each regime
    model = MarkovRegression(series, k_regimes=2, trend='c', switching_variance=True)
    res = model.fit()
    
    print(res.summary())
    
    # Extract Probabilities
    # smoothed_marginal_probabilities: Prob of being in regime i at time t given all data
    probs = res.smoothed_marginal_probabilities
    
    # Align with original index
    probs.index = series.index
    
    # Identify which regime is "High Volatility"
    # We look at the estimated variance parameters (sigma2)
    print("\n   Parâmetros do Modelo:")
    print(res.params)
    
    # The params usually have names like 'sigma2[0]', 'sigma2[1]'
    sigma2_0 = res.params['sigma2[0]']
    sigma2_1 = res.params['sigma2[1]']
    
    if sigma2_1 > sigma2_0:
        high_vol_regime = 1
        low_vol_regime = 0
        print(f"   Regime 1 é Alta Volatilidade (Var: {sigma2_1:.4f})")
    else:
        high_vol_regime = 0
        low_vol_regime = 1
        print(f"   Regime 0 é Alta Volatilidade (Var: {sigma2_0:.4f})")
        
    # Create a DataFrame for plotting
    df_regime = pd.DataFrame({
        'return': series,
        'prob_high_vol': probs[high_vol_regime],
        'prob_low_vol': probs[low_vol_regime]
    })
    
    # Save Probabilities
    df_regime.to_csv(OUTPUT_DIR / "markov_regime_probs.csv")
    print(f"   Probabilidades salvas em: {OUTPUT_DIR / 'markov_regime_probs.csv'}")
    
    # Plotting
    print("   Gerando Gráficos de Regime...")
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [1.5, 1]})
    
    # Plot 1: Returns colored by Regime
    axes[0].plot(df_regime.index, df_regime['return'], color='black', lw=0.5, alpha=0.6, label='Retorno Diário')
    axes[0].set_title('Retornos Diários PETR4 (%) e Regimes de Volatilidade (Markov Switching)', fontweight='bold')
    axes[0].set_ylabel('Retorno (%)')
    
    # Shade High Volatility periods (Prob > 0.5)
    # We create a boolean mask
    is_high_vol = df_regime['prob_high_vol'] > 0.5
    
    # Use fill_between to shade regions
    # We need to handle the x-axis (dates) correctly for fill_between with conditions
    # A simple way is to fill the whole area with alpha proportional to probability, but that can be messy.
    # Let's stick to the second subplot for probability.
    
    # Plot 2: Probability of Crisis Regime
    axes[1].plot(df_regime.index, df_regime['prob_high_vol'], color=COLORS['negative'], lw=1.5, label='Prob. Alta Volatilidade')
    axes[1].fill_between(df_regime.index, 0, df_regime['prob_high_vol'], color=COLORS['negative'], alpha=0.3)
    
    axes[1].set_title('Probabilidade de Regime de Crise (Alta Volatilidade)', fontweight='bold')
    axes[1].set_ylabel('Probabilidade')
    axes[1].set_ylim(0, 1.05)
    axes[1].axhline(0.5, color='gray', linestyle='--', lw=1)
    
    # Add some annotations for major crises if possible (e.g. COVID)
    covid_start = pd.to_datetime('2020-02-20')
    if covid_start in df_regime.index:
        axes[1].annotate('COVID-19', xy=(covid_start, 0.9), xytext=(covid_start, 1.1),
                         arrowprops=dict(facecolor='black', shrink=0.05), ha='center')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "markov_regimes.pdf")
    print(f"   Gráfico salvo em: {FIGURES_DIR / 'markov_regimes.pdf'}")
    
    # Save model summary
    with open(OUTPUT_DIR / "markov_summary.txt", "w") as f:
        f.write(res.summary().as_text())

if __name__ == "__main__":
    train_markov_model()
