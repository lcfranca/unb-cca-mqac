"""
Módulo de Coleta de Dados Macro (Fase 3).

Coleta e processa variáveis exógenas:
1. Petróleo Brent (Yahoo: BZ=F)
2. Câmbio USD/BRL (Yahoo: BRL=X)
3. Risco País EMBI+ (Ipeadata: JPM366_EMBI366)

Gera dataset consolidado para modelagem M4.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import ipeadatapy as ipea
from pathlib import Path
from src.core.config import PROJECT_ROOT

def fetch_yahoo_data(tickers, start_date, end_date):
    """Coleta dados do Yahoo Finance."""
    print(f"Coletando {tickers} via Yahoo Finance...")
    # auto_adjust=False garante que Adj Close exista
    df = yf.download(tickers, start=start_date, end=end_date, progress=False, auto_adjust=False)
    
    # Ajuste para múltiplos tickers ou único
    if len(tickers) == 1:
        if 'Adj Close' in df.columns:
            df = df['Adj Close'].to_frame()
        else:
            df = df['Close'].to_frame()
        df.columns = tickers
    else:
        if 'Adj Close' in df.columns:
            df = df['Adj Close']
        else:
            df = df['Close']
        
    return df

def fetch_embi(start_date):
    """Coleta EMBI+ via Ipeadata."""
    print("Coletando EMBI+ via Ipeadata...")
    try:
        # JPM366_EMBI366 - EMBI+ Risco Brasil (Pontos base)
        # Ipeadata retorna dataframe com índice data
        embi = ipea.timeseries('JPM366_EMBI366')
        
        # Filtrar data
        embi = embi[embi.index >= pd.to_datetime(start_date)]
        
        # Renomear coluna
        # O nome da coluna pode variar, vamos pegar a última coluna que geralmente é o valor
        # Ou usar o nome exato visto no teste: 'VALUE (-)'
        col_name = 'VALUE (-)'
        if col_name not in embi.columns:
            # Tentar encontrar coluna de valor
            cols = [c for c in embi.columns if 'VALUE' in c]
            if cols:
                col_name = cols[0]
        
        embi = embi[[col_name]].rename(columns={col_name: 'EMBI'})
        
        # Converter índice para datetime se não for
        embi.index = pd.to_datetime(embi.index)
        
        return embi
    except Exception as e:
        print(f"Erro ao coletar EMBI: {e}")
        return pd.DataFrame()

def run_fetch_macro():
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    returns_path = processed_dir / "returns" / "returns.parquet"
    output_path = processed_dir / "macro_returns.parquet"
    
    # Carregar dados existentes para pegar range de datas
    print("Carregando dados de retornos existentes...")
    df_returns = pd.read_parquet(returns_path).sort_values('date')
    start_date = df_returns['date'].min().strftime('%Y-%m-%d')
    end_date = df_returns['date'].max().strftime('%Y-%m-%d')
    
    print(f"Período: {start_date} a {end_date}")
    
    # 1. Coletar Yahoo (Brent e FX)
    # BZ=F: Brent Crude Oil Last Day Finance
    # BRL=X: USD/BRL Exchange Rate
    yahoo_tickers = ['BZ=F', 'BRL=X']
    df_yahoo = fetch_yahoo_data(yahoo_tickers, start_date, end_date)
    
    # 2. Coletar EMBI
    df_embi = fetch_embi(start_date)
    
    # 3. Unificar (Merge)
    # Usar índice de data
    df_yahoo.index = pd.to_datetime(df_yahoo.index).tz_localize(None)
    if not df_embi.empty:
        df_embi.index = pd.to_datetime(df_embi.index).tz_localize(None)
        
    # Merge tudo no dataframe de retornos original para garantir alinhamento
    df_macro = df_returns.set_index('date').copy()
    
    # Join Yahoo
    df_macro = df_macro.join(df_yahoo, how='left')
    
    # Join EMBI
    if not df_embi.empty:
        df_macro = df_macro.join(df_embi, how='left')
    else:
        print("AVISO: EMBI não disponível. Preenchendo com NaN.")
        df_macro['EMBI'] = np.nan
        
    # 4. Tratamento de Missing Values (Forward Fill)
    # Commodities e Câmbio podem ter feriados diferentes
    df_macro = df_macro.ffill()
    
    # 5. Engenharia de Features (Transformações)
    
    # Brent: Log Return
    df_macro['ret_brent'] = np.log(df_macro['BZ=F'] / df_macro['BZ=F'].shift(1))
    
    # FX: Log Return
    df_macro['ret_fx'] = np.log(df_macro['BRL=X'] / df_macro['BRL=X'].shift(1))
    
    # EMBI: First Difference (Delta)
    # EMBI é em pontos base (ex: 200, 300). Delta mostra variação do risco.
    df_macro['delta_embi'] = df_macro['EMBI'] - df_macro['EMBI'].shift(1)
    
    # Remover NaNs gerados pelos shifts
    df_macro = df_macro.dropna()
    
    # Reset index
    df_macro = df_macro.reset_index()
    
    # Salvar
    df_macro.to_parquet(output_path)
    print(f"Dados Macro salvos em {output_path}")
    print(df_macro[['date', 'ret_brent', 'ret_fx', 'delta_embi']].tail())

if __name__ == "__main__":
    run_fetch_macro()
