"""
Backtest Comparativo: Buy & Hold vs M5-Linear vs M5-ML.

Simula estratégias de trading baseadas nas predições geradas por `train_m5_models.py`.
Gera métricas de performance (Sharpe, Drawdown, Retorno Total) e curvas de capital.

Output:
    - data/outputs/backtest_results.json
    - data/outputs/figures/backtest_equity_curve.pdf
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

def calculate_drawdown(equity_curve):
    """Calcula a série de Drawdown e o Max Drawdown."""
    peak = equity_curve.cummax()
    drawdown = (equity_curve - peak) / peak
    return drawdown, drawdown.min()

def calculate_metrics(returns):
    """Calcula métricas de performance da estratégia."""
    total_return = (1 + returns).prod() - 1
    # Sharpe anualizado (assumindo rf=0 para simplificação ou excess return)
    mean_ret = returns.mean() * 252
    vol = returns.std() * np.sqrt(252)
    sharpe = mean_ret / vol if vol > 0 else 0
    
    # Sortino
    downside_returns = returns[returns < 0]
    downside_vol = downside_returns.std() * np.sqrt(252)
    sortino = mean_ret / downside_vol if downside_vol > 0 else 0
    
    return {
        "Total Return": total_return,
        "Annualized Return": mean_ret,
        "Volatility": vol,
        "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino
    }

def run_backtest():
    print("Iniciando Backtest M5...")
    set_style()
    
    # 1. Carregar Predições
    input_path = PROJECT_ROOT / "data" / "outputs" / "m5_predictions.parquet"
    if not input_path.exists():
        raise FileNotFoundError("Execute src.analysis.train_m5_models primeiro.")
        
    df = pd.read_parquet(input_path)
    
    # 2. Definir Sinais
    # Buy & Hold: Sempre comprado (1.0)
    df['signal_bh'] = 1.0
    
    # M5-Linear: Long se pred > 0, Short se pred < 0 (ou Neutro)
    # Vamos usar Long-Only para comparação justa com B&H, ou Long-Short?
    # O usuário pediu "contra Buy and Hold". Geralmente Long-Short vs Long-Only é injusto.
    # Vamos fazer Long-Only com filtro: Se pred > 0, compra. Se pred < 0, fica em caixa (retorno 0).
    # Ou Long-Short. Vamos testar Long-Short para mostrar "Estado da Arte".
    
    # Estratégia: S = sign(pred).shift(1)
    # Como o modelo é Explanatory (target = t), o sinal gerado em t só pode ser usado em t+1.
    # Isso testa se a "explicação" de hoje tem poder preditivo (momentum/reversão) para amanhã.
    df['signal_linear'] = np.sign(df['pred_linear']).shift(1).fillna(0)
    df['signal_ml'] = np.sign(df['pred_ml']).shift(1).fillna(0)
    
    # 3. Calcular Retornos da Estratégia
    # Retorno da estratégia = Sinal(t) * Retorno(t+1)
    # O dataframe já tem y_true alinhado (target_return é o retorno de t+1)
    # Mas cuidado: y_true em train_m5_models era shift(-1).
    # No arquivo salvo, 'y_true' é o retorno que a predição tentou acertar.
    # Então: Strategy Return = Signal * y_true
    
    df['ret_bh'] = df['signal_bh'] * df['y_true']
    df['ret_linear'] = df['signal_linear'] * df['y_true']
    df['ret_ml'] = df['signal_ml'] * df['y_true']
    
    # Custos de Transação (Simplificado: 0.1% por trade)
    # trade = abs(signal_t - signal_{t-1})
    cost_bps = 0.0010
    
    for strat in ['linear', 'ml']:
        trades = df[f'signal_{strat}'].diff().abs().fillna(0)
        df[f'ret_{strat}_net'] = df[f'ret_{strat}'] - (trades * cost_bps)
    
    # B&H tem custo zero (só entrada)
    df['ret_bh_net'] = df['ret_bh']
    
    # 4. Curvas de Capital
    df['equity_bh'] = (1 + df['ret_bh_net']).cumprod()
    df['equity_linear'] = (1 + df['ret_linear_net']).cumprod()
    df['equity_ml'] = (1 + df['ret_ml_net']).cumprod()
    
    # 5. Métricas
    metrics = {
        "Buy & Hold": calculate_metrics(df['ret_bh_net']),
        "M5-Linear": calculate_metrics(df['ret_linear_net']),
        "M5-ML": calculate_metrics(df['ret_ml_net'])
    }
    
    # Adicionar Max Drawdown
    for name, col in [("Buy & Hold", "equity_bh"), ("M5-Linear", "equity_linear"), ("M5-ML", "equity_ml")]:
        _, mdd = calculate_drawdown(df[col])
        metrics[name]["Max Drawdown"] = mdd
        
    # Salvar Métricas
    output_metrics = PROJECT_ROOT / "data" / "outputs" / "backtest_results.json"
    with open(output_metrics, 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print("Métricas calculadas:")
    print(json.dumps(metrics, indent=2))
    
    # 6. Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    
    # Equity Curve
    ax1.plot(df.index, df['equity_bh'], label='Buy & Hold (Petrobras)', color='gray', alpha=0.7, linestyle='--')
    ax1.plot(df.index, df['equity_linear'], label='M5-Linear (ElasticNet)', color=COLORS['primary'], linewidth=2)
    ax1.plot(df.index, df['equity_ml'], label='M5-ML (XGBoost)', color=COLORS['secondary'], linewidth=2)
    
    ax1.set_ylabel('Retorno Acumulado (Base 1.0)', fontweight='bold')
    ax1.set_title('Backtest Comparativo: Estratégias M5 vs Benchmark', fontweight='bold', pad=20)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Drawdown
    dd_bh, _ = calculate_drawdown(df['equity_bh'])
    dd_linear, _ = calculate_drawdown(df['equity_linear'])
    dd_ml, _ = calculate_drawdown(df['equity_ml'])
    
    ax2.fill_between(df.index, dd_bh, 0, color='gray', alpha=0.3, label='DD B&H')
    ax2.plot(df.index, dd_linear, color=COLORS['primary'], linewidth=1, label='DD Linear')
    ax2.plot(df.index, dd_ml, color=COLORS['secondary'], linewidth=1, label='DD ML')
    
    ax2.set_ylabel('Drawdown', fontweight='bold')
    ax2.set_xlabel('Data', fontweight='bold')
    ax2.legend(loc='lower left', fontsize='small')
    ax2.grid(True, alpha=0.3)
    
    output_fig = PROJECT_ROOT / "data" / "outputs" / "figures" / "backtest_equity_curve.pdf"
    output_fig.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_fig)
    print(f"Gráfico salvo em: {output_fig}")

if __name__ == "__main__":
    run_backtest()
