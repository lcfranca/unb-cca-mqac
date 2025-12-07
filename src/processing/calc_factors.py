"""
Cálculo de Proxies para Fatores Fama-French (Adaptado para Single Stock).

Gera as séries temporais de características da firma que servem como proxies
para os fatores de risco/estilo:
1. CMA (Conservative Minus Aggressive) -> Proxy: Crescimento de Ativos (Asset Growth)
2. RMW (Robust Minus Weak) -> Proxy: ROE ou Margem EBITDA (Profitability)

Entrada:
    - data/processed/fundamentals/fundamentals_petr4.parquet
Saída:
    - data/processed/factors/petr4_factors.parquet
"""

import pandas as pd
import numpy as np
from pathlib import Path
from src.core.config import PROJECT_ROOT

def calculate_factors():
    # Caminhos
    input_path = PROJECT_ROOT / "data" / "processed" / "fundamentals" / "fundamentals_petr4.parquet"
    output_dir = PROJECT_ROOT / "data" / "processed" / "factors"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "petr4_factors.parquet"
    
    print(f"Lendo fundamentos de {input_path}...")
    df = pd.read_parquet(input_path)
    df = df.sort_values('quarter_end')
    
    # 1. CMA Proxy: Asset Growth
    # Variação percentual anual dos ativos totais
    # Como os dados são trimestrais, podemos fazer YoY ou QoQ. 
    # Fama-French usa variação anual. Vamos usar YoY para suavizar sazonalidade.
    df['asset_growth_yoy'] = df['total_assets'].pct_change(periods=4)
    
    # Se não tiver histórico suficiente para YoY no começo, preencher ou deixar NaN
    # Vamos usar fillna(0) para o começo ou bfill, mas ideal é deixar NaN e cortar na regressão
    
    # 2. RMW Proxy: Profitability (ROE)
    # ROE já vem calculado, mas vamos garantir
    # Se ROE não estiver disponível, usar Net Margin
    if 'roe' in df.columns:
        df['profitability'] = df['roe']
    else:
        df['profitability'] = df['net_margin']
        
    # 3. Padronização (Z-Score Rolling)
    # Para evitar look-ahead bias, idealmente usar janela expansiva ou fixa.
    # Aqui vamos usar Z-Score expansivo (com mínimo de 4 trimestres)
    
    def expanding_zscore(series):
        return (series - series.expanding(min_periods=4).mean()) / series.expanding(min_periods=4).std()
    
    df['cma_proxy'] = expanding_zscore(df['asset_growth_yoy'])
    df['rmw_proxy'] = expanding_zscore(df['profitability'])
    
    # Selecionar colunas finais
    cols = ['quarter_end', 'total_assets', 'asset_growth_yoy', 'profitability', 'cma_proxy', 'rmw_proxy']
    df_factors = df[cols].dropna().copy()
    
    # Disponibilidade da informação (Lag de publicação)
    # Assumimos que a informação do trimestre T está disponível em T + 3 meses (conservador)
    df_factors['available_date'] = pd.to_datetime(df_factors['quarter_end']) + pd.DateOffset(months=3)
    
    print(f"Fatores calculados. Amostra: {len(df_factors)} trimestres.")
    print(df_factors[['quarter_end', 'cma_proxy', 'rmw_proxy']].tail())
    
    df_factors.to_parquet(output_path)
    print(f"Salvo em {output_path}")

if __name__ == "__main__":
    calculate_factors()
