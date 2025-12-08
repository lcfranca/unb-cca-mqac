"""
Backtest da Estratégia de Valor Justo (Fair Value Strategy).

Esta estratégia utiliza as predições de retorno acumulado (21 dias) dos modelos M5
para calcular um Preço Justo Implícito e operar com base no spread de valor (Upside).

Lógica:
    1. P_fair = P_current * (1 + pred_ret_21d) / (1 + cdi_21d)
    2. Upside = (P_fair / P_current) - 1  ~= pred_ret_21d - cdi_21d
    3. Se Upside > Entry_Threshold: COMPRA (Long)
    4. Se Upside < Exit_Threshold: VENDA (Cash/CDI)

Output:
    - data/outputs/backtest/ (CSV de resultados e Figuras)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style

# Configs
PREDICTIONS_PATH = PROJECT_ROOT / "data/outputs/m5_horizon_predictions.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data/outputs/backtest"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COST_BPS = 0.0005 # 5 bps transaction cost (slippage + fees)
HORIZON = 21

class FairValueBacktest:
    def __init__(self, df, model_col, entry_threshold=0.02, exit_threshold=0.0):
        self.df = df.copy()
        self.model_col = model_col
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.results = None
        
    def run(self):
        # 1. Calculate Upside (Spread de Valor)
        # Upside = (1 + pred) / (1 + cdi_21d) - 1
        
        # Proxy para CDI futuro: CDI atual extrapolado
        self.df['cdi_21d_proxy'] = (1 + self.df['cdi_daily']) ** HORIZON - 1
        
        self.df['upside'] = (1 + self.df[self.model_col]) / (1 + self.df['cdi_21d_proxy']) - 1
        
        # 2. Generate Signals (State Machine)
        positions = np.zeros(len(self.df))
        current_pos = 0 # 0 = Cash/CDI, 1 = Long PETR4
        
        upside_arr = self.df['upside'].values
        
        for i in range(len(upside_arr)):
            upside = upside_arr[i]
            
            if current_pos == 0: # Currently in Cash
                if upside > self.entry_threshold:
                    current_pos = 1 # Enter Long
            elif current_pos == 1: # Currently Long
                if upside < self.exit_threshold:
                    current_pos = 0 # Exit to Cash
            
            positions[i] = current_pos
            
        self.df['position'] = positions
        
        # 3. Calculate Returns
        # Transaction Costs: when pos changes
        self.df['pos_change'] = self.df['position'].diff().abs().fillna(0)
        self.df['costs'] = self.df['pos_change'] * COST_BPS
        
        # Strategy Return
        # Shift position by 1 to simulate execution at next open/close (avoid lookahead)
        # If signal is generated at t (close), we trade at t+1.
        # So return at t+1 depends on position at t.
        
        pos_lag = self.df['position'].shift(1).fillna(0)
        
        # Retorno Bruto:
        # Se pos_lag = 1: ret_petr4
        # Se pos_lag = 0: cdi_daily
        self.df['strategy_gross'] = (
            pos_lag * self.df['ret_petr4'] + 
            (1 - pos_lag) * self.df['cdi_daily']
        )
        
        # Retorno Líquido (desconta custos no dia da execução)
        # Custo incide em t se a posição mudou de t-1 para t?
        # Se mudamos de posição em t (baseado em sinal t-1), pagamos custo em t.
        # pos_change_lag = abs(pos_t - pos_t-1) -> Isso é o que calculamos acima?
        # Não, self.df['pos_change'] é abs(pos_t - pos_t-1).
        # Mas a execução ocorre em t baseada em t-1?
        # Vamos assumir execução no fechamento de t+1 (ou abertura).
        # O custo ocorre no dia que o retorno é realizado.
        
        costs_lag = self.df['pos_change'].shift(1).fillna(0) * COST_BPS
        
        self.df['strategy_net'] = self.df['strategy_gross'] - costs_lag
        
        # Cumulative
        self.df['equity'] = (1 + self.df['strategy_net']).cumprod()
        self.df['benchmark_buyhold'] = (1 + self.df['ret_petr4']).cumprod()
        self.df['benchmark_cdi'] = (1 + self.df['cdi_daily']).cumprod()
        
        return self.df

    def plot_results(self, title):
        set_style()
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot Equity Curves
        ax.plot(self.df.index, self.df['equity'], label='Strategy (Fair Value)', color='blue', linewidth=1.5)
        ax.plot(self.df.index, self.df['benchmark_buyhold'], label='Buy & Hold (PETR4)', color='gray', alpha=0.5, linewidth=1)
        ax.plot(self.df.index, self.df['benchmark_cdi'], label='CDI', color='green', linestyle='--', linewidth=1)
        
        # Plot Drawdown area for Strategy?
        # Maybe too cluttered.
        
        ax.set_title(title)
        ax.set_ylabel("Cumulative Return (1.0 = Start)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add metrics text box
        total_ret = self.df['equity'].iloc[-1] - 1
        sharpe = self.calculate_sharpe()
        textstr = f'Total Ret: {total_ret:.1%}\nSharpe: {sharpe:.2f}'
        props = dict(boxstyle='round', facecolor='white', alpha=0.8)
        ax.text(0.02, 0.95, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        return fig
    
    def calculate_sharpe(self):
        excess_ret = self.df['strategy_net'] - self.df['cdi_daily']
        if excess_ret.std() == 0: return 0
        return (excess_ret.mean() * 252) / (excess_ret.std() * np.sqrt(252))

def run_backtest():
    print("🚀 Iniciando Backtest: Fair Value Strategy...")
    
    # Load Predictions
    df = pd.read_parquet(PREDICTIONS_PATH)
    df = df.sort_index()
    
    # Filter for Out-of-Sample (2023+)
    df_oos = df[df.index >= '2023-01-01'].copy()
    
    print(f"   Período: {df_oos.index.min().date()} a {df_oos.index.max().date()}")
    
    # =========================================================================
    # 1. M5a (Huber) - Mais volátil, exige threshold maior
    # =========================================================================
    print("\n   --- Executando para M5a (Huber) ---")
    # Threshold 5% (só entra se tiver muito desconto)
    bt_huber = FairValueBacktest(df_oos, 'pred_huber_21d', entry_threshold=0.05, exit_threshold=0.0)
    res_huber = bt_huber.run()
    print_metrics("M5a (Huber)", res_huber)
    
    fig_huber = bt_huber.plot_results("M5a (Huber) - Fair Value Strategy (Entry > 5%)")
    fig_huber.savefig(OUTPUT_DIR / "backtest_m5a_fairvalue.png")
    
    # =========================================================================
    # 2. M5b (XGBoost) - Mais conservador
    # =========================================================================
    print("\n   --- Executando para M5b (XGBoost) ---")
    # Threshold 2% (mais sensível)
    bt_xgb = FairValueBacktest(df_oos, 'pred_xgb_21d', entry_threshold=0.02, exit_threshold=0.0)
    res_xgb = bt_xgb.run()
    print_metrics("M5b (XGBoost)", res_xgb)
    
    fig_xgb = bt_xgb.plot_results("M5b (XGBoost) - Fair Value Strategy (Entry > 2%)")
    fig_xgb.savefig(OUTPUT_DIR / "backtest_m5b_fairvalue.png")
    
    # Save Results CSV
    res_xgb.to_csv(OUTPUT_DIR / "backtest_results_m5b.csv")
    print(f"\n   Resultados salvos em: {OUTPUT_DIR}")

def print_metrics(name, df):
    total_ret = df['equity'].iloc[-1] - 1
    ann_ret = (1 + total_ret) ** (252 / len(df)) - 1
    vol = df['strategy_net'].std() * np.sqrt(252)
    
    # Sharpe vs CDI
    excess_ret = df['strategy_net'] - df['cdi_daily']
    sharpe = (excess_ret.mean() * 252) / (excess_ret.std() * np.sqrt(252))
    
    trades = df['pos_change'].sum()
    
    print(f"   Total Return: {total_ret:.2%}")
    print(f"   Annual Return: {ann_ret:.2%}")
    print(f"   Volatility: {vol:.2%}")
    print(f"   Sharpe Ratio (vs CDI): {sharpe:.2f}")
    print(f"   Trades: {int(trades)}")
    print(f"   Final Equity: {df['equity'].iloc[-1]:.4f}")

if __name__ == "__main__":
    run_backtest()
