"""
Gerador da Tabela 5.4 - Comparação de Modelos (M0 a M5).
Consolidado a partir de full_model_comparison.json e dynamic_metrics.json.
"""
import json
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def gen_table_model_comparison():
    input_path = PROJECT_ROOT / "data" / "outputs" / "full_model_comparison.json"
    dynamic_path = PROJECT_ROOT / "data" / "outputs" / "dynamic_metrics.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "comparacao_modelos.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(input_path, 'r') as f:
        data = json.load(f)
        
    with open(dynamic_path, 'r') as f:
        dynamic_data = json.load(f)
    
    latex = []
    latex.append(r"\begin{table}[H]")
    latex.append(r"\centering")
    latex.append(r"\caption{Comparação de Performance Preditiva e Ajuste (M0 a M5)}")
    latex.append(r"\label{tab:model_comparison}")
    latex.append(r"\begin{tabular}{lccccc}")
    latex.append(r"\toprule")
    latex.append(r"Modelo & $R^2_{Adj}$ (In) & $R^2_{OOS}$ (Out) & MSE ($10^{-4}$) & AIC & Params \\")
    latex.append(r"\midrule")
    
    # Lista manual de modelos para a tabela
    models_to_show = [
        ("M0 (CAPM)", data.get("M0 (CAPM)", {})),
        ("Dynamic CAPM", dynamic_data.get("Dynamic CAPM", {})),
        ("M4 (Macro)", data.get("M4 (Macro)", {})),
        ("M5 (Fatores)", data.get("M5 (Fatores)", {}))
    ]
    
    for name, v in models_to_show:
        if not v: continue
        
        # Extrair métricas
        r2_adj = v.get('R2_Adj', 0) * 100
        r2_oos = v.get('R2_OOS', 0) * 100
        mse = v.get('MSE', 0) * 10000 # Escalar para legibilidade
        aic = v.get('AIC', 0)
        params = v.get('Num_Params', 0)
        
        # Dynamic CAPM não tem AIC/Params no JSON, tratar
        if name == "Dynamic CAPM":
            aic_str = "-"
            params_str = "1 (Rolling)"
            r2_adj_str = "-" # Geralmente não calculado da mesma forma
        else:
            aic_str = f"{aic:.0f}"
            params_str = str(params)
            r2_adj_str = f"{r2_adj:.2f}\%"
        
        # Destaque para o melhor OOS (M5) e o salto (M4)
        if "M5" in name:
            row = f"\\textbf{{{name}}} & {r2_adj_str} & \\textbf{{{r2_oos:.2f}\\%}} & {mse:.4f} & {aic_str} & {params_str} \\\\"
        else:
            row = f"{name} & {r2_adj_str} & {r2_oos:.2f}\\% & {mse:.4f} & {aic_str} & {params_str} \\\\"
        
        latex.append(row)
        
    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}")
    latex.append(r"\footnotesize")
    latex.append(r"Nota: $R^2_{OOS}$ mede a capacidade preditiva fora da amostra. MSE escalado por $10^4$. AIC: Critério de Akaike (menor é melhor).")
    latex.append(r"\end{table}")

    with open(output_path, 'w') as f:
        f.write("\n".join(latex))
    
    print(f"Tabela salva em {output_path}")

if __name__ == "__main__":
    gen_table_model_comparison()
