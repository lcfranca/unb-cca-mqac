"""
Gerador da Tabela 5.5 - Critérios de Informação (AIC/BIC).
"""
import json
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def gen_table_aic_bic():
    input_path = PROJECT_ROOT / "data" / "outputs" / "model_comparison.json"
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "criterios_informacao.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(input_path, 'r') as f:
        results = json.load(f)
    
    # Mapeamento de nomes
    model_names = {
        "M0_CAPM": "M0: CAPM",
        "M1_SingleFactor": "M1: CAPM + Earnings Yield",
        "M2_MultiFactor": "M2: CAPM + Valor + Qualidade + Risco",
        "M3_QVAL": "M3: CAPM + Q-VAL Score"
    }
    
    # Preparar dados para DataFrame
    data = []
    for key, metrics in results.items():
        data.append({
            "Modelo": model_names.get(key, key),
            "AIC": metrics["aic"],
            "BIC": metrics["bic"],
            "Adj R2": metrics["adj_r_squared"]
        })
    
    df = pd.DataFrame(data)
    
    # Calcular Delta AIC/BIC em relação ao melhor (menor valor)
    min_aic = df["AIC"].min()
    min_bic = df["BIC"].min()
    
    df["Delta AIC"] = df["AIC"] - min_aic
    df["Delta BIC"] = df["BIC"] - min_bic
    
    # Ordenar por AIC
    df = df.sort_values("AIC")
    
    latex = []
    latex.append(r"\begin{table}[h]")
    latex.append(r"\centering")
    latex.append(r"\caption{Seleção de Modelos via Critérios de Informação}")
    latex.append(r"\label{tab:aic_bic}")
    latex.append(r"\begin{tabular}{lccccc}")
    latex.append(r"\toprule")
    latex.append(r"Modelo & AIC & $\Delta$ AIC & BIC & $\Delta$ BIC & Adj. $R^2$ \\")
    latex.append(r"\midrule")
    
    for _, row in df.iterrows():
        # Formatação
        aic_str = f"{row['AIC']:.1f}"
        bic_str = f"{row['BIC']:.1f}"
        delta_aic_str = f"{row['Delta AIC']:.1f}"
        delta_bic_str = f"{row['Delta BIC']:.1f}"
        r2_str = f"{row['Adj R2']:.4f}"
        
        # Destaque para o melhor modelo (Delta = 0)
        if row['Delta AIC'] == 0:
            delta_aic_str = r"\textbf{0.0}"
        if row['Delta BIC'] == 0:
            delta_bic_str = r"\textbf{0.0}"
            
        latex.append(f"{row['Modelo']} & {aic_str} & {delta_aic_str} & {bic_str} & {delta_bic_str} & {r2_str} \\\\")
        
    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}")
    latex.append(r"\footnotesize")
    latex.append(r"Nota: Menores valores de AIC/BIC indicam melhor trade-off entre ajuste e complexidade.")
    latex.append(r"\end{table}")

    with open(output_path, 'w') as f:
        f.write("\n".join(latex))
    
    print(f"Tabela 5.5 salva em {output_path}")

if __name__ == "__main__":
    gen_table_aic_bic()
