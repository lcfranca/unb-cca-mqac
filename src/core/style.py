"""
style.py - Configuração centralizada de estilo para visualizações

Padrão visual acadêmico alinhado com Times New Roman (ABNT) e
paleta de cores profissional para documentos técnicos.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl

# ==============================================================================
# PALETA DE CORES - Profissional e acessível
# ==============================================================================

COLORS = {
    # Cores principais
    'primary': '#1f4e79',      # Azul corporativo escuro
    'secondary': '#c45911',    # Laranja profissional
    'tertiary': '#538135',     # Verde corporativo
    
    # Cores de status
    'positive': '#2e7d32',     # Verde positivo
    'negative': '#c62828',     # Vermelho negativo
    'neutral': '#616161',      # Cinza neutro
    
    # Cores de gráficos
    'chart_1': '#1f4e79',      # Azul
    'chart_2': '#c45911',      # Laranja
    'chart_3': '#538135',      # Verde
    'chart_4': '#7b4f9d',      # Roxo
    'chart_5': '#bf9000',      # Amarelo escuro
    'chart_6': '#4a86c7',      # Azul claro
    
    # Fundos e grades
    'background': '#ffffff',
    'grid': '#e0e0e0',
    'text': '#212121',
    'text_light': '#757575',
}

# Lista de cores para uso sequencial
PALETTE = [
    COLORS['chart_1'], COLORS['chart_2'], COLORS['chart_3'],
    COLORS['chart_4'], COLORS['chart_5'], COLORS['chart_6']
]

# ==============================================================================
# CONFIGURAÇÃO MATPLOTLIB - Padrão acadêmico ABNT
# ==============================================================================

STYLE_CONFIG = {
    # Tamanho de figura padrão (polegadas)
    'figure.figsize': (8, 5),
    'figure.dpi': 100,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    
    # Tipografia - Times New Roman (padrão ABNT)
    'font.family': 'serif',
    'font.serif': ['TeX Gyre Termes', 'Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 11,
    'mathtext.fontset': 'stix',  # Fonte matemática compatível com Times
    
    # Tamanhos de fonte específicos
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'legend.title_fontsize': 11,
    
    # Eixos
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.8,
    'axes.edgecolor': COLORS['text_light'],
    'axes.labelcolor': COLORS['text'],
    'axes.titlecolor': COLORS['text'],
    'axes.titleweight': 'bold',
    'axes.titlepad': 12,
    'axes.labelpad': 8,
    
    # Grade
    'axes.grid': True,
    'axes.grid.which': 'major',
    'grid.alpha': 0.4,
    'grid.linewidth': 0.5,
    'grid.color': COLORS['grid'],
    
    # Ticks
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 4,
    'ytick.major.size': 4,
    'xtick.minor.size': 2,
    'ytick.minor.size': 2,
    'xtick.color': COLORS['text_light'],
    'ytick.color': COLORS['text_light'],
    
    # Legenda
    'legend.frameon': True,
    'legend.framealpha': 0.95,
    'legend.edgecolor': COLORS['grid'],
    'legend.fancybox': False,
    'legend.loc': 'best',
    
    # Cores
    'axes.facecolor': COLORS['background'],
    'figure.facecolor': COLORS['background'],
    'axes.prop_cycle': plt.cycler('color', PALETTE),
    
    # Linhas
    'lines.linewidth': 1.5,
    'lines.markersize': 6,
    
    # Scatter
    'scatter.edgecolors': 'face',
}


def setup_style():
    """
    Aplica configuração de estilo global ao matplotlib.
    
    Deve ser chamado no início de scripts de visualização.
    
    Example:
        >>> from src.core.style import setup_style
        >>> setup_style()
    """
    plt.rcParams.update(STYLE_CONFIG)
    

def reset_style():
    """Restaura estilo padrão do matplotlib."""
    mpl.rcdefaults()


def get_color(name: str) -> str:
    """
    Retorna cor da paleta por nome.
    
    Args:
        name: Nome da cor (primary, secondary, positive, negative, etc.)
    
    Returns:
        Código hexadecimal da cor.
    """
    return COLORS.get(name, COLORS['primary'])


def format_axis_pct(ax, axis='y', decimals=0):
    """
    Formata eixo como porcentagem.
    
    Args:
        ax: Axes matplotlib
        axis: 'x' ou 'y'
        decimals: Casas decimais
    """
    from matplotlib.ticker import FuncFormatter
    fmt = FuncFormatter(lambda x, _: f'{x:.{decimals}f}%')
    if axis == 'y':
        ax.yaxis.set_major_formatter(fmt)
    else:
        ax.xaxis.set_major_formatter(fmt)


def format_axis_currency(ax, axis='y', prefix='R$', decimals=2):
    """
    Formata eixo como moeda.
    
    Args:
        ax: Axes matplotlib
        axis: 'x' ou 'y'
        prefix: Prefixo monetário
        decimals: Casas decimais
    """
    from matplotlib.ticker import FuncFormatter
    fmt = FuncFormatter(lambda x, _: f'{prefix} {x:,.{decimals}f}'.replace(',', '.'))
    if axis == 'y':
        ax.yaxis.set_major_formatter(fmt)
    else:
        ax.xaxis.set_major_formatter(fmt)


def add_source_note(fig, text="Fonte: Elaboração própria.", y=-0.02):
    """
    Adiciona nota de fonte abaixo da figura.
    
    Args:
        fig: Figure matplotlib
        text: Texto da nota
        y: Posição vertical (negativo = abaixo)
    """
    fig.text(
        0.5, y, text,
        ha='center', va='top',
        fontsize=9, style='italic',
        color=COLORS['text_light']
    )


# ==============================================================================
# TEMAS PARA CASOS ESPECÍFICOS
# ==============================================================================

def apply_dark_theme():
    """Aplica tema escuro para apresentações."""
    dark_overrides = {
        'axes.facecolor': '#1e1e1e',
        'figure.facecolor': '#1e1e1e',
        'axes.edgecolor': '#ffffff',
        'axes.labelcolor': '#ffffff',
        'axes.titlecolor': '#ffffff',
        'xtick.color': '#ffffff',
        'ytick.color': '#ffffff',
        'grid.color': '#444444',
        'text.color': '#ffffff',
    }
    plt.rcParams.update(STYLE_CONFIG)
    plt.rcParams.update(dark_overrides)


def apply_print_theme():
    """Aplica tema otimizado para impressão (alto contraste)."""
    print_overrides = {
        'axes.edgecolor': '#000000',
        'axes.labelcolor': '#000000',
        'axes.titlecolor': '#000000',
        'xtick.color': '#000000',
        'ytick.color': '#000000',
        'grid.color': '#cccccc',
        'lines.linewidth': 2.0,
    }
    plt.rcParams.update(STYLE_CONFIG)
    plt.rcParams.update(print_overrides)


if __name__ == '__main__':
    # Demonstração do estilo
    import numpy as np
    
    setup_style()
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Gráfico de linha
    x = np.linspace(0, 10, 100)
    axes[0].plot(x, np.sin(x), label='Série A')
    axes[0].plot(x, np.cos(x), label='Série B')
    axes[0].set_title('Exemplo de Gráfico de Linhas')
    axes[0].set_xlabel('Tempo (t)')
    axes[0].set_ylabel('Valor')
    axes[0].legend()
    
    # Gráfico de barras
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [23, 45, 56, 78, 32]
    colors = [COLORS['chart_1'], COLORS['chart_2'], COLORS['chart_3'], 
              COLORS['chart_4'], COLORS['chart_5']]
    axes[1].bar(categories, values, color=colors)
    axes[1].set_title('Exemplo de Gráfico de Barras')
    axes[1].set_xlabel('Categoria')
    axes[1].set_ylabel('Frequência')
    
    add_source_note(fig, "Fonte: Dados simulados para demonstração.")
    
    plt.tight_layout()
    plt.savefig('data/outputs/figures/style_demo.pdf')
    plt.close()
    
    print("✓ Demonstração de estilo salva em data/outputs/figures/style_demo.pdf")
