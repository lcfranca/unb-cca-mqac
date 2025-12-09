"""
Gera gráfico de evolução do R2 Out-of-Sample para os modelos M0-M5.
Versão aprimorada (State of the Art) - Compatível com Estratégia Aninhada.
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
    
    input_path = PROJECT_ROOT / "data" / "outputs" / "nested_models_results.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "figures" / "r2_evolution.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(input_path, 'r') as f:
        data = json.load(f)
        
    # Construir lista manual para garantir a ordem e fontes corretas
    plot_data = []
    
    # Mapeamento de Chaves para Labels e Tipos
    model_map = [
        ('M0_HM', 'M0 (Média)', 'Benchmark'),
        ('M1_Static', 'M1 (Estático)', 'Linear'),
        ('M2_Dynamic', 'M2 (Dinâmico)', 'Dinâmico'),
        ('M3_Fundamentals', 'M3 (Fundamentos)', 'Multifator'),
        ('M4_Macro', 'M4 (Macro)', 'Multifator'),
        ('M5_Score', 'M5 (Score)', 'Multifator'),
        # M5 Linear removido se for muito negativo (polui o gráfico)
        ('M5_Linear', 'M5 (Linear)', 'Granular'), 
        ('M5_ML', 'M5 (ML)', 'Granular')
    ]
    
    for key, label, tipo in model_map:
        if key in data:
            r2_val = data[key]['R2_OOS'] * 100
            # Filtrar outliers negativos extremos para visualização
            if r2_val > -10: 
                plot_data.append({
                    'Modelo': label,
                    'R2 OOS (%)': r2_val,
                    'Tipo': tipo
                })
        
    df = pd.DataFrame(plot_data)
    
    # Plot
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    # Cores baseadas no Tipo (Sóbrias e Profissionais)
    palette = {
        'Benchmark': '#7f8c8d', # Cinza Escuro
        'Linear': '#2980b9',    # Azul Forte
        'Dinâmico': '#d35400',  # Laranja Queimado
        'Multifator': '#27ae60', # Verde Esmeralda
        'Granular': '#8e44ad'   # Roxo Profundo
    }
    
    # Hue order
    hue_order = ['Benchmark', 'Linear', 'Dinâmico', 'Multifator', 'Granular']
    
    bars = sns.barplot(
        data=df, 
        x='Modelo', 
        y='R2 OOS (%)', 
        ax=ax1, 
        hue='Tipo', 
        palette=palette, 
        dodge=False, 
        alpha=0.95,
        hue_order=hue_order
    )
    
    # Labels e Títulos
    ax1.set_ylabel('R² Out-of-Sample (%)', fontweight='bold', labelpad=10)
    ax1.set_xlabel('', fontweight='bold', labelpad=10)
    
    plt.title('Evolução da Eficiência Informacional: Ganho Marginal de Informação', pad=20, fontweight='bold', fontsize=14)
    
    # Ajuste de limites
    min_val = df['R2 OOS (%)'].min()
    max_val = df['R2 OOS (%)'].max()
    ax1.set_ylim(min(0, min_val) - 5, max_val * 1.2) # Mais espaço no topo
    
    # Anotações nas Barras (OOS)
    patches = []
    for container in ax1.containers:
        patches.extend(container.patches)
    
    # Filtrar patches que não são NaN
    patches = [p for p in patches if not pd.isna(p.get_height())]
    # Ordenar por posição X
    patches.sort(key=lambda x: x.get_x())
    
    # Adicionar labels de valor e deltas
    for i, p in enumerate(patches):
        height = p.get_height()
        x_center = p.get_x() + p.get_width() / 2.
        
        # 1. Valor Principal (R2)
        ax1.text(
            x_center,
            height + 1.0 if height > 0 else height - 3.0,
            f'{height:.1f}%',
            ha='center',
            va='bottom',
            fontweight='bold',
            color='black',
            fontsize=11
        )
        
        # 2. Delta (se não for o primeiro)
        if i > 0:
            prev_height = patches[i-1].get_height()
            diff = height - prev_height
            
            color = '#27ae60' if diff >= 0 else '#c0392b'
            symbol = '▲' if diff >= 0 else '▼'
            
            # Posicionar dentro da barra (topo) se houver espaço, senão acima
            if height > 5:
                y_pos = height - 2.0
                txt_color = 'white'
            else:
                y_pos = height + 3.5
                txt_color = color

            ax1.text(
                x_center,
                y_pos, 
                f'{symbol}{abs(diff):.1f}',
                ha='center',
                va='center',
                color=txt_color,
                fontweight='bold',
                fontsize=9
            )

    # Linha de base (0%)
    ax1.axhline(0, color='black', linewidth=1, linestyle='-')
    
    # Legenda (Interna - Upper Left)
    plt.legend(title='Classe de Modelo', loc='upper left', frameon=True, framealpha=0.95)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figura salva em: {output_path}")

if __name__ == "__main__":
    run()
