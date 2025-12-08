"""
Gerador de Tabela de Performance dos Modelos (M0-M5).

Lê os resultados de `data/outputs/nested_models_results.json` e gera
uma tabela LaTeX formatada para a Nota Técnica.
"""

import json
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def run():
    # 1. Carregar Resultados
    input_path = PROJECT_ROOT / "data" / "outputs" / "nested_models_results.json"
    with open(input_path, 'r') as f:
        results = json.load(f)
    
    # 2. Converter para DataFrame
    rows = []
    models_order = [
        "M0_RW", "M0_HM", 
        "M1_Static", "M2_Dynamic", 
        "M3_Fundamentals", "M4_Macro", 
        "M5_Score"
    ]
    
    model_labels = {
        "M0_RW": "M0 (Random Walk)",
        "M0_HM": "M0 (Média Hist.)",
        "M1_Static": "M1 (CAPM Estático)",
        "M2_Dynamic": "M2 (CAPM Dinâmico)",
        "M3_Fundamentals": "M3 (Fundamentos)",
        "M4_Macro": "M4 (Macro e Fatores)",
        "M5_Score": "M5 (Score Agregado)"
    }
    
    for m in models_order:
        if m in results:
            res = results[m]
            rows.append({
                "Modelo": model_labels[m],
                "MSE": res["MSE"],
                "RMSE": res["RMSE"],
                "MAE": res["MAE"],
                "R2_OOS": res["R2_OOS"],
                "AIC": res["AIC"],
                "BIC": res["BIC"]
            })
            
    df = pd.DataFrame(rows)
    
    # 3. Formatar Tabela LaTeX
    # Colunas: Modelo | MSE | RMSE | MAE | R2 (%) | AIC | BIC
    
    latex_rows = []
    latex_rows.append(r"\begin{table}[H]")
    latex_rows.append(r"\centering")
    latex_rows.append(r"\caption{Performance Comparativa dos Modelos (Out-of-Sample)}")
    latex_rows.append(r"\label{tab:model_performance}")
    latex_rows.append(r"\begin{tabular}{lcccccc}")
    latex_rows.append(r"\toprule")
    latex_rows.append(r"Modelo & MSE ($10^{-4}$) & RMSE & MAE & $R^2_{OOS}$ (\%) & AIC & BIC \\")
    latex_rows.append(r"\midrule")
    
    for _, row in df.iterrows():
        # MSE scaled by 10^4 for readability
        mse_scaled = row['MSE'] * 10000
        r2_pct = row['R2_OOS'] * 100
        
        line = (
            f"{row['Modelo']} & "
            f"{mse_scaled:.2f} & "
            f"{row['RMSE']:.4f} & "
            f"{row['MAE']:.4f} & "
            f"{r2_pct:.2f}\% & "
            f"{row['AIC']:.0f} & "
            f"{row['BIC']:.0f} \\\\"
        )
        latex_rows.append(line)
        
    latex_rows.append(r"\bottomrule")
    latex_rows.append(r"\end{tabular}")
    latex_rows.append(r"\footnotesize{Nota: MSE escalado por $10^4$. $R^2_{OOS}$ calculado em relação à média histórica do treino.}")
    latex_rows.append(r"\end{table}")
    
    # 4. Salvar
    output_dir = PROJECT_ROOT / "data" / "outputs" / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "tabela_performance_modelos.tex"
    
    with open(output_path, 'w') as f:
        f.write("\n".join(latex_rows))
        
    print(f"Tabela salva em: {output_path}")

if __name__ == "__main__":
    run()
