"""
style.py - Configuração centralizada de estilo para visualizações (State of the Art)

Padrão visual acadêmico/profissional utilizando Seaborn como base,
alinhado com Times New Roman (ABNT) e paleta de cores otimizada.
"""

import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# PALETA DE CORES - Profissional e acessível
# ==============================================================================

COLORS = {
    # Cores principais (Baseadas em Seaborn Deep/Muted mas ajustadas)
    'primary': '#4c72b0',      # Azul Seaborn
    'secondary': '#c44e52',    # Vermelho Seaborn
    'tertiary': '#55a868',     # Verde Seaborn
    'quaternary': '#8172b3',   # Roxo Seaborn
    'quinary': '#ccb974',      # Amarelo Seaborn
    'senary': '#64b5cd',       # Ciano Seaborn
    
    # Cores Semânticas
    'positive': '#2ca02c',     # Verde Compra
    'negative': '#d62728',     # Vermelho Venda
    'neutral': '#e3d6a3',      # Bege/Amarelo Neutro
    'text': '#333333',         # Cinza Escuro
    'grid': '#dddddd',         # Cinza Claro
}

def set_style():
    """
    Aplica o estilo global 'State of the Art' para todos os gráficos.
    Deve ser chamado no início de cada script de geração de figura.
    """
    # Resetar configurações anteriores
    plt.rcParams.update(plt.rcParamsDefault)
    
    # Usar estilo base do Seaborn
    sns.set_theme(style="whitegrid", context="paper")
    
    # Customizações Finas (RC Params)
    plt.rcParams.update({
        # Tipografia
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
        'font.size': 12,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16,
        
        # Cores e Linhas
        'axes.labelcolor': COLORS['text'],
        'axes.titlecolor': COLORS['text'],
        'axes.edgecolor': COLORS['grid'],
        'grid.color': COLORS['grid'],
        'grid.linestyle': '--',
        'grid.alpha': 0.6,
        
        # Layout
        'figure.figsize': (10, 6),
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,
        
        # Legenda
        'legend.frameon': True,
        'legend.framealpha': 0.9,
        'legend.facecolor': 'white',
        'legend.edgecolor': '#cccccc',
        'legend.fancybox': True,
    })
    
    # Definir paleta padrão do Seaborn
    sns.set_palette(sns.color_palette("deep"))

def get_palette(n_colors=6):
    """Retorna a paleta de cores padrão."""
    return sns.color_palette("deep", n_colors)
