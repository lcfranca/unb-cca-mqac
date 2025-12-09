"""
Gera gráfico de Feature Importance para o modelo M5b (XGBoost).
Abre a "Caixa Preta" do modelo de Machine Learning.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

# Configurações
TRAIN_TEST_SPLIT = "2023-01-01"
HORIZON = 21
ROLLING_WINDOW = 252

def load_data_horizon():
    """Carrega e prepara o dataset para horizonte estendido (Cópia de train_m5_horizon.py)."""
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # 1. Retornos
    df_ret = pd.read_parquet(processed_dir / "returns" / "returns.parquet")
    df_ret['date'] = pd.to_datetime(df_ret['date'])
    
    # 2. Macro
    df_macro = pd.read_parquet(processed_dir / "macro_returns.parquet")
    df_macro['date'] = pd.to_datetime(df_macro['date'])
    
    # Merge
    df = pd.merge(
        df_ret[['date', 'ret_petr4', 'excess_ret_petr4', 'excess_ret_ibov', 'cdi_daily']],
        df_macro[['date', 'ret_brent', 'ret_fx', 'delta_embi']],
        on='date',
        how='inner'
    )
    
    # M2 Base
    full_exog = sm.add_constant(df['excess_ret_ibov'])
    rolling_model = RollingOLS(df['excess_ret_petr4'], full_exog, window=ROLLING_WINDOW)
    rolling_params = rolling_model.fit().params
    lagged_params = rolling_params.shift(1)
    df['y_hat_m2_daily'] = (lagged_params['const'] + lagged_params['excess_ret_ibov'] * df['excess_ret_ibov'])
    
    # 3. Q-VAL
    df_qval = pd.read_parquet(processed_dir / "qval" / "qval_timeseries.parquet")
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    df_qval = df_qval.sort_values('available_date')
    
    # 4. Fatores
    df_factors = pd.read_parquet(processed_dir / "factors" / "petr4_factors.parquet")
    df_factors['available_date'] = pd.to_datetime(df_factors['available_date'])
    df_factors = df_factors.sort_values('available_date')
    
    # Merge AsOf
    df = df.sort_values('date')
    z_cols = ['z_earnings_yield', 'z_ev_ebitda', 'z_pb_ratio', 'z_roe', 'z_debt_to_equity']
    available_z_cols = [c for c in z_cols if c in df_qval.columns]
    
    df = pd.merge_asof(df, df_qval[['available_date'] + available_z_cols], left_on='date', right_on='available_date', direction='backward')
    df = pd.merge_asof(df, df_factors[['available_date', 'cma_proxy', 'rmw_proxy']], left_on='date', right_on='available_date', direction='backward')
    
    # Feature Engineering
    df['vol_21d'] = df['ret_petr4'].rolling(21).std()
    df['mom_21d'] = df['ret_petr4'].rolling(21).mean()
    
    for col in available_z_cols:
        df[col] = df[col].clip(lower=-5, upper=5)
    
    # Target
    indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=HORIZON)
    df['target_return_21d'] = df['ret_petr4'].rolling(window=indexer).apply(lambda x: np.prod(1 + x) - 1)
    
    cols_features = [
        'y_hat_m2_daily', 'excess_ret_ibov', 'ret_brent', 'ret_fx', 'delta_embi',
        'cma_proxy', 'rmw_proxy', 'vol_21d', 'mom_21d'
    ] + available_z_cols
    
    df_model = df.dropna(subset=cols_features + ['target_return_21d']).copy()
    return df_model.set_index('date'), cols_features

def run():
    set_style()
    sns.set_theme(style="whitegrid", rc={"grid.linestyle": ":", "axes.spines.right": False, "axes.spines.top": False})
    
    df, features = load_data_horizon()
    
    # Train XGBoost
    train = df[df.index < TRAIN_TEST_SPLIT]
    X_train = train[features]
    y_train = train['target_return_21d']
    
    model_xgb = xgb.XGBRegressor(
        n_estimators=500, learning_rate=0.01, max_depth=4, subsample=0.8, colsample_bytree=0.8,
        objective='reg:squarederror', random_state=42, n_jobs=-1, early_stopping_rounds=50
    )
    
    val_size = int(len(X_train) * 0.2)
    X_train_sub = X_train.iloc[:-val_size]
    y_train_sub = y_train.iloc[:-val_size]
    X_val = X_train.iloc[-val_size:]
    y_val = y_train.iloc[-val_size:]
    
    model_xgb.fit(X_train_sub, y_train_sub, eval_set=[(X_val, y_val)], verbose=False)
    
    # Extract Feature Importance (Gain)
    importance = model_xgb.get_booster().get_score(importance_type='gain')
    df_imp = pd.DataFrame(list(importance.items()), columns=['Feature', 'Gain'])
    df_imp = df_imp.sort_values('Gain', ascending=False).head(10)
    
    # Map Semantic Names
    name_map = {
        'y_hat_m2_daily': 'Beta Dinâmico (M2)',
        'excess_ret_ibov': 'Risco de Mercado (Ibovespa)',
        'ret_brent': 'Petróleo (Brent)',
        'ret_fx': 'Câmbio (USD/BRL)',
        'delta_embi': 'Risco País (EMBI+)',
        'cma_proxy': 'Fator Investimento (CMA)',
        'rmw_proxy': 'Fator Lucratividade (RMW)',
        'vol_21d': 'Volatilidade (21d)',
        'mom_21d': 'Momentum (21d)',
        'z_earnings_yield': 'Valor: Earnings Yield',
        'z_ev_ebitda': 'Valor: EV/EBITDA',
        'z_pb_ratio': 'Valor: P/VP',
        'z_roe': 'Qualidade: ROE',
        'z_debt_to_equity': 'Risco: Dívida/PL'
    }
    df_imp['Feature'] = df_imp['Feature'].map(name_map).fillna(df_imp['Feature'])
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df_imp, x='Gain', y='Feature', palette='viridis', ax=ax)
    
    ax.set_title('Top 10 Drivers de Valor Justo (XGBoost Feature Importance)', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Ganho Médio (Importância Preditiva)', fontsize=11)
    ax.set_ylabel('')
    
    # Add values to bars
    for i, v in enumerate(df_imp['Gain']):
        ax.text(v + v*0.01, i, f'{v:.1f}', va='center', fontsize=10, fontweight='bold', color='#333333')
        
    plt.tight_layout()
    
    output_path = PROJECT_ROOT / "data/outputs/figures/feature_importance_m5b.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figura salva em: {output_path}")

if __name__ == "__main__":
    run()
