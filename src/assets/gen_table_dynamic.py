"""
Gera tabela LaTeX comparando M0 (CAPM Estático) vs Dynamic CAPM (Beta Rolante).
"""

import json
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def run():
    # Caminhos
    static_path = PROJECT_ROOT / "data" / "outputs" / "full_model_comparison.json"
    dynamic_path = PROJECT_ROOT / "data" / "outputs" / "dynamic_metrics.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "dynamic_metrics.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Carregar dados
    with open(static_path, 'r') as f:
        static_data = json.load(f)
        
    with open(dynamic_path, 'r') as f:
        dynamic_data = json.load(f)
        
    latex = []
    latex.append(r"\begin{table}[H]")
    latex.append(r"\centering")
    latex.append(r"\caption{Impacto da Dinâmica Temporal: CAPM Estático vs. Dinâmico}")
    latex.append(r"\label{tab:dynamic_comparison}")
    latex.append(r"\begin{tabular}{lcccc}")
    latex.append(r"\toprule")
    latex.append(r"Modelo & MSE ($10^{-4}$) & MAE & RMSE & $R^2_{OOS}$ (\\%) \\\\")
    latex.append(r"\midrule")
    
    # M0 (Static)
    if "M0 (CAPM)" in static_data:
        v = static_data["M0 (CAPM)"]
        mse = v.get('MSE', 0) * 10000
        # MAE/RMSE might not be in full_model_comparison.json for M0, check naive_metrics.json if needed
        # But let's assume they are or calculate/fetch from naive_metrics
        # Actually, full_model_comparison usually has MSE/R2. Let's check naive_metrics for consistency.
        pass

    # Better approach: Load naive_metrics for CAPM to get all stats consistent
    naive_path = PROJECT_ROOT / "data" / "outputs" / "naive_metrics.json"
    with open(naive_path, 'r') as f:
        naive_data = json.load(f)
        
    # 1. M0 (CAPM)
    if "CAPM" in naive_data:
        v = naive_data["CAPM"]
        mse = v['MSE'] * 10000
        mae = v['MAE']
        rmse = v['RMSE']
        r2 = v['R2_OOS'] * 100
        latex.append(f"M0 (CAPM Estático) & {mse:.4f} & {mae:.4f} & {rmse:.4f} & {r2:.2f}\\% \\\\")
        
    # 2. Dynamic CAPM
    if "Dynamic CAPM" in dynamic_data:
        v = dynamic_data["Dynamic CAPM"]
        mse = v['MSE'] * 10000
        mae = v['MAE']
        rmse = v['RMSE']
        r2 = v['R2_OOS'] * 100
        latex.append(f"\\textbf{{CAPM Dinâmico}} & \\textbf{{{mse:.4f}}} & \\textbf{{{mae:.4f}}} & \\textbf{{{rmse:.4f}}} & \\textbf{{{r2:.2f}\\%}} \\\\")
        
    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}")
    latex.append(r"\footnotesize")
    latex.append(r"Nota: O modelo dinâmico utiliza janelas rolantes de 252 dias para estimar o Beta.")
    latex.append(r"\end{table}")
    
    with open(output_path, 'w') as f:
        f.write("\n".join(latex))
        
    print(f"Tabela salva em {output_path}")

if __name__ == "__main__":
    run()
