"""
Estimativa de Modelos Aninhados de Eficiência Informacional (M0-M5).

Este módulo implementa a estratégia de "Comparação Progressiva e Aninhada" definida no Roadmap.
Calcula métricas de performance (MSE, R2, AIC, BIC) para uma hierarquia de modelos,
partindo de benchmarks Naïve até modelos multifatoriais com scores fundamentalistas.

Hierarquia:
    M0: Benchmarks Naïve (Random Walk, Média Histórica)
    M1: CAPM Estático (Beta constante)
    M2: CAPM Dinâmico (Beta rolante - Rolling OLS)
    M3: Fundamentos (M2 + Valor, Qualidade, Risco)
    M4: Macro & Fatores (M3 + Brent, FX, EMBI, Fatores FF)
    M5: Síntese (M2 + Score Q-VAL Agregado)

Output:
    data/outputs/nested_models_results.json
"""

import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
from xgboost import XGBRegressor
from pathlib import Path
from typing import Dict, Any, List, Tuple

from src.core.config import PROJECT_ROOT

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================
TRAIN_TEST_SPLIT = "2023-01-01"
ROLLING_WINDOW = 252  # 1 ano de negociação
MIN_OBS = 126         # Mínimo para começar a prever

def load_and_prepare_data() -> pd.DataFrame:
    """
    Carrega e unifica todas as fontes de dados (Retornos, Q-VAL, Macro, Fatores).
    Realiza o alinhamento temporal (merge_asof) para evitar look-ahead bias.
    """
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # 1. Retornos Diários (Target e Mercado)
    df_ret = pd.read_parquet(processed_dir / "returns" / "returns.parquet")
    df_ret['date'] = pd.to_datetime(df_ret['date'])
    
    # 2. Macroeconomia (Diário)
    # Note: macro_returns.parquet já contém retornos diários
    df_macro = pd.read_parquet(processed_dir / "macro_returns.parquet")
    df_macro['date'] = pd.to_datetime(df_macro['date'])
    
    # Merge Retornos + Macro
    df_daily = pd.merge(
        df_ret[['date', 'excess_ret_petr4', 'excess_ret_ibov']],
        df_macro[['date', 'ret_brent', 'ret_fx', 'delta_embi']],
        on='date',
        how='inner'
    )
    
    # 3. Q-VAL (Trimestral -> Diário)
    df_qval = pd.read_parquet(processed_dir / "qval" / "qval_timeseries.parquet")
    # Lag de Disponibilidade: 3 meses após o fim do trimestre
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    df_qval = df_qval.sort_values('available_date')
    
    # 4. Fatores (Trimestral -> Diário)
    df_factors = pd.read_parquet(processed_dir / "factors" / "petr4_factors.parquet")
    df_factors['available_date'] = pd.to_datetime(df_factors['available_date'])
    df_factors = df_factors.sort_values('available_date')
    
    # Merge AsOf (Backward) para propagar o último dado disponível
    df_daily = df_daily.sort_values('date')
    
    # Merge Q-VAL
    df_full = pd.merge_asof(
        df_daily, 
        df_qval[['available_date', 'score_valor', 'score_qualidade', 'score_risco', 'qval_scaled',
                 'z_earnings_yield', 'z_ev_ebitda', 'z_pb_ratio', 'z_dividend_yield', 
                 'z_roe', 'z_debt_to_equity']], 
        left_on='date', 
        right_on='available_date', 
        direction='backward'
    )
    
    # Merge Fatores
    df_full = pd.merge_asof(
        df_full,
        df_factors[['available_date', 'cma_proxy', 'rmw_proxy']],
        left_on='date',
        right_on='available_date',
        direction='backward'
    )
    
    # Limpeza de NaNs (apenas nas colunas essenciais)
    cols_needed = [
        'excess_ret_petr4', 'excess_ret_ibov', 
        'score_valor', 'score_qualidade', 'score_risco', 'qval_scaled',
        'ret_brent', 'ret_fx', 'delta_embi',
        'cma_proxy', 'rmw_proxy',
        'z_earnings_yield', 'z_ev_ebitda', 'z_pb_ratio', 
        'z_roe', 'z_debt_to_equity'
    ]
    df_model = df_full.dropna(subset=cols_needed).copy()
    
    return df_model.set_index('date')

def calculate_metrics(y_true: np.array, y_pred: np.array, y_train_mean: float, n_params: int) -> Dict[str, float]:
    """Calcula métricas de performance (MSE, RMSE, MAE, R2 OOS, AIC, BIC)."""
    residuals = y_true - y_pred
    mse = np.mean(residuals**2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(residuals))
    
    # R2 Out-of-Sample: 1 - (MSE_model / MSE_naive_mean)
    # Onde MSE_naive_mean usa a média do TREINO como predição constante
    mse_naive = np.mean((y_true - y_train_mean)**2)
    r2_oos = 1 - (mse / mse_naive)
    
    # AIC/BIC (Aproximação para OLS com erros normais)
    n = len(y_true)
    # Log-Likelihood approx: -n/2 * (1 + log(2*pi)) - n/2 * log(mse)
    ll = -n/2 * (1 + np.log(2 * np.pi)) - n/2 * np.log(mse)
    
    aic = 2 * n_params - 2 * ll
    bic = n_params * np.log(n) - 2 * ll
    
    return {
        "MSE": mse,
        "RMSE": rmse,
        "MAE": mae,
        "R2_OOS": r2_oos,
        "AIC": aic,
        "BIC": bic
    }

def run_estimation():
    print("Iniciando estimativa de modelos aninhados...")
    
    # 1. Dados
    df = load_and_prepare_data()
    
    # Split
    train = df[df.index < TRAIN_TEST_SPLIT]
    test = df[df.index >= TRAIN_TEST_SPLIT]
    
    y_train = train['excess_ret_petr4']
    y_test = test['excess_ret_petr4']
    y_train_mean = y_train.mean()
    
    print(f"Treino: {len(train)} obs | Teste: {len(test)} obs")
    
    results = {}
    predictions = pd.DataFrame(index=test.index)
    predictions['y_true'] = y_test
    
    # =========================================================================
    # M0: Benchmarks Naïve
    # =========================================================================
    # M0-RW: Random Walk (Pred = 0)
    pred_m0_rw = np.zeros_like(y_test)
    results['M0_RW'] = calculate_metrics(y_test, pred_m0_rw, y_train_mean, 0)
    
    # M0-HM: Historical Mean (Pred = Mean(Train))
    pred_m0_hm = np.full_like(y_test, y_train_mean)
    results['M0_HM'] = calculate_metrics(y_test, pred_m0_hm, y_train_mean, 1)
    
    # =========================================================================
    # M1: CAPM Estático
    # =========================================================================
    X_train_m1 = sm.add_constant(train['excess_ret_ibov'])
    model_m1 = sm.OLS(y_train, X_train_m1).fit()
    
    X_test_m1 = sm.add_constant(test['excess_ret_ibov'], has_constant='add')
    pred_m1 = model_m1.predict(X_test_m1)
    results['M1_Static'] = calculate_metrics(y_test, pred_m1, y_train_mean, 2)
    
    # =========================================================================
    # M2: CAPM Dinâmico (Rolling)
    # =========================================================================
    # Estimação Rolling em toda a base (para ter histórico no início do teste)
    # Precisamos das betas no tempo t-1 para prever t?
    # Abordagem padrão: RollingOLS no tempo t usa janela [t-W, t].
    # O beta_t é o beta realizado naquele período.
    # Para previsão ex-ante: y_hat_t = alpha_{t-1} + beta_{t-1} * X_t
    
    full_exog = sm.add_constant(df['excess_ret_ibov'])
    rolling_model = RollingOLS(df['excess_ret_petr4'], full_exog, window=ROLLING_WINDOW)
    rolling_params = rolling_model.fit().params
    
    # Shift params para evitar look-ahead bias na previsão
    # params_t são usados para prever t+1
    lagged_params = rolling_params.shift(1)
    
    # Filtrar para período de teste
    test_params = lagged_params.loc[test.index]
    test_exog = sm.add_constant(test['excess_ret_ibov'], has_constant='add')
    
    # Predição M2: alpha_{t-1} + beta_{t-1} * Rm_t
    pred_m2 = (test_params['const'] + test_params['excess_ret_ibov'] * test['excess_ret_ibov']).fillna(0) # Fillna 0 para início se necessário
    
    # Se houver NaNs no início do teste (devido ao shift/window), tratar
    # Como o teste começa em 2023 e dados começam antes, deve estar ok.
    valid_idx = ~np.isnan(pred_m2)
    results['M2_Dynamic'] = calculate_metrics(y_test[valid_idx], pred_m2[valid_idx], y_train_mean, 2) # Params count is tricky for rolling
    
    # Salvar predição M2 para uso nos próximos modelos (Âncora)
    # Precisamos da predição M2 para TODO o dataset para treinar M3/M4/M5
    # Mas M3/M4/M5 são regressões estáticas sobre o output do M2?
    # Roadmap: "OLS: R_t = delta * R_M2_hat + ..."
    # Então precisamos gerar R_M2_hat para Treino e Teste.
    
    # Gerar R_M2_hat para todo o dataset (com shift)
    all_pred_m2 = (lagged_params['const'] + lagged_params['excess_ret_ibov'] * df['excess_ret_ibov'])
    df['y_hat_m2'] = all_pred_m2
    
    # Remover período inicial sem rolling window
    df_reg = df.dropna(subset=['y_hat_m2']).copy()
    
    # Re-split com dados válidos de M2
    train_reg = df_reg[df_reg.index < TRAIN_TEST_SPLIT]
    test_reg = df_reg[df_reg.index >= TRAIN_TEST_SPLIT]
    
    # =========================================================================
    # M3: Fundamentos (M2 + Valor, Qualidade, Risco)
    # =========================================================================
    features_m3 = ['y_hat_m2', 'score_valor', 'score_qualidade', 'score_risco']
    
    model_m3 = sm.OLS(train_reg['excess_ret_petr4'], train_reg[features_m3]).fit()
    pred_m3 = model_m3.predict(test_reg[features_m3])
    
    results['M3_Fundamentals'] = calculate_metrics(test_reg['excess_ret_petr4'], pred_m3, y_train_mean, len(features_m3))
    
    # =========================================================================
    # M4: Macro & Fatores (M3 + Macro + Fatores)
    # =========================================================================
    features_m4 = features_m3 + ['ret_brent', 'ret_fx', 'delta_embi', 'cma_proxy', 'rmw_proxy']
    
    model_m4 = sm.OLS(train_reg['excess_ret_petr4'], train_reg[features_m4]).fit()
    pred_m4 = model_m4.predict(test_reg[features_m4])
    
    results['M4_Macro'] = calculate_metrics(test_reg['excess_ret_petr4'], pred_m4, y_train_mean, len(features_m4))
    
    # =========================================================================
    # M5: Síntese (M2 + Score Q-VAL)
    # =========================================================================
    features_m5 = ['y_hat_m2', 'qval_scaled']
    
    model_m5 = sm.OLS(train_reg['excess_ret_petr4'], train_reg[features_m5]).fit()
    pred_m5 = model_m5.predict(test_reg[features_m5])
    
    results['M5_Score'] = calculate_metrics(test_reg['excess_ret_petr4'], pred_m5, y_train_mean, len(features_m5))

    # =========================================================================
    # M5-New: Granular Meta-Models (Linear & ML)
    # =========================================================================
    # Carregar predições geradas pelo train_m5_models.py (Stacked/Residual Learning)
    m5_preds_path = PROJECT_ROOT / "data" / "outputs" / "m5_predictions.parquet"
    
    if m5_preds_path.exists():
        print(f"Carregando predições M5 Granular de: {m5_preds_path}")
        df_m5_preds = pd.read_parquet(m5_preds_path)
        
        # Alinhar índices (Interseção entre test_reg e df_m5_preds)
        common_idx = test_reg.index.intersection(df_m5_preds.index)
        
        if len(common_idx) > 0:
            y_true_m5 = df_m5_preds.loc[common_idx, 'y_true']
            
            # M5-Linear (Huber)
            if 'pred_linear' in df_m5_preds.columns:
                pred_linear = df_m5_preds.loc[common_idx, 'pred_linear']
                results['M5_Linear'] = calculate_metrics(y_true_m5, pred_linear, y_train_mean, 15)
            
            # M5-ML (Stacked XGBoost)
            if 'pred_ml' in df_m5_preds.columns:
                pred_ml = df_m5_preds.loc[common_idx, 'pred_ml']
                results['M5_ML'] = calculate_metrics(y_true_m5, pred_ml, y_train_mean, 15)
        else:
            print("AVISO: Sem interseção de datas entre Test Set e M5 Predictions.")
    else:
        print("AVISO: Arquivo m5_predictions.parquet não encontrado. Execute train_m5_models.py primeiro.")
    
    # =========================================================================
    # Salvar Resultados
    # =========================================================================
    output_path = PROJECT_ROOT / "data" / "outputs" / "nested_models_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"Resultados salvos em: {output_path}")
    
    # Print resumo
    print("\nResumo R2 OOS:")
    for m, res in results.items():
        print(f"{m}: {res['R2_OOS']:.4f}")

if __name__ == "__main__":
    run_estimation()
