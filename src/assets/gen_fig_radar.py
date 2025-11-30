#!/usr/bin/env python3
"""
Gera figura de Radar Chart para o Score Q-VAL.
Visualiza as três dimensões: Valor, Qualidade, Risco.

Saída: data/outputs/figures/radar_score.pdf
"""

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Configuração de caminhos
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import get_paths

# Obter caminhos
paths = get_paths()
PROCESSED_DATA_DIR = paths.data_processed
OUTPUTS_DIR = paths.root / "data" / "outputs"

# Configurar matplotlib
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'legend.fontsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})


def create_radar_chart(categories: list, values: list, title: str = "") -> plt.Figure:
    """
    Cria um radar chart com as dimensões do Q-VAL.
    
    Args:
        categories: Lista de nomes das dimensões
        values: Lista de valores (Z-scores normalizados para 0-100)
        title: Título do gráfico
    
    Returns:
        Figure matplotlib
    """
    # Número de variáveis
    N = len(categories)
    
    # Ângulos para cada eixo
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Fechar o polígono
    
    # Valores (adicionar primeiro valor no final para fechar)
    values_plot = values + values[:1]
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Configurar eixos
    ax.set_theta_offset(np.pi / 2)  # Começar do topo
    ax.set_theta_direction(-1)  # Sentido horário
    
    # Labels dos eixos
    plt.xticks(angles[:-1], categories, size=12, fontweight='bold')
    
    # Limites do eixo radial (0 a 100)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80])
    ax.set_yticklabels(['20', '40', '60', '80'], size=9, color='gray')
    
    # Linhas de grade
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.xaxis.grid(True, linestyle='-', alpha=0.3)
    
    # Área de referência (score neutro = 50)
    neutral_values = [50] * (N + 1)
    ax.plot(angles, neutral_values, 'k--', linewidth=1, alpha=0.3, label='Neutro (50)')
    ax.fill(angles, neutral_values, alpha=0.1, color='gray')
    
    # Plotar dados
    ax.plot(angles, values_plot, 'o-', linewidth=2.5, color='#1f77b4', markersize=10)
    ax.fill(angles, values_plot, alpha=0.25, color='#1f77b4')
    
    # Adicionar valores nos pontos
    for angle, value, cat in zip(angles[:-1], values, categories):
        # Ajustar posição do texto
        ha = 'center'
        va = 'bottom' if value > 50 else 'top'
        offset = 8 if value > 50 else -8
        
        ax.annotate(
            f'{value:.0f}',
            xy=(angle, value),
            xytext=(0, offset),
            textcoords='offset points',
            ha=ha,
            va=va,
            fontsize=11,
            fontweight='bold',
            color='#1f77b4'
        )
    
    # Título
    if title:
        plt.title(title, size=14, fontweight='bold', y=1.08)
    
    plt.tight_layout()
    return fig


def main():
    """Gera o radar chart do Q-VAL."""
    # Carregar resultados
    with open(PROCESSED_DATA_DIR / "qval_results.json", "r") as f:
        results = json.load(f)
    
    # Extrair Z-scores das dimensões
    z_valor = results["z_valor"]
    z_qualidade = results["z_qualidade"]
    z_risco = results["z_risco"]
    
    # Converter Z-scores para escala 0-100 (mesmo método do score final)
    # Score = 50 + 10 * Z, limitado a 0-100
    def z_to_scale(z):
        return max(0, min(100, 50 + 10 * z))
    
    categories = ['Valor', 'Qualidade', 'Risco']
    values = [
        z_to_scale(z_valor),
        z_to_scale(z_qualidade),
        z_to_scale(z_risco)
    ]
    
    # Criar radar chart
    fig = create_radar_chart(
        categories=categories,
        values=values,
        title=f"Score Q-VAL por Dimensão — PETR4\n(Score Final: {results['score_final']:.1f}/100)"
    )
    
    # Salvar figura
    output_path = OUTPUTS_DIR / "figures" / "radar_score.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"✓ Radar chart salvo: {output_path}")
    print(f"\nDimensões (escala 0-100):")
    print(f"  Valor:     {values[0]:.1f} (Z={z_valor:+.2f})")
    print(f"  Qualidade: {values[1]:.1f} (Z={z_qualidade:+.2f})")
    print(f"  Risco:     {values[2]:.1f} (Z={z_risco:+.2f})")


if __name__ == "__main__":
    main()
