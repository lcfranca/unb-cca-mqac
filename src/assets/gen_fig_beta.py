"""
Gera gráfico da evolução do Beta Dinâmico (Rolling Window).
Estado da arte em visualização: Seaborn + Style Customizado.
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
    input_path = PROJECT_ROOT / "data" / "outputs" / "dynamic_results.parquet"
    output_path = PROJECT_ROOT / "data" / "outputs" / "figures" / "beta_evolution.pdf"
    
    # Carregar dados
    df = pd.read_parquet(input_path)
    
    # Filtrar para remover NaNs iniciais da janela de rolagem
    df = df.dropna(subset=['rolling_beta'])
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plotar Beta
    ax.plot(df['date'], df['rolling_beta'], color=style.COLORS['primary'], linewidth=1.5, label=r'Beta Rolante (252 dias)')
    
    # Adicionar média do Beta (linha tracejada)
    mean_beta = df['rolling_beta'].mean()
    ax.axhline(mean_beta, color=style.COLORS['secondary'], linestyle='--', linewidth=1.2, label=f'Beta Médio ({mean_beta:.2f})')
    
    # Adicionar linha de referência Beta=1 (Mercado)
    ax.axhline(1.0, color='gray', linestyle=':', linewidth=1, alpha=0.7, label='Beta de Mercado (1.0)')
    
    # Identificar regimes (State of the Art: Shading)
    # Beta > 1 (Agressivo/Alto Risco) vs Beta < 1 (Defensivo/Baixo Risco)
    
    # Preencher área acima de 1.0 (Risco > Mercado)
    ax.fill_between(df['date'], df['rolling_beta'], 1.0, 
                    where=(df['rolling_beta'] >= 1.0), 
                    color=style.COLORS['negative'], alpha=0.1, interpolate=True, label='Beta > 1 (Agressivo)')
    
    # Preencher área abaixo de 1.0 (Risco < Mercado)
    ax.fill_between(df['date'], df['rolling_beta'], 1.0, 
                    where=(df['rolling_beta'] < 1.0), 
                    color=style.COLORS['positive'], alpha=0.1, interpolate=True, label='Beta < 1 (Defensivo)')
    
    # Formatação
    ax.set_ylabel(r'Beta ($\beta_t$)', fontsize=12)
    ax.set_xlabel('Data', fontsize=12)
    ax.set_title('Evolução Temporal do Risco Sistemático (PETR4)', fontsize=14, fontweight='bold', pad=15)
    
    # Formatar datas
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Grid e Legenda
    ax.grid(True, which='major', linestyle='--', alpha=0.6)
    ax.legend(loc='upper left', frameon=True, framealpha=0.9, ncol=2)
    
    # Anotação do Beta Atual
    current_beta = df['rolling_beta'].iloc[-1]
    current_date = df['date'].iloc[-1]
    
    ax.annotate(f'Atual: {current_beta:.2f}', 
                xy=(current_date, current_beta), 
                xytext=(10, 0), textcoords='offset points',
                arrowprops=dict(arrowstyle='->', color='black'),
                fontsize=10, fontweight='bold', color=style.COLORS['primary'])
    
    # Estatísticas descritivas no gráfico
    stats_text = (
        f"Mín: {df['rolling_beta'].min():.2f}\n"
        f"Máx: {df['rolling_beta'].max():.2f}\n"
        f"Média: {mean_beta:.2f}\n"
        f"Vol: {df['rolling_beta'].std():.2f}"
    )
    ax.text(0.02, 0.05, stats_text, transform=ax.transAxes, 
            fontsize=10, bbox=dict(facecolor='white', alpha=0.8, edgecolor='lightgray'))

    plt.tight_layout()
    
    # Salvar
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figura salva em {output_path}")
    plt.close()

if __name__ == "__main__":
    run()
