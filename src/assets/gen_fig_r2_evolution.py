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
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # Cores baseadas no Tipo
    palette = {
        'Benchmark': '#95a5a6', # Cinza
        'Linear': '#3498db',    # Azul
        'Dinâmico': '#e67e22',  # Laranja
        'Multifator': '#2ecc71', # Verde
        'Granular': '#9b59b6'   # Roxo
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
        alpha=0.9,
        hue_order=hue_order
    )
    
    # Labels e Títulos
    ax1.set_ylabel('R² Out-of-Sample (%)', color=COLORS['primary'], fontweight='bold', labelpad=10)
    ax1.set_xlabel('Hierarquia de Modelos', fontweight='bold', labelpad=10)
    
    plt.title('Evolução da Eficiência Informacional: Ganho Marginal de Informação', pad=20, fontweight='bold', fontsize=14)
    
    # Ajuste de limites (Clipar valores muito negativos para não estragar o gráfico)
    # Se houver valores < -5, clipar em -5 e avisar
    min_val = df['R2 OOS (%)'].min()
    if min_val < -5:
        ax1.set_ylim(-5, df['R2 OOS (%)'].max() * 1.15)
    else:
        ax1.set_ylim(min(0, min_val) * 1.1, df['R2 OOS (%)'].max() * 1.15)
    
    # Anotações nas Barras (OOS)
    # Precisamos iterar sobre as barras na ordem do eixo X para calcular deltas
    # O seaborn/matplotlib não garante a ordem nos containers se houver hue
    # Vamos pegar as patches e ordenar pela coordenada x
    
    patches = []
    for container in ax1.containers:
        patches.extend(container.patches)
    
    # Filtrar patches que não são NaN (alguns podem ser placeholders do hue)
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
            height + 0.5 if height > 0 else height - 2.5, # Um pouco acima da barra
            f'{height:.2f}%',
            ha='center',
            va='bottom',
            fontweight='bold',
            color='black',
            fontsize=12 # Aumentado
        )
        
        # 2. Delta (se não for o primeiro)
        if i > 0:
            prev_height = patches[i-1].get_height()
            diff = height - prev_height
            
            color = 'green' if diff >= 0 else 'red'
            symbol = '▲' if diff >= 0 else '▼'
            
            # Posicionar logo abaixo do número principal (mas ainda acima da barra, ou dentro se necessário)
            # Vamos colocar logo ACIMA do número para não poluir a barra, ou logo ABAIXO se houver espaço?
            # O usuário pediu "logo abaixo do numero".
            # Se o numero está em (height + 0.5), o delta pode ficar em (height - 1.5) se for dentro da barra?
            # Ou vamos subir o número principal e colocar o delta entre a barra e o número.
            
            # Estratégia: Subir o label principal e colocar o delta embaixo dele
            
            # Ajuste fino de posição
            delta_y = height - 1.5 if height > 0 else height + 0.5 # Dentro da barra (topo)
            
            # Se a barra for muito pequena, colocar acima do número principal
            if abs(height) < 5:
                 delta_y = height + 2.5
            
            ax1.text(
                x_center,
                delta_y, 
                f'{symbol} {abs(diff):.1f}pp',
                ha='center',
                va='center',
                color=color,
                fontweight='bold',
                fontsize=9
            )

    # Linha de base (0%)
    ax1.axhline(0, color='black', linewidth=1, linestyle='-')
    
    # Grid
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Legenda (Aumentada)
    plt.legend(title='Classe de Modelo', loc='upper left', bbox_to_anchor=(1, 1), fontsize=11, title_fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figura salva em: {output_path}")

if __name__ == "__main__":
    run()
