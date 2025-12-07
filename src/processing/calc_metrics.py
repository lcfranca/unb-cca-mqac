"""
Módulo de Cálculo de Métricas (Asset 2.2).

Calcula métricas fundamentalistas derivadas e métricas de mercado (Beta, Volatilidade)
em janelas móveis, consolidando em uma base trimestral.

Input:
    - data/processed/fundamentals_petr4.parquet
    - data/processed/returns.parquet
    - data/processed/cdi.parquet

Output:
    - data/processed/metrics.parquet
"""

import pandas as pd
import numpy as np
from pathlib import Path
from src.core.config import PROJECT_ROOT, load_params

def calculate_metrics():
    processed_dir = PROJECT_ROOT / "data" / "processed"
    fund_path = processed_dir / "fundamentals" / "fundamentals_petr4.parquet"
    
    # Input from previous step
    returns_path = processed_dir / "returns" / "returns.parquet"
    
    cdi_path = processed_dir / "cdi" / "cdi.parquet"
    
    # Output directory
    output_dir = processed_dir / "metrics"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_parquet = output_dir / "metrics.parquet"
    output_csv = output_dir / "metrics.csv"

    if not all(p.exists() for p in [fund_path, returns_path, cdi_path]):
        raise FileNotFoundError(f"Arquivos de entrada necessários não encontrados: {[p for p in [fund_path, returns_path, cdi_path] if not p.exists()]}")

    # Load params (only for weights or other non-financial assumptions if needed)
    # params = load_params()
    
    print("Carregando dados...")
    df_fund = pd.read_parquet(fund_path)
    df_ret = pd.read_parquet(returns_path)
    df_cdi = pd.read_parquet(cdi_path)
    
    # =========================================================================
    # 0. Cálculo Dinâmico de Premissas (MRP e Tax Rate)
    # =========================================================================
    print("Calculando premissas financeiras dinamicamente...")
    
    # 1. Market Risk Premium (MRP)
    # Média histórica do retorno em excesso do mercado (Ibovespa - CDI)
    # Usamos todo o histórico disponível no arquivo de retornos
    if 'excess_ret_ibov' in df_ret.columns:
        # Retorno diário médio * 252
        avg_daily_excess = df_ret['excess_ret_ibov'].mean()
        mrp = avg_daily_excess * 252
        print(f"MRP calculado (média histórica): {mrp:.4f} ({mrp*100:.2f}%)")
    else:
        print("Aviso: 'excess_ret_ibov' não encontrado. Usando fallback 6%.")
        mrp = 0.06

    # 2. Tax Rate Efetiva
    # Média histórica de (Income Tax Expense / Income Before Tax)
    # Se colunas não existirem, usar estatutária 34%
    if 'tax_provision' in df_fund.columns and 'pre_tax_income' in df_fund.columns:
        # Evitar divisão por zero
        valid_tax = df_fund[df_fund['pre_tax_income'] != 0].copy()
        if not valid_tax.empty:
            valid_tax['effective_tax_rate'] = valid_tax['tax_provision'] / valid_tax['pre_tax_income']
            # Filtrar outliers (tax rate negativo ou > 100% pode acontecer em ajustes contábeis, mas para valuation queremos a normalizada)
            # Vamos pegar a mediana para ser robusto a outliers
            tax_rate = valid_tax['effective_tax_rate'].median()
            
            # Tax provision geralmente é negativo no DRE? Depende da fonte.
            # Se tax_provision for negativo (despesa) e income positivo, rate é negativo.
            # Vamos assumir que queremos a taxa positiva (0.34).
            tax_rate = abs(tax_rate)
            
            # Clamp entre 0 e 1 (ou 0 e 0.5) para sanidade
            if tax_rate > 0.5 or tax_rate < 0.1:
                 print(f"Aviso: Tax Rate calculado ({tax_rate:.2f}) fora do comum. Usando 34%.")
                 tax_rate = 0.34
            else:
                print(f"Tax Rate efetiva calculada (mediana): {tax_rate:.4f} ({tax_rate*100:.2f}%)")
        else:
            tax_rate = 0.34
    else:
        print("Colunas de imposto não encontradas. Usando alíquota estatutária 34%.")
        tax_rate = 0.34

    # Garantir datetime
    df_fund['quarter_end'] = pd.to_datetime(df_fund['quarter_end'])
    df_ret['date'] = pd.to_datetime(df_ret['date'])
    df_cdi['date'] = pd.to_datetime(df_cdi['date'])

    # Set index
    df_ret.set_index('date', inplace=True)
    df_cdi.set_index('date', inplace=True)

    # =========================================================================
    # 1. Cálculo de Métricas de Mercado (Rolling Window)
    # =========================================================================
    print("Calculando Beta e Volatilidade (Rolling 252 dias)...")
    
    window = 252
    
    # Volatilidade Anualizada
    # Std Dev diário * sqrt(252)
    rolling_std = df_ret['ret_petr4'].rolling(window=window).std()
    df_ret['volatility'] = rolling_std * np.sqrt(252)

    # Beta
    # Cov(Ri, Rm) / Var(Rm)
    rolling_cov = df_ret['ret_petr4'].rolling(window=window).cov(df_ret['ret_ibov'])
    rolling_var = df_ret['ret_ibov'].rolling(window=window).var()
    df_ret['beta'] = rolling_cov / rolling_var

    # Resample para trimestral (pegando o último valor do trimestre)
    # Precisamos alinhar com as datas de quarter_end do df_fund
    # Vamos fazer um merge asof ou merge normal baseado na data mais próxima anterior
    
    # =========================================================================
    # 2. Cálculo de Métricas Fundamentalistas Derivadas
    # =========================================================================
    print("Calculando métricas fundamentalistas...")
    
    # Earnings Yield = 1 / P/L
    df_fund['earnings_yield'] = 1 / df_fund['pe_ratio']
    
    # EBITDA Margin = EBITDA / Revenue
    df_fund['ebitda_margin'] = df_fund['ebitda'] / df_fund['revenue']
    
    # ROIC (Aproximação)
    # NOPAT ~ EBITDA * (1 - t)
    # Invested Capital ~ Total Debt + Equity
    nopat = df_fund['ebitda'] * (1 - tax_rate)
    invested_capital = df_fund['total_debt'] + df_fund['equity']
    df_fund['roic'] = nopat / invested_capital
    
    # Tratamento de divisão por zero ou nulos
    df_fund.replace([np.inf, -np.inf], np.nan, inplace=True)

    # =========================================================================
    # 3. Integração Mercado + Fundamentos
    # =========================================================================
    print("Integrando dados de mercado e fundamentos...")
    
    # Ordenar por data
    df_fund.sort_values('quarter_end', inplace=True)
    df_ret.sort_index(inplace=True)
    
    # Para cada quarter_end, pegar o beta e vol do dia (ou dia útil anterior)
    market_metrics = df_ret[['beta', 'volatility']].reset_index()
    
    df_merged = pd.merge_asof(
        df_fund,
        market_metrics,
        left_on='quarter_end',
        right_on='date',
        direction='backward'
    )
    
    # Pegar CDI anual para o cálculo do WACC/Ke
    # O CDI está diário, precisamos do anualizado ou pegar da coluna cdi_annual se existir
    # No script anterior, cdi.parquet tem 'cdi_annual'
    cdi_metrics = df_cdi[['cdi_annual']].reset_index()
    df_merged = pd.merge_asof(
        df_merged,
        cdi_metrics,
        left_on='quarter_end',
        right_on='date',
        direction='backward',
        suffixes=('', '_cdi')
    )

    # =========================================================================
    # 4. Cálculo do EVS (Economic Value Spread)
    # =========================================================================
    print("Calculando EVS...")
    
    # Ke = Rf + Beta * MRP
    # Rf = CDI Anual
    # MRP calculado dinamicamente acima
    
    # cdi_annual vem como percentual (ex: 0.10 para 10%) ou inteiro?
    # Vamos verificar no próximo passo, mas assumindo decimal.
    # Se for > 1 (ex: 10.5), dividir por 100.
    
    # Verificação rápida da escala do CDI
    if df_merged['cdi_annual'].mean() > 1:
        df_merged['cdi_annual'] = df_merged['cdi_annual'] / 100.0
        
    df_merged['ke'] = df_merged['cdi_annual'] + df_merged['beta'] * mrp
    
    # EVS = ROIC - Ke (Usando Ke como proxy de custo de capital total ou WACC simplificado)
    df_merged['evs'] = df_merged['roic'] - df_merged['ke']

    # Selecionar colunas finais
    cols_final = [
        'quarter_end', 
        'earnings_yield', 'ev_ebitda', 'pb_ratio', 'dividend_yield', 
        'roic', 'roe', 'ebitda_margin', 'evs', 
        'beta', 'volatility', 'debt_to_equity', 'current_ratio'
    ]
    
    # Filtrar apenas colunas existentes (algumas podem ter nomes diferentes no df original)
    # debt_to_equity veio do fundamentals
    # current_ratio veio do fundamentals
    
    # Verificar colunas disponíveis
    available_cols = [c for c in cols_final if c in df_merged.columns]
    df_final = df_merged[available_cols].copy()

    # Salvar
    print(f"Salvando {len(df_final)} registros em {output_dir}...")
    df_final.to_parquet(output_parquet)
    df_final.to_csv(output_csv, index=False)
    print("Concluído.")

if __name__ == "__main__":
    calculate_metrics()
