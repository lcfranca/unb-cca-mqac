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
from src.core.style import setup_style, COLORS

def gen_fig_model_diagnostics():
    setup_style()
    
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    outputs_dir = PROJECT_ROOT / "data" / "outputs"
    
    returns_path = processed_dir / "returns" / "returns.parquet"
    qval_path = processed_dir / "qval" / "qval_timeseries.parquet"
    rolling_r2_path = outputs_dir / "rolling_r2.parquet"
    
    figures_dir = outputs_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # ==========================================================================
    # 1. Rolling R2
    # ==========================================================================
    if rolling_r2_path.exists():
        print("Gerando Rolling R2...")
        df_rolling = pd.read_parquet(rolling_r2_path)
        
        plt.figure(figsize=(10, 5))
        
        # Plotar M0 (CAPM) e M3 (Q-VAL)
        # Colunas identificadas: 'adj_r2_m0', 'adj_r2_m3'
        
        plt.plot(df_rolling['date'], df_rolling['adj_r2_m0'], label='CAPM', color='gray', linestyle='--', alpha=0.7)
        plt.plot(df_rolling['date'], df_rolling['adj_r2_m3'], label='CAPM + Q-VAL', color=COLORS['primary'], linewidth=1.5)
        
        plt.title('Estabilidade Temporal do Poder Explicativo ($R^2$ Móvel - 24 meses)')
        plt.ylabel('$R^2$ Ajustado')
        plt.xlabel('Data')
        plt.legend()
        plt.grid(True, alpha=0.3)
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
    # 2. Scatter Plot (Previsto vs Realizado)
    # ==========================================================================
    print("Gerando Scatter Plot...")
    plt.figure(figsize=(6, 6))
    
    # Scatter points
    plt.scatter(df_merged['predicted'], df_merged['excess_ret_petr4'], 
                alpha=0.3, color=COLORS['primary'], s=15, label='Observações')
    
    # Linha 45 graus (Perfeita previsão)
    min_val = min(df_merged['predicted'].min(), df_merged['excess_ret_petr4'].min())
    max_val = max(df_merged['predicted'].max(), df_merged['excess_ret_petr4'].max())
    plt.plot([min_val, max_val], [min_val, max_val], color='black', linestyle='--', label='Perfeito')
    
    # Linha de Regressão do Scatter (Bias check)
    sns.regplot(x=df_merged['predicted'], y=df_merged['excess_ret_petr4'], 
                scatter=False, color=COLORS['secondary'], label='Ajuste', ci=None)
    
    plt.title('Aderência do Modelo: Previsto vs Realizado')
    plt.xlabel('Retorno Excedente Previsto')
    plt.ylabel('Retorno Excedente Realizado')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(figures_dir / "scatter_pred_actual.pdf")
    plt.close()

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
