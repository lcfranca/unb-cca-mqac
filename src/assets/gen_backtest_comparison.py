"""
Gera tabela consolidada de performance de investimento (Backtesting) para todos os modelos (M0-M6).
Implementa o protocolo de teste definido em ESTRATEGIA_EVOLUCAO_MODELAGEM.md.

Protocolo:
1. Previsão E[R_t+21] (ou proxy diária acumulada).
2. Sinal: Compra se E[R] > CDI, else Neutro.
3. Métricas: Retorno Total, Volatilidade, Sharpe, Max Drawdown.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
import xgboost as xgb
from pathlib import Path
import json
from src.core.config import PROJECT_ROOT

# Configurações
TRAIN_TEST_SPLIT = "2023-01-01"
ROLLING_WINDOW = 252
COST_BPS = 0.0010  # 0.10% por trade

def load_data_backtest():
    """Carrega dados unificados para backtest."""
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # 1. Retornos e CDI
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
    
    # 3. Q-VAL e Fatores (para M3-M6)
    df_qval = pd.read_parquet(processed_dir / "qval" / "qval_timeseries.parquet")
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    df_qval = df_qval.sort_values('available_date')
    
    df_factors = pd.read_parquet(processed_dir / "factors" / "petr4_factors.parquet")
    df_factors['available_date'] = pd.to_datetime(df_factors['available_date'])
    df_factors = df_factors.sort_values('available_date')
    
    df = df.sort_values('date')
    
    # Z-Scores
    z_cols = ['z_earnings_yield', 'z_ev_ebitda', 'z_pb_ratio', 'z_roe', 'z_debt_to_equity', 'z_evs']
    available_z_cols = [c for c in z_cols if c in df_qval.columns]
    
    df = pd.merge_asof(df, df_qval[['available_date'] + available_z_cols], left_on='date', right_on='available_date', direction='backward')
    df = pd.merge_asof(df, df_factors[['available_date', 'cma_proxy', 'rmw_proxy']], left_on='date', right_on='available_date', direction='backward')
    
    # Fillna com 0 para Z-Scores antes do início da disponibilidade (ou drop)
    df = df.dropna().copy()
    
    return df.set_index('date'), available_z_cols

def generate_horizon_predictions_all_models(df, z_cols):
    """
    Gera predições de Horizonte 21 dias para M0-M4.
    Target: Retorno Acumulado em 21 dias (Forward).
    """
    print("Treinando modelos de Horizonte 21d (M0-M4)...")
    
    # Preparar Target
    indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=21)
    df['target_return_21d'] = df['ret_petr4'].rolling(window=indexer).apply(lambda x: np.prod(1 + x) - 1)
    
    # Split
    train = df[df.index < TRAIN_TEST_SPLIT]
    test = df[df.index >= TRAIN_TEST_SPLIT]
    
    preds = pd.DataFrame(index=test.index)
    preds['ret_petr4'] = test['ret_petr4']
    preds['cdi_daily'] = test['cdi_daily']
    
    # --- M0: Média Histórica (Rolling 252d de retornos 21d) ---
    # Shift(21) para garantir que usamos apenas dados conhecidos?
    # Se estamos em T, queremos prever T->T+21.
    # Podemos usar a média dos retornos de 21d passados.
    # Retorno 21d passado: R_{t-21, t}.
    df['past_ret_21d'] = df['ret_petr4'].rolling(21).apply(lambda x: np.prod(1 + x) - 1)
    preds['pred_m0_horizon'] = df['past_ret_21d'].rolling(252).mean().shift(1).loc[test.index]
    
    # --- M1: CAPM Estático (Predictive) ---
    # E[R] = Rf + Beta * ERP.
    # Rf = CDI_21d (conhecido em t? CDI futuro não. CDI hoje extrapolado).
    # ERP = Média Histórica do Excesso de Mercado (21d).
    
    # Beta
    X_train = sm.add_constant(train['excess_ret_ibov'])
    y_train = train['excess_ret_petr4']
    beta_m1 = sm.OLS(y_train, X_train).fit().params['excess_ret_ibov']
    
    # ERP Proxy (Média móvel 252d do excesso de mercado 21d)
    df['excess_market_21d'] = df['excess_ret_ibov'].rolling(21).sum() # Aprox log-retorno ou soma simples
    erp_proxy = df['excess_market_21d'].rolling(252).mean().shift(1)
    
    cdi_21d_proxy = (1 + test['cdi_daily'])**21 - 1
    preds['pred_m1_horizon'] = cdi_21d_proxy + beta_m1 * erp_proxy.loc[test.index]
    
    # --- M2: CAPM Dinâmico ---
    # Beta Dinâmico * ERP Proxy
    full_exog = sm.add_constant(df['excess_ret_ibov'])
    rolling_model = RollingOLS(df['excess_ret_petr4'], full_exog, window=ROLLING_WINDOW)
    rolling_params = rolling_model.fit().params.shift(1)
    
    beta_dynamic = rolling_params['excess_ret_ibov'].loc[test.index]
    preds['pred_m2_horizon'] = cdi_21d_proxy + beta_dynamic * erp_proxy.loc[test.index]
    
    # --- M3: Fundamentos (OLS Horizon) ---
    # Regressão: Target_21d ~ Z-Scores
    # Features disponíveis em T
    features_m3 = z_cols
    
    # Drop NaNs para treino
    train_m3 = train.dropna(subset=features_m3 + ['target_return_21d'])
    model_m3 = sm.OLS(train_m3['target_return_21d'], sm.add_constant(train_m3[features_m3])).fit()
    
    preds['pred_m3_horizon'] = model_m3.predict(sm.add_constant(test[features_m3]))
    
    # --- M4: Macro (OLS Horizon) ---
    features_m4 = features_m3 + ['ret_brent', 'ret_fx', 'delta_embi']
    train_m4 = train.dropna(subset=features_m4 + ['target_return_21d'])
    model_m4 = sm.OLS(train_m4['target_return_21d'], sm.add_constant(train_m4[features_m4])).fit()
    
    preds['pred_m4_horizon'] = model_m4.predict(sm.add_constant(test[features_m4]))
    
    return preds

def run_fair_value_backtest(df_preds, model_col, horizon=21, entry_threshold=0.02, exit_threshold=0.0):
    """
    Executa a estratégia de Valor Justo (Fair Value) com State Machine.
    Lógica:
        Upside = (1 + Pred_21d) / (1 + CDI_21d) - 1
        Se Upside > Entry: Compra
        Se Upside < Exit: Venda
    """
    # Proxy CDI Futuro (Extrapolação do CDI diário atual)
    cdi_21d = (1 + df_preds['cdi_daily']) ** horizon - 1
    upside = (1 + df_preds[model_col]) / (1 + cdi_21d) - 1
    
    positions = np.zeros(len(df_preds))
    current_pos = 0
    
    upside_vals = upside.values
    
    for i in range(len(upside_vals)):
        u = upside_vals[i]
        if current_pos == 0:
            if u > entry_threshold:
                current_pos = 1
        elif current_pos == 1:
            if u < exit_threshold:
                current_pos = 0
        positions[i] = current_pos
        
    # Lagged Signal (Operamos no dia seguinte ao sinal)
    signal = pd.Series(positions, index=df_preds.index).shift(1).fillna(0)
    
    # Retornos
    strat_ret = signal * df_preds['ret_petr4'] + (1 - signal) * df_preds['cdi_daily']
    trades = signal.diff().abs().fillna(0)
    strat_ret_net = strat_ret - (trades * COST_BPS)
    
    return strat_ret_net, trades.sum()

def run():
    print("🚀 Iniciando Backtest Unificado (M0-M5) - Estratégia Fair Value...")
    df, z_cols = load_data_backtest()
    
    # 1. Gerar Predições Horizon para M0-M4
    preds_horizon = generate_horizon_predictions_all_models(df, z_cols)
    
    # 2. Carregar Predições M5b (Já existentes)
    path_m5_h = PROJECT_ROOT / "data" / "outputs" / "m5_horizon_predictions.parquet"
    if path_m5_h.exists():
        df_m5 = pd.read_parquet(path_m5_h)
        preds_horizon['pred_m5b_horizon'] = df_m5['pred_xgb_21d']
        if 'pred_huber_21d' in df_m5.columns:
            preds_horizon['pred_m5a_horizon'] = df_m5['pred_huber_21d']
    
    # 3. Executar Backtest Fair Value para todos
    fv_results = []
    equity_curves = pd.DataFrame(index=preds_horizon.index)
    
    # Benchmark Buy & Hold
    bh_cum = (1 + preds_horizon['ret_petr4']).cumprod()
    equity_curves['Buy & Hold'] = bh_cum
    bh_dd = (bh_cum / bh_cum.cummax()) - 1
    fv_results.append({
        'Model': 'Buy & Hold',
        'Total Return': bh_cum.iloc[-1] - 1,
        'Annualized Vol': preds_horizon['ret_petr4'].std() * np.sqrt(252),
        'Sharpe': (preds_horizon['ret_petr4'].mean() * 252) / (preds_horizon['ret_petr4'].std() * np.sqrt(252)),
        'Max Drawdown': bh_dd.min(),
        'Trades': 1
    })
    
    # Benchmark CDI
    cdi_cum = (1 + preds_horizon['cdi_daily']).cumprod()
    equity_curves['CDI'] = cdi_cum
    fv_results.append({
        'Model': 'CDI',
        'Total Return': cdi_cum.iloc[-1] - 1,
        'Annualized Vol': preds_horizon['cdi_daily'].std() * np.sqrt(252),
        'Sharpe': 0.0, # Risk Free
        'Max Drawdown': 0.0,
        'Trades': 0
    })
    
    models_map = {
        'M0_Mean': 'pred_m0_horizon',
        'M1_Static': 'pred_m1_horizon',
        'M2_Dynamic': 'pred_m2_horizon',
        'M3_Fund': 'pred_m3_horizon',
        'M4_Macro': 'pred_m4_horizon',
        'M5a_Huber': 'pred_m5a_horizon',
        'M5b_ML': 'pred_m5b_horizon'
    }
    
    for model_name, col in models_map.items():
        if col not in preds_horizon.columns:
            print(f"Aviso: Coluna {col} não encontrada.")
            continue
            
        # Filtrar NaNs (M0/M1 podem ter NaNs no início do OOS se rolling window não estiver cheia)
        df_model = preds_horizon.dropna(subset=[col]).copy()
        
        ret, trades = run_fair_value_backtest(df_model, col)
        
        cum_ret = (1 + ret).cumprod()
        
        # Alinhar com o índice original para salvar na tabela de curvas
        equity_curves[model_name] = cum_ret
        
        dd = (cum_ret / cum_ret.cummax()) - 1
        ann_vol = ret.std() * np.sqrt(252)
        sharpe = (ret.mean() * 252) / ann_vol if ann_vol > 0 else 0
        
        fv_results.append({
            'Model': model_name,
            'Total Return': cum_ret.iloc[-1] - 1,
            'Annualized Vol': ann_vol,
            'Sharpe': sharpe,
            'Max Drawdown': dd.min(),
            'Trades': trades
        })
        
    # Consolidar
    df_results = pd.DataFrame(fv_results)
    
    print("\n" + "="*60)
    print("RESULTADOS DO BACKTEST - ESTRATÉGIA FAIR VALUE (2023-2024)")
    print("="*60)
    print(df_results.round(4).to_string(index=False))
    
    output_path = PROJECT_ROOT / "data" / "outputs" / "tables" / "backtest_fair_value_all.csv"
    df_results.to_csv(output_path, index=False)
    print(f"\nTabela salva em {output_path}")
    
    # Salvar Curvas de Capital
    curves_path = PROJECT_ROOT / "data" / "outputs" / "backtest_equity_curves.parquet"
    equity_curves.to_parquet(curves_path)
if __name__ == "__main__":
    run()