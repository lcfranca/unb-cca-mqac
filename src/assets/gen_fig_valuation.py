#!/usr/bin/env python3
"""
Gera figura comparando ICC vs Ke (CAPM).
Visualiza o diagnóstico de mispricing.

Saída: data/outputs/figures/icc_vs_capm.pdf
"""

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

# Configuração de caminhos
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import get_paths

paths = get_paths()
PROCESSED_DIR = paths.data_processed
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


def create_icc_vs_capm_chart(valuation: dict) -> plt.Figure:
    """
    Cria gráfico de barras comparando ICC e Ke.
    """
    diagnosis = valuation["mispricing_diagnosis"]
    icc_data = valuation["implied_cost_of_capital"]
    gordon = valuation["gordon_model"]
    
    # Dados para o gráfico
    categories = ['Ke (CAPM)', 'ICC\n(Gordon)', 'ICC\n(Earn. Yield)', 'ICC\n(Ponderado)']
    values = [
        diagnosis["ke_capm"] * 100,
        icc_data["icc_gordon"] * 100,
        icc_data["icc_earnings_yield"] * 100,
        icc_data["icc_weighted"] * 100,
    ]
    
    # Cores
    colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.2)
    
    # Adicionar valores nas barras
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(f'{val:.2f}%',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 5),
                   textcoords="offset points",
                   ha='center', va='bottom',
                   fontsize=12, fontweight='bold')
    
    # Linha de referência do Ke
    ke = diagnosis["ke_capm"] * 100
    ax.axhline(y=ke, color='#2ecc71', linestyle='--', linewidth=2, alpha=0.7, label=f'Ke CAPM = {ke:.2f}%')
    
    # Área de mispricing
    spread = diagnosis["spread"] * 100
    if spread > 0:
        ax.fill_between([2.5, 3.5], ke, values[3], alpha=0.3, color='green', label=f'Subprecificado (+{spread:.2f}%)')
    else:
        ax.fill_between([2.5, 3.5], values[3], ke, alpha=0.3, color='red', label=f'Sobreprecificado ({spread:.2f}%)')
    
    # Configurações do eixo
    ax.set_ylabel('Taxa de Retorno (%)', fontsize=12)
    ax.set_title('Custo de Capital Implícito (ICC) vs. CAPM — PETR4', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(values) * 1.2)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    
    # Legenda
    ax.legend(loc='upper right', framealpha=0.9)
    
    # Anotação do diagnóstico
    classification = diagnosis["classification"]
    signal = diagnosis["icc_signal"]
    ax.text(0.02, 0.98, f'Diagnóstico: {classification}\nSinal: {signal}',
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    return fig


def create_valuation_summary_chart(valuation: dict) -> plt.Figure:
    """
    Cria gráfico resumo de valuation (Fair Value vs Current Price).
    """
    gordon = valuation["gordon_model"]
    diagnosis = valuation["mispricing_diagnosis"]
    
    current_price = gordon["current_price"]
    fair_value = gordon["fair_value"]
    upside = gordon["upside_percent"]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Barras
    categories = ['Preço Atual', 'Valor Justo\n(Gordon DDM)']
    values = [current_price, fair_value]
    colors = ['#3498db', '#2ecc71' if upside > 0 else '#e74c3c']
    
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.2, width=0.5)
    
    # Valores nas barras
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(f'R$ {val:.2f}',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 5),
                   textcoords="offset points",
                   ha='center', va='bottom',
                   fontsize=14, fontweight='bold')
    
    # Seta de upside/downside
    mid_x = 0.5
    ax.annotate('',
               xy=(1, fair_value),
               xytext=(0, current_price),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    
    # Texto de upside
    mid_y = (current_price + fair_value) / 2
    color = 'green' if upside > 0 else 'red'
    ax.text(0.5, mid_y, f'{upside:+.1f}%', ha='center', va='center',
            fontsize=16, fontweight='bold', color=color,
            bbox=dict(boxstyle='round', facecolor='white', edgecolor=color, alpha=0.9))
    
    # Configurações
    ax.set_ylabel('Preço (R$)', fontsize=12)
    ax.set_title('Valuation por Gordon DDM — PETR4', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(values) * 1.3)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    
    # Anotação
    recommendation = diagnosis["final_recommendation"]
    emoji_text = "COMPRA" if "Compra" in recommendation else ("VENDA" if "Venda" in recommendation else "NEUTRO")
    ax.text(0.98, 0.98, f'Recomendação: {emoji_text}',
            transform=ax.transAxes, fontsize=12, verticalalignment='top', ha='right',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    
    plt.tight_layout()
    return fig


def main():
    """Gera figuras de valuation."""
    # Carregar resultados
    with open(PROCESSED_DIR / "valuation_results.json", "r") as f:
        valuation = json.load(f)
    
    # Figura 1: ICC vs CAPM
    fig1 = create_icc_vs_capm_chart(valuation)
    output1 = OUTPUTS_DIR / "figures" / "icc_vs_capm.pdf"
    output1.parent.mkdir(parents=True, exist_ok=True)
    fig1.savefig(output1, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig1)
    print(f"✓ Figura salva: {output1}")
    
    # Figura 2: Valuation Summary
    fig2 = create_valuation_summary_chart(valuation)
    output2 = OUTPUTS_DIR / "figures" / "valuation_summary.pdf"
    fig2.savefig(output2, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig2)
    print(f"✓ Figura salva: {output2}")
    
    # Resumo
    diagnosis = valuation["mispricing_diagnosis"]
    gordon = valuation["gordon_model"]
    print(f"\nResumo:")
    print(f"  ICC: {diagnosis['icc']*100:.2f}%")
    print(f"  Ke:  {diagnosis['ke_capm']*100:.2f}%")
    print(f"  Spread: {diagnosis['spread']*100:+.2f}%")
    print(f"  Fair Value: R$ {gordon['fair_value']:.2f}")
    print(f"  Upside: {gordon['upside_percent']:+.1f}%")


if __name__ == "__main__":
    main()
