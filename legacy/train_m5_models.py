"""
Treinamento dos Modelos M5 (Linear e ML) - Estado da Arte.

Este módulo implementa a nova geração de modelos M5, que integram
Fundamentos (Q-VAL), Macroeconomia e Dinâmica de Mercado.

Modelos:
1. M5-Linear (ElasticNet): Regressão linear penalizada para seleção de features.
2. M5-ML (XGBoost): Gradient Boosting para captura de não-linearidades e interações.

Output:
    - data/outputs/m5_predictions.parquet (Scores e Probabilidades)
    - data/outputs/m5_models/ (Modelos serializados - opcional)
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS

from src.core.config import PROJECT_ROOT

# Configurações
TRAIN_TEST_SPLIT = "2023-01-01"
TARGET_HORIZON = 0  # 0 = Explanatory (Contemporâneo), 1 = Predictive (t+1)
ROLLING_WINDOW = 252 # Para M2 Base

def load_data():
    """Carrega e prepara o dataset unificado."""
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # 1. Retornos
    df_ret = pd.read_parquet(processed_dir / "returns" / "returns.parquet")
    df_ret['date'] = pd.to_datetime(df_ret['date'])
    
    # 2. Macro
    df_macro = pd.read_parquet(processed_dir / "macro_returns.parquet")
    df_macro['date'] = pd.to_datetime(df_macro['date'])
    
    # Merge Retornos + Macro
    df = pd.merge(
        df_ret[['date', 'excess_ret_petr4', 'excess_ret_ibov']],
        df_macro[['date', 'ret_brent', 'ret_fx', 'delta_embi']],
        on='date',
        how='inner'
    )
    
    # =========================================================================
    # GERAÇÃO DO SINAL BASE (M2 - Dynamic CAPM)
    # =========================================================================
    full_exog = sm.add_constant(df['excess_ret_ibov'])
    rolling_model = RollingOLS(df['excess_ret_petr4'], full_exog, window=ROLLING_WINDOW)
    rolling_params = rolling_model.fit().params
    
    # Shift params para evitar look-ahead bias
    lagged_params = rolling_params.shift(1)
    
    # Predição Base (M2)
    df['y_hat_m2'] = (lagged_params['const'] + lagged_params['excess_ret_ibov'] * df['excess_ret_ibov'])
    
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
    
    # Lista de Z-Scores individuais (Granularidade Máxima)
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
    df['vol_21d'] = df['excess_ret_petr4'].rolling(21).std()
    df['mom_21d'] = df['excess_ret_petr4'].rolling(21).mean()
    
    # Target: Retorno em t+1
    df['target_return'] = df['excess_ret_petr4'].shift(-TARGET_HORIZON)
    
    # RESIDUAL LEARNING
    df['target_residual'] = df['target_return'] - df['y_hat_m2']
    
    # Drop NaNs
    cols_features = [
        'y_hat_m2',          
        'excess_ret_ibov',   
        'ret_brent', 'ret_fx', 'delta_embi',
        'cma_proxy', 'rmw_proxy',
        'vol_21d', 'mom_21d'
    ] + available_z_cols
    
    df_model = df.dropna(subset=cols_features + ['target_return', 'target_residual']).copy()
    return df_model.set_index('date'), cols_features

def train_models():
    print("Iniciando treinamento M5 (Linear vs ML)...")
    
    df, features = load_data()
    
    # Split
    train = df[df.index < TRAIN_TEST_SPLIT]
    test = df[df.index >= TRAIN_TEST_SPLIT]
    
    X_train = train[features]
    y_train_full = train['target_return']
    y_train_resid = train['target_residual']
    
    X_test = test[features]
    y_test_full = test['target_return']
    
    print(f"Treino: {len(train)} | Teste: {len(test)}")
    
    # =========================================================================
    # 1. M5-Linear (RidgeCV - Auto Tuning)
    # =========================================================================
    print("Treinando M5-Linear (RidgeCV)...")
    
    # Usar RobustScaler para lidar com outliers nos retornos
    model_linear = Pipeline([
        ('scaler', RobustScaler()),
        ('regressor', RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0, 1000.0]))
    ])
    
    model_linear.fit(X_train, y_train_full)
    pred_linear = model_linear.predict(X_test)
    
    r2_linear = r2_score(y_test_full, pred_linear)
    print(f"M5-Linear R2 OOS: {r2_linear:.4f}")
    print(f"Melhor Alpha: {model_linear.named_steps['regressor'].alpha_}")
    
    # =========================================================================
    # 2. M5-ML (Stacked: Ridge Base + XGBoost Residual)
    # =========================================================================
    print("Treinando M5-ML (Stacked)...")
    
    # Passo 1: Base Linear Robusta (M4-like)
    # Usamos RidgeCV também para a base para garantir estabilidade
    macro_cols = ['y_hat_m2', 'ret_brent', 'ret_fx', 'delta_embi', 'cma_proxy', 'rmw_proxy']
    
    model_base = Pipeline([
        ('scaler', RobustScaler()),
        ('regressor', RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0]))
    ])
    
    model_base.fit(X_train[macro_cols], y_train_full)
    
    base_pred_train = model_base.predict(X_train[macro_cols])
    base_pred_test = model_base.predict(X_test[macro_cols])
    
    r2_base = r2_score(y_test_full, base_pred_test)
    print(f"Base Model (M4-like) R2 OOS: {r2_base:.4f}")
    
    # Passo 2: Calcular Resíduo
    resid_train = y_train_full - base_pred_train
    
    # Passo 3: Treinar XGBoost no Resíduo
    # Focar em capturar o que sobrou (Z-Scores e Dinâmica)
    model_ml = xgb.XGBRegressor(
        n_estimators=50,        # Poucas árvores para evitar overfitting no ruído
        learning_rate=0.05,
        max_depth=2,            # Árvores muito simples (interações de baixa ordem)
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=1.0,              # Regularização conservadora
        random_state=42,
        n_jobs=-1
    )
    
    model_ml.fit(X_train, resid_train)
    
    pred_residual_ml = model_ml.predict(X_test)
    pred_ml = base_pred_test + pred_residual_ml
    
    r2_ml = r2_score(y_test_full, pred_ml)
    print(f"M5-ML R2 OOS: {r2_ml:.4f}")
    
    # =========================================================================
    # Salvar Predições
    # =========================================================================
    results = pd.DataFrame(index=test.index)
    results['y_true'] = y_test_full
    results['pred_linear'] = pred_linear
    results['pred_ml'] = pred_ml


def load_data():
    """Carrega e prepara o dataset unificado (mesma lógica do estimate_nested_models)."""
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # 1. Retornos
    df_ret = pd.read_parquet(processed_dir / "returns" / "returns.parquet")
    df_ret['date'] = pd.to_datetime(df_ret['date'])
    
    # 2. Macro
    df_macro = pd.read_parquet(processed_dir / "macro_returns.parquet")
    df_macro['date'] = pd.to_datetime(df_macro['date'])
    
    # Merge Retornos + Macro
    df = pd.merge(
        df_ret[['date', 'excess_ret_petr4', 'excess_ret_ibov']],
        df_macro[['date', 'ret_brent', 'ret_fx', 'delta_embi']],
        on='date',
        how='inner'
    )
    
    # =========================================================================
    # GERAÇÃO DO SINAL BASE (M2 - Dynamic CAPM)
    # =========================================================================
    full_exog = sm.add_constant(df['excess_ret_ibov'])
    rolling_model = RollingOLS(df['excess_ret_petr4'], full_exog, window=ROLLING_WINDOW)
    rolling_params = rolling_model.fit().params
    
    # Shift params para evitar look-ahead bias
    lagged_params = rolling_params.shift(1)
    
    # Predição Base (M2)
    df['y_hat_m2'] = (lagged_params['const'] + lagged_params['excess_ret_ibov'] * df['excess_ret_ibov'])
    
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
    
    # Lista de Z-Scores individuais (Granularidade Máxima)
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
    df['vol_21d'] = df['excess_ret_petr4'].rolling(21).std()
    df['mom_21d'] = df['excess_ret_petr4'].rolling(21).mean()
    
    # Target: Retorno Contemporâneo (Explanatory Model)
    # Para ser comparável com M4 (que usa Macro contemporâneo), não devemos shiftar.
    # Se quiséssemos um modelo puramente preditivo, teríamos que lagar Macro também.
    # Como o objetivo é "Eficiência Informacional" (quanto os dados explicam), usamos t.
    df['target_return'] = df['excess_ret_petr4']
    
    # RESIDUAL LEARNING (Apenas para ML)
    df['target_residual'] = df['target_return'] - df['y_hat_m2']
    
    # Drop NaNs
    cols_features = [
        'y_hat_m2',          
        'excess_ret_ibov',   
        'ret_brent', 'ret_fx', 'delta_embi',
        'cma_proxy', 'rmw_proxy',
        'vol_21d', 'mom_21d'
    ] + available_z_cols
    
    df_model = df.dropna(subset=cols_features + ['target_return', 'target_residual']).copy()
    return df_model.set_index('date'), cols_features

def train_models():
    print("Iniciando treinamento M5 (Linear vs ML)...")
    
    df, features = load_data()
    
    # Split
    train = df[df.index < TRAIN_TEST_SPLIT]
    test = df[df.index >= TRAIN_TEST_SPLIT]
    
    X_train = train[features]
    y_train_full = train['target_return']
    
    X_test = test[features]
    y_test_full = test['target_return']
    
    print(f"Treino: {len(train)} | Teste: {len(test)}")
    
    # =========================================================================
    # 1. M5-Linear (RidgeCV - Auto Tuning)
    # =========================================================================
    print("Treinando M5-Linear (RidgeCV)...")
    
    # Usar RobustScaler para lidar com outliers nos retornos
    model_linear = Pipeline([
        ('scaler', RobustScaler()),
        ('regressor', RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0, 1000.0]))
    ])
    
    model_linear.fit(X_train, y_train_full)
    pred_linear = model_linear.predict(X_test)
    
    r2_linear = r2_score(y_test_full, pred_linear)
    print(f"M5-Linear R2 OOS: {r2_linear:.4f}")
    print(f"Melhor Alpha: {model_linear.named_steps['regressor'].alpha_}")
    
    # =========================================================================
    # 2. M5-ML (Stacked: Linear Macro Base + XGBoost Residual)
    # =========================================================================
    print("Treinando M5-ML (Stacked)...")
    
    # Passo 1: Base Linear Robusta (M4-like)
    # Usamos RidgeCV também para a base para garantir estabilidade
    macro_cols = ['y_hat_m2', 'ret_brent', 'ret_fx', 'delta_embi', 'cma_proxy', 'rmw_proxy']
    
    model_base = Pipeline([
        ('scaler', RobustScaler()),
        ('regressor', RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0]))
    ])
    
    model_base.fit(X_train[macro_cols], y_train_full)
    
    base_pred_train = model_base.predict(X_train[macro_cols])
    base_pred_test = model_base.predict(X_test[macro_cols])
    
    r2_base = r2_score(y_test_full, base_pred_test)
    print(f"Base Model (M4-like) R2 OOS: {r2_base:.4f}")
    
    # Passo 2: Calcular Resíduo
    resid_train = y_train_full - base_pred_train
    
    # Passo 3: Treinar XGBoost no Resíduo
    # Focar em capturar o que sobrou (Z-Scores e Dinâmica)
    model_ml = xgb.XGBRegressor(
        n_estimators=100,       # Mais árvores
        learning_rate=0.05,
        max_depth=3,            # Um pouco mais complexo
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=0.1,              # Menos regularização
        random_state=42,
        n_jobs=-1
    )
    
    model_ml.fit(X_train, resid_train)
    
    pred_residual_ml = model_ml.predict(X_test)
    pred_ml = base_pred_test + pred_residual_ml
    
    r2_ml = r2_score(y_test_full, pred_ml)
    print(f"M5-ML R2 OOS: {r2_ml:.4f}")
    
    # =========================================================================
    # Salvar Predições
    # =========================================================================
    results = pd.DataFrame(index=test.index)
    results['y_true'] = y_test_full
    results['pred_linear'] = pred_linear
    results['pred_ml'] = pred_ml
    
    output_dir = PROJECT_ROOT / "data" / "outputs"
    output_path = output_dir / "m5_predictions.parquet"
    results.to_parquet(output_path)
    
    print(f"Predições salvas em: {output_path}")
    
    # Salvar Feature Importance (ML)
    importance = pd.DataFrame({
        'Feature': features,
        'Importance': model_ml.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\nTop 5 Features (M5-ML):")
    print(importance.head(5))

if __name__ == "__main__":
    train_models()
