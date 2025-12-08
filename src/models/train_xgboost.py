import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score, classification_report
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

# Config
DATA_PATH = PROJECT_ROOT / "data/processed/ml_dataset.parquet"
MODELS_DIR = PROJECT_ROOT / "data/models"
OUTPUT_DIR = PROJECT_ROOT / "data/outputs/models"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

set_style()

def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    
    df = pd.read_parquet(DATA_PATH)
    if 'date' in df.columns:
        df = df.set_index('date')
    df = df.sort_index()
    return df

def train_model(target_type='regression', horizon=5):
    print(f"🚀 Iniciando Treinamento XGBoost ({target_type.capitalize()} - {horizon}d Horizon)...")
    
    df = load_data()
    
    # Define Target
    target_col = f'target_return_{horizon}d'
    df = df.dropna(subset=[target_col])
    
    # Define Features
    drop_cols = ['target_return_1d', 'target_return_5d', 'target_return_21d', 'ticker', 'date', 'available_date', 'days_since_release', 'price_index']
    features = [c for c in df.columns if c not in drop_cols]
    
    print(f"   Features ({len(features)}): {features}")
    
    X = df[features]
    y = df[target_col]
    
    if target_type == 'classification':
        # Convert to binary class: 1 if return > 0, else 0
        y = (y > 0).astype(int)
        print(f"   Distribuição de Classes: {y.value_counts(normalize=True).to_dict()}")
    
    # Time Series Split for Validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Model Setup
    if target_type == 'classification':
        model = xgb.XGBClassifier(
            objective='binary:logistic',
            n_jobs=-1,
            random_state=42,
            tree_method='hist' # Faster on CPU, supports GPU if configured
        )
        scoring = 'accuracy'
    else:
        model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_jobs=-1,
            random_state=42,
            tree_method='hist'
        )
        scoring = 'neg_mean_squared_error'
        
    # Hyperparameter Grid (Simplified for demo)
    param_dist = {
        'n_estimators': [100, 300, 500, 1000],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [3, 5, 7],
        'subsample': [0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0],
        'min_child_weight': [1, 3, 5]
    }
    
    print("   Otimizando Hiperparâmetros (RandomizedSearchCV)...")
    search = RandomizedSearchCV(
        model, 
        param_distributions=param_dist, 
        n_iter=20, 
        scoring=scoring, 
        cv=tscv, 
        verbose=1, 
        n_jobs=-1, 
        random_state=42
    )
    
    search.fit(X, y)
    
    best_model = search.best_estimator_
    print(f"   Melhores Parâmetros: {search.best_params_}")
    
    # Evaluate on last split (Holdout proxy)
    train_index, test_index = list(tscv.split(X))[-1]
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]
    
    # Refit best model on train split to get clean metrics
    best_model.fit(X_train, y_train)
    preds = best_model.predict(X_test)
    
    print("\n📊 Avaliação do Modelo (Último Fold):")
    if target_type == 'classification':
        acc = accuracy_score(y_test, preds)
        print(f"   Acurácia: {acc:.2%}")
        print(classification_report(y_test, preds))
    else:
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        ic = np.corrcoef(y_test, preds)[0, 1]
        print(f"   RMSE: {rmse:.4f}")
        print(f"   MAE: {mae:.4f}")
        print(f"   R²: {r2:.4f}")
        print(f"   Information Coefficient (IC): {ic:.4f}")
        
    # Train on Full Data for Final Model
    print("\n   Treinando Modelo Final (Full Dataset)...")
    best_model.fit(X, y)
    
    # Save Model
    model_path = MODELS_DIR / f"xgb_{target_type}_{horizon}d.pkl"
    joblib.dump(best_model, model_path)
    print(f"   Modelo salvo em: {model_path}")
    
    # SHAP Analysis
    print("\n   Gerando SHAP Values...")
    explainer = shap.TreeExplainer(best_model)
    shap_values = explainer.shap_values(X)
    
    # Summary Plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X, show=False)
    plt.title(f'SHAP Summary - {target_type.capitalize()} ({horizon}d)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"shap_summary_{target_type}_{horizon}d.pdf")
    print(f"   Plot SHAP salvo em: {OUTPUT_DIR / f'shap_summary_{target_type}_{horizon}d.pdf'}")
    
    return best_model

if __name__ == "__main__":
    # Run Classification as requested by Roadmap
    train_model(target_type='classification', horizon=5)
    
    # Run Regression as well for completeness
    train_model(target_type='regression', horizon=5)
