"""
Gerador de Figuras de Diagnóstico do Modelo (Asset 5.6 - 5.9).

Gera:
1. Rolling R2 (Estabilidade Temporal)
2. Scatter Plot (Previsto vs Realizado)
3. Histograma de Resíduos
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

def gen_fig_model_diagnostics():
    set_style()
    
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    outputs_dir = PROJECT_ROOT / "data" / "outputs"
    
    returns_path = processed_dir / "returns" / "returns.parquet"
    qval_path = processed_dir / "qval" / "qval_timeseries.parquet"
    rolling_r2_path = outputs_dir / "rolling_r2.parquet"
    
    figures_dir = outputs_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # ==========================================================================
    # 1. Rolling R2 (Com Delta R2)
    # ==========================================================================
    if rolling_r2_path.exists():
        print("Gerando Rolling R2...")
        df_rolling = pd.read_parquet(rolling_r2_path)
        
        # Calcular Delta R2 se não existir
        if 'delta_adj_r2' not in df_rolling.columns:
            df_rolling['delta_adj_r2'] = df_rolling['adj_r2_m3'] - df_rolling['adj_r2_m0']
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        
        # Painel Superior: R2 Absoluto
        ax1.plot(df_rolling['date'], df_rolling['adj_r2_m0'], label='M0: CAPM (Mercado)', color='gray', linestyle='--', alpha=0.6)
        ax1.plot(df_rolling['date'], df_rolling['adj_r2_m3'], label='M3: CAPM + Q-VAL', color=COLORS['primary'], linewidth=1.5)
        
        ax1.set_title('Estabilidade Temporal do Poder Explicativo ($R^2$ Móvel - 24 meses)', fontweight='bold')
        ax1.set_ylabel('$R^2$ Ajustado')
        ax1.legend(loc='lower left')
        ax1.grid(True, alpha=0.3)
        
        # Painel Inferior: Delta R2 (Contribuição Marginal)
        ax2.plot(df_rolling['date'], df_rolling['delta_adj_r2'], color='black', linewidth=0.5, alpha=0.5)
        ax2.fill_between(df_rolling['date'], df_rolling['delta_adj_r2'], 0, 
                         where=(df_rolling['delta_adj_r2'] >= 0), color=COLORS['positive'], alpha=0.3, label='Ganho de Informação')
        ax2.fill_between(df_rolling['date'], df_rolling['delta_adj_r2'], 0, 
                         where=(df_rolling['delta_adj_r2'] < 0), color=COLORS['negative'], alpha=0.3, label='Perda/Ruído')
        
        ax2.axhline(0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_ylabel('$\Delta R^2$ (M3 - M0)')
        ax2.set_xlabel('Data')
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(figures_dir / "rolling_r2.pdf")
        plt.close()
    else:
        print(f"Aviso: {rolling_r2_path} não encontrado. Pulando Rolling R2.")

    # ==========================================================================
    # Preparar Dados para Scatter e Resíduos
    # ==========================================================================
    df_ret = pd.read_parquet(returns_path).sort_values('date')
    df_qval = pd.read_parquet(qval_path).sort_values('quarter_end')
    
    # Merge
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    df_merged = pd.merge_asof(df_ret, df_qval[['available_date', 'qval_scaled']], 
                              left_on='date', right_on='available_date', direction='backward').dropna()
    
    # Modelo Final (M3)
    y = df_merged['excess_ret_petr4']
    X = sm.add_constant(df_merged[['excess_ret_ibov', 'qval_scaled']])
    model = sm.OLS(y, X).fit()
    
    df_merged['predicted'] = model.predict(X)
    df_merged['residuals'] = model.resid

    # ==========================================================================
    # 2. Scatter Plot (Previsto vs Realizado) - State of the Art
    # ==========================================================================
    print("Gerando Scatter Plot (JointPlot)...")
    
    # Calcular limites para linha de identidade
    min_val = min(df_merged['predicted'].min(), df_merged['excess_ret_petr4'].min())
    max_val = max(df_merged['predicted'].max(), df_merged['excess_ret_petr4'].max())
    
    g = sns.jointplot(x='predicted', y='excess_ret_petr4', data=df_merged,
                      kind='reg', height=7, color=COLORS['primary'],
                      scatter_kws={'alpha': 0.2, 's': 15},
                      line_kws={'color': COLORS['secondary'], 'linewidth': 2, 'label': 'Regressão Linear'})
    
    # Adicionar linha de identidade (Perfeição)
    g.ax_joint.plot([min_val, max_val], [min_val, max_val], 
                    color='black', linestyle='--', linewidth=1.5, label='Identidade (y=x)')
    
    g.fig.suptitle('Aderência do Modelo: Retorno Previsto vs Realizado', fontsize=14, fontweight='bold', y=1.02)
    g.set_axis_labels('Retorno Previsto (Modelo M3)', 'Retorno Realizado (PETR4)', fontsize=12)
    
    # Legenda
    g.ax_joint.legend(loc='upper left')
    
    # Anotação R2
    r2 = model.rsquared
    g.ax_joint.text(0.05, 0.85, f'$R^2$ In-Sample: {r2:.3f}', 
                    transform=g.ax_joint.transAxes, fontsize=12, 
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='lightgray'))
    
    # ==========================================================================
    # 3. Histograma de Resíduos
    # ==========================================================================
    print("Gerando Histograma de Resíduos...")
    plt.figure(figsize=(8, 5))
    
    sns.histplot(df_merged['residuals'], kde=True, color=COLORS['primary'], stat='density', bins=50)
    
    # Normal teórica
    mu, std = df_merged['residuals'].mean(), df_merged['residuals'].std()
    x = np.linspace(min(df_merged['residuals']), max(df_merged['residuals']), 100)
    p = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / std) ** 2)
    plt.plot(x, p, 'k--', linewidth=1.5, label='Normal Teórica')
    
    plt.title('Distribuição dos Resíduos do Modelo Q-VAL')
    plt.xlabel('Resíduos')
    plt.ylabel('Densidade')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(figures_dir / "residuals_hist.pdf")
    plt.close()
    
    print("Figuras de diagnóstico geradas com sucesso.")

if __name__ == "__main__":
    gen_fig_model_diagnostics()
