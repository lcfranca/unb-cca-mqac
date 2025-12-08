import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import xgboost as xgb
import shap
import joblib
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

# Config
DATA_PATH = PROJECT_ROOT / "data/processed/ml_dataset.parquet"
MODEL_PATH = PROJECT_ROOT / "data/models/xgb_regression_5d.pkl"
MARKOV_PATH = PROJECT_ROOT / "data/outputs/models/markov_regime_probs.csv"
OUTPUT_DIR = PROJECT_ROOT / "data/outputs/figures"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

set_style()

def run():
    print("🚀 Gerando Visualizações Comparativas...")
    
    # 1. Load Data
    df = pd.read_parquet(DATA_PATH)
    if 'date' in df.columns:
        df = df.set_index('date')
    df = df.sort_index()
    
    # Load Model
    model = joblib.load(MODEL_PATH)
    
    # Load Markov Probs
    if MARKOV_PATH.exists():
        markov_df = pd.read_csv(MARKOV_PATH, index_col=0, parse_dates=True)
        # Join with main df
        df = df.join(markov_df, how='left')
    else:
        print("AVISO: Probabilidades Markov não encontradas. Pulando Regime Map.")
        markov_df = None

    # Prepare Features for Model
    target_col = 'target_return_5d'
    # We need to drop NaNs for prediction to match training
    # But for backtest we want the whole timeline.
    # We will predict on valid rows.
    
    drop_cols = ['target_return_1d', 'target_return_5d', 'target_return_21d', 'ticker', 'date', 'available_date', 'days_since_release', 'price_index']
    features = [c for c in df.columns if c not in drop_cols and c in model.feature_names_in_]
    
    X = df[features].dropna()
    
    # Generate Predictions
    print("   Gerando previsões do XGBoost...")
    df.loc[X.index, 'pred_ret_5d'] = model.predict(X)
    
    # --- CHART 1: Equity Curve (Backtest) ---
    print("   1. Gerando Curva de Equity (Backtest)...")
    plot_equity_curve(df)
    
    # --- CHART 2: SHAP Beeswarm (Feature Importance) ---
    print("   2. Gerando SHAP Beeswarm...")
    plot_shap_beeswarm(model, X)
    
    # --- CHART 3: Regime Map (Markov) ---
    if markov_df is not None:
        print("   3. Gerando Mapa de Regimes...")
        # Reconstruct price index if 'close' is missing
        if 'close' not in df.columns:
            # Start from 100 for better visualization
            df['close'] = 100 * (1 + df['ret_petr4'].fillna(0)).cumprod()
            
        plot_regime_map(df)
        
    # --- CHART 4: Interaction Surface (Partial Dependence) ---
    print("   4. Gerando Superfície de Interação...")
    plot_interaction_surface(model, X, df)

def plot_equity_curve(df):
    # Simple Strategy:
    # Long if pred > 0.5% (approx cost), Short if pred < -0.5%
    # Hold for 5 days (simplified to daily rebalance for visualization)
    
    # Filter for out-of-sample period (approx 2023+) or full period?
    # Let's show 2021+ for clarity
    plot_df = df[df.index >= '2021-01-01'].copy()
    plot_df = plot_df.dropna(subset=['pred_ret_5d', 'ret_petr4'])
    
    # Signal
    threshold = 0.01 # 1% expected return in 5 days
    plot_df['position'] = 0
    plot_df.loc[plot_df['pred_ret_5d'] > threshold, 'position'] = 1
    plot_df.loc[plot_df['pred_ret_5d'] < -threshold, 'position'] = -1
    
    # Strategy Return (Daily approximation)
    # We shift position by 1 day to avoid look-ahead bias in execution
    plot_df['strat_ret'] = plot_df['position'].shift(1) * plot_df['ret_petr4']
    
    # Cumulative
    plot_df['cum_bnh'] = (1 + plot_df['ret_petr4']).cumprod()
    plot_df['cum_strat'] = (1 + plot_df['strat_ret']).cumprod()
    
    # Metrics
    total_ret_bnh = plot_df['cum_bnh'].iloc[-1] - 1
    total_ret_strat = plot_df['cum_strat'].iloc[-1] - 1
    vol_bnh = plot_df['ret_petr4'].std() * np.sqrt(252)
    vol_strat = plot_df['strat_ret'].std() * np.sqrt(252)
    sharpe_bnh = (total_ret_bnh / len(plot_df) * 252) / vol_bnh # Approx
    sharpe_strat = (total_ret_strat / len(plot_df) * 252) / vol_strat # Approx
    
    plt.figure(figsize=(12, 6))
    plt.plot(plot_df.index, plot_df['cum_bnh'], label=f'Buy & Hold (Ret: {total_ret_bnh:.1%}, Vol: {vol_bnh:.1%})', color='gray', alpha=0.7)
    plt.plot(plot_df.index, plot_df['cum_strat'], label=f'ML Strategy (Ret: {total_ret_strat:.1%}, Vol: {vol_strat:.1%})', color=COLORS['primary'], linewidth=2)
    
    plt.title('Backtest Comparativo: ML Strategy vs Buy & Hold (2021-2025)', fontweight='bold')
    plt.ylabel('Retorno Acumulado (Base 1.0)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "ml_comparison_equity_curve.pdf")
    print(f"      Salvo: {OUTPUT_DIR / 'ml_comparison_equity_curve.pdf'}")

def plot_shap_beeswarm(model, X):
    # Sample for speed if X is huge
    if len(X) > 2000:
        X_sample = X.sample(2000, random_state=42)
    else:
        X_sample = X
        
    # Rename columns for better readability
    feature_map = {
        'ret_lag1': 'Retorno (t-1)',
        'ret_lag5': 'Retorno (t-5)',
        'ret_lag21': 'Retorno (t-21)',
        'vol_20d': 'Volatilidade (20d)',
        'z_beta': 'Beta (Z-Score)',
        'z_volatility': 'Volatilidade Implícita (Z)',
        'z_earnings_yield': 'Earnings Yield (Z)',
        'z_ev_ebitda': 'EV/EBITDA (Z)',
        'z_pb_ratio': 'P/VP (Z)',
        'z_dividend_yield': 'Dividend Yield (Z)',
        'z_roe': 'ROE (Z)',
        'z_debt_to_equity': 'Dívida/PL (Z)',
        'score_valor': 'Score Valor',
        'score_qualidade': 'Score Qualidade',
        'score_risco': 'Score Risco',
        'EMBI': 'Risco País (EMBI)',
        'ret_brent': 'Retorno Brent',
        'ret_fx': 'Retorno Câmbio',
        'inter_beta_vol': 'Interação Beta x Vol',
        'inter_value_bear': 'Interação Valor x Bear',
        'mkt_vol_regime': 'Regime Volatilidade'
    }
    
    X_display = X_sample.rename(columns=feature_map)
    
    explainer = shap.TreeExplainer(model)
    # We need to pass the original X to explainer if it expects specific feature names, 
    # but for summary_plot we can pass the values and the display names.
    shap_values = explainer.shap_values(X_sample)
    
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_display, show=False, max_display=15, cmap=plt.get_cmap("coolwarm"))
    plt.title('Top 15 Determinantes de Retorno (SHAP Values)', fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "ml_feature_importance_beeswarm.pdf")
    print(f"      Salvo: {OUTPUT_DIR / 'ml_feature_importance_beeswarm.pdf'}")

def plot_regime_map(df):
    # Plot Price colored by Regime Probability
    plot_df = df[df.index >= '2018-01-01'].copy()
    plot_df = plot_df.dropna(subset=['prob_high_vol', 'close'])
    
    # Create segments for multicolored line
    points = np.array([mdates.date2num(plot_df.index), plot_df['close']]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # Color based on High Vol Probability
    # 0 (Low Vol) -> Green, 1 (High Vol) -> Red
    cmap = LinearSegmentedColormap.from_list("RegimeCmap", [COLORS['positive'], COLORS['negative']])
    norm = plt.Normalize(0, 1)
    
    from matplotlib.collections import LineCollection
    lc = LineCollection(segments, cmap=cmap, norm=norm)
    lc.set_array(plot_df['prob_high_vol'].values)
    lc.set_linewidth(2)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.add_collection(lc)
    ax.autoscale_view()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Add colorbar
    cbar = plt.colorbar(lc, ax=ax, pad=0.02)
    cbar.set_label('Probabilidade de Regime de Crise (Alta Vol.)', rotation=270, labelpad=15)
    
    ax.set_title('Mapa de Regimes de Mercado: Preço PETR4 Condicionado à Volatilidade', fontweight='bold')
    ax.set_ylabel('Preço (R$)')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "markov_regime_map.pdf")
    print(f"      Salvo: {OUTPUT_DIR / 'markov_regime_map.pdf'}")

def plot_interaction_surface(model, X, df):
    # We want to see how Predicted Return varies with Beta and Brent
    # We create a synthetic grid
    
    # Define range for Beta and Brent (based on historical data)
    beta_range = np.linspace(df['z_beta'].min(), df['z_beta'].max(), 50)
    brent_range = np.linspace(df['ret_brent'].min(), df['ret_brent'].max(), 50) # Using returns for brent as it is in features
    
    # But wait, 'ret_brent' is daily return. 'z_beta' is a level.
    # Maybe better to use 'inter_beta_vol' or just 'z_beta' vs 'mkt_vol_regime'?
    # Let's stick to the roadmap: "Beta vs Brent".
    # Assuming 'ret_brent' is the feature used.
    
    # Create meshgrid
    XX, YY = np.meshgrid(beta_range, brent_range)
    
    # Create a base sample (median of all other features)
    base_sample = X.median().to_frame().T
    
    # Predict for each point in grid
    Z = np.zeros_like(XX)
    
    # This is slow loop, but fine for 50x50=2500
    for i in range(50):
        for j in range(50):
            sample = base_sample.copy()
            sample['z_beta'] = XX[i, j]
            sample['ret_brent'] = YY[i, j]
            # Update interaction terms if they exist
            if 'inter_brent_earnings' in sample.columns:
                 # We don't have earnings here, assume median
                 pass
            
            Z[i, j] = model.predict(sample)[0]
            
    # Plot Heatmap
    plt.figure(figsize=(10, 8))
    plt.contourf(XX, YY, Z, levels=20, cmap='viridis')
    plt.colorbar(label='Retorno Esperado (5 dias)')
    
    plt.xlabel('Beta (Z-Score)')
    plt.ylabel('Retorno Brent (Diário)')
    plt.title('Superfície de Resposta: Beta vs Brent', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "interaction_surface_2d.pdf")
    print(f"      Salvo: {OUTPUT_DIR / 'interaction_surface_2d.pdf'}")

if __name__ == "__main__":
    run()
