"""
Treinamento dos Modelos M5 de Horizonte Estendido (M5-H).

Este módulo treina modelos para prever o retorno acumulado em 21 dias (mensal),
servindo de base para a estratégia de Valor Justo (Fair Value).

Modelos:
1. M5a-H (Huber): Regressão robusta para capturar tendência linear.
2. M5b-H (XGBoost): Gradient Boosting para capturar não-linearidades.

Target:
    - Retorno Total Acumulado em 21 dias (ret_21d).

Output:
    - data/outputs/m5_horizon_predictions.parquet
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.linear_model import HuberRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS

from src.core.config import PROJECT_ROOT

# Configurações
TRAIN_TEST_SPLIT = "2023-01-01"
HORIZON = 21  # 21 dias úteis (~1 mês)
ROLLING_WINDOW = 252 # Para M2 Base

def load_data_horizon():
    """Carrega e prepara o dataset para horizonte estendido."""
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # 1. Retornos (Total e CDI)
    df_ret = pd.read_parquet(processed_dir / "returns" / "returns.parquet")
    df_ret['date'] = pd.to_datetime(df_ret['date'])
    
    # 2. Macro
    df_macro = pd.read_parquet(processed_dir / "macro_returns.parquet")
    df_macro['date'] = pd.to_datetime(df_macro['date'])
    
    # Merge Retornos + Macro
    df = pd.merge(
        df_ret[['date', 'ret_petr4', 'excess_ret_petr4', 'excess_ret_ibov', 'cdi_daily']],
        df_macro[['date', 'ret_brent', 'ret_fx', 'delta_embi']],
        on='date',
        how='inner'
    )
    
    # =========================================================================
    # GERAÇÃO DO SINAL BASE (M2 - Dynamic CAPM) - Mantido como Feature
    # =========================================================================
    full_exog = sm.add_constant(df['excess_ret_ibov'])
    rolling_model = RollingOLS(df['excess_ret_petr4'], full_exog, window=ROLLING_WINDOW)
    rolling_params = rolling_model.fit().params
    
    # Shift params para evitar look-ahead bias
    lagged_params = rolling_params.shift(1)
    
    # Predição Base (M2) - Diária
    df['y_hat_m2_daily'] = (lagged_params['const'] + lagged_params['excess_ret_ibov'] * df['excess_ret_ibov'])
    
    # 3. Q-VAL (Trimestral -> Diário)
    df_qval = pd.read_parquet(processed_dir / "qval" / "qval_timeseries.parquet")
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    df_qval = df_qval.sort_values('available_date')
    
    # 4. Fatores
    df_factors = pd.read_parquet(processed_dir / "factors" / "petr4_factors.parquet")
    df_factors['available_date'] = pd.to_datetime(df_factors['available_date'])
    df_factors = df_factors.sort_values('available_date')
    
    # Merge AsOf
    df = df.sort_values('date')
    
    # Lista de Z-Scores
    z_cols = [
        'z_earnings_yield', 'z_ev_ebitda', 'z_pb_ratio', # Valor
        'z_roe',                                         # Qualidade
        'z_debt_to_equity'                               # Risco
    ]
    
    available_z_cols = [c for c in z_cols if c in df_qval.columns]
    
    df = pd.merge_asof(
        df, 
        df_qval[['available_date'] + available_z_cols], 
        left_on='date', 
        right_on='available_date', 
        direction='backward'
    )
    
    df = pd.merge_asof(
        df,
        df_factors[['available_date', 'cma_proxy', 'rmw_proxy']],
        left_on='date',
        right_on='available_date',
        direction='backward'
    )
    
    # Feature Engineering Adicional (Dinâmica)
    df['vol_21d'] = df['ret_petr4'].rolling(21).std()
    df['mom_21d'] = df['ret_petr4'].rolling(21).mean()
    
    # Clip Z-Scores para evitar outliers extremos (ex: z_ev_ebitda = -189)
    for col in available_z_cols:
        df[col] = df[col].clip(lower=-5, upper=5)
    
    # =========================================================================
    # TARGET: Retorno Acumulado em 21 dias (Total Return)
    # =========================================================================
    # R_{t -> t+21} = prod(1 + r) - 1
    # Usamos rolling reverso (shiftado)
    
    indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=HORIZON)
    df['target_return_21d'] = df['ret_petr4'].rolling(window=indexer).apply(lambda x: np.prod(1 + x) - 1)
    
    # Drop NaNs (perdemos os últimos 21 dias e os primeiros 252 dias)
    cols_features = [
        'y_hat_m2_daily',          
        'excess_ret_ibov',   
        'ret_brent', 'ret_fx', 'delta_embi',
        'cma_proxy', 'rmw_proxy',
        'vol_21d', 'mom_21d'
    ] + available_z_cols
    
    df_model = df.dropna(subset=cols_features + ['target_return_21d']).copy()
    return df_model.set_index('date'), cols_features

def train_horizon_models():
    print(f"Iniciando treinamento M5 Horizon (H={HORIZON} dias)...")
    
    df, features = load_data_horizon()
    
    # Split
    train = df[df.index < TRAIN_TEST_SPLIT]
    test = df[df.index >= TRAIN_TEST_SPLIT]
    
    X_train = train[features]
    y_train = train['target_return_21d']
    
    X_test = test[features]
    y_test = test['target_return_21d']
    
    print(f"   Treino: {len(train)} amostras | Teste: {len(test)} amostras")
    
    # =========================================================================
    # 1. M5a-H: Huber Regressor (Robusto a outliers)
    # =========================================================================
    print("   Treinando M5a-H (Huber)...")
    pipe_huber = Pipeline([
        ('scaler', StandardScaler()),
        ('model', HuberRegressor(epsilon=1.35, max_iter=1000))
    ])
    pipe_huber.fit(X_train, y_train)
    
    y_pred_huber_train = pipe_huber.predict(X_train)
    y_pred_huber_test = pipe_huber.predict(X_test)
    
    r2_huber = r2_score(y_test, y_pred_huber_test)
    mae_huber = mean_absolute_error(y_test, y_pred_huber_test)
    print(f"   [M5a-H] R² Test: {r2_huber:.4f} | MAE: {mae_huber:.4f}")
    
    # =========================================================================
    # 2. M5b-H: XGBoost (Non-Linear)
    # =========================================================================
    print("   Treinando M5b-H (XGBoost)...")
    model_xgb = xgb.XGBRegressor(
        n_estimators=500,
        learning_rate=0.01,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='reg:squarederror',
        random_state=42,
        n_jobs=-1,
        early_stopping_rounds=50
    )
    
    # XGBoost precisa de eval set para early stopping
    # Usaremos os primeiros 20% do teste como validação ou um split do treino?
    # Para manter consistência temporal, vamos usar os últimos 20% do treino como validação
    val_size = int(len(X_train) * 0.2)
    X_train_sub = X_train.iloc[:-val_size]
    y_train_sub = y_train.iloc[:-val_size]
    X_val = X_train.iloc[-val_size:]
    y_val = y_train.iloc[-val_size:]
    
    model_xgb.fit(
        X_train_sub, y_train_sub,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    y_pred_xgb_train = model_xgb.predict(X_train)
    y_pred_xgb_test = model_xgb.predict(X_test)
    
    r2_xgb = r2_score(y_test, y_pred_xgb_test)
    mae_xgb = mean_absolute_error(y_test, y_pred_xgb_test)
    print(f"   [M5b-H] R² Test: {r2_xgb:.4f} | MAE: {mae_xgb:.4f}")
    
    # =========================================================================
    # Salvar Predições
    # =========================================================================
    print("   Salvando predições...")
    
    # Criar DataFrame com predições para todo o período (incluindo treino para visualização)
    df_out = df[['target_return_21d', 'ret_petr4', 'cdi_daily']].copy()
    
    # Predições Huber
    df_out['pred_huber_21d'] = pipe_huber.predict(df[features])
    
    # Predições XGBoost
    df_out['pred_xgb_21d'] = model_xgb.predict(df[features])
    
    # Salvar
    output_path = PROJECT_ROOT / "data/outputs/m5_horizon_predictions.parquet"
    df_out.to_parquet(output_path)
    print(f"   Salvo em: {output_path}")

if __name__ == "__main__":
    train_horizon_models()
