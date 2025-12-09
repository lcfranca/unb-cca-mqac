"""
Gera tabela comparativa entre M5b e M6 para a Nota Técnica.
Lê os resultados de `data/outputs/m6_comparison.json`.
"""
import json
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def run():
    input_path = PROJECT_ROOT / "data" / "outputs" / "m6_comparison.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "comparacao_m5b_m6.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not input_path.exists():
        print(f"Arquivo {input_path} não encontrado. Execute gen_model_m6.py primeiro.")
        return

    with open(input_path, 'r') as f:
        data = json.load(f)
        
    m5b = data['M5b']
    m6 = data['M6']
    comp = data['Comparison']
    
    latex = []
    latex.append(r"\begin{table}[H]")
    latex.append(r"\centering")
    latex.append(r"\caption{Comparação de Performance: M5b (Fundamentos) vs. M6 (Integração Total)}")
    latex.append(r"\label{tab:m6_comparison}")
    latex.append(r"\begin{tabular}{lcccc}")
    latex.append(r"\toprule")
    latex.append(r"Modelo & $R^2_{OOS}$ (\%) & RMSE & AIC & $\Delta R^2$ \\")
    latex.append(r"\midrule")
    
    # M5b Row
    r2_m5b = m5b['R2_OOS'] * 100
    rmse_m5b = m5b['RMSE']
    aic_m5b = m5b['AIC']
    latex.append(f"M5b (Fundamentos) & {r2_m5b:.2f}\\% & {rmse_m5b:.4f} & {aic_m5b:.0f} & - \\\\")
    
    # M6 Row
    r2_m6 = m6['R2_OOS'] * 100
    rmse_m6 = m6['RMSE']
    aic_m6 = m6['AIC']
    delta_r2 = comp['Delta_R2'] * 100
    
    # Highlight if better
    if delta_r2 > 0:
        delta_str = f"\\textbf{{+{delta_r2:.2f}\\%}}"
    else:
        delta_str = f"{delta_r2:.2f}\\%"
        
    latex.append(f"M6 (Integração Total) & {r2_m6:.2f}\\% & {rmse_m6:.4f} & {aic_m6:.0f} & {delta_str} \\\\")
    
    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}")
    latex.append(r"\footnotesize")
    latex.append(r"Nota: Horizonte de previsão de 21 dias. M5b utiliza apenas Z-Scores e dinâmica de mercado. M6 adiciona variáveis macro e fatores.")
    latex.append(r"\end{table}")
    
    with open(output_path, 'w') as f:
        f.write("\n".join(latex))
        
    print(f"Tabela salva em {output_path}")

if __name__ == "__main__":
    run()
