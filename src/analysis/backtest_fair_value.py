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
HORIZON_PREDICTIONS_PATH = PROJECT_ROOT / "data/outputs/m5_horizon_predictions.parquet"
DAILY_PREDICTIONS_PATH = PROJECT_ROOT / "data/outputs/m5_predictions.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data/outputs/backtest"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COST_BPS = 0.0005 # 5 bps transaction cost (slippage + fees)
HORIZON = 21

class NaiveDirectionalBacktest:
    def __init__(self, df, model_col):
        self.df = df.copy()
        self.model_col = model_col
        
    def run(self):
        # Signal: 1 if pred > 0, else 0 (Cash/CDI)
        # Or Short? Let's assume Long/Cash for fair comparison with Fair Value
        # If pred > 0 -> Long
        # If pred <= 0 -> Cash (CDI)
        
        self.df['position'] = np.where(self.df[self.model_col] > 0, 1, 0)
        
        # Transaction Costs
        self.df['pos_change'] = self.df['position'].diff().abs().fillna(0)
        
        # Strategy Return (Shifted)
        pos_lag = self.df['position'].shift(1).fillna(0)
        
        self.df['strategy_gross'] = (
            pos_lag * self.df['ret_petr4'] + 
            (1 - pos_lag) * self.df['cdi_daily']
        )
        
        costs_lag = self.df['pos_change'].shift(1).fillna(0) * COST_BPS
        self.df['strategy_net'] = self.df['strategy_gross'] - costs_lag
        
        # Cumulative
        self.df['equity'] = (1 + self.df['strategy_net']).cumprod()
        return self.df

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

    def plot_results(self, title, comparison_df=None, comparison_label=None):
        set_style()
        # Use Seaborn style for better aesthetics
        sns.set_theme(style="whitegrid", rc={"grid.linestyle": ":", "axes.spines.right": False, "axes.spines.top": False})
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Define data and colors for iteration
        lines = [
            {'data': self.df, 'col': 'equity', 'label': 'Fair Value (M5b)', 'color': '#1f77b4', 'style': '-'},
            {'data': self.df, 'col': 'benchmark_buyhold', 'label': 'Buy & Hold (PETR4)', 'color': 'gray', 'style': '-'},
            {'data': self.df, 'col': 'benchmark_cdi', 'label': 'CDI', 'color': 'green', 'style': ':'}
        ]
        
        if comparison_df is not None:
            lines.insert(1, {'data': comparison_df, 'col': 'equity', 'label': 'Naive (Day-Trade)', 'color': '#d62728', 'style': '--'})

        # Plot loop
        for line in lines:
            data = line['data']
            col = line['col']
            last_date = data.index[-1]
            last_val = data[col].iloc[-1]
            
            sns.lineplot(x=data.index, y=data[col], label=line['label'], 
                         color=line['color'], linestyle=line['style'], linewidth=2, ax=ax)
            
            # Add annotation at the end
            ax.annotate(f"{last_val:.2f}x", 
                        xy=(last_date, last_val), 
                        xytext=(8, 0), textcoords='offset points', 
                        color=line['color'], fontweight='bold', fontsize=10,
                        verticalalignment='center')

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel("Capital Acumulado (1.0 = Início)", fontsize=11)
        ax.set_xlabel("")
        
        # Legend inside plot (Best location)
        ax.legend(loc='upper left', frameon=True, framealpha=0.9, edgecolor='lightgray', fontsize=10)
        
        plt.tight_layout()
        return fig
    
    def calculate_sharpe(self):
        excess_ret = self.df['strategy_net'] - self.df['cdi_daily']
        if excess_ret.std() == 0: return 0
        return (excess_ret.mean() * 252) / (excess_ret.std() * np.sqrt(252))

def run_backtest():
    print("🚀 Iniciando Backtest: Fair Value Strategy vs Naive Directional...")
    
    # Load Horizon Predictions (Fair Value)
    df_horizon = pd.read_parquet(HORIZON_PREDICTIONS_PATH)
    df_horizon = df_horizon.sort_index()
    
    # Load Daily Predictions (Naive)
    if DAILY_PREDICTIONS_PATH.exists():
        df_daily = pd.read_parquet(DAILY_PREDICTIONS_PATH)
        df_daily = df_daily.sort_index()
        # Merge daily predictions into horizon df
        # df_daily has 'pred_ml' (XGBoost) and 'pred_linear' (ElasticNet)
        # We need to join on index
        df_combined = df_horizon.join(df_daily[['pred_ml']], how='left')
    else:
        print("⚠️ Predições diárias não encontradas. Usando placeholder.")
        df_combined = df_horizon.copy()
        df_combined['pred_ml'] = 0 # Placeholder
    
    # Filter for Out-of-Sample (2023+)
    df_oos = df_combined[df_combined.index >= '2023-01-01'].copy()
    
    print(f"   Período: {df_oos.index.min().date()} a {df_oos.index.max().date()}")
    
    # =========================================================================
    # 1. Naive Directional (M5b Daily)
    # =========================================================================
    print("\n   --- Executando Naive Directional (M5b Daily) ---")
    bt_naive = NaiveDirectionalBacktest(df_oos, 'pred_ml')
    res_naive = bt_naive.run()
    print_metrics("Naive Directional", res_naive)
    
    # =========================================================================
    # 2. Fair Value (M5b Horizon)
    # =========================================================================
    print("\n   --- Executando Fair Value (M5b Horizon) ---")
    # Threshold 2% (mais sensível)
    bt_fair = FairValueBacktest(df_oos, 'pred_xgb_21d', entry_threshold=0.02, exit_threshold=0.0)
    res_fair = bt_fair.run()
    print_metrics("Fair Value (M5b)", res_fair)
    
    # Plot Comparison
    fig_comp = bt_fair.plot_results(
        "M5b: Fair Value (Swing) vs Naive Directional (Day-Trade)",
        comparison_df=res_naive,
        comparison_label="Naive Directional (Day-Trade)"
    )
    
    # Save Figure to the correct figures directory for LaTeX inclusion
    FIGURES_DIR = PROJECT_ROOT / "data/outputs/figures"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig_comp.savefig(FIGURES_DIR / "backtest_comparison_m5b.png", dpi=300, bbox_inches='tight')
    print(f"   Figura salva em: {FIGURES_DIR / 'backtest_comparison_m5b.png'}")
    
    # Save Results CSV
    res_fair.to_csv(OUTPUT_DIR / "backtest_results_fairvalue.csv")
    res_naive.to_csv(OUTPUT_DIR / "backtest_results_naive.csv")
    
    # Generate LaTeX Table
    generate_latex_table(res_fair, res_naive)
    
    print(f"\n   Resultados salvos em: {OUTPUT_DIR}")

def generate_latex_table(df_fair, df_naive):
    """Gera tabela LaTeX comparativa."""
    
    def get_metrics(df):
        total_ret = df['equity'].iloc[-1] - 1
        ann_ret = (1 + total_ret) ** (252 / len(df)) - 1
        vol = df['strategy_net'].std() * np.sqrt(252)
        excess_ret = df['strategy_net'] - df['cdi_daily']
        sharpe = (excess_ret.mean() * 252) / (excess_ret.std() * np.sqrt(252))
        trades = df['pos_change'].sum()
        return total_ret, ann_ret, vol, sharpe, trades

    m_fair = get_metrics(df_fair)
    m_naive = get_metrics(df_naive)
    
    # Benchmark CDI
    cdi_total = df_fair['benchmark_cdi'].iloc[-1] - 1
    cdi_ann = (1 + cdi_total) ** (252 / len(df_fair)) - 1
    cdi_vol = df_fair['cdi_daily'].std() * np.sqrt(252)
    
    # Benchmark Buy & Hold
    bh_total = df_fair['benchmark_buyhold'].iloc[-1] - 1
    bh_ann = (1 + bh_total) ** (252 / len(df_fair)) - 1
    bh_vol = df_fair['ret_petr4'].std() * np.sqrt(252)
    bh_excess = df_fair['ret_petr4'] - df_fair['cdi_daily']
    bh_sharpe = (bh_excess.mean() * 252) / (bh_excess.std() * np.sqrt(252))

    def fmt_pct(val):
        return f"{val:.2%}".replace("%", r"\%")

    latex = r"""
\begin{table}[H]
\centering
\caption{Performance Comparativa: Fair Value vs. Naive Directional vs. Benchmarks (Jan/2023 - Out/2025)}
\label{tab:backtest_comparison}
\begin{tabular}{lccccc}
\toprule
\textbf{Estratégia} & \textbf{Retorno Total} & \textbf{Retorno Anual} & \textbf{Volatilidade} & \textbf{Sharpe} & \textbf{Trades} \\
\midrule
M5b Fair Value & \textbf{""" + fmt_pct(m_fair[0]) + r"""} & """ + fmt_pct(m_fair[1]) + r""" & """ + fmt_pct(m_fair[2]) + r""" & \textbf{""" + f"{m_fair[3]:.2f}" + r"""} & """ + f"{int(m_fair[4])}" + r""" \\
M5b Naive (Day-Trade) & """ + fmt_pct(m_naive[0]) + r""" & """ + fmt_pct(m_naive[1]) + r""" & """ + fmt_pct(m_naive[2]) + r""" & """ + f"{m_naive[3]:.2f}" + r""" & """ + f"{int(m_naive[4])}" + r""" \\
Buy \& Hold (PETR4) & """ + fmt_pct(bh_total) + r""" & """ + fmt_pct(bh_ann) + r""" & """ + fmt_pct(bh_vol) + r""" & """ + f"{bh_sharpe:.2f}" + r""" & 1 \\
CDI (Risk Free) & """ + fmt_pct(cdi_total) + r""" & """ + fmt_pct(cdi_ann) + r""" & """ + fmt_pct(cdi_vol) + r""" & - & - \\
\bottomrule
\end{tabular}
\footnotesize{Nota: Sharpe Ratio calculado sobre o CDI. Volatilidade anualizada.}
\end{table}
"""
    
    with open(PROJECT_ROOT / "data/outputs/tables/backtest_comparison.tex", "w") as f:
        f.write(latex)
    print("   Tabela LaTeX gerada em: data/outputs/tables/backtest_comparison.tex")

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
