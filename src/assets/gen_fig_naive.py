"""
Gera gráfico de Erro Quadrático Acumulado (Cumulative Squared Error - CSE).
Estado da arte em visualização: Seaborn + Style Customizado + Shading.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
from src.core.config import PROJECT_ROOT
import src.core.style as style

def run():
    # Configurar estilo
    style.set_style()
    
    # Caminhos
    input_path = PROJECT_ROOT / "data" / "outputs" / "naive_errors.parquet"
    output_path = PROJECT_ROOT / "data" / "outputs" / "figures" / "cse_comparison.pdf"
    
    # Carregar dados
    df = pd.read_parquet(input_path)
    
    # Calcular diferença de CSE (HM - CAPM)
    # Se > 0, HM tem erro maior que CAPM -> CAPM é melhor
    delta_se = df['se_hm'] - df['se_capm']
    cum_delta_se = delta_se.cumsum()
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plotar linha principal
    ax.plot(df['date'], cum_delta_se, color=style.COLORS['primary'], linewidth=2, label=r'$\Delta$ CSE (HM - CAPM)')
    
    # Adicionar linha zero
    ax.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.8)
    
    # Preencher áreas (Verde se > 0 [CAPM ganha], Vermelho se < 0 [HM ganha])
    ax.fill_between(df['date'], cum_delta_se, 0, where=(cum_delta_se >= 0), 
                    color=style.COLORS['positive'], alpha=0.1, interpolate=True, label='CAPM Supera HM')
    ax.fill_between(df['date'], cum_delta_se, 0, where=(cum_delta_se < 0), 
                    color=style.COLORS['negative'], alpha=0.1, interpolate=True, label='HM Supera CAPM')
    
    # Formatação de Eixos
    ax.set_ylabel(r'Diferença de Erro Quadrático Acumulado ($\sum \Delta e^2$)', fontsize=12)
    ax.set_xlabel('Data', fontsize=12)
    ax.set_title('Performance Preditiva Relativa: CAPM vs. Média Histórica', fontsize=14, fontweight='bold', pad=15)
    
    # Formatar datas no eixo X
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Grid e Legenda
    ax.grid(True, which='major', linestyle='--', alpha=0.6)
    ax.legend(loc='upper left', frameon=True, framealpha=0.9, edgecolor='gray')
    
    # Anotação final (State of the Art: Box Annotation)
    last_date = df['date'].iloc[-1]
    last_val = cum_delta_se.iloc[-1]
    
    if last_val > 0:
        title = "CAPM Vence"
        msg = f"Erro Reduzido:\n{last_val:.2f} pts"
        color = style.COLORS['positive']
        y_offset = 40
    else:
        title = "HM Vence"
        msg = f"Erro Aumentado:\n{last_val:.2f} pts"
        color = style.COLORS['negative']
        y_offset = -40
        
    # Caixa de texto estilizada
    bbox_props = dict(boxstyle="round,pad=0.5", fc="white", ec=color, lw=2, alpha=0.9)
    
    ax.annotate(f"{title}\n{msg}", 
                xy=(last_date, last_val), 
                xytext=(0, y_offset), textcoords='offset points',
                ha='center', va='center',
                color=color, fontweight='bold', fontsize=10,
                bbox=bbox_props,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.5))

    # Título e Subtítulo
    ax.set_title('Performance Preditiva Relativa: CAPM vs. Média Histórica', fontsize=16, fontweight='bold', pad=25)
    ax.text(0.5, 1.02, 'Acumulado da Diferença de Erros Quadráticos (CSE)', 
            transform=ax.transAxes, ha='center', fontsize=12, color='gray')

    # Ajustar layout
    plt.tight_layout()
    
    # Salvar
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figura salva em {output_path}")
    plt.close()

if __name__ == "__main__":
    run()
