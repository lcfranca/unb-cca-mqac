"""
Figura: Matriz de Correlação
============================

Gera heatmap de correlação entre PETR4 e IBOV.
Salva em data/outputs/figures/correlacao.pdf
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.figsize': (6, 5),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def main():
    base_path = Path(__file__).resolve().parents[2]
    
    returns_path = base_path / "data" / "processed" / "returns.csv"
    output_path = base_path / "data" / "outputs" / "figures" / "correlacao.pdf"
    
    df = pd.read_csv(returns_path, parse_dates=["date"])
    df = df.dropna(subset=["r_petr4", "r_ibov"])
    
    corr_data = df[["r_petr4", "r_ibov"]].copy()
    corr_data.columns = ["PETR4", "IBOVESPA"]
    
    corr_matrix = corr_data.corr()
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    
    sns.heatmap(corr_matrix, 
                annot=True, 
                fmt='.3f',
                cmap='RdYlBu_r',
                center=0,
                square=True,
                linewidths=0.5,
                cbar_kws={'shrink': 0.8, 'label': 'Correlação'},
                annot_kws={'size': 14, 'weight': 'bold'},
                ax=ax)
    
    ax.set_title('Matriz de Correlação — Retornos Diários')
    
    plt.tight_layout()
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    
    print(f"✓ Figura salva em: {output_path}")
    print(f"  Correlação PETR4 x IBOV: {corr_matrix.loc['PETR4', 'IBOVESPA']:.4f}")

if __name__ == "__main__":
    main()
