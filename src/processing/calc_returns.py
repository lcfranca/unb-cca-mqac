"""
Módulo de Cálculo de Retornos (Asset 2.1).

Calcula retornos logarítmicos diários e retornos em excesso para PETR4 e Ibovespa,
utilizando o CDI diário como taxa livre de risco.

Input:
    - data/processed/prices_petr4.parquet
    - data/processed/ibovespa.parquet
    - data/processed/cdi.parquet

Output:
    - data/processed/returns.parquet
"""

import pandas as pd
import numpy as np
from pathlib import Path
from src.core.config import PROJECT_ROOT

def calculate_returns():
    """
    Calcula retornos logarítmicos e em excesso.
    """
    # Caminhos dos arquivos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    prices_path = processed_dir / "prices" / "prices_petr4.parquet"
    ibov_path = processed_dir / "ibovespa" / "ibovespa.parquet"
    cdi_path = processed_dir / "cdi" / "cdi.parquet"
    
    # Output directory
    output_dir = processed_dir / "returns"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_parquet = output_dir / "returns.parquet"
    output_csv = output_dir / "returns.csv"

    # Verificar existência dos arquivos
    if not all(p.exists() for p in [prices_path, ibov_path, cdi_path]):
        raise FileNotFoundError("Arquivos de entrada não encontrados em data/processed/")

    # 1. Carregar dados
    print("Carregando dados...")
    df_petr4 = pd.read_parquet(prices_path)
    df_ibov = pd.read_parquet(ibov_path)
    df_cdi = pd.read_parquet(cdi_path)

    # Garantir que 'date' é datetime e setar como index
    for df in [df_petr4, df_ibov, df_cdi]:
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

    # 2. Calcular Retornos Logarítmicos
    # R_t = ln(P_t / P_{t-1})
    print("Calculando retornos logarítmicos...")
    
    # PETR4
    df_petr4['ret_petr4'] = np.log(df_petr4['adjusted_close'] / df_petr4['adjusted_close'].shift(1))
    
    # Ibovespa
    df_ibov['ret_ibov'] = np.log(df_ibov['adjusted_close'] / df_ibov['adjusted_close'].shift(1))

    # 3. Merge das séries
    print("Unificando séries...")
    # Começamos com PETR4 como base
    df_returns = df_petr4[['ret_petr4']].copy()
    
    # Join com Ibovespa
    df_returns = df_returns.join(df_ibov[['ret_ibov']], how='inner')
    
    # Join com CDI
    # O CDI já deve estar em taxa diária decimal (ex: 0.0004 para 0.04%)
    df_returns = df_returns.join(df_cdi[['cdi_daily']], how='inner')

    # 4. Calcular Retornos em Excesso
    print("Calculando retornos em excesso...")
    df_returns['excess_ret_petr4'] = df_returns['ret_petr4'] - df_returns['cdi_daily']
    df_returns['excess_ret_ibov'] = df_returns['ret_ibov'] - df_returns['cdi_daily']

    # 5. Limpeza
    # Remover NaNs (primeira linha devido ao shift, ou dias sem CDI)
    initial_len = len(df_returns)
    df_returns.dropna(inplace=True)
    final_len = len(df_returns)
    print(f"Removidas {initial_len - final_len} linhas com dados faltantes.")

    # Reset index para salvar 'date' como coluna
    df_returns.reset_index(inplace=True)

    # 6. Salvar
    print(f"Salvando em {output_dir}...")
    df_returns.to_parquet(output_parquet)
    df_returns.to_csv(output_csv, index=False)
    print("Concluído.")

if __name__ == "__main__":
    calculate_returns()
