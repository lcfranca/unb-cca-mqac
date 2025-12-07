"""
Gerador da Tabela 5.3 - Score Q-VAL e Componentes.
"""
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def gen_table_qval_score():
    qval_path = PROJECT_ROOT / "data" / "processed" / "qval" / "qval_timeseries.parquet"
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "score_comprabilidade.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(qval_path)
    last_row = df.iloc[-1]
    
    # Mapeamento de métricas para labels
    # Nota: O arquivo qval_timeseries.parquet tem os Z-Scores agregados e o score final.
    # Para ter os componentes individuais (z_earnings_yield, etc), precisamos garantir que eles estão lá.
    # O script calc_qval_timeseries.py salva tudo.
    
    # Estrutura hierárquica
    structure = {
        "VALOR": [
            ("Earnings Yield", "z_earnings_yield"),
            ("EV/EBITDA", "z_ev_ebitda"),
            ("P/VP", "z_pb_ratio"),
            ("Dividend Yield", "z_dividend_yield")
        ],
        "QUALIDADE": [
            ("ROIC", "z_roic"),
            ("ROE", "z_roe"),
            ("Margem EBITDA", "z_ebitda_margin"),
            ("EVS", "z_evs")
        ],
        "RISCO": [
            ("Beta", "z_beta"),
            ("Volatilidade", "z_volatility"),
            ("Dívida/PL", "z_debt_to_equity") # Nome da coluna pode variar, checar
        ]
    }
    
    # Verificar nome correto da coluna de dívida
    debt_col = 'z_debt_to_equity' if 'z_debt_to_equity' in df.columns else 'z_debt_equity'

    latex = []
    latex.append(r"\begin{table}[h]")
    latex.append(r"\centering")
    latex.append(f"\\caption{{Decomposição do Score Q-VAL (Trimestre: {last_row['quarter_end'].date()})}}")
    latex.append(r"\label{tab:qval_score}")
    latex.append(r"\begin{tabular}{lccc}")
    latex.append(r"\toprule")
    latex.append(r"Dimensão / Métrica & Z-Score & Peso & Contribuição \\")
    latex.append(r"\midrule")
    
    # Dimensão VALOR
    latex.append(r"\textbf{VALOR} & & \textbf{33.3\%} & \textbf{" + f"{last_row['score_valor']:.2f}" + r"} \\")
    for label, col in structure["VALOR"]:
        val = last_row.get(col, 0)
        latex.append(f"\\hspace{{3mm}} {label} & {val:+.2f} & 25\% & {val*0.25:+.2f} \\\\")
        
    latex.append(r"\midrule")
    
    # Dimensão QUALIDADE
    latex.append(r"\textbf{QUALIDADE} & & \textbf{33.3\%} & \textbf{" + f"{last_row['score_qualidade']:.2f}" + r"} \\")
    for label, col in structure["QUALIDADE"]:
        val = last_row.get(col, 0)
        latex.append(f"\\hspace{{3mm}} {label} & {val:+.2f} & 25\% & {val*0.25:+.2f} \\\\")
        
    latex.append(r"\midrule")
    
    # Dimensão RISCO
    latex.append(r"\textbf{RISCO} & & \textbf{33.3\%} & \textbf{" + f"{last_row['score_risco']:.2f}" + r"} \\")
    # Ajustar lista de risco com coluna correta
    risk_metrics = [("Beta", "z_beta"), ("Volatilidade", "z_volatility"), ("Dívida/PL", debt_col)]
    for label, col in risk_metrics:
        val = last_row.get(col, 0)
        latex.append(f"\\hspace{{3mm}} {label} & {val:+.2f} & 33\% & {val*0.333:+.2f} \\\\")
        
    latex.append(r"\midrule")
    latex.append(r"\midrule")
    
    # Score Final
    latex.append(r"\textbf{SCORE FINAL (0-100)} & & & \textbf{" + f"{last_row['qval_scaled']:.2f}" + r"} \\")
    latex.append(r"\textbf{Recomendação} & & & \textbf{" + f"{last_row['recommendation']}" + r"} \\")
    
    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}")
    latex.append(r"\end{table}")

    with open(output_path, 'w') as f:
        f.write("\n".join(latex))
    
    print(f"Tabela 5.3 salva em {output_path}")

if __name__ == "__main__":
    gen_table_qval_score()
