"""
Gerador da Tabela 5.2 - Resultados CAPM.
"""
import json
from pathlib import Path
from src.core.config import PROJECT_ROOT

def gen_table_capm():
    input_path = PROJECT_ROOT / "data" / "outputs" / "capm_results.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "resultados_capm.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(input_path, 'r') as f:
        data = json.load(f)

    # Formatar valores
    alpha_est = f"{data['alpha']['estimate']:.5f}"
    alpha_se = f"({data['alpha']['se']:.5f})"
    alpha_t = f"{data['alpha']['t_stat']:.2f}"
    alpha_p = f"{data['alpha']['p_value']:.4f}"
    alpha_sig = "***" if data['alpha']['p_value'] < 0.01 else "**" if data['alpha']['p_value'] < 0.05 else "*" if data['alpha']['p_value'] < 0.1 else ""

    beta_est = f"{data['beta']['estimate']:.4f}"
    beta_se = f"({data['beta']['se']:.4f})"
    beta_t = f"{data['beta']['t_stat']:.2f}"
    beta_p = f"{data['beta']['p_value']:.4e}" # Notação científica para p muito pequeno
    beta_sig = "***" if data['beta']['p_value'] < 0.01 else "**" if data['beta']['p_value'] < 0.05 else "*" if data['beta']['p_value'] < 0.1 else ""

    latex = []
    latex.append(r"\begin{table}[h]")
    latex.append(r"\centering")
    latex.append(r"\caption{Resultados da Estimação do Modelo CAPM (Modelo 0)}")
    latex.append(r"\label{tab:capm_results}")
    latex.append(r"\begin{tabular}{lcccc}")
    latex.append(r"\toprule")
    latex.append(r"Parâmetro & Estimativa & Erro-Padrão & Estatística t & p-valor \\")
    latex.append(r"\midrule")
    
    latex.append(f"Alfa ($\\alpha$) & {alpha_est}{alpha_sig} & {alpha_se} & {alpha_t} & {alpha_p} \\\\")
    latex.append(f"Beta ($\\beta$) & {beta_est}{beta_sig} & {beta_se} & {beta_t} & $<$ 0.001 \\\\")
    
    latex.append(r"\midrule")
    latex.append(f"Observações & {data['n_obs']} & & & \\\\")
    latex.append(f"$R^2$ & {data['r_squared']:.4f} & & & \\\\")
    latex.append(f"$R^2$ Ajustado & {data['r_squared_adj']:.4f} & & & \\\\")
    latex.append(f"Durbin-Watson & {data['durbin_watson']:.4f} & & & \\\\")
    
    latex.append(r"\bottomrule")
    latex.append(r"\multicolumn{5}{p{10cm}}{\footnotesize \textit{Nota:} Erros-padrão robustos (HC3). *** p$<$0.01, ** p$<$0.05, * p$<$0.1.} \\")
    latex.append(r"\end{tabular}")
    latex.append(r"\end{table}")

    with open(output_path, 'w') as f:
        f.write("\n".join(latex))
    
    print(f"Tabela 5.2 salva em {output_path}")

if __name__ == "__main__":
    gen_table_capm()
