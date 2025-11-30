"""
Figura: Security Market Line (SML)
==================================

Gera gráfico da Linha de Mercado de Títulos com posição de PETR4.
Salva em data/outputs/figures/sml_capm.pdf
"""

import json
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
    
    capm_path = base_path / "data" / "processed" / "capm_results.json"
    output_path = base_path / "data" / "outputs" / "figures" / "sml_capm.pdf"
    
    with open(capm_path, "r") as f:
        capm = json.load(f)
    
    rf = capm["rf_annual"] * 100
    rm = capm["rm_annual"] * 100
    beta_petr4 = capm["beta"]
    r_petr4 = capm["r_petr4_annual"] * 100
    ke_capm = capm["ke_capm"] * 100
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    betas = np.linspace(0, 2.0, 100)
    sml = rf + betas * (rm - rf)
    ax.plot(betas, sml, 'b-', linewidth=2, label='Security Market Line (SML)')
    
    ax.scatter([0], [rf], color='green', s=100, zorder=5, marker='s', label=f'Rf = {rf:.1f}%')
    ax.scatter([1], [rm], color='blue', s=100, zorder=5, marker='^', label=f'Mercado (β=1) = {rm:.1f}%')
    
    ax.scatter([beta_petr4], [r_petr4], color='red', s=150, zorder=5, marker='o', 
               label=f'PETR4 Realizado = {r_petr4:.1f}%')
    ax.scatter([beta_petr4], [ke_capm], color='orange', s=100, zorder=5, marker='D',
               label=f'PETR4 Esperado (CAPM) = {ke_capm:.1f}%')
    
    if r_petr4 > ke_capm:
        ax.annotate('', xy=(beta_petr4, r_petr4), xytext=(beta_petr4, ke_capm),
                    arrowprops=dict(arrowstyle='->', color='green', lw=2))
        ax.text(beta_petr4 + 0.05, (r_petr4 + ke_capm) / 2, 
                f'α = {r_petr4 - ke_capm:.1f}%', fontsize=9, color='green')
    else:
        ax.annotate('', xy=(beta_petr4, r_petr4), xytext=(beta_petr4, ke_capm),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2))
        ax.text(beta_petr4 + 0.05, (r_petr4 + ke_capm) / 2, 
                f'α = {r_petr4 - ke_capm:.1f}%', fontsize=9, color='red')
    
    ax.axhline(y=rf, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
    ax.axvline(x=1, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
    
    ax.set_xlabel('Beta (Risco Sistemático)')
    ax.set_ylabel('Retorno Esperado (% a.a.)')
    ax.set_title('Linha de Mercado de Títulos (SML) — CAPM')
    
    ax.set_xlim(-0.1, 2.1)
    y_min = min(rf - 2, r_petr4 - 2)
    y_max = max(rm + 5, r_petr4 + 5)
    ax.set_ylim(y_min, y_max)
    
    ax.legend(loc='upper left', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    
    print(f"✓ Figura salva em: {output_path}")

if __name__ == "__main__":
    main()
