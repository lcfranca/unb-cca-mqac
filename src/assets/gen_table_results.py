"""
Tabela: Resultados CAPM
=======================

Gera tabela LaTeX com resultados da estimação CAPM.
Salva em data/outputs/tables/resultados_capm.tex
"""

import json
from pathlib import Path

def main():
    base_path = Path(__file__).resolve().parents[2]
    
    capm_path = base_path / "data" / "processed" / "capm_results.json"
    output_path = base_path / "data" / "outputs" / "tables" / "resultados_capm.tex"
    
    with open(capm_path, "r") as f:
        capm = json.load(f)
    
    beta = capm["beta"]
    alpha = capm["alpha_annual"]
    r_squared = capm["r_squared"]
    std_err = capm["std_err_beta"]
    p_value = capm["p_value_beta"]
    n = capm["n_observations"]
    rf = capm["rf_annual"]
    rm = capm["rm_annual"]
    r_petr4 = capm["r_petr4_annual"]
    market_premium = capm["market_premium"]
    ke = capm["ke_capm"]
    idio_vol = capm["idiosyncratic_volatility"]
    
    mispricing = r_petr4 - ke
    
    latex = r"""\begin{table}[H]
\centering
\caption{Resultados da Estimação CAPM — PETR4}
\label{tab:resultados_capm}
\begin{tabular}{lr}
\toprule
\textbf{Parâmetro} & \textbf{Valor} \\
\midrule
\multicolumn{2}{l}{\textit{Parâmetros da Regressão}} \\
Beta ($\beta$) & """ + f"{beta:.4f}" + r""" \\
Erro-padrão do Beta & """ + f"{std_err:.4f}" + r""" \\
p-valor & """ + f"{p_value:.6f}" + r""" \\
Alfa ($\alpha$) anualizado & """ + f"{alpha*100:.2f}" + r"""\% \\
$R^2$ & """ + f"{r_squared*100:.2f}" + r"""\% \\
Observações & """ + f"{n:,}".replace(",", ".") + r""" \\
\midrule
\multicolumn{2}{l}{\textit{Taxas de Retorno}} \\
Taxa Livre de Risco ($R_f$) & """ + f"{rf*100:.2f}" + r"""\% a.a. \\
Retorno de Mercado ($R_m$) & """ + f"{rm*100:.2f}" + r"""\% a.a. \\
Prêmio de Mercado ($R_m - R_f$) & """ + f"{market_premium*100:.2f}" + r"""\% a.a. \\
\midrule
\multicolumn{2}{l}{\textit{Custo de Capital}} \\
$K_e$ (CAPM) = $R_f + \beta(R_m - R_f)$ & """ + f"{ke*100:.2f}" + r"""\% a.a. \\
Retorno Realizado (PETR4) & """ + f"{r_petr4*100:.2f}" + r"""\% a.a. \\
\textbf{Mispricing} ($r_{realizado} - K_e$) & \textbf{""" + f"{mispricing*100:+.2f}" + r"""\%} \\
\midrule
\multicolumn{2}{l}{\textit{Risco}} \\
Volatilidade Idiossincrática & """ + f"{idio_vol*100:.2f}" + r"""\% a.a. \\
\bottomrule
\end{tabular}
\par\medskip\footnotesize
Nota: Período de """ + capm['period_start'] + r""" a """ + capm['period_end'] + r""". Regressão OLS dos retornos em excesso.
\end{table}
"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    
    print(f"✓ Tabela salva em: {output_path}")
    print(f"  Ke (CAPM): {ke*100:.2f}%")
    print(f"  Retorno Realizado: {r_petr4*100:.2f}%")
    print(f"  Mispricing: {mispricing*100:+.2f}%")

if __name__ == "__main__":
    main()
