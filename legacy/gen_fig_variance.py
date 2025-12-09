"""
Gera gráfico de Decomposição de Variância (Waterfall ou Pie Chart).
Mostra a contribuição de cada fator para o R2 total.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from src.core.config import PROJECT_ROOT
import src.core.style as style

def run():
    # Configurar estilo
    style.set_style()
    
    # Caminhos
    input_path = PROJECT_ROOT / "data" / "outputs" / "macro_metrics.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "figures" / "variance_decomposition.pdf"
    
    # Carregar dados
    with open(input_path, 'r') as f:
        metrics = json.load(f)
        
    decomp = metrics['Variance_Decomposition']
    
    # Preparar dados para plotagem
    # Remover resíduo para focar nos fatores explicativos?
    # Ou mostrar resíduo para evidenciar o que falta?
    # Vamos mostrar tudo.
    
    labels = {
        'excess_ret_ibov': 'Mercado (Ibov)',
        'ret_brent': 'Petróleo (Brent)',
        'ret_fx': 'Câmbio (USD)',
        'delta_embi': 'Risco País (EMBI)',
        'Residual': 'Não Explicado (Resíduo)'
    }
    
    data = {labels.get(k, k): v for k, v in decomp.items()}
    
    # Ordenar por valor
    # Separar Resíduo para ficar no final
    residual = data.pop('Não Explicado (Resíduo)')
    
    # Ordenar fatores
    sorted_factors = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    
    # Reintegrar resíduo
    sorted_factors['Não Explicado (Resíduo)'] = residual
    
    names = list(sorted_factors.keys())
    values = list(sorted_factors.values())
    
    # Cores
    colors = [style.COLORS['primary'], style.COLORS['secondary'], 
              style.COLORS['tertiary'], style.COLORS['quaternary'], 
              'lightgray']
    
    # Criar gráfico (State of the Art: Horizontal Bar with Icons/Styling)
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Converter para porcentagem
    values_pct = [v * 100 for v in values]
    
    # Plotar barras
    bars = ax.barh(names, values_pct, color=colors, edgecolor='white', linewidth=1.5)
    
    # Inverter eixo Y para maior em cima
    ax.invert_yaxis()
    
    # Adicionar rótulos de valor e ícones (simulados com texto)
    icons = {
        'Mercado (Ibov)': '📈',
        'Petróleo (Brent)': '🛢️',
        'Câmbio (USD)': '💵',
        'Risco País (EMBI)': '🇧🇷',
        'Não Explicado (Resíduo)': '❓'
    }
    
    for i, bar in enumerate(bars):
        width = bar.get_width()
        name = names[i]
        icon = icons.get(name, '')
        
        # Label de valor
        label_x_pos = width + 1 if width < 85 else width - 8
        align = 'left' if width < 85 else 'right'
        color = 'black' if width < 85 else 'white'
        
        ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.1f}%',
                va='center', ha=align, color=color, fontweight='bold', fontsize=11)
        
        # Adicionar ícone no eixo Y (opcional, ou apenas melhorar o texto)
        # Vamos manter simples e limpo, mas com fonte melhor
        
    # Título e Eixos
    ax.set_title('Decomposição da Variância dos Retornos da PETR4 (Modelo M4)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Contribuição para a Variância Total (%)', fontsize=12, fontweight='bold')
    
    # Remover spines desnecessários
    sns.despine(left=True, bottom=False)
    
    # Limite X
    ax.set_xlim(0, 100)
    
    # Grid vertical apenas
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    ax.grid(axis='y', b=False)
    
    # Nota de rodapé explicativa
    r2_total = metrics['M4_R2'] * 100
    note = f"Nota: O modelo explica {r2_total:.1f}% da variância total.\nO restante ({100-r2_total:.1f}%) é ruído idiossincrático."
    plt.figtext(0.02, 0.02, note, ha="left", fontsize=9, style='italic', color='gray')

    plt.tight_layout()
    
    # Salvar
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figura salva em {output_path}")
    plt.close()

if __name__ == "__main__":
    run()
