"""
Gera o Modelo M6 de Horizonte Estendido (M6-H) e suas predições.
Baseado em src/analysis/train_m5_horizon.py, mas integrando variáveis Macro.

Target: Retorno Acumulado em 21 dias.
Features: Fundamentos + Macro + Dinâmica.
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
from pathlib import Path
from src.core.config import PROJECT_ROOT

# Configurações
TRAIN_TEST_SPLIT = "2023-01-01"
HORIZON = 21
ROLLING_WINDOW = 252

def load_data_horizon_m6():
    """Carrega e prepara o dataset para horizonte estendido (M6)."""
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
    
    # Q-VAL & Fatores
    df_qval = pd.read_parquet(processed_dir / "qval" / "qval_timeseries.parquet")
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    df_qval = df_qval.sort_values('available_date')
    
    df_factors = pd.read_parquet(processed_dir / "factors" / "petr4_factors.parquet")
    df_factors['available_date'] = pd.to_datetime(df_factors['available_date'])
    df_factors = df_factors.sort_values('available_date')
    
    df = df.sort_values('date')
    
    z_cols = ['z_earnings_yield', 'z_ev_ebitda', 'z_pb_ratio', 'z_roe', 'z_debt_to_equity', 'z_evs']
    available_z_cols = [c for c in z_cols if c in df_qval.columns]
    
    df = pd.merge_asof(df, df_qval[['available_date'] + available_z_cols], left_on='date', right_on='available_date', direction='backward')
    df = pd.merge_asof(df, df_factors[['available_date', 'cma_proxy', 'rmw_proxy']], left_on='date', right_on='available_date', direction='backward')
    
    # Feature Engineering
    df['vol_21d'] = df['ret_petr4'].rolling(21).std()
    df['mom_21d'] = df['ret_petr4'].rolling(21).mean()
    
    for col in available_z_cols:
        df[col] = df[col].clip(lower=-5, upper=5)
    
    # Target: Retorno Acumulado 21d (Forward)
    # Usamos FixedForwardWindowIndexer para garantir que na linha T temos o retorno de T a T+21
    indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=HORIZON)
    df['target_return_21d'] = df['ret_petr4'].rolling(window=indexer).apply(lambda x: np.prod(1 + x) - 1)
    
    # Features M6 (Full)
    features = [
        'y_hat_m2_daily', 'excess_ret_ibov', 'vol_21d', 'mom_21d',
        'ret_brent', 'ret_fx', 'delta_embi', 'cma_proxy', 'rmw_proxy'
    ] + available_z_cols
    
    df_model = df.dropna(subset=features + ['target_return_21d']).copy()
    return df_model.set_index('date'), features

def run():
    print("🚀 Treinando M6 Horizon (21d)...")
    df, features = load_data_horizon_m6()
    
    # Split
    train = df[df.index < TRAIN_TEST_SPLIT]
    test = df[df.index >= TRAIN_TEST_SPLIT]
    
    X_train = train[features]
    y_train = train['target_return_21d']
    X_test = test[features]
    
    # Train XGBoost
    model = xgb.XGBRegressor(
        n_estimators=500, learning_rate=0.01, max_depth=4, subsample=0.8, colsample_bytree=0.8,
        objective='reg:squarederror', random_state=42, n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Predict
    pred_train = model.predict(X_train)
    pred_test = model.predict(X_test)
    
    # Save Predictions
    df_preds = pd.DataFrame(index=df.index)
    df_preds['target_return_21d'] = df['target_return_21d']
    df_preds['pred_m6_horizon'] = np.nan
    df_preds.loc[train.index, 'pred_m6_horizon'] = pred_train
    df_preds.loc[test.index, 'pred_m6_horizon'] = pred_test
    
    # Save to Parquet
    output_path = PROJECT_ROOT / "data" / "outputs" / "m6_horizon_predictions.parquet"
    df_preds.to_parquet(output_path)
    print(f"Predições salvas em {output_path}")

if __name__ == "__main__":
    run()
