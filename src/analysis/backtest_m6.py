"""
Módulo de Backtest do Modelo M6 (Swing Trade) - Fase 4 do Roadmap.

Este módulo implementa a lógica de execução da estratégia M6, comparando-a
com o benchmark Buy & Hold.

Lógica de Trading (Swing Trade):
- Regime Filter: Só opera se Prob(Regime Calm) > 0.5.
- Entry: Regime Calm E Modelo prevê Alta (Prob > 0.5).
- Exit: Regime vira Crise OU Modelo prevê Baixa com convicção OU Macro vira negativo.
- Custos: Considera corretagem e slippage.

Outputs:
- Curva de Capital (Equity Curve).
- Métricas de Performance (Sharpe, Drawdown, Win Rate).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Adicionar raiz do projeto ao path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.core.config import PROJECT_ROOT
from src.core.style import set_style

def load_data():
    """Carrega predições e dados de mercado."""
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # 1. Predições M6
    df_pred = pd.read_parquet(processed_dir / "m6_predictions.parquet")
    
    # 2. Dados de Mercado (Retornos Reais e CDI)
    # Precisamos de 'ret_petr4' e 'cdi_daily' que estão no ml_dataset
    df_mkt = pd.read_parquet(processed_dir / "ml_dataset.parquet")
    if 'date' in df_mkt.columns:
        df_mkt = df_mkt.set_index('date')
        
    # Selecionar colunas necessárias do mercado
    cols_mkt = ['ret_petr4', 'cdi_daily']
    df_mkt = df_mkt[cols_mkt]
    
    # Merge
    df = df_pred.join(df_mkt, how='left')
    df = df.dropna()
    
    return df

def apply_strategy(df, cost_bps=10):
    """
    Aplica a lógica de trading Swing Trade com Volatility Targeting e Regime-Dependent Strategies.
    
    Args:
        df (pd.DataFrame): DataFrame com predições e dados de mercado.
        cost_bps (float): Custo de transação em basis points (ex: 10bps = 0.10%).
        
    Returns:
        pd.DataFrame: DataFrame com posições e retornos da estratégia.
    """
    df = df.copy()
    
    # --- 1. Volatility Targeting ---
    # Target Vol Anual = 15% -> Diária ~ 0.94%
    target_vol_daily = 0.15 / np.sqrt(252)
    
    # Forecast Vol (usando vol_20d como proxy, garantindo que não seja zero)
    # vol_20d já está no dataset (desvio padrão de 20 dias)
    forecast_vol = df['vol_20d'].replace(0, 0.01) 
    
    # Exposure = Target / Forecast (Capped at 1.0, no leverage)
    vol_exposure = (target_vol_daily / forecast_vol).clip(upper=1.0)
    
    # --- 2. Regime-Dependent Signals ---
    
    # Regime 0 = Calm (Baixa Volatilidade)
    is_calm = df['prob_regime_0'] > 0.5
    
    # Signal A: Trend Following (Para Regime Calmo)
    # Usa o classificador M6 (XGBoost)
    signal_trend = (df['pred_prob'] > 0.5).astype(int)
    
    # Signal B: Mean Reversion (Para Regime Crise)
    # Compra se houve queda forte no dia anterior (ret_lag1 < -2%)
    # ret_lag1 é o retorno de t-1. Se t-1 caiu muito, compramos em t esperando repique.
    signal_mean_rev = (df['ret_lag1'] < -0.02).astype(int)
    
    # Combinar Sinais baseados no Regime
    # Se Calm: Segue Trend
    # Se Crisis: Segue Mean Reversion
    base_signal = np.where(is_calm, signal_trend, signal_mean_rev)
    
    # --- 3. Posição Final ---
    # Position = Signal * Volatility Exposure
    # Se Signal é 0 (Cash), Exposure não importa.
    # Se Signal é 1 (Long), Exposure define o tamanho (0.2, 0.5, 1.0...)
    
    # Suavização de sinal para evitar churn excessivo? 
    # O Vol Targeting já varia dia a dia. Vamos manter simples.
    
    positions = base_signal * vol_exposure
    
    df['position'] = positions
    
    # Calcular Retornos
    # Se position=0.5, ganha 0.5*ret_petr4 + 0.5*cdi_daily
    # Se position=0, ganha 1.0*cdi_daily
    
    # Mudança de posição (Turnover)
    trades = df['position'].diff().abs().fillna(0)
    
    # Custo (bps convertido para decimal)
    cost = trades * (cost_bps / 10000)
    
    # Retorno Bruto
    # Parte investida em PETR4 + Parte em Caixa (CDI)
    df['strategy_gross'] = (df['position'] * df['ret_petr4']) + ((1 - df['position']) * df['cdi_daily'])
    
    # Retorno Líquido
    df['strategy_net'] = df['strategy_gross'] - cost
    
    # Benchmark (Buy & Hold)
    df['bnh_ret'] = df['ret_petr4']
    
    return df

def calculate_metrics(df):
    """Calcula métricas de performance (Sharpe, Drawdown, etc)."""
    metrics = {}
    
    # Retornos Acumulados
    df['cum_strategy'] = (1 + df['strategy_net']).cumprod()
    df['cum_bnh'] = (1 + df['bnh_ret']).cumprod()
    df['cum_cdi'] = (1 + df['cdi_daily']).cumprod()
    
    # Total Return
    metrics['Total Return (M6)'] = df['cum_strategy'].iloc[-1] - 1
    metrics['Total Return (B&H)'] = df['cum_bnh'].iloc[-1] - 1
    metrics['Total Return (CDI)'] = df['cum_cdi'].iloc[-1] - 1
    
    # Volatilidade Anualizada
    vol_strat = df['strategy_net'].std() * np.sqrt(252)
    vol_bnh = df['bnh_ret'].std() * np.sqrt(252)
    metrics['Volatilidade (M6)'] = vol_strat
    metrics['Volatilidade (B&H)'] = vol_bnh
    
    # Sharpe Ratio (considerando CDI como Risk Free)
    # Excesso de retorno diário sobre CDI
    excess_strat = df['strategy_net'] - df['cdi_daily']
    excess_bnh = df['bnh_ret'] - df['cdi_daily']
    
    sharpe_strat = (excess_strat.mean() / excess_strat.std()) * np.sqrt(252)
    sharpe_bnh = (excess_bnh.mean() / excess_bnh.std()) * np.sqrt(252)
    
    metrics['Sharpe (M6)'] = sharpe_strat
    metrics['Sharpe (B&H)'] = sharpe_bnh
    
    # Max Drawdown
    def max_drawdown(series):
        cum = (1 + series).cumprod()
        peak = cum.cummax()
        dd = (cum - peak) / peak
        return dd.min()
        
    metrics['Max Drawdown (M6)'] = max_drawdown(df['strategy_net'])
    metrics['Max Drawdown (B&H)'] = max_drawdown(df['bnh_ret'])
    
    # Win Rate (Dias positivos vs negativos quando posicionado)
    active_days = df[df['position'] == 1]
    if len(active_days) > 0:
        win_rate = (active_days['ret_petr4'] > 0).mean()
        metrics['Win Rate (Long)'] = win_rate
    else:
        metrics['Win Rate (Long)'] = 0.0
        
    # Trades Count
    n_trades = df['position'].diff().abs().sum() / 2 # Entrada + Saída = 1 Trade completo (aprox)
    metrics['Total Trades'] = n_trades
    
    return metrics

def plot_results(df):
    """Gera gráficos de performance."""
    set_style()
    
    # 1. Equity Curve
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['cum_strategy'], label='M6 Strategy (Swing)', linewidth=1.5)
    plt.plot(df.index, df['cum_bnh'], label='Buy & Hold (PETR4)', alpha=0.7, linewidth=1)
    plt.plot(df.index, df['cum_cdi'], label='CDI (Benchmark)', linestyle='--', alpha=0.7)
    
    plt.title('M6 Strategy vs Benchmarks (Equity Curve)')
    plt.ylabel('Retorno Acumulado (1.0 = Inicial)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_dir = PROJECT_ROOT / "data" / "outputs" / "figures"
    plt.savefig(output_dir / "m6_equity_curve.pdf")
    print(f"Gráfico salvo em {output_dir / 'm6_equity_curve.pdf'}")
    
    # 2. Drawdown
    plt.figure(figsize=(12, 4))
    cum_strat = (1 + df['strategy_net']).cumprod()
    peak_strat = cum_strat.cummax()
    dd_strat = (cum_strat - peak_strat) / peak_strat
    
    cum_bnh = (1 + df['bnh_ret']).cumprod()
    peak_bnh = cum_bnh.cummax()
    dd_bnh = (cum_bnh - peak_bnh) / peak_bnh
    
    plt.plot(df.index, dd_strat, label='M6 Drawdown', color='red', linewidth=1)
    plt.plot(df.index, dd_bnh, label='B&H Drawdown', color='gray', alpha=0.3, linewidth=1)
    plt.fill_between(df.index, dd_strat, 0, color='red', alpha=0.1)
    
    plt.title('Drawdown Profile')
    plt.ylabel('% Queda do Topo')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig(output_dir / "m6_drawdown.pdf")

def run_backtest():
    print("--- M6 Phase 4: Backtest Swing Trade ---")
    
    # 1. Load
    df = load_data()
    print(f"Dados carregados: {len(df)} dias.")
    
    # 2. Apply Strategy
    # Custo de 10bps (0.10%) por trade (corretagem + slippage)
    df_res = apply_strategy(df, cost_bps=10)
    
    # 3. Metrics
    metrics = calculate_metrics(df_res)
    
    print("\n--- Resultados de Performance ---")
    for k, v in metrics.items():
        if 'Return' in k or 'Drawdown' in k or 'Win Rate' in k or 'Volatilidade' in k:
            print(f"{k}: {v:.2%}")
        elif 'Sharpe' in k:
            print(f"{k}: {v:.2f}")
        else:
            print(f"{k}: {v:.1f}")
            
    # 4. Plot
    plot_results(df_res)
    
    # 5. Save Results
    df_res.to_parquet(PROJECT_ROOT / "data" / "processed" / "m6_backtest_results.parquet")

if __name__ == "__main__":
    run_backtest()
