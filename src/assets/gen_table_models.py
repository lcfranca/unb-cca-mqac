"""
Gera tabela LaTeX consolidada com métricas de todos os modelos (Naive + Dynamic).
"""

import json
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def run():
    # Caminhos
    naive_path = PROJECT_ROOT / "data" / "outputs" / "naive_metrics.json"
    dynamic_path = PROJECT_ROOT / "data" / "outputs" / "dynamic_metrics.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "model_comparison.tex"
    
    # Carregar dados
    with open(naive_path, 'r') as f:
        naive_metrics = json.load(f)
        
    with open(dynamic_path, 'r') as f:
        dynamic_metrics = json.load(f)
        
    # Unificar dicionários
    all_metrics = {**naive_metrics, **dynamic_metrics}
    
    # Converter para DataFrame
    df = pd.DataFrame(all_metrics).T
    
    # Reordenar linhas
    order = ['RW', 'HM', 'CAPM', 'Dynamic CAPM']
    df = df.reindex(order)
    
    # LaTeX Header
    latex_content = [
        "\\begin{table}[H]",
        "\\centering",
        "\\caption{Comparação de Performance Preditiva (Out-of-Sample)}",
        "\\label{tab:model_comparison}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Modelo & MSE ($10^{-4}$) & MAE & RMSE & $R^2_{OOS}$ (\\%) \\\\",
        "\\midrule"
    ]
    
    # Encontrar o melhor R2 para destacar
    best_r2 = df['R2_OOS'].max()
    
    for model in order:
        if model not in df.index: continue
        
        vals = df.loc[model]
        mse_scaled = vals['MSE'] * 10000
        mae = vals['MAE']
        rmse = vals['RMSE']
        r2_oos = vals['R2_OOS'] * 100
        
        # Formatação
        r2_str = f"{r2_oos:.2f}"
        
        # Negrito para o melhor modelo (maior R2)
        is_best = (vals['R2_OOS'] == best_r2)
        
        if is_best:
            row = f"\\textbf{{{model}}} & \\textbf{{{mse_scaled:.4f}}} & \\textbf{{{mae:.4f}}} & \\textbf{{{rmse:.4f}}} & \\textbf{{{r2_str}}} \\\\"
        else:
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
