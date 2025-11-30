"""
Figura: Distribuição de Retornos
================================

Gera histogramas dos retornos diários de PETR4 e IBOV.
Salva em data/outputs/figures/distribuicao_retornos.pdf
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.figsize': (10, 5),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def main():
    base_path = Path(__file__).resolve().parents[2]
    
    returns_path = base_path / "data" / "processed" / "returns.csv"
    output_path = base_path / "data" / "outputs" / "figures" / "distribuicao_retornos.pdf"
    
    df = pd.read_csv(returns_path, parse_dates=["date"])
    df = df.dropna(subset=["r_petr4", "r_ibov"])
    
    r_petr4 = df["r_petr4"].values * 100
    r_ibov = df["r_ibov"].values * 100
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    
    ax1 = axes[0]
    n_bins = 50
    counts, bins, _ = ax1.hist(r_petr4, bins=n_bins, density=True, alpha=0.7, 
                               color='steelblue', edgecolor='white', linewidth=0.5)
    
    mu, sigma = r_petr4.mean(), r_petr4.std()
    x = np.linspace(bins.min(), bins.max(), 100)
    ax1.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
             label=f'Normal($\\mu$={mu:.2f}%, $\\sigma$={sigma:.2f}%)')
    
    skew = stats.skew(r_petr4)
    kurt = stats.kurtosis(r_petr4)
    textstr = f'Assimetria: {skew:.2f}\nCurtose: {kurt:.2f}'
    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
    ax1.text(0.95, 0.95, textstr, transform=ax1.transAxes, fontsize=9,
             verticalalignment='top', horizontalalignment='right', bbox=props)
    
    ax1.set_xlabel('Retorno Diário (%)')
    ax1.set_ylabel('Densidade')
    ax1.set_title('PETR4')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    ax2 = axes[1]
    counts, bins, _ = ax2.hist(r_ibov, bins=n_bins, density=True, alpha=0.7, 
                               color='darkgreen', edgecolor='white', linewidth=0.5)
    
    mu, sigma = r_ibov.mean(), r_ibov.std()
    x = np.linspace(bins.min(), bins.max(), 100)
    ax2.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2,
             label=f'Normal($\\mu$={mu:.2f}%, $\\sigma$={sigma:.2f}%)')
    
    skew = stats.skew(r_ibov)
    kurt = stats.kurtosis(r_ibov)
    textstr = f'Assimetria: {skew:.2f}\nCurtose: {kurt:.2f}'
    ax2.text(0.95, 0.95, textstr, transform=ax2.transAxes, fontsize=9,
             verticalalignment='top', horizontalalignment='right', bbox=props)
    
    ax2.set_xlabel('Retorno Diário (%)')
    ax2.set_ylabel('Densidade')
    ax2.set_title('IBOVESPA')
    ax2.legend(loc='upper left', fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    
    print(f"✓ Figura salva em: {output_path}")

if __name__ == "__main__":
    main()
