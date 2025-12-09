"""
Gerador da Tabela 5.1 - Estatísticas Descritivas.
"""
import json
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def gen_table_descriptive():
    input_path = PROJECT_ROOT / "data" / "outputs" / "descriptive_stats.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "estatisticas_descritivas.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(input_path, 'r') as f:
        data = json.load(f)

    # Painel A: Retornos
    rows_a = []
    for asset, label in [('petr4', 'PETR4'), ('ibov', 'Ibovespa')]:
        stats = data['returns'][f'ret_{asset}']
        row = {
            "Variável": label,
            "Média": f"{stats['mean']*100:.2f}\%",
            "Mediana": f"{stats['median']*100:.2f}\%",
            "D.P.": f"{stats['std']*100:.2f}\%",
            "Mín": f"{stats['min']*100:.2f}\%",
            "Máx": f"{stats['max']*100:.2f}\%",
            "Assim.": f"{stats['skew']:.2f}",
            "Curt.": f"{stats['kurt']:.2f}"
        }
        rows_a.append(row)
    
    df_a = pd.DataFrame(rows_a)

    # Painel B: Métricas (Selecionadas)
    metrics_map = {
        'earnings_yield': 'Earnings Yield',
        'ev_ebitda': 'EV/EBITDA',
        'pb_ratio': 'P/VP',
        'dividend_yield': 'Dividend Yield',
        'roe': 'ROE',
        'debt_equity': 'Dívida/PL'
    }
    
    rows_b = []
    if 'metrics' in data:
        for key, label in metrics_map.items():
            if key in data['metrics']:
                stats = data['metrics'][key]
                # Algumas métricas são percentuais, outras absolutas
                is_pct = key in ['earnings_yield', 'dividend_yield', 'roe']
                mult = 100 if is_pct else 1
                suffix = "\%" if is_pct else ""
                
                row = {
                    "Variável": label,
                    "Média": f"{stats['mean']*mult:.2f}{suffix}",
                    "Mediana": f"{stats['median']*mult:.2f}{suffix}",
                    "D.P.": f"{stats['std']*mult:.2f}{suffix}",
                    "Mín": f"{stats['min']*mult:.2f}{suffix}",
                    "Máx": f"{stats['max']*mult:.2f}{suffix}",
                    "Assim.": f"{stats['skew']:.2f}",
                    "Curt.": f"{stats['kurt']:.2f}"
                }
                rows_b.append(row)

    df_b = pd.DataFrame(rows_b)

    # Gerar LaTeX manual para controle total
    latex = []
    latex.append(r"\begin{table}[h]")
    latex.append(r"\centering")
    latex.append(r"\caption{Estatísticas Descritivas dos Retornos e Métricas Fundamentalistas}")
    latex.append(r"\label{tab:desc_stats}")
    latex.append(r"\begin{tabular}{lccccccc}")
    latex.append(r"\toprule")
    latex.append(r"Variável & Média & Mediana & D.P. & Mín & Máx & Assim. & Curt. \\")
    
    latex.append(r"\midrule")
    latex.append(r"\multicolumn{8}{l}{\textit{Painel A: Retornos Diários}} \\")
    for _, row in df_a.iterrows():
        line = f"{row['Variável']} & {row['Média']} & {row['Mediana']} & {row['D.P.']} & {row['Mín']} & {row['Máx']} & {row['Assim.']} & {row['Curt.']} \\\\"
        latex.append(line)
        
    latex.append(r"\midrule")
    latex.append(r"\multicolumn{8}{l}{\textit{Painel B: Métricas Fundamentalistas (Trimestrais)}} \\")
    for _, row in df_b.iterrows():
        line = f"{row['Variável']} & {row['Média']} & {row['Mediana']} & {row['D.P.']} & {row['Mín']} & {row['Máx']} & {row['Assim.']} & {row['Curt.']} \\\\"
        latex.append(line)
        
    latex.append(r"\bottomrule")
    latex.append(r"\multicolumn{8}{p{12cm}}{\footnotesize \textit{Nota:} Retornos diários logarítmicos. Métricas fundamentalistas calculadas trimestralmente. Período: 2016-2025.} \\")
    latex.append(r"\end{tabular}")
    latex.append(r"\end{table}")

    with open(output_path, 'w') as f:
        f.write("\n".join(latex))
    
    print(f"Tabela 5.1 salva em {output_path}")

if __name__ == "__main__":
    gen_table_descriptive()
