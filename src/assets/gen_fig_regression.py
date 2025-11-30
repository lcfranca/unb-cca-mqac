"""
Figura: Regressão Beta
======================

Gera scatter plot dos retornos em excesso com linha de regressão.
Salva em data/outputs/figures/regressao_beta.pdf
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.figsize': (8, 6),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def main():
    base_path = Path(__file__).resolve().parents[2]
    
    returns_path = base_path / "data" / "processed" / "returns.csv"
    capm_path = base_path / "data" / "processed" / "capm_results.json"
    output_path = base_path / "data" / "outputs" / "figures" / "regressao_beta.pdf"
    
    df = pd.read_csv(returns_path, parse_dates=["date"])
    df = df.dropna(subset=["r_petr4_excess", "r_ibov_excess"])
    
    with open(capm_path, "r") as f:
        capm = json.load(f)
    
    X = df["r_ibov_excess"].values * 100
    y = df["r_petr4_excess"].values * 100
    
    beta = capm["beta"]
    alpha = capm["alpha_daily"] * 100
    r_squared = capm["r_squared"]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.scatter(X, y, alpha=0.3, s=15, c='steelblue', edgecolors='none')
    
    x_line = np.linspace(X.min(), X.max(), 100)
    y_line = alpha + beta * x_line
    ax.plot(x_line, y_line, 'r-', linewidth=2, 
            label=f'$r_{{PETR4}} - r_f = {alpha:.4f} + {beta:.2f}(r_m - r_f)$')
    
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    
    ax.set_xlabel('Retorno em Excesso do Mercado (%)')
    ax.set_ylabel('Retorno em Excesso de PETR4 (%)')
    ax.set_title('Estimação do Beta via Regressão Linear')
    
    textstr = f'$\\beta$ = {beta:.2f}\n$R^2$ = {r_squared:.2%}\nn = {capm["n_observations"]}'
    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=props)
    
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    
    print(f"✓ Figura salva em: {output_path}")

if __name__ == "__main__":
    main()
