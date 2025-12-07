"""
Gerador de Tabela de Comparação de Modelos (Asset 3.3).

Re-estima os modelos M0-M3 e gera uma tabela LaTeX formatada para a Nota Técnica.
Inclui coeficientes, t-stats (entre parênteses), R2 Ajustado, AIC e BIC.
"""

import pandas as pd
import statsmodels.api as sm
import numpy as np
from pathlib import Path
from src.core.config import PROJECT_ROOT

def gen_table_models():
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    returns_path = processed_dir / "returns" / "returns.parquet"
    qval_path = processed_dir / "qval" / "qval_timeseries.parquet"
    
    output_dir = PROJECT_ROOT / "data" / "outputs" / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "comparacao_modelos.tex"

    # 1. Carregar e Preparar Dados (Mesma lógica de estimate_models.py)
    df_ret = pd.read_parquet(returns_path)
    df_qval = pd.read_parquet(qval_path)
    
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    qval_cols = ['available_date', 'z_earnings_yield', 'score_valor', 'score_qualidade', 'score_risco', 'qval_scaled']
    df_qval_ready = df_qval[qval_cols].sort_values('available_date')
    
    df_ret = df_ret.sort_values('date')
    df_merged = pd.merge_asof(df_ret, df_qval_ready, left_on='date', right_on='available_date', direction='backward')
    
    required_cols = ['excess_ret_petr4', 'excess_ret_ibov', 'z_earnings_yield', 
                     'score_valor', 'score_qualidade', 'score_risco', 'qval_scaled']
    df_model = df_merged.dropna(subset=required_cols).copy()

    # 2. Definir e Estimar Modelos
    models_config = {
        "M0 (CAPM)": ["excess_ret_ibov"],
        "M1 (Fator Único)": ["excess_ret_ibov", "z_earnings_yield"],
        "M2 (Multifator)": ["excess_ret_ibov", "score_valor", "score_qualidade", "score_risco"],
        "M3 (Q-VAL)": ["excess_ret_ibov", "qval_scaled"]
    }

    results_list = []

    for label, features in models_config.items():
        y = df_model['excess_ret_petr4']
        X = sm.add_constant(df_model[features])
        model = sm.OLS(y, X).fit(cov_type='HC3')
        
        # Formatar resultados para a tabela
        res_dict = {"Modelo": label}
        
        # Alpha
        alpha = model.params['const']
        alpha_t = model.tvalues['const']
        res_dict["Alpha"] = f"{alpha:.4f} ({alpha_t:.2f})"
        
        # Beta (Mercado)
        beta = model.params['excess_ret_ibov']
        beta_t = model.tvalues['excess_ret_ibov']
        res_dict["Beta (Rm)"] = f"{beta:.4f} ({beta_t:.2f})"
        
        # Outros coeficientes (agregados ou específicos)
        # Para simplificar a tabela, vamos focar nas métricas de ajuste, 
        # mas podemos listar coeficientes extras se necessário.
        # Aqui vamos listar apenas se são significativos ou colocar "Sim"
        
        res_dict["Adj R2"] = f"{model.rsquared_adj:.4f}"
        res_dict["AIC"] = f"{model.aic:.1f}"
        res_dict["BIC"] = f"{model.bic:.1f}"
        
        results_list.append(res_dict)

    # 3. Gerar DataFrame e LaTeX
    df_table = pd.DataFrame(results_list)
    
    latex_code = df_table.to_latex(
        index=False,
        caption="Comparação de Modelos de Precificação (M0 a M3)",
        label="tab:model_comparison",
        column_format="lccccc",
        position="h"
    )
    
    # Ajustes finos no LaTeX (opcional)
    latex_code = latex_code.replace("toprule", "hline").replace("midrule", "hline").replace("bottomrule", "hline")

    with open(output_path, 'w') as f:
        f.write(latex_code)
        
    print(f"Tabela salva em {output_path}")
    print(df_table)

if __name__ == "__main__":
    gen_table_models()
