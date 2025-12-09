"""
Gera o Modelo M6 (Integração Total via ML) e calcula métricas de performance.
Este modelo expande o M5b ao integrar explicitamente variáveis macroeconômicas e fatores de risco
no vetor de features do XGBoost.
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
from pathlib import Path
import json
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from src.core.config import PROJECT_ROOT

# Configurações
TRAIN_TEST_SPLIT = "2023-01-01"
HORIZON = 0  # 0 = Explanatory (Contemporâneo), 1 = Predictive (t+1)
ROLLING_WINDOW = 252

def load_data_m6():
    """Carrega e prepara o dataset para o Modelo M6 (Full Integration)."""
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # 1. Retornos
    df_ret = pd.read_parquet(processed_dir / "returns" / "returns.parquet")
    df_ret['date'] = pd.to_datetime(df_ret['date'])
    
    # 2. Macro (M4)
    df_macro = pd.read_parquet(processed_dir / "macro_returns.parquet")
    df_macro['date'] = pd.to_datetime(df_macro['date'])
    
    # Merge Retornos + Macro
    df = pd.merge(
        df_ret[['date', 'ret_petr4', 'excess_ret_petr4', 'excess_ret_ibov', 'cdi_daily']],
        df_macro[['date', 'ret_brent', 'ret_fx', 'delta_embi']],
        on='date',
        how='inner'
    )
    
    # 3. Dinâmica de Mercado (M2)
    # Recalculando predição do CAPM Dinâmico como feature base
    full_exog = sm.add_constant(df['excess_ret_ibov'])
    rolling_model = RollingOLS(df['excess_ret_petr4'], full_exog, window=ROLLING_WINDOW)
    rolling_params = rolling_model.fit().params
    lagged_params = rolling_params.shift(1)
    df['y_hat_m2_daily'] = (lagged_params['const'] + lagged_params['excess_ret_ibov'] * df['excess_ret_ibov'])
    
    # Volatilidade e Momentum (21d)
    df['vol_21d'] = df['ret_petr4'].rolling(21).std()
    df['mom_21d'] = df['ret_petr4'].rolling(21).mean()
    
    # 4. Fundamentos (M3/M5) - Z-Scores
    df_qval = pd.read_parquet(processed_dir / "qval" / "qval_timeseries.parquet")
    # Ajuste de data de disponibilidade (Quarter End + 3 meses de lag de divulgação)
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    df_qval = df_qval.sort_values('available_date')
    
    # 5. Fatores de Risco (Fama-French Proxies)
    df_factors = pd.read_parquet(processed_dir / "factors" / "petr4_factors.parquet")
    df_factors['available_date'] = pd.to_datetime(df_factors['available_date'])
    df_factors = df_factors.sort_values('available_date')
    
    # Merge AsOf (Backward) para garantir que usamos apenas dados disponíveis
    df = df.sort_values('date')
    
    # Selecionar colunas de Z-Score
    z_cols = ['z_earnings_yield', 'z_ev_ebitda', 'z_pb_ratio', 'z_roe', 'z_debt_to_equity', 'z_evs']
    available_z_cols = [c for c in z_cols if c in df_qval.columns]
    
    df = pd.merge_asof(df, df_qval[['available_date'] + available_z_cols], left_on='date', right_on='available_date', direction='backward')
    df = pd.merge_asof(df, df_factors[['available_date', 'cma_proxy', 'rmw_proxy']], left_on='date', right_on='available_date', direction='backward')
    
    # Tratamento de Outliers nos Z-Scores (Clip)
    for col in available_z_cols:
        df[col] = df[col].clip(lower=-5, upper=5)
    
    # Target: Retorno Contemporâneo (Explanatory) ou Predictive (t+1)
    # Para alinhar com M5-ML (R2 ~ 33%), usamos HORIZON=0 (Contemporâneo)
    if HORIZON == 0:
        df['target_return'] = df['excess_ret_petr4']
    else:
        df['target_return'] = df['excess_ret_petr4'].shift(-HORIZON)
    
    # Definição dos Feature Sets
    
    # M5b (Baseline): Mercado + Fundamentos
    features_m5b = [
        'y_hat_m2_daily', 'excess_ret_ibov', 'vol_21d', 'mom_21d'
    ] + available_z_cols
    
    # M6 (Full): M5b + Macro + Fatores
    features_m6 = features_m5b + ['ret_brent', 'ret_fx', 'delta_embi', 'cma_proxy', 'rmw_proxy']
    
    # Limpeza
    df_model = df.dropna(subset=features_m6 + ['target_return']).copy()
    
    return df_model.set_index('date'), features_m5b, features_m6

def calculate_metrics(y_true, y_pred, n_params):
    """Calcula métricas de performance (MSE, RMSE, MAE, R2, AIC, BIC)."""
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    # AIC/BIC (aproximação para regressão com erros normais)
    n = len(y_true)
    k = n_params
    resid = y_true - y_pred
    sse = np.sum(resid**2)
    
    aic = n * np.log(sse/n) + 2 * k
    bic = n * np.log(sse/n) + k * np.log(n)
    
    return {
        "MSE": mse,
        "RMSE": rmse,
        "MAE": mae,
        "R2_OOS": r2,
        "AIC": aic,
        "BIC": bic
    }

def train_and_evaluate(df, features, target_col, name):
    print(f"\n--- Treinando {name} ---")
    print(f"Features ({len(features)}): {features}")
    
    # Split Train/Test
    train = df[df.index < TRAIN_TEST_SPLIT]
    test = df[df.index >= TRAIN_TEST_SPLIT]
    
    X_train = train[features]
    y_train = train[target_col]
    X_test = test[features]
    y_test = test[target_col]
    
    # Treinamento XGBoost
    model = xgb.XGBRegressor(
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
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        verbose=False
    )
    
    y_pred = model.predict(X_test)
    
    n_params = len(features)
    metrics = calculate_metrics(y_test, y_pred, n_params)
    
    print(f"R2 OOS: {metrics['R2_OOS']:.4f}")
    print(f"RMSE: {metrics['RMSE']:.4f}")
    
    return metrics

def run():
    print("🚀 Iniciando Comparação M5b vs M6 (Horizonte Contemporâneo - Explanatory)...")
    
    df, features_m5b, features_m6 = load_data_m6()
    target_col = 'target_return'
    
    metrics_m5b = train_and_evaluate(df, features_m5b, target_col, "M5b (Fundamentos)")
    metrics_m6 = train_and_evaluate(df, features_m6, target_col, "M6 (Integração Total)")
    
    # Comparação
    delta_r2 = metrics_m6['R2_OOS'] - metrics_m5b['R2_OOS']
    delta_rmse = metrics_m6['RMSE'] - metrics_m5b['RMSE']
    
    print("\n" + "="*40)
    print("RESULTADO DA COMPARAÇÃO (M6 vs M5b)")
    print("="*40)
    print(f"Delta R2: {delta_r2:.4f} ({'MELHOROU' if delta_r2 > 0 else 'PIOROU'})")
    print(f"Delta RMSE: {delta_rmse:.4f} ({'MELHOROU' if delta_rmse < 0 else 'PIOROU'})")
    
    results = {
        "M5b": metrics_m5b,
        "M6": metrics_m6,
        "Comparison": {
            "Delta_R2": delta_r2,
            "Delta_RMSE": delta_rmse
        }
    }
    
    # Salvar Métricas
    output_dir = PROJECT_ROOT / "data" / "outputs"
    output_path = output_dir / "m6_comparison.json"
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"Resultados salvos em {output_path}")

if __name__ == "__main__":
    run()
