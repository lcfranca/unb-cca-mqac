"""
Módulo de Treinamento do Modelo M6 (Classificador) - Fase 3 do Roadmap.

Este módulo treina um classificador XGBoost para prever a direção do retorno
de PETR4 (Up/Down) no dia seguinte (t+1), utilizando um conjunto de features
híbrido:
1. Fundamentos Granulares (M5)
2. Nowcasting Macro (M6 Fase 1)
3. Regimes de Mercado (M6 Fase 2)

Metodologia:
- Target: Binário (1 se Retorno > 0, 0 caso contrário).
- Split: Time Series Split (Janela Expansiva).
- Métrica: Acurácia, Precision, Recall, ROC-AUC.
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, classification_report
from sklearn.model_selection import TimeSeriesSplit
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Adicionar raiz do projeto ao path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.core.config import PROJECT_ROOT
from src.core.style import set_style

def load_and_merge_data():
    """
    Carrega e unifica os datasets das fases anteriores.
    """
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # 1. Carregar Dataset Base (M5 - Fundamentos + Retornos)
    df_m5 = pd.read_parquet(processed_dir / "ml_dataset.parquet")
    if 'date' in df_m5.columns:
        df_m5 = df_m5.set_index('date')
        
    # 2. Carregar Macro Forecasts (M6 Fase 1)
    df_macro = pd.read_parquet(processed_dir / "macro_forecasts.parquet")
    # df_macro já tem index datetime
    
    # 3. Carregar Regimes (M6 Fase 2)
    df_regime = pd.read_parquet(processed_dir / "ibovespa_regimes.parquet")
    if 'date' in df_regime.columns:
        df_regime = df_regime.set_index('date')
        
    # Selecionar colunas relevantes de regime
    regime_cols = [c for c in df_regime.columns if 'prob_regime' in c or 'regime' in c]
    df_regime = df_regime[regime_cols]
    
    # Merge (Left Join no M5 para manter a base de trading)
    df = df_m5.join(df_macro, how='left')
    df = df.join(df_regime, how='left')
    
    # Remover linhas sem dados (devido a lags ou janelas de forecast)
    df = df.dropna()
    
    return df

def prepare_features_targets(df):
    """
    Prepara features (X) e target (y).
    """
    # Target: Retorno do dia seguinte > 0
    # ml_dataset já tem 'target_return_1d' que é o retorno de t+1 (verificar documentação do projeto)
    # Assumindo que target_return_1d é R_{t+1}
    
    # Criar Target Binário
    df['target_bin'] = (df['target_return_1d'] > 0).astype(int)
    
    # Definir Features
    
    # 1. Fundamentos (Z-Scores)
    feat_fundamentals = [c for c in df.columns if c.startswith('z_')]
    
    # 2. Macro Forecasts (Predicted)
    feat_macro_pred = [c for c in df.columns if '_pred_' in c]
    
    # 3. Regimes (Probabilidades)
    feat_regime = [c for c in df.columns if 'prob_regime' in c]
    
    # 4. Technicals (Momentum/Vol) - Já presentes no M5
    feat_tech = ['vol_20d', 'ret_lag1', 'ret_lag5', 'ret_lag21']
    
    features = feat_fundamentals + feat_macro_pred + feat_regime + feat_tech
    
    # Verificar se todas existem
    missing = [f for f in features if f not in df.columns]
    if missing:
        print(f"AVISO: Features faltando: {missing}")
        features = [f for f in features if f in df.columns]
        
    X = df[features]
    y = df['target_bin']
    
    return X, y, features

def train_model(X, y):
    """
    Treina o modelo XGBoost com validação TimeSeriesSplit.
    """
    print(f"Treinando M6 Classifier com {X.shape[1]} features...")
    
    # Configuração do Modelo
    # Scale pos weight para balancear classes se necessário (geralmente mercado é 50/50, mas bom verificar)
    ratio = float(np.sum(y == 0)) / np.sum(y == 1)
    
    model = xgb.XGBClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='binary:logistic',
        scale_pos_weight=ratio,
        random_state=42,
        n_jobs=-1
    )
    
    # Time Series Split para avaliação robusta
    tscv = TimeSeriesSplit(n_splits=5)
    
    metrics = []
    
    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_train, y_train), (X_test, y_test)],
            verbose=False
        )
        
        # Predições
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # Métricas
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        
        metrics.append({
            'fold': fold,
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'auc': auc
        })
        
        print(f"Fold {fold}: Acc={acc:.2%}, AUC={auc:.4f}")
        
    # Treinar no dataset completo para deploy/backtest final
    print("\nTreinando modelo final no dataset completo...")
    model.fit(X, y, verbose=False)
    
    return model, pd.DataFrame(metrics)

def save_results(model, X, y, metrics_df):
    """Salva modelo, métricas e predições."""
    output_dir = PROJECT_ROOT / "data" / "outputs" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Salvar Modelo
    joblib.dump(model, output_dir / "m6_classifier.joblib")
    
    # Salvar Métricas
    metrics_df.to_csv(output_dir / "m6_cv_metrics.csv", index=False)
    
    # Gerar Predições Finais (In-Sample + Out-of-Sample logic would be better, but for now full history)
    # Idealmente, para backtest, usaríamos cross_val_predict, mas em TimeSeries é tricky.
    # Vamos gerar as probabilidades do modelo final para análise.
    y_prob = model.predict_proba(X)[:, 1]
    y_pred = model.predict(X)
    
    df_res = X.copy()
    df_res['target_real'] = y
    df_res['pred_prob'] = y_prob
    df_res['pred_class'] = y_pred
    
    df_res.to_parquet(PROJECT_ROOT / "data" / "processed" / "m6_predictions.parquet")
    
    print(f"\nResultados salvos em {output_dir}")
    print(f"Predições salvas em data/processed/m6_predictions.parquet")
    
    # Feature Importance Plot
    plot_feature_importance(model, X.columns)

def plot_feature_importance(model, feature_names):
    set_style()
    plt.figure(figsize=(10, 8))
    
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    # Top 20 features
    top_n = min(20, len(feature_names))
    plt.title(f"Top {top_n} Feature Importances (M6 Classifier)")
    plt.barh(range(top_n), importances[indices][:top_n], align="center")
    plt.yticks(range(top_n), [feature_names[i] for i in indices][:top_n])
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    plt.savefig(PROJECT_ROOT / "data" / "outputs" / "figures" / "m6_feature_importance.pdf")
    print("Feature Importance plot salvo.")

def run_training():
    print("--- M6 Phase 3: Model Training (XGBoost Classifier) ---")
    
    # 1. Load
    df = load_and_merge_data()
    print(f"Dataset unificado: {df.shape}")
    
    # 2. Prepare
    X, y, features = prepare_features_targets(df)
    print(f"Features selecionadas: {len(features)}")
    
    # 3. Train
    model, metrics = train_model(X, y)
    
    # 4. Report
    print("\n--- Performance Média (CV) ---")
    print(metrics.mean())
    
    # 5. Save
    save_results(model, X, y, metrics)

if __name__ == "__main__":
    run_training()
