"""
Gera tabela LaTeX com resultados da regressão M4 (Macro).
"""

import json
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def run():
    # Caminhos
    input_path = PROJECT_ROOT / "data" / "outputs" / "macro_metrics.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "macro_regression.tex"
    
    # Carregar dados
    with open(input_path, 'r') as f:
        metrics = json.load(f)
    
    coefs = metrics['Coefficients']
    tvals = metrics['TValues']
    pvals = metrics['PValues']
    
    # Mapeamento de nomes
    names = {
        'const': 'Intercepto',
        'excess_ret_ibov': 'Risco de Mercado (Ibov)',
        'ret_brent': 'Petróleo (Brent)',
        'ret_fx': 'Câmbio (USD/BRL)',
        'delta_embi': 'Risco País (EMBI+)'
    }
    
    # LaTeX Header
    latex_content = [
        "\\begin{table}[H]",
        "\\centering",
        "\\caption{Resultados da Regressão Multifatorial (Modelo M4)}",
        "\\label{tab:macro_regression}",
        "\\begin{tabular}{lrrr}",
        "\\toprule",
        "Fator & Coeficiente & Estatística-t & P-Valor \\\\",
        "\\midrule"
    ]
    
    # Ordem de exibição
    vars_order = ['const', 'excess_ret_ibov', 'ret_brent', 'ret_fx', 'delta_embi']
    
    for var in vars_order:
        name = names.get(var, var)
        coef = coefs[var]
        t = tvals[var]
        p = pvals[var]
        
        # Estrelas de significância
        stars = ""
        if p < 0.01: stars = "***"
        elif p < 0.05: stars = "**"
        elif p < 0.1: stars = "*"
        
        # Formatação
        # EMBI tem coef muito pequeno, usar notação científica ou multiplicar?
        # Melhor mostrar como está, mas formatado
        if abs(coef) < 0.001:
            coef_str = f"{coef:.2e}"
        else:
            coef_str = f"{coef:.4f}"
            
        row = f"{name} & {coef_str}{stars} & {t:.2f} & {p:.4f} \\\\"
        latex_content.append(row)
        
    latex_content.extend([
        "\\midrule",
        f"Observações & {2461} & & \\\\", # Hardcoded do output anterior ou carregar df
        f"$R^2$ & {metrics['M4_R2']:.4f} & & \\\\",
        f"$R^2$ Ajustado & {metrics['M4_Adj_R2']:.4f} & & \\\\",
        "\\bottomrule",
        "\\multicolumn{4}{l}{\\footnotesize *** p<0.01, ** p<0.05, * p<0.1}",
        "\\end{tabular}",
        "\\end{table}"
    ])
    
    # Salvar
    with open(output_path, 'w') as f:
        f.write("\n".join(latex_content))
    
    print(f"Tabela salva em {output_path}")

if __name__ == "__main__":
    run()
