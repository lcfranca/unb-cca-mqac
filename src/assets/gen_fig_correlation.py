"""
Gera Heatmap de Correlação dos Z-Scores (Valor, Qualidade, Risco).
Visualiza a estrutura de dependência entre os fundamentos.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

# Configurações
ROLLING_WINDOW = 252

def load_data_zscores():
    """Carrega apenas os dados necessários para correlação de Z-Scores."""
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # 1. Retornos (para datas)
    df_ret = pd.read_parquet(processed_dir / "returns" / "returns.parquet")
    df_ret['date'] = pd.to_datetime(df_ret['date'])
    
    # 2. Q-VAL
    df_qval = pd.read_parquet(processed_dir / "qval" / "qval_timeseries.parquet")
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    df_qval = df_qval.sort_values('available_date')
    
    # Merge AsOf
    df = df_ret[['date']].sort_values('date')
    z_cols = ['z_earnings_yield', 'z_ev_ebitda', 'z_pb_ratio', 'z_roe', 'z_debt_to_equity']
    available_z_cols = [c for c in z_cols if c in df_qval.columns]
    
    df = pd.merge_asof(df, df_qval[['available_date'] + available_z_cols], left_on='date', right_on='available_date', direction='backward')
    
    # Clip Z-Scores
    for col in available_z_cols:
        df[col] = df[col].clip(lower=-5, upper=5)
        
    return df.set_index('date')[available_z_cols]

def run():
    set_style()
    sns.set_theme(style="white", rc={"axes.spines.right": False, "axes.spines.top": False}) # White style for heatmap
    
    df_z = load_data_zscores()
    
    # Semantic Names
    name_map = {
        'z_earnings_yield': 'Valor: Earnings Yield',
        'z_ev_ebitda': 'Valor: EV/EBITDA',
        'z_pb_ratio': 'Valor: P/VP',
        'z_roe': 'Qualidade: ROE',
        'z_debt_to_equity': 'Risco: Dívida/PL'
    }
    df_z = df_z.rename(columns=name_map)
    
    # Compute Correlation
    corr = df_z.corr()
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Mask upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    # Diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    
    sns.heatmap(corr, mask=mask, cmap=cmap, vmax=1, vmin=-1, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=True, fmt=".2f", ax=ax)
    
    ax.set_title('Matriz de Correlação: Valor, Qualidade e Risco', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    output_path = PROJECT_ROOT / "data/outputs/figures/zscore_correlation.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figura salva em: {output_path}")

if __name__ == "__main__":
    run()
