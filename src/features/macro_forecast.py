"""
Módulo de Engenharia de Features Macro (Nowcasting) - Fase 1 do Roadmap M6.

Este módulo implementa modelos de séries temporais (ARIMA-GARCH) para prever
o retorno e a volatilidade de variáveis macroeconômicas chave (Brent e Câmbio).
O objetivo é gerar previsões "Out-of-Sample" que seriam conhecidas em t-1 para t,
evitando o viés de contemporaneidade (Look-Ahead Bias).

Metodologia:
- Rolling Window Forecast (Janela Móvel)
- Modelo: AR(1)-GARCH(1,1)
- Target: Retornos Logarítmicos (Brent, FX)
"""

import pandas as pd
import numpy as np
from arch import arch_model
import warnings
from tqdm import tqdm
from pathlib import Path
import sys

# Adicionar raiz do projeto ao path para imports
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.core.config import PROJECT_ROOT

# Suprimir warnings de convergência para manter o log limpo
warnings.filterwarnings("ignore")

def load_macro_data():
    """
    Carrega os dados macroeconômicos processados.
    Espera encontrar 'ret_brent' e 'ret_fx' no arquivo.
    """
    path = PROJECT_ROOT / "data" / "processed" / "macro_returns.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}. Execute 'make data' primeiro.")
    
    df = pd.read_parquet(path)
    
    # Garantir índice datetime
    if 'date' in df.columns:
        df = df.set_index('date')
    
    return df

def fit_predict_rolling(series, window_size=1000, refit_every=5):
    """
    Realiza previsão Rolling Window usando AR(1)-GARCH(1,1).
    
    Args:
        series (pd.Series): Série temporal de retornos.
        window_size (int): Tamanho da janela de treinamento (ex: 1000 dias ~ 4 anos).
        refit_every (int): Reestimar parâmetros a cada N dias (otimização de performance).
        
    Returns:
        pd.DataFrame: DataFrame com previsões de retorno (mean) e volatilidade (vol).
    """
    n = len(series)
    preds_mean = []
    preds_vol = []
    dates = []
    
    print(f"Iniciando Rolling Forecast para {series.name} (n={n}, window={window_size})...")
    
    # Escala para facilitar convergência do GARCH (retornos são muito pequenos)
    scale = 100.0
    series_scaled = series * scale
    
    # Armazenar último modelo ajustado
    last_res = None
    
    # Loop de previsão Out-of-Sample
    # Começamos em 'window_size' e prevemos t+1 usando dados até t
    for i in tqdm(range(window_size, n)):
        # Janela de treino: [i-window : i]
        # Ex: se i=1000, usamos 0 a 999 para prever 1000
        train_data = series_scaled.iloc[i-window_size:i]
        target_date = series.index[i]
        
        should_refit = (i - window_size) % refit_every == 0
        
        try:
            if should_refit or last_res is None:
                # Reestimar modelo
                # AR(1) para média, GARCH(1,1) para volatilidade
                # dist='skewt' para capturar assimetria e caudas gordas (comum em finance)
                model = arch_model(train_data, mean='AR', lags=1, vol='Garch', p=1, q=1, dist='skewt')
                res = model.fit(disp='off', show_warning=False)
                last_res = res
            
            # Previsão 1 passo à frente
            # Se não re-fitamos, usamos os parâmetros do último modelo ('last_res')
            # mas precisamos passar os dados atuais para o forecast.
            # O método forecast do arch usa os dados passados no fit.
            # Para usar dados novos sem refit, teríamos que criar um novo objeto result com params fixos.
            # Pela complexidade disso no arch, vamos simplificar:
            # Se não for dia de refit, usamos a previsão "naive" do último fit? Não.
            # Vamos forçar refit a cada 5 dias. Nos dias intermediários, aceitamos o custo de refit
            # OU (melhor para rigor): Refit sempre.
            # Dado o tamanho da amostra (~2500), refit sempre pode demorar 10-20 min.
            # Vamos tentar refit sempre para garantir "State of the Art".
            
            # Decisão: Refit SEMPRE para máxima precisão científica.
            model = arch_model(train_data, mean='AR', lags=1, vol='Garch', p=1, q=1, dist='skewt')
            res = model.fit(disp='off', show_warning=False)
            
            forecast = res.forecast(horizon=1)
            
            # Extrair valores e desfazer escala
            pred_mean = forecast.mean.iloc[-1, 0] / scale
            pred_vol = np.sqrt(forecast.variance.iloc[-1, 0]) / scale
            
        except Exception as e:
            # Fallback robusto: Média Móvel e Volatilidade Histórica
            # Isso evita que o script pare por um erro de convergência pontual
            pred_mean = train_data.mean() / scale
            pred_vol = train_data.std() / scale
        
        preds_mean.append(pred_mean)
        preds_vol.append(pred_vol)
        dates.append(target_date)
        
    return pd.DataFrame({
        f'{series.name}_pred_ret': preds_mean,
        f'{series.name}_pred_vol': preds_vol
    }, index=dates)

def run_macro_forecast():
    print("--- M6 Phase 1: Macro Feature Engineering (Nowcasting) ---")
    
    # 1. Carregar Dados
    try:
        df = load_macro_data()
    except FileNotFoundError as e:
        print(e)
        return

    print(f"Dados carregados. Período: {df.index.min()} a {df.index.max()}")
    
    # 2. Definir Targets
    # ret_brent: Retorno Log do Petróleo Brent
    # ret_fx: Retorno Log do Câmbio USD/BRL
    targets = ['ret_brent', 'ret_fx']
    
    results = []
    
    for col in targets:
        if col not in df.columns:
            print(f"AVISO: Coluna {col} não encontrada.")
            continue
            
        # Remover NaNs iniciais da série específica
        series = df[col].dropna()
        
        # Executar Previsão
        # Window Size: 1000 dias (~4 anos) para ter histórico suficiente para GARCH
        # Se a série for curta, ajustamos.
        window_size = 1000
        if len(series) < window_size + 100:
            window_size = int(len(series) * 0.5)
            print(f"Ajustando window_size para {window_size} devido ao tamanho da série.")
            
        forecast_df = fit_predict_rolling(series, window_size=window_size)
        results.append(forecast_df)
        
    # 3. Consolidar e Salvar
    if results:
        final_df = pd.concat(results, axis=1)
        
        # Alinhar com o índice original (pode haver gaps se window_size cortou o início)
        # O índice do final_df já são as datas de predição (t+1)
        
        output_path = PROJECT_ROOT / "data" / "processed" / "macro_forecasts.parquet"
        final_df.to_parquet(output_path)
        
        print("\n--- Concluído ---")
        print(f"Previsões salvas em: {output_path}")
        print(f"Shape: {final_df.shape}")
        print("\nAmostra das últimas previsões:")
        print(final_df.tail())
        
        # Validação Rápida (Directional Accuracy)
        # Comparar sinal da previsão com sinal do realizado
        print("\n--- Validação Rápida (Directional Accuracy) ---")
        for col in targets:
            pred_col = f'{col}_pred_ret'
            if pred_col in final_df.columns:
                # Join com realizado
                validation = final_df[[pred_col]].join(df[[col]], how='inner')
                
                # Accuracy: Sinal Correto
                correct_sign = np.sign(validation[pred_col]) == np.sign(validation[col])
                accuracy = correct_sign.mean()
                print(f"{col} Directional Accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    run_macro_forecast()
