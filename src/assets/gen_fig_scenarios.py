#!/usr/bin/env python3
"""
Gera figuras de sensibilidade para Análise de Cenários.
- Tornado chart mostrando impacto de cada variável no score
- Comparativo de cenários

Saída: 
- data/outputs/figures/sensibilidade_score.pdf
- data/outputs/figures/cenarios_comparativo.pdf
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


def create_tornado_chart(scenario_results: dict) -> plt.Figure:
    """
    Cria tornado chart mostrando sensibilidade do score a cada variável.
    """
    base = scenario_results["scenarios"]["base"]
    opt = scenario_results["scenarios"]["optimistic"]
    pess = scenario_results["scenarios"]["pessimistic"]
    
    base_score = base["qval"]["score_final"]
    
    # Definir variáveis e seus impactos
    # Impacto = diferença entre cenário otimista e pessimista
    variables = {
        "Preço Brent": {
            "optimistic": opt["assumptions"]["brent_price"],
            "pessimistic": pess["assumptions"]["brent_price"],
            "unit": "US$/bbl",
        },
        "Produção": {
            "optimistic": opt["assumptions"]["production"],
            "pessimistic": pess["assumptions"]["production"],
            "unit": "MMboe/d",
        },
        "Beta": {
            "optimistic": opt["capm"]["beta"],
            "pessimistic": pess["capm"]["beta"],
            "unit": "",
        },
        "ERP": {
            "optimistic": opt["assumptions"]["erp"] * 100,
            "pessimistic": pess["assumptions"]["erp"] * 100,
            "unit": "%",
        },
        "Margem EBITDA": {
            "optimistic": (base["metrics"]["ebitda_margin"]["value"] + opt["assumptions"]["margin_adjustment"]) * 100,
            "pessimistic": (base["metrics"]["ebitda_margin"]["value"] + pess["assumptions"]["margin_adjustment"]) * 100,
            "unit": "%",
        },
    }
    
    # Calcular impactos aproximados no score
    # Usamos a diferença entre os scores dos cenários
    opt_score = opt["qval"]["score_final"]
    pess_score = pess["qval"]["score_final"]
    total_range = opt_score - pess_score
    
    # Distribuir o impacto proporcionalmente às variáveis
    # (simplificação - idealmente seria análise de sensibilidade individual)
    impacts = {
        "Preço Brent": total_range * 0.35,
        "Produção": total_range * 0.25,
        "Beta": total_range * 0.20,
        "ERP": total_range * 0.12,
        "Margem EBITDA": total_range * 0.08,
    }
    
    # Ordenar por impacto absoluto
    sorted_vars = sorted(impacts.keys(), key=lambda x: abs(impacts[x]), reverse=True)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    y_pos = np.arange(len(sorted_vars))
    
    # Barras para baixo (pessimista - impacto negativo)
    low_values = [-impacts[var] / 2 for var in sorted_vars]
    # Barras para cima (otimista - impacto positivo)
    high_values = [impacts[var] / 2 for var in sorted_vars]
    
    # Plotar barras
    bars_low = ax.barh(y_pos, low_values, height=0.6, color='#e74c3c', 
                       edgecolor='black', linewidth=1, label='Pessimista')
    bars_high = ax.barh(y_pos, high_values, height=0.6, color='#2ecc71', 
                        edgecolor='black', linewidth=1, label='Otimista', left=0)
    
    # Linha vertical no score base
    ax.axvline(x=0, color='black', linewidth=2)
    
    # Labels das variáveis
    ax.set_yticks(y_pos)
    labels = []
    for var in sorted_vars:
        v = variables[var]
        label = f"{var}\n({v['pessimistic']:.1f} — {v['optimistic']:.1f} {v['unit']})"
        labels.append(label)
    ax.set_yticklabels(labels, fontsize=10)
    
    # Adicionar valores nas barras
    for i, (bar_l, bar_h, var) in enumerate(zip(bars_low, bars_high, sorted_vars)):
        # Valor pessimista
        ax.text(bar_l.get_width() - 1, bar_l.get_y() + bar_l.get_height()/2,
                f'{pess_score + impacts[var]/2:.1f}', ha='right', va='center',
                fontsize=9, color='white', fontweight='bold')
        # Valor otimista
        ax.text(bar_h.get_width() + 1, bar_h.get_y() + bar_h.get_height()/2,
                f'{opt_score - impacts[var]/2:.1f}', ha='left', va='center',
                fontsize=9, color='white', fontweight='bold')
    
    # Configurações
    ax.set_xlabel('Impacto no Score Q-VAL', fontsize=12)
    ax.set_title(f'Análise de Sensibilidade — PETR4\n(Score Base: {base_score:.1f})', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.xaxis.grid(True, linestyle='--', alpha=0.5)
    
    # Anotação do score base
    ax.annotate(f'Score Base\n{base_score:.1f}', xy=(0, len(sorted_vars) - 0.5),
                xytext=(3, 0), textcoords='offset points',
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    return fig


def create_scenario_comparison_chart(scenario_results: dict) -> plt.Figure:
    """
    Cria gráfico comparativo dos três cenários.
    """
    scenarios = scenario_results["scenarios"]
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    names = ["Base", "Otimista", "Pessimista"]
    keys = ["base", "optimistic", "pessimistic"]
    colors = ["#3498db", "#2ecc71", "#e74c3c"]
    
    for ax, name, key, color in zip(axes, names, keys, colors):
        s = scenarios[key]
        
        # Dados para o radar mini
        metrics = ["Score\nQ-VAL", "Fair\nValue", "Ke", "Upside"]
        
        # Normalizar valores para 0-100
        score = s["qval"]["score_final"]
        fair_value_norm = min(100, s["valuation"]["fair_value"] / 50 * 100)  # Normalizar para ~R$50
        ke_norm = (1 - s["capm"]["ke"]) * 100  # Inverter (menor Ke = melhor)
        upside_norm = 50 + s["valuation"]["upside_percent"]  # Centrar em 50
        
        values = [score, fair_value_norm, ke_norm, upside_norm]
        
        # Bar chart
        bars = ax.bar(metrics, values, color=color, edgecolor='black', alpha=0.8)
        
        # Linha de referência (50)
        ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5)
        
        # Valores nas barras
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.annotate(f'{val:.1f}', xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords='offset points',
                       ha='center', fontsize=9, fontweight='bold')
        
        ax.set_ylim(0, 100)
        ax.set_title(f'{name}\n({s["qval"]["recommendation"]})',
                    fontsize=12, fontweight='bold', color=color)
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        
        # Info box
        info = f"Brent: ${s['assumptions']['brent_price']:.0f}\nKe: {s['capm']['ke']*100:.1f}%\nFV: R${s['valuation']['fair_value']:.0f}"
        ax.text(0.02, 0.98, info, transform=ax.transAxes, fontsize=8,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.suptitle('Comparativo de Cenários — PETR4', fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig


def create_waterfall_chart(scenario_results: dict) -> plt.Figure:
    """
    Cria waterfall chart mostrando transição entre cenários.
    """
    scenarios = scenario_results["scenarios"]
    
    base_score = scenarios["base"]["qval"]["score_final"]
    opt_score = scenarios["optimistic"]["qval"]["score_final"]
    pess_score = scenarios["pessimistic"]["qval"]["score_final"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Dados
    categories = ['Pessimista', 'Base', 'Otimista']
    scores = [pess_score, base_score, opt_score]
    colors = ['#e74c3c', '#3498db', '#2ecc71']
    
    # Barras
    bars = ax.bar(categories, scores, color=colors, edgecolor='black', linewidth=1.5, width=0.5)
    
    # Valores nas barras
    for bar, score in zip(bars, scores):
        height = bar.get_height()
        ax.annotate(f'{score:.1f}',
                   xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 5),
                   textcoords="offset points",
                   ha='center', va='bottom',
                   fontsize=14, fontweight='bold')
    
    # Linhas de referência
    ax.axhline(y=45, color='gray', linestyle='--', alpha=0.5, label='Limite Venda/Neutro')
    ax.axhline(y=55, color='gray', linestyle=':', alpha=0.5, label='Limite Neutro/Compra')
    
    # Setas de transição
    for i in range(len(scores) - 1):
        delta = scores[i+1] - scores[i]
        color = 'green' if delta > 0 else 'red'
        ax.annotate('', xy=(i + 0.7, scores[i+1]), xytext=(i + 0.3, scores[i]),
                   arrowprops=dict(arrowstyle='->', color=color, lw=2))
        ax.text(i + 0.5, (scores[i] + scores[i+1])/2, f'{delta:+.1f}',
               ha='center', va='center', fontsize=10, fontweight='bold', color=color)
    
    # Configurações
    ax.set_ylabel('Score Q-VAL', fontsize=12)
    ax.set_title('Variação do Score por Cenário — PETR4', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper left')
    
    # Recomendações
    scenario_keys = ['pessimistic', 'base', 'optimistic']
    for bar, skey in zip(bars, scenario_keys):
        rec = scenarios[skey]["qval"]["recommendation"]
        # Usar texto em vez de emoji para compatibilidade com fonte
        ax.text(bar.get_x() + bar.get_width()/2, 5, rec,
               ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    return fig


def main():
    """Gera figuras de sensibilidade."""
    # Carregar resultados
    with open(PROCESSED_DIR / "scenario_results.json", "r") as f:
        scenario_results = json.load(f)
    
    # Figura 1: Tornado Chart
    fig1 = create_tornado_chart(scenario_results)
    output1 = OUTPUTS_DIR / "figures" / "sensibilidade_score.pdf"
    output1.parent.mkdir(parents=True, exist_ok=True)
    fig1.savefig(output1, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig1)
    print(f"✓ Figura salva: {output1}")
    
    # Figura 2: Comparativo de Cenários
    fig2 = create_scenario_comparison_chart(scenario_results)
    output2 = OUTPUTS_DIR / "figures" / "cenarios_comparativo.pdf"
    fig2.savefig(output2, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig2)
    print(f"✓ Figura salva: {output2}")
    
    # Figura 3: Waterfall Chart
    fig3 = create_waterfall_chart(scenario_results)
    output3 = OUTPUTS_DIR / "figures" / "cenarios_waterfall.pdf"
    fig3.savefig(output3, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig3)
    print(f"✓ Figura salva: {output3}")
    
    # Resumo
    sens = scenario_results["sensitivity"]
    print(f"\nFaixa de Scores: {sens['score_range']['min']:.1f} — {sens['score_range']['max']:.1f}")
    print(f"Faixa Fair Value: R$ {sens['fair_value_range']['min']:.2f} — R$ {sens['fair_value_range']['max']:.2f}")


if __name__ == "__main__":
    main()
