"""
prep_ml_data.py - Preparação de Dados para Machine Learning

Objetivo:
    Criar um dataset 'Model-Ready' que alinhe frequências (Diário vs Trimestral)
    e garanta causalidade temporal (evitar Look-Ahead Bias).

Inputs:
    - data/processed/macro_returns.parquet (Diário: Retornos + Macro)
    - data/processed/zscores/zscores.parquet (Trimestral: Z-Scores Fundamentalistas)

Output:
    - data/processed/ml_dataset.parquet
"""

import pandas as pd
import numpy as np
from pathlib import Path
from src.core.config import PROJECT_ROOT

def run():
    print("=== Iniciando Preparação de Dados para ML ===")
    
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    macro_path = processed_dir / "macro_returns.parquet"
    zscores_path = processed_dir / "zscores" / "zscores.parquet"
    output_path = processed_dir / "ml_dataset.parquet"
    
    # 1. Carregar Dados
    print("Carregando dados...")
    df_macro = pd.read_parquet(macro_path).sort_values('date')
    
    # Usar qval_timeseries em vez de zscores puro, pois já tem os scores compostos
    qval_path = processed_dir / "qval" / "qval_timeseries.parquet"
    if qval_path.exists():
        df_zscores = pd.read_parquet(qval_path).sort_values('quarter_end')
        print("Usando QVal Timeseries (com scores compostos).")
    else:
        df_zscores = pd.read_parquet(zscores_path).sort_values('quarter_end')
        print("AVISO: QVal Timeseries não encontrado. Usando Z-Scores brutos.")
    
    # 2. Alinhamento Temporal (Forward Fill Disciplinado)
    # Definir data de disponibilidade da informação fundamentalista
    # Conservador: 3 meses após o fim do trimestre (garante divulgação)
    df_zscores['available_date'] = pd.to_datetime(df_zscores['quarter_end']) + pd.DateOffset(months=3)
    
    # Selecionar colunas relevantes do Z-Score e Scores Compostos
    z_cols = [c for c in df_zscores.columns if c.startswith('z_') or c.startswith('score_')]
    df_zscores_ready = df_zscores[['available_date'] + z_cols].sort_values('available_date')
    
    print(f"Z-Scores Range: {df_zscores_ready['available_date'].min()} a {df_zscores_ready['available_date'].max()}")
    print(f"Macro Range: {df_macro['date'].min()} a {df_macro['date'].max()}")

    print(f"Realizando merge asof (Backward)...")
    # Merge asof: Para cada data em df_macro, pega o último available_date <= date
    df_merged = pd.merge_asof(
        df_macro,
        df_zscores_ready,
        left_on='date',
        right_on='available_date',
        direction='backward'
    )
    
    print(f"Shape após merge: {df_merged.shape}")
    print(f"Nulos em z_earnings_yield: {df_merged['z_earnings_yield'].isna().sum()}")
    
    # Debug: Check nulls per column
    print("Nulls per column in z_cols:")
    print(df_merged[z_cols].isna().sum())

    # Remover dados antes da primeira divulgação de balanço disponível
    # df_merged = df_merged.dropna(subset=z_cols)
    # Relaxar dropna: Apenas se TODAS as colunas Z forem nulas? Não, precisamos de features.
    # Vamos ver quais colunas estão problemáticas.
    
    # Se houver colunas inteiramente nulas (ex: z_roic se não tiver dados), vamos removê-las da lista de features em vez de dropar as linhas.
    valid_z_cols = [c for c in z_cols if df_merged[c].notna().sum() > 0]
    dropped_cols = set(z_cols) - set(valid_z_cols)
    if dropped_cols:
        print(f"AVISO: Colunas Z inteiramente nulas removidas do dataset: {dropped_cols}")
        df_merged = df_merged.drop(columns=list(dropped_cols))
    
    # Agora dropna apenas nas colunas válidas
    df_merged = df_merged.dropna(subset=valid_z_cols)
    print(f"Shape após dropna(valid_z_cols): {df_merged.shape}")
    
        # 3. Feature Engineering (Lags e Técnicos)
    print("Gerando Features (Lags e Técnicos)...")
    
    # Target 1: Retorno Excedente PETR4 (t+1) - Curto Prazo
    df_merged['target_return_1d'] = df_merged['excess_ret_petr4'].shift(-1)
    
    # Target 2: Retorno Excedente PETR4 (t+5) - Médio Prazo (Semanal)
    # Rolling sum dos próximos 5 dias
    indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=5)
    df_merged['target_return_5d'] = df_merged['excess_ret_petr4'].rolling(window=indexer).sum()
    
    # Target 3: Retorno Excedente PETR4 (t+21) - Longo Prazo (Mensal)
    indexer_21 = pd.api.indexers.FixedForwardWindowIndexer(window_size=21)
    df_merged['target_return_21d'] = df_merged['excess_ret_petr4'].rolling(window=indexer_21).sum()

    # Features de Lag (Momentum de Curto Prazo)
    df_merged['ret_lag1'] = df_merged['excess_ret_petr4'].shift(1)
    df_merged['ret_lag5'] = df_merged['excess_ret_petr4'].shift(5) # Semanal
    df_merged['ret_lag21'] = df_merged['excess_ret_petr4'].shift(21) # Mensal
    
    # Volatilidade Recente (20 dias)
    df_merged['vol_20d'] = df_merged['excess_ret_petr4'].rolling(window=20).std()
    
    # Regime de Mercado (SMA 200 do IBOV)
    # Reconstruir índice de preço a partir dos retornos para calcular SMA
    ibov_index = (1 + df_merged['ret_ibov']).cumprod()
    sma_200 = ibov_index.rolling(window=200).mean()
    df_merged['mkt_trend_sma200'] = (ibov_index > sma_200).astype(int) # 1 se Bull, 0 se Bear
    
    # Regime de Volatilidade (VIX Proxy - Volatilidade do IBOV)
    vol_ibov_20d = df_merged['ret_ibov'].rolling(window=20).std()
    vol_ibov_median = vol_ibov_20d.rolling(window=252).median() # Mediana móvel de 1 ano
    df_merged['mkt_vol_regime'] = (vol_ibov_20d > vol_ibov_median).astype(int) # 1 se Alta Vol, 0 se Baixa
    
    # 4. Feature Engineering (Interações)
    print("Gerando Features de Interação...")
    
    # Hipótese: Beta importa mais quando o mercado cai?
    if 'z_beta' in df_merged.columns:
        # Interação: Beta * Dummy de Queda do Mercado (ret_ibov < 0)
        down_market = (df_merged['ret_ibov'] < 0).astype(int)
        df_merged['inter_beta_mkt_down'] = df_merged['z_beta'] * down_market
        
        # Interação: Beta * Regime de Volatilidade
        df_merged['inter_beta_vol'] = df_merged['z_beta'] * df_merged['mkt_vol_regime']

    # Hipótese: Dívida importa mais quando juros (EMBI/Risco País) sobem?
    if 'z_debt_to_equity' in df_merged.columns:
        df_merged['inter_debt_embi'] = df_merged['z_debt_to_equity'] * df_merged['delta_embi']

    # Hipótese: Earnings Yield importa mais quando Brent cai? (Value Trap risk)
    if 'z_earnings_yield' in df_merged.columns:
        df_merged['inter_brent_earnings'] = df_merged['z_earnings_yield'] * df_merged['ret_brent']
        
    # Hipótese: Score de Valor importa mais em Bear Markets?
    if 'score_valor' in df_merged.columns:
        df_merged['inter_value_bear'] = df_merged['score_valor'] * (1 - df_merged['mkt_trend_sma200'])

    # 5. Feature Engineering (Informational Decay)
    print("Gerando Feature de Decaimento Informacional...")
    # Calcular dias desde a última divulgação (available_date)
    # available_date já está alinhado pelo merge_asof backward, então para cada linha,
    # available_date é a data da divulgação mais recente.
    df_merged['days_since_release'] = (df_merged['date'] - df_merged['available_date']).dt.days
    
    # Limpeza Final
    # Remover linhas com NaNs gerados pelos lags/rolling e targets
    # Cuidado para não remover o fim do dataset onde targets são NaN (para predição futura)
    # Mas para treino precisamos de targets.
    # Vamos manter NaNs nos targets por enquanto e filtrar no treino.
    
    # Drop NaNs apenas nas features
    feature_cols = [c for c in df_merged.columns if c not in ['target_return_1d', 'target_return_5d', 'target_return_21d']]
    df_merged = df_merged.dropna(subset=feature_cols)
    
    # Garantir que available_date e days_since_release sejam mantidos
    # Eles não são features de treino, mas metadados importantes para análise
    
    print(f"Shape Final: {df_merged.shape}")
    print(f"Colunas: {df_merged.columns.tolist()}")
    
    # Salvar
    df_merged.to_parquet(output_path)
    print(f"Dataset salvo em: {output_path}")

if __name__ == "__main__":
    run()

if __name__ == "__main__":
    run()
