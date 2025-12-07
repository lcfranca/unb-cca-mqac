"""
Gera tabela LaTeX com métricas de erro (MSE, MAE, RMSE) e R2 OOS para os benchmarks Naïve.
"""

import json
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def run():
    # Caminhos
    input_path = PROJECT_ROOT / "data" / "outputs" / "naive_metrics.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "naive_metrics.tex"
    
    # Carregar dados
    with open(input_path, 'r') as f:
        metrics = json.load(f)
    
    # Converter para DataFrame
    df = pd.DataFrame(metrics).T
    
    # Selecionar e reordenar colunas
    cols = ['MSE', 'MAE', 'RMSE', 'R2_OOS']
    df = df[cols]
    
    # LaTeX Header
    latex_content = [
        "\\begin{table}[H]",
        "\\centering",
        "\\caption{Comparação de Performance Preditiva (Out-of-Sample)}",
        "\\label{tab:naive_metrics}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Modelo & MSE ($10^{-4}$) & MAE & RMSE & $R^2_{OOS}$ (\\%) \\\\",
        "\\midrule"
    ]
    
    for model in ['RW', 'HM', 'CAPM']:
        vals = df.loc[model]
        mse_scaled = vals['MSE'] * 10000
        mae = vals['MAE']
        rmse = vals['RMSE']
        r2_oos = vals['R2_OOS'] * 100 # Converter para %
        
        # Formatação condicional para R2
        r2_str = f"{r2_oos:.2f}"
        
        row = f"{model} & {mse_scaled:.4f} & {mae:.4f} & {rmse:.4f} & {r2_str} \\\\"
        latex_content.append(row)
        
    latex_content.extend([
        "\\bottomrule",
        "\\multicolumn{5}{l}{\\footnotesize *MSE escalado por $10^4$. $R^2_{OOS}$ relativo à Média Histórica.}",
        "\\end{tabular}",
        "\\end{table}"
    ])
    
    # Salvar
    with open(output_path, 'w') as f:
        f.write("\n".join(latex_content))
    
    print(f"Tabela salva em {output_path}")

if __name__ == "__main__":
    run()
