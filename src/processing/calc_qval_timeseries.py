"""
Módulo de Cálculo da Série Temporal Q-VAL (Asset 2.4).

Agrega os Z-Scores nas dimensões de Valor, Qualidade e Risco,
calcula o score Q-VAL composto e gera recomendações de investimento.

Input:
    - data/processed/zscores.parquet

Output:
    - data/processed/qval_timeseries.parquet
"""

import pandas as pd
import numpy as np
from pathlib import Path
from src.core.config import PROJECT_ROOT

def calculate_qval():
    processed_dir = PROJECT_ROOT / "data" / "processed"
    input_path = processed_dir / "zscores" / "zscores.parquet"
    
    output_dir = processed_dir / "qval"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_parquet = output_dir / "qval_timeseries.parquet"
    output_csv = output_dir / "qval_timeseries.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo {input_path} não encontrado.")

    print("Carregando Z-Scores...")
    df = pd.read_parquet(input_path)
    df.set_index('quarter_end', inplace=True)

    # Definição dos componentes
    components = {
        'score_valor': ['z_earnings_yield', 'z_ev_ebitda', 'z_pb_ratio', 'z_dividend_yield'],
        'score_qualidade': ['z_roic', 'z_roe', 'z_ebitda_margin', 'z_evs'],
        'score_risco': ['z_beta', 'z_volatility', 'z_debt_to_equity']
    }

    print("Calculando scores dimensionais...")
    
    # Calcular média simples para cada dimensão, ignorando NaNs
    for dim_name, cols in components.items():
        # Verificar colunas existentes
        valid_cols = [c for c in cols if c in df.columns]
        if len(valid_cols) < len(cols):
            missing = set(cols) - set(valid_cols)
            print(f"Aviso: Colunas faltantes para {dim_name}: {missing}")
        
        if valid_cols:
            df[dim_name] = df[valid_cols].mean(axis=1)
        else:
            df[dim_name] = np.nan

    print("Calculando Q-VAL Agregado...")
    
    # Q-VAL Bruto = Média das 3 dimensões
    # Se alguma dimensão for NaN, o resultado será NaN (comportamento padrão do pandas + mean se skipna=False, mas aqui queremos ser estritos?)
    # Vamos permitir skipna=False para exigir as 3 dimensões?
    # Como é uma série histórica longa, pode haver momentos sem dados.
    # Vamos usar mean(axis=1) que por padrão faz skipna=True, mas vamos monitorar.
    
    dims = ['score_valor', 'score_qualidade', 'score_risco']
    df['qval_raw'] = df[dims].mean(axis=1)
    
    # Transformação para escala 0-100
    # Q-VAL Scaled = 50 + 10 * Raw
    df['qval_scaled'] = 50 + 10 * df['qval_raw']
    
    # Clip para garantir limites razoáveis (opcional, mas estético)
    # df['qval_scaled'] = df['qval_scaled'].clip(0, 100) 
    # A metodologia não menciona clip, mas Z-scores podem ser extremos. Vamos manter raw.

    print("Gerando recomendações...")
    def get_recommendation(score):
        if pd.isna(score):
            return "INSUFICIENTE"
        if score > 60:
            return "COMPRA"
        elif score < 40:
            return "VENDA"
        else:
            return "NEUTRO"

    df['recommendation'] = df['qval_scaled'].apply(get_recommendation)

    # Salvar
    print(f"Salvando em {output_dir}...")
    df.reset_index(inplace=True)
    df.to_parquet(output_parquet)
    df.to_csv(output_csv, index=False)
    
    # Preview
    latest = df.iloc[-1]
    print("-" * 30)
    print(f"Último Trimestre: {latest['quarter_end']}")
    print(f"Q-VAL Score: {latest['qval_scaled']:.2f}")
    print(f"Recomendação: {latest['recommendation']}")
    print("-" * 30)
    print("Concluído.")

if __name__ == "__main__":
    calculate_qval()
