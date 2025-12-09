"""
Gera o gráfico final de sinal de trading do Q-VAL (Buy/Hold/Sell).
Visualiza a evolução do Score Q-VAL com zonas coloridas de decisão.

Input:
    - data/processed/qval/qval_timeseries.parquet
    - data/processed/returns/returns.parquet (para plotar preço junto, opcional)

Output:
    - data/outputs/figures/qval_signal_evolution.pdf
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

def run():
    # Configuração de Estilo
    set_style()
    
    # Caminhos
    qval_path = PROJECT_ROOT / "data" / "processed" / "qval" / "qval_timeseries.parquet"
    prices_path = PROJECT_ROOT / "data" / "processed" / "prices" / "prices_petr4.parquet"
    output_path = PROJECT_ROOT / "data" / "outputs" / "figures" / "qval_signal_evolution.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Carregar Dados
    df_qval = pd.read_parquet(qval_path)
    df_prices = pd.read_parquet(prices_path)
    
    # Ajustar datas
    df_qval['date'] = pd.to_datetime(df_qval['quarter_end'])
    df_prices['date'] = pd.to_datetime(df_prices['date'])
    
    # Filtrar período de interesse (2016-2026)
    start_date = "2016-01-01"
    end_date = "2026-01-01"
    
    df_qval = df_qval[(df_qval['date'] >= start_date) & (df_qval['date'] <= end_date)].sort_values('date')
    df_prices = df_prices[(df_prices['date'] >= start_date) & (df_prices['date'] <= end_date)].sort_values('date')
    
    # Normalizar Score para Z-Score Real (Mean 0, Std 1) para o plot
    # O qval_scaled original parece ser uma soma ou escala diferente.
    # Vamos padronizar para que os thresholds 0.75 façam sentido visualmente.
    score_mean = df_qval['qval_scaled'].mean()
    score_std = df_qval['qval_scaled'].std()
    df_qval['plot_score'] = (df_qval['qval_scaled'] - score_mean) / score_std
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    
    # --- Painel 1: Preço da Ação ---
    ax1.plot(df_prices['date'], df_prices['close'], color='black', linewidth=1.5, label='PETR4 (Preço)')
    ax1.set_ylabel('Preço (BRL)', fontweight='bold')
    ax1.set_title('Evolução de Preço e Sinal Q-VAL (2016-2025)', fontweight='bold', pad=15)
    ax1.legend(loc='upper left')
    ax1.grid(True, which='major', linestyle='--', alpha=0.6)
    
    # --- Painel 2: Score Q-VAL e Zonas ---
    dates = df_qval['date']
    scores = df_qval['plot_score']
    
    # Plot da linha do score
    ax2.plot(dates, scores, color=COLORS['text'], linewidth=2, marker='o', markersize=4, label='Q-VAL Score (Padronizado)')
    
    # Limites do eixo Y para preenchimento
    y_min, y_max = scores.min() - 0.5, scores.max() + 0.5
    ax2.set_ylim(y_min, y_max)
    
    # Definir limiares (Z-Score Real)
    # Compra: > 0.75 (Verde)
    # Neutro: -0.75 a 0.75 (Bege/Amarelo)
    # Venda: < -0.75 (Vermelho)
    
    # Zona de Compra (Verde)
    ax2.axhspan(0.75, y_max, color=COLORS['positive'], alpha=0.2, label='Compra (> +0.75$\sigma$)')
    
    # Zona Neutra (Bege/Amarelo)
    ax2.axhspan(-0.75, 0.75, color=COLORS['neutral'], alpha=0.3, label='Neutro')
    
    # Zona de Venda (Vermelho)
    ax2.axhspan(y_min, -0.75, color=COLORS['negative'], alpha=0.2, label='Venda (< -0.75$\sigma$)')
    
    # Linha zero
    ax2.axhline(0, color='gray', linestyle='--', alpha=0.5)
    
    # Anotação sobre a natureza do sinal
    ax2.text(0.02, 0.05, "Nota: Estratégia de Reversão à Média (Contrarian).\nSinais de compra indicam subavaliação fundamentalista.", 
             transform=ax2.transAxes, fontsize=8, style='italic', 
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='lightgray'))
    
    ax2.set_ylabel('Score Q-VAL ($\sigma$)', fontweight='bold')
    ax2.set_xlabel('Data', fontweight='bold')
    
    # Legenda customizada
    ax2.legend(loc='lower left', ncol=4, frameon=True, fontsize=9)
    
    # Formatação de datas
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Gráfico salvo em {output_path}")

if __name__ == "__main__":
    run()
