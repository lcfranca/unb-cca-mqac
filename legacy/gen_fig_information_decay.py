import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

# Config
DATA_PATH = PROJECT_ROOT / "data/processed/ml_dataset.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data/outputs/figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

set_style()

def run():
    print("🚀 Gerando Gráfico Mestre de Eficiência Informacional...")
    
    # 1. Load Data
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    
    df = pd.read_parquet(DATA_PATH)
    if 'date' in df.columns:
        df = df.set_index('date')
    df = df.sort_index()
    
    # 1. Load Data
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    
    df_full = pd.read_parquet(DATA_PATH)
    if 'date' in df_full.columns:
        df_full = df_full.set_index('date')
    df_full = df_full.sort_index()
    
    # Reconstruct Price Index since 'close' is not in the dataset
    # We assume the first value is 100
    df_full['price_index'] = (1 + df_full['ret_petr4']).cumprod() * 100
    
    # 2. Train Model (On Full History for Robustness)
    print("   Treinando modelo (Histórico Completo) para extração de SHAP...")
    target_col = 'target_return_5d'
    df_model = df_full.dropna(subset=[target_col])
    
    drop_cols = ['target_return_1d', 'target_return_5d', 'target_return_21d', 'ticker', 'date', 'available_date', 'days_since_release', 'price_index']
    features = [c for c in df_model.columns if c not in drop_cols]
    
    X = df_model[features]
    y = df_model[target_col]
    
    params = {'subsample': 0.8, 'n_estimators': 500, 'min_child_weight': 1, 'max_depth': 5, 'learning_rate': 0.1, 'gamma': 0.1, 'colsample_bytree': 0.7}
    model = xgb.XGBRegressor(**params, objective='reg:squarederror', n_jobs=-1, random_state=42)
    model.fit(X, y)
    
    # 3. Compute SHAP
    print("   Calculando valores SHAP...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    shap_df = pd.DataFrame(shap_values, columns=features, index=X.index)
    
    # 4. Calculate "Fundamental Dominance"
    # Define categories
    fund_cols = [c for c in features if c.startswith('z_') or c.startswith('score_') or 'value' in c]
    macro_cols = [c for c in features if c in ['ret_brent', 'delta_embi', 'excess_ret_ibov', 'ret_fx', 'mkt_vol_regime', 'mkt_trend_sma200']]
    tech_cols = [c for c in features if 'lag' in c or 'vol_20d' in c]
    
    print(f"   Features Fundamentais ({len(fund_cols)}): {fund_cols}")
    
    # Sum absolute importance per category
    shap_df['total_imp'] = shap_df.abs().sum(axis=1)
    shap_df['fund_imp'] = shap_df[fund_cols].abs().sum(axis=1)
    
    # Calculate Ratio (Fundamental Dominance)
    # Smoothing is essential to remove daily noise and show the "Regime"
    # We calculate this on the full dataset first
    df_model['fund_dominance'] = (shap_df['fund_imp'] / shap_df['total_imp']).rolling(10).mean() # Increased smoothing slightly
    
    # Debug
    print(f"   Média Dominância Fundamentalista: {df_model['fund_dominance'].mean():.4f}")
    if df_model['fund_dominance'].mean() == 0:
        print("   AVISO: Dominância é zero. Verifique as features.")
        print("   Exemplo de SHAP values (Fund):")
        print(shap_df[fund_cols].head())

    # 5. Filter for Visualization (2021+)
    df = df_model[df_model.index >= '2021-01-01'].copy()
    
    # 6. Plotting the Master Chart
    print("   Renderizando visualização...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True, gridspec_kw={'height_ratios': [1.5, 1], 'hspace': 0.05})
    
    # --- AX1: Price & Efficiency Windows ---
    
    # Plot Price
    ax1.plot(df.index, df['price_index'], color='black', linewidth=1.5, label='Índice de Preço (Base 100)')
    
    # Identify Earnings Releases
    releases = df['available_date'].unique()
    releases = sorted([pd.to_datetime(d) for d in releases if pd.to_datetime(d) >= df.index.min()])
    
    # Add "Efficiency Windows" (Shaded Areas)
    # We shade the first 15 days after each release
    for i, date in enumerate(releases):
        # Define window end
        window_end = date + pd.Timedelta(days=15)
        
        # Shade
        ax1.axvspan(date, window_end, color=COLORS['primary'], alpha=0.15, lw=0)
        
        # Add Vertical Line
        ax1.axvline(date, color=COLORS['primary'], linestyle='--', alpha=0.6, linewidth=1)
        
        # Label specific events (avoid overcrowding)
        # Label every other event or just the year? Let's try labeling the quarter if possible
        # Assuming standard quarters, we can just label "Divulgação"
        if i % 2 == 0: # Label every 2nd event to save space
            ax1.text(date, df['price_index'].max()*0.95, 'Divulgação\nResultados', rotation=90, verticalalignment='top', fontsize=8, color=COLORS['primary'], alpha=0.8)

        # --- Add Shading to Bottom Panel (AX2) as well ---
        ax2.axvspan(date, window_end, color=COLORS['primary'], alpha=0.15, lw=0)
        ax2.axvline(date, color=COLORS['primary'], linestyle='--', alpha=0.6, linewidth=1)

    # Legend for Shading
    from matplotlib.patches import Patch
    legend_elements = [
        plt.Line2D([0], [0], color='black', lw=1.5, label='Índice de Preço'),
        Patch(facecolor=COLORS['primary'], alpha=0.15, label='Janela de Eficiência (15 dias pós-evento)'),
        plt.Line2D([0], [0], color=COLORS['primary'], linestyle='--', label='Data de Divulgação')
    ]
    ax1.legend(handles=legend_elements, loc='upper left', frameon=True)
    ax1.set_ylabel('Índice de Retorno Acumulado', fontweight='bold')
    ax1.set_title('Dinâmica de Eficiência Informacional: Ciclos de Relevância Fundamentalista (PETR4)', fontweight='bold', fontsize=14)
    ax1.grid(True, alpha=0.2)
    
    # --- AX2: Fundamental Dominance (The Decay) ---
    
    # Plot Dominance Curve
    # Color gradient based on value? Or just a line?
    # Let's use a filled area
    
    ax2.plot(df.index, df['fund_dominance'], color=COLORS['secondary'], linewidth=1.5)
    ax2.fill_between(df.index, df['fund_dominance'], 0, color=COLORS['secondary'], alpha=0.1)
    
    # Add Threshold Line (e.g., average dominance)
    avg_dom = df['fund_dominance'].mean()
    ax2.axhline(avg_dom, color='gray', linestyle=':', label=f'Média Histórica ({avg_dom:.2f})')
    
    # Highlight the decay pattern
    # We can add arrows or text for one specific clear example
    # Find a clear peak
    
    ax2.set_ylabel('Dominância Fundamentalista\n(% da Importância Total)', fontweight='bold')
    ax2.set_xlabel('Data', fontweight='bold')
    
    # Format X Axis
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b/%y'))
    plt.xticks(rotation=45)
    
    # Add explanatory text box
    textstr = '\n'.join((
        r'$\bf{Interpretação:}$',
        r'Picos indicam momentos onde',
        r'os fundamentos explicam',
        r'a maior parte do preço.',
        r'Quedas indicam transição',
        r'para regime Macro/Ruído.'
    ))
    props = dict(boxstyle='round', facecolor='white', alpha=0.8)
    ax2.text(0.02, 0.05, textstr, transform=ax2.transAxes, fontsize=9,
            verticalalignment='bottom', bbox=props)
    
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.2)
    
    # Align axes
    plt.tight_layout()
    
    # Save
    outfile = OUTPUT_DIR / "master_efficiency_dynamics.pdf"
    plt.savefig(outfile)
    print(f"   Salvo: {outfile}")

    # 7. Generate Decay Table (LaTeX)
    print("   Gerando Tabela de Decaimento Informacional...")
    
    # We need to calculate metrics aggregated by time buckets
    # Metrics: Fundamental Dominance, Predictive Power (IC - Correlation)
    
    # Add predictions to df_model (the full dataset) to calculate IC
    df_model['predicted_return'] = model.predict(X)
    
    # Define Buckets
    bins = [0, 5, 10, 15, 20, 40, 65]
    labels = ['0-5 dias', '6-10 dias', '11-15 dias', '16-20 dias', '21-40 dias', '41-65 dias']
    
    df_model['day_bucket'] = pd.cut(df_model['days_since_release'], bins=bins, labels=labels, right=True, include_lowest=True)
    
    # Group by Bucket
    decay_stats = []
    
    for label in labels:
        subset = df_model[df_model['day_bucket'] == label]
        if len(subset) > 0:
            # Fundamental Dominance
            avg_dom = subset['fund_dominance'].mean() * 100
            
            # Predictive Power (IC)
            ic = subset[target_col].corr(subset['predicted_return']) * 100
            
            # R2 (Out of Sample proxy)
            from sklearn.metrics import r2_score
            r2 = r2_score(subset[target_col], subset['predicted_return']) * 100
            
            decay_stats.append({
                'Janela Temporal': label,
                'Dominância Fund. (%)': f"{avg_dom:.1f}\%",
                'Info. Coefficient (IC) (%)': f"{ic:.1f}\%",
                'R² (%)': f"{r2:.1f}\%"
            })
            
    decay_df = pd.DataFrame(decay_stats)
    
    # Export to LaTeX
    table_path = PROJECT_ROOT / "data/outputs/tables/tab_decaimento_informacional.tex"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    
    latex_content = decay_df.to_latex(index=False, escape=False, column_format='lccc', caption='Decaimento da Eficiência Informacional e Dominância Fundamentalista', label='tab:decaimento_info')
    
    # Style the table slightly for better look in the document
    latex_content = latex_content.replace('\\toprule', '\\toprule\n\\textbf{Janela Temporal} & \\textbf{Dominância Fund.} & \\textbf{Info. Coefficient} & \\textbf{R² (Poder Preditivo)} \\\\')
    
    with open(table_path, 'w') as f:
        f.write(latex_content)
        
    print(f"   Tabela salva em: {table_path}")
    print(decay_df)

if __name__ == "__main__":
    run()
