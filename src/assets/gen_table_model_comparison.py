"""
Gerador da Tabela 5.4 - Comparação de Modelos (In-Sample vs Out-of-Sample).
"""
import json
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def gen_table_model_comparison():
    oos_path = PROJECT_ROOT / "data" / "outputs" / "oos_results.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "comparacao_modelos.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(oos_path, 'r') as f:
        results = json.load(f)
    
    # Mapeamento de nomes
    model_names = {
        "M0": "CAPM (1 Fator)",
        "M3": "Fama-French (3 Fatores)"
    }
    
    latex = []
    latex.append(r"\begin{table}[h]")
    latex.append(r"\centering")
    latex.append(r"\caption{Comparação de Performance: In-Sample vs Out-of-Sample}")
    latex.append(r"\label{tab:model_comparison}")
    latex.append(r"\begin{tabular}{lccccc}")
    latex.append(r"\toprule")
    latex.append(r"& \multicolumn{2}{c}{\textbf{In-Sample (2016-2022)}} & \multicolumn{3}{c}{\textbf{Out-of-Sample (2023-2025)}} \\")
    latex.append(r"\cmidrule(lr){2-3} \cmidrule(lr){4-6}")
    latex.append(r"Modelo & $R^2$ & Adj. $R^2$ & $R^2_{OOS}$ & RMSE & MAE \\")
    latex.append(r"\midrule")
    
    for model_key in ["M0", "M3"]:
        name = model_names.get(model_key, model_key)
        
        # In-Sample
        is_metrics = results["in_sample"].get(model_key, {})
        r2 = is_metrics.get("r2", 0)
        adj_r2 = is_metrics.get("adj_r2", 0)
        
        # Out-of-Sample
        oos_metrics = results["out_of_sample"].get(model_key, {})
        r2_oos = oos_metrics.get("r2_oos", 0)
        rmse = oos_metrics.get("rmse", 0)
        mae = oos_metrics.get("mae", 0)
        
        # Format row
        # Multiplicando RMSE/MAE por 100 para % se forem retornos, mas geralmente RMSE é na escala original.
        # Assumindo escala original (decimal) para RMSE/MAE e % para R2.
        # R2 OOS pode ser negativo, mas aqui parece positivo.
        
        row = f"{name} & {r2:.3f} & {adj_r2:.3f} & {r2_oos:.3f} & {rmse:.4f} & {mae:.4f} \\\\"
        latex.append(row)
        
    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}")
    latex.append(r"\footnotesize")
    latex.append(r"Nota: $R^2_{OOS}$ calculado como $1 - \frac{\sum(y - \hat{y})^2}{\sum(y - \bar{y}_{train})^2}$. RMSE e MAE em escala decimal.")
    latex.append(r"\end{table}")

    with open(output_path, 'w') as f:
        f.write("\n".join(latex))
    
    print(f"Tabela 5.4 salva em {output_path}")

if __name__ == "__main__":
    gen_table_model_comparison()
