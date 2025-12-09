"""
Módulo de Modelagem de Regimes de Mercado (HMM) - Fase 2 do Roadmap M6.

Este módulo implementa um Hidden Markov Model (HMM) para identificar regimes
de volatilidade no mercado brasileiro (Ibovespa).

Objetivo:
- Classificar o mercado em estados latentes (ex: Baixa Volatilidade/Alta, Alta Volatilidade/Baixa).
- O estado "Alta Volatilidade" (Crash/Bear) deve ser evitado pelo algoritmo de trading.

Metodologia:
- Input: Retornos logarítmicos do Ibovespa.
- Modelo: GaussianHMM com 2 ou 3 componentes.
- Output: Série temporal de probabilidades de regime (P(State=k)).
"""

import pandas as pd
import numpy as np
from hmmlearn.hmm import GaussianHMM
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import joblib

# Adicionar raiz do projeto ao path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.core.config import PROJECT_ROOT
from src.core.style import set_style

def load_ibovespa_data():
    """Carrega dados históricos do Ibovespa."""
    path = PROJECT_ROOT / "data" / "processed" / "ibovespa" / "ibovespa.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    
    df = pd.read_parquet(path)
    
    # Garantir que 'date' seja datetime e index
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
    
    # Calcular retornos se não existirem
    if 'log_return' not in df.columns:
        # Assumindo que existe coluna 'Close' ou 'Adj Close'
        # Ajuste para colunas em minúsculo (padrão do projeto)
        if 'adjusted_close' in df.columns:
            price_col = 'adjusted_close'
        elif 'close' in df.columns:
            price_col = 'close'
        elif 'Adj Close' in df.columns:
            price_col = 'Adj Close'
        else:
            price_col = 'Close'
            
        df['log_return'] = np.log(df[price_col] / df[price_col].shift(1))
    
    df = df.dropna()
    return df

def fit_hmm(returns, n_components=2):
    """
    Ajusta um HMM Gaussiano aos retornos.
    
    Args:
        returns (pd.Series): Série de retornos logarítmicos.
        n_components (int): Número de estados latentes (2 ou 3).
        
    Returns:
        model: Modelo HMM treinado.
        hidden_states: Sequência de estados preditos.
    """
    # Reshape para (n_samples, 1)
    X = returns.values.reshape(-1, 1)
    
    print(f"Treinando HMM com {n_components} estados...")
    model = GaussianHMM(n_components=n_components, covariance_type="full", n_iter=100, random_state=42)
    model.fit(X)
    
    # Prever estados
    hidden_states = model.predict(X)
    
    # Diagnóstico dos Estados
    print("\n--- Diagnóstico dos Regimes Identificados ---")
    for i in range(n_components):
        mean = model.means_[i][0]
        var = np.diag(model.covars_[i])[0]
        print(f"Estado {i}: Média = {mean:.6f}, Volatilidade (std) = {np.sqrt(var):.6f}")
        
    return model, hidden_states

def reorder_states(model, hidden_states):
    """
    Reordena os estados para que o Estado 0 seja sempre o de 'Baixa Volatilidade'
    e o último estado seja o de 'Alta Volatilidade'.
    Isso facilita a interpretação downstream.
    """
    # Calcular volatilidade de cada estado
    vols = []
    for i in range(model.n_components):
        vols.append(np.sqrt(np.diag(model.covars_[i])[0]))
    
    # Criar mapa de reordenação (menor vol -> maior vol)
    sorted_indices = np.argsort(vols)
    mapping = {old_idx: new_idx for new_idx, old_idx in enumerate(sorted_indices)}
    
    # Reordenar estados preditos
    new_hidden_states = np.array([mapping[s] for s in hidden_states])
    
    # Reordenar parâmetros do modelo (opcional, mas bom para consistência se formos salvar o modelo)
    # Nota: hmmlearn não tem método fácil para reordenar internamente, 
    # então vamos confiar apenas no output remapeado para o dataset.
    
    print("\n--- Reordenação de Estados ---")
    print(f"Ordem original (por índice): {list(range(len(vols)))}")
    print(f"Volatilidades originais: {[f'{v:.6f}' for v in vols]}")
    print(f"Novo mapeamento (0=Menor Vol): {mapping}")
    
    return new_hidden_states, mapping

def plot_regimes(df, hidden_states, output_path):
    """Gera gráfico dos regimes identificados."""
    set_style()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plotar preço (log scale para visualizar melhor longo prazo)
    # Ajuste para colunas em minúsculo
    if 'adjusted_close' in df.columns:
        price_col = 'adjusted_close'
    elif 'close' in df.columns:
        price_col = 'close'
    elif 'Adj Close' in df.columns:
        price_col = 'Adj Close'
    else:
        price_col = 'Close'
    
    # Colorir fundo de acordo com o regime
    # Assumindo 2 estados: 0 (Calm), 1 (Volatile)
    # Se 3 estados: 0 (Calm), 1 (Neutral), 2 (Volatile)
    
    # Criar máscaras
    dates = df.index
    
    # Plotar preço
    ax.plot(dates, df[price_col], color='black', linewidth=1, label='Ibovespa')
    
    # Adicionar áreas coloridas para regimes de alta volatilidade
    # Estado mais alto (último índice) é o mais volátil
    high_vol_state = hidden_states.max()
    
    # Usar fill_between para marcar períodos de alta volatilidade
    # Criar uma série binária onde 1 = High Vol
    is_high_vol = (hidden_states == high_vol_state).astype(int)
    
    # Truque para preencher áreas: usar fill_between onde a condição é verdadeira
    # Precisamos transformar em limites contínuos
    ylim = ax.get_ylim()
    ax.fill_between(dates, ylim[0], ylim[1], where=is_high_vol==1, 
                    color='red', alpha=0.3, label='Regime de Alta Volatilidade')
    
    ax.set_title('Regimes de Volatilidade do Ibovespa (HMM)')
    ax.set_ylabel('Pontos (Log Scale)')
    ax.set_yscale('log')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Gráfico salvo em: {output_path}")

def run_regime_modeling():
    print("--- M6 Phase 2: Regime Modeling (HMM) ---")
    
    # 1. Carregar Dados
    try:
        df = load_ibovespa_data()
    except FileNotFoundError as e:
        print(e)
        return
        
    print(f"Dados carregados: {len(df)} observações ({df.index.min().date()} a {df.index.max().date()})")
    
    # 2. Ajustar HMM
    # Testar com 2 estados (Calm vs Crisis) - geralmente mais robusto para trading
    n_states = 2
    model, hidden_states = fit_hmm(df['log_return'], n_components=n_states)
    
    # 3. Reordenar Estados (0 = Calm, 1 = Crisis)
    hidden_states, mapping = reorder_states(model, hidden_states)
    
    # 4. Salvar Resultados
    df['regime'] = hidden_states
    
    # Calcular probabilidades posteriores (certeza do modelo sobre o estado)
    # Precisamos reordenar as probabilidades também
    X = df['log_return'].values.reshape(-1, 1)
    posteriors = model.predict_proba(X)
    
    # Reordenar colunas de probabilidade
    sorted_indices = sorted(mapping, key=mapping.get) # [idx_old_0, idx_old_1, ...]
    posteriors_sorted = posteriors[:, sorted_indices]
    
    for i in range(n_states):
        df[f'prob_regime_{i}'] = posteriors_sorted[:, i]
        
    output_file = PROJECT_ROOT / "data" / "processed" / "ibovespa_regimes.parquet"
    df.to_parquet(output_file)
    print(f"Dados de regime salvos em: {output_file}")
    
    # 5. Visualização e Validação
    fig_path = PROJECT_ROOT / "data" / "outputs" / "figures" / "hmm_regimes.pdf"
    plot_regimes(df, hidden_states, fig_path)
    
    # Validação Histórica: Verificar datas críticas
    print("\n--- Validação Histórica (Crises Conhecidas) ---")
    crises = {
        'Joesley Day': '2017-05-18',
        'Greve Caminhoneiros': '2018-05-28',
        'Covid Crash': '2020-03-12',
        'Eleições 2022 (Pós)': '2022-11-10' # Exemplo
    }
    
    for name, date_str in crises.items():
        if date_str in df.index:
            regime = df.loc[date_str, 'regime']
            prob_crisis = df.loc[date_str, f'prob_regime_{n_states-1}'] # Prob do estado mais volátil
            print(f"{name} ({date_str}): Regime {regime} (Prob High Vol: {prob_crisis:.2%})")
        else:
            print(f"{name} ({date_str}): Data não encontrada no dataset.")

if __name__ == "__main__":
    run_regime_modeling()
