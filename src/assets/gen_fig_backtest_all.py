"""
Gera gráficos e tabelas finais de Backtest para a Nota Técnica.
Lê os dados gerados por `gen_backtest_comparison.py`.

Outputs:
    - data/outputs/figures/backtest_equity_all.pdf (Curvas de Capital)
    - data/outputs/tables/backtest_metrics_all.tex (Tabela LaTeX)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

def run():
    set_style()
    
    # 1. Carregar Dados
    output_dir = PROJECT_ROOT / "data" / "outputs"
    curves_path = output_dir / "backtest_equity_curves.parquet"
    metrics_path = output_dir / "tables" / "backtest_fair_value_all.csv"
    
    if not curves_path.exists() or not metrics_path.exists():
        raise FileNotFoundError("Execute src.assets.gen_backtest_comparison primeiro.")
        
    df_curves = pd.read_parquet(curves_path)
    df_metrics = pd.read_csv(metrics_path)
    
    # 2. Plotar Curvas de Capital (Equity Curves)
    plt.figure(figsize=(12, 7))
    
    # Definir cores e estilos
    # M5b (Winner) -> Destaque
    # Benchmarks -> Tracejado/Cinza
    # Outros -> Cores suaves
    
    palette = {
        'Buy & Hold': 'black',
        'CDI': '#333333', # Darker gray for better visibility
        'M0_Mean': COLORS['primary'],
        'M1_Static': '#777777', # Visible gray
        'M2_Dynamic': '#777777',
        'M3_Fund': COLORS['tertiary'],
        'M4_Macro': COLORS['quinary'],
        'M5a_Huber': COLORS['quaternary'],
        'M5b_ML': COLORS['secondary'] # Destaque
    }
    
    styles = {
        'Buy & Hold': '--',
        'CDI': ':',
        'M0_Mean': '-',
        'M1_Static': '-',
        'M2_Dynamic': '-',
        'M3_Fund': '-',
        'M4_Macro': '-',
        'M5a_Huber': '-',
        'M5b_ML': '-'
    }
    
    linewidths = {
        'Buy & Hold': 1.5,
        'CDI': 1.5,
        'M0_Mean': 1.0,
        'M1_Static': 0.8,
        'M2_Dynamic': 0.8,
        'M3_Fund': 1.0,
        'M4_Macro': 1.0,
        'M5a_Huber': 1.5,
        'M5b_ML': 2.5 # Destaque
    }
    
    # Plotar
    for col in df_curves.columns:
        if col not in palette: continue # Skip unknown columns
        
        # Normalizar para 100 (Base 100)
        series = df_curves[col] * 100
        
        sns.lineplot(
            x=df_curves.index, 
            y=series, 
            label=col,
            color=palette.get(col, 'gray'),
            linestyle=styles.get(col, '-'),
            linewidth=linewidths.get(col, 1.0)
        )
        
    plt.title("Evolução do Capital: Estratégia de Valor Justo (2023-2024)", fontsize=14, pad=20)
    plt.ylabel("Capital Acumulado (Base 100)", fontsize=12)
    plt.xlabel("")
    plt.legend(loc='upper left', frameon=True, fontsize=10)
    
    # Ajustes finais
    plt.tight_layout()
    
    # Salvar Figura
    fig_path = output_dir / "figures" / "backtest_equity_all.pdf"
    plt.savefig(fig_path, dpi=300)
    print(f"Gráfico salvo em {fig_path}")
    
    # 3. Gerar Tabela LaTeX
    # Selecionar colunas e formatar
    # Colunas: Model, Total Return, Annualized Vol, Sharpe, Max Drawdown, Trades
    
    # Renomear colunas para LaTeX
    rename_map = {
        'Model': 'Modelo',
        'Total Return': 'Retorno Total',
        'Annualized Vol': 'Volatilidade (a.a.)',
        'Sharpe': 'Sharpe Ratio',
        'Max Drawdown': 'Max Drawdown',
        'Trades': 'Trades'
    }
    
    df_tex = df_metrics.rename(columns=rename_map)
    
    # Formatar percentuais
    df_tex['Retorno Total'] = df_tex['Retorno Total'].apply(lambda x: f"{x*100:.2f}\\%")
    df_tex['Volatilidade (a.a.)'] = df_tex['Volatilidade (a.a.)'].apply(lambda x: f"{x*100:.2f}\\%")
    df_tex['Max Drawdown'] = df_tex['Max Drawdown'].apply(lambda x: f"{x*100:.2f}\\%")
    df_tex['Sharpe Ratio'] = df_tex['Sharpe Ratio'].apply(lambda x: f"{x:.2f}")
    df_tex['Trades'] = df_tex['Trades'].astype(int)
    
    # Reordenar linhas: Benchmarks primeiro, depois modelos
    order = ['CDI', 'Buy & Hold', 'M0_Mean', 'M1_Static', 'M2_Dynamic', 'M3_Fund', 'M4_Macro', 'M5a_Huber', 'M5b_ML']
    
    # Filtrar apenas os que existem no dataframe
    existing_order = [o for o in order if o in df_tex['Modelo'].values]
    
    df_tex['Modelo'] = pd.Categorical(df_tex['Modelo'], categories=existing_order, ordered=True)
    df_tex = df_tex.sort_values('Modelo')
    
    # Renomear Modelos para nomes amigáveis (remove underscores e escapa &)
    model_map = {
        'CDI': 'CDI',
        'Buy & Hold': 'Buy \\& Hold',
        'M0_Mean': 'M0 (Média Histórica)',
        'M1_Static': 'M1 (CAPM Estático)',
        'M2_Dynamic': 'M2 (CAPM Dinâmico)',
        'M3_Fund': 'M3 (Linear Fundamentos)',
        'M4_Macro': 'M4 (Linear Macro)',
        'M5a_Huber': 'M5a (Huber Robust)',
        'M5b_ML': 'M5b (XGBoost ML)'
    }
    df_tex['Modelo'] = df_tex['Modelo'].apply(lambda x: model_map.get(x, x))
    
    # Gerar LaTeX
    latex_path = output_dir / "tables" / "backtest_metrics_all.tex"
    
    latex_content = df_tex.to_latex(
        index=False,
        column_format="lccccc",
        caption="Performance da Estratégia de Valor Justo (2023-2024)",
        label="tab:backtest_results",
        escape=False # Para manter o \%
    )
    
    # Ajustar tamanho da fonte para caber na página
    latex_content = latex_content.replace('\\begin{table}', '\\begin{table}\n\\small')
    
    with open(latex_path, 'w') as f:
        f.write(latex_content)
        
    print(f"Tabela LaTeX salva em {latex_path}")

if __name__ == "__main__":
    run()
