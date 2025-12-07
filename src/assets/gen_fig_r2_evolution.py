"""
Gera gráfico de evolução do R2 Out-of-Sample para os modelos M0-M5.
Versão aprimorada (State of the Art).
"""
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

def run():
    # Configuração de Estilo Profissional
    set_style()
    
    input_path = PROJECT_ROOT / "data" / "outputs" / "full_model_comparison.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "figures" / "r2_evolution.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(input_path, 'r') as f:
        data = json.load(f)
        
    # Preparar DataFrame
    models = []
    r2_oos = []
    r2_adj = []
    
    # Ordem correta
    order_keys = ["M0 (CAPM)", "M1 (CAPM + Value)", "M2 (CAPM + Quality)", "M3 (CAPM + Q-VAL)", "M4 (Macro)", "M5 (Fatores)"]
    
    for k in order_keys:
        if k in data:
            v = data[k]
            short_name = k.split(' ')[0] # M0, M1, etc
            models.append(short_name)
            r2_oos.append(v['R2_OOS'] * 100)
            r2_adj.append(v['R2_Adj'] * 100)
        
    df = pd.DataFrame({
        'Modelo': models,
        'R2 OOS (%)': r2_oos,
        'R2 Adj In-Sample (%)': r2_adj
    })
    
    # Plot
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Bar plot para OOS (Eixo Esquerdo)
    # Usando uma paleta sequencial para dar ideia de evolução, mas destacando M4/M5
    colors = sns.color_palette("Blues", n_colors=len(df))
    bars = sns.barplot(data=df, x='Modelo', y='R2 OOS (%)', ax=ax1, palette=colors, alpha=0.9)
    
    # Line plot para In-Sample (Eixo Direito)
    ax2 = ax1.twinx()
    line = sns.lineplot(data=df, x='Modelo', y='R2 Adj In-Sample (%)', ax=ax2, color=COLORS['secondary'], marker='o', markersize=8, lw=2.5)
    
    # Labels e Títulos
    ax1.set_ylabel('R² Out-of-Sample (%)', color=COLORS['primary'], fontweight='bold', labelpad=10)
    ax2.set_ylabel('R² Ajustado In-Sample (%)', color=COLORS['secondary'], fontweight='bold', labelpad=10)
    ax1.set_xlabel('Estratégia de Modelagem', fontweight='bold', labelpad=10)
    
    plt.title('Evolução da Eficiência Informacional: M0 a M5', pad=20, fontweight='bold')
    
    # Ajuste de limites para estética
    ax1.set_ylim(0, max(r2_oos) * 1.2)
    ax2.set_ylim(min(r2_adj) * 0.99, max(r2_adj) * 1.01)
    
    # Anotações nas Barras (OOS)
    for i, v in enumerate(df['R2 OOS (%)']):
        ax1.text(i, v + 0.5, f"{v:.1f}%", ha='center', va='bottom', color=COLORS['text'], fontweight='bold', fontsize=10)
        
        # Seta de crescimento (State of the Art)
        if i > 0:
            prev = df['R2 OOS (%)'][i-1]
            if v > prev:
                growth = v - prev
                # Pequena seta verde indicando ganho marginal
                ax1.annotate(f"+{growth:.1f}pp", 
                             xy=(i, v), xytext=(i, v + 3),
                             ha='center', fontsize=8, color=COLORS['positive'], fontweight='bold',
                             arrowprops=dict(arrowstyle='->', color=COLORS['positive'], lw=1, shrinkA=0, shrinkB=5))

    # Legenda Unificada e Limpa
    # Criar handles manuais para garantir unicidade
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    
    legend_elements = [
        Patch(facecolor=colors[-2], edgecolor='none', label='R² OOS (Teste)'),
        Line2D([0], [0], color=COLORS['secondary'], lw=2.5, marker='o', label='R² Adj (Treino)')
    ]
    
    # Posicionar legenda dentro do gráfico, canto superior esquerdo (onde geralmente há espaço nas barras menores)
    ax1.legend(handles=legend_elements, loc='upper left', frameon=True, framealpha=0.9, facecolor='white', edgecolor='#cccccc')
    
    # Grid apenas no eixo Y principal
    ax1.grid(True, axis='y', linestyle='--', alpha=0.4)
    ax2.grid(False) # Desligar grid do eixo secundário para não poluir
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Gráfico salvo em {output_path}")

if __name__ == "__main__":
    run()
