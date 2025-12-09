"""
Gera tabela LaTeX consolidada de performance de investimento (Backtesting).
Lê data/outputs/tables/backtest_fair_value_all.csv e formata para o padrão da Nota Técnica.
"""

import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def run():
    input_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "backtest_fair_value_all.csv"
    df = pd.read_csv(input_path)
    
    # Selecionar colunas e renomear
    # Model, Total Return, Annualized Vol, Sharpe, Max Drawdown, Trades
    
    # Formatar porcentagens
    cols_pct = ['Total Return', 'Annualized Vol', 'Max Drawdown']
    for col in cols_pct:
        df[col] = df[col].apply(lambda x: f"{x*100:.2f}\%")
        
    # Formatar decimais
    df['Sharpe'] = df['Sharpe'].apply(lambda x: f"{x:.2f}")
    df['Trades'] = df['Trades'].astype(int)
    
    # Renomear Modelos
    model_map = {
        'Buy & Hold': 'Buy & Hold (Benchmark)',
        'M0_Mean': 'M0 (Média Histórica)',
        'M1_Static': 'M1 (CAPM Estático)',
        'M2_Dynamic': 'M2 (CAPM Dinâmico)',
        'M3_Fund': 'M3 (Linear Fundamentos)',
        'M4_Macro': 'M4 (Linear Macro)',
        'M5b_ML': 'M5b (ML Fair Value)'
    }
    df['Model'] = df['Model'].replace(model_map)
    
    # Reordenar linhas (M0 -> M5b -> Benchmark)
    order = [
        'M0 (Média Histórica)', 'M1 (CAPM Estático)', 'M2 (CAPM Dinâmico)',
        'M3 (Linear Fundamentos)', 'M4 (Linear Macro)', 'M5b (ML Fair Value)',
        'Buy & Hold (Benchmark)'
    ]
    
    # Criar coluna categórica para ordenação
    df['Model'] = pd.Categorical(df['Model'], categories=order, ordered=True)
    df = df.sort_values('Model')
    
    # Renomear Colunas para LaTeX
    cols_map = {
        'Model': 'Estratégia',
        'Total Return': 'Retorno Total',
        'Annualized Vol': 'Volatilidade (a.a.)',
        'Sharpe': 'Sharpe Ratio',
        'Max Drawdown': 'Max Drawdown',
        'Trades': 'Trades'
    }
    df = df.rename(columns=cols_map)
    
    # Gerar LaTeX
    latex_code = df.to_latex(
        index=False,
        column_format='lccccc',
        caption='Performance Comparativa das Estratégias de Investimento (Fair Value)',
        label='tab:backtest_results',
        escape=False # Para permitir %
    )
    
    # Salvar
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "backtest_results_consolidated.tex"
    with open(output_path, 'w') as f:
        f.write(latex_code)
        
    print(f"Tabela LaTeX salva em {output_path}")

if __name__ == "__main__":
    run()
