import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

def run():
    # Configuração de Estilo
    set_style()
    
    input_path = PROJECT_ROOT / "data/outputs/m5_horizon_predictions.parquet"
    output_path = PROJECT_ROOT / "data/outputs/figures/rolling_r2_comparison.pdf"
    
    if not input_path.exists():
        print(f"File not found: {input_path}")
        return

    df = pd.read_parquet(input_path)
    
    # Window size: 12 months * 21 days/month approx = 252 days
    window = 252
    
    # Calculate Rolling R2
    def rolling_r2(y_true, y_pred, window):
        # SS_res
        ss_res = (y_true - y_pred)**2
        ss_res_rolling = ss_res.rolling(window=window).sum()
        
        # SS_tot
        # We need sum((y - y_mean)^2) over the window.
        # This is equivalent to var(y) * (n-1)
        # Using ddof=0 for population variance consistency with R2 definition usually
        ss_tot_rolling = y_true.rolling(window=window).var(ddof=0) * window
        
        # Avoid division by zero
        r2 = 1 - (ss_res_rolling / ss_tot_rolling)
        return r2

    # Calculate for both models
    # Huber is the Linear (Robust) baseline
    # XGB is the ML (M5b) model
    df['r2_linear'] = rolling_r2(df['target_return_21d'], df['pred_huber_21d'], window)
    df['r2_ml'] = rolling_r2(df['target_return_21d'], df['pred_xgb_21d'], window)
    
    # Drop NaNs (start of window)
    plot_df = df.dropna(subset=['r2_linear', 'r2_ml'])
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot Lines
    ax.plot(plot_df.index, plot_df['r2_linear'], label='Linear (Robust)', color=COLORS['primary'], linewidth=2, alpha=0.8)
    ax.plot(plot_df.index, plot_df['r2_ml'], label='Machine Learning (M5b)', color=COLORS['secondary'], linewidth=2.5)
    
    # Styling
    ax.set_title('Evidência de Adaptabilidade: Rolling $R^2$ (12 Meses)', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Rolling $R^2$', fontweight='bold')
    ax.set_xlabel('', fontweight='bold')
    
    # Add zero line
    ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Highlight periods where ML outperforms
    # Fill between
    ax.fill_between(plot_df.index, plot_df['r2_linear'], plot_df['r2_ml'], 
                    where=(plot_df['r2_ml'] > plot_df['r2_linear']),
                    interpolate=True, color=COLORS['secondary'], alpha=0.1, label='ML Outperformance')
    
    ax.legend(frameon=True, loc='best')
    
    # Format Date Axis
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    
    # Adjust limits if necessary (e.g. ignore extreme negative R2 for visualization if needed)
    # But usually better to show truth.
    # Let's clip y-axis bottom if it's too low (e.g. -1) to keep focus on positive/near-zero
    # Check data range first? No, let's set a reasonable floor if it goes to -10.
    # But for now let auto-scale handle it, unless it's crazy.
    
    plt.tight_layout()
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    print(f"Figure saved to {output_path}")

if __name__ == "__main__":
    run()
