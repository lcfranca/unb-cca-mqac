"""
Módulo de Cálculo de Z-Scores (Asset 2.3).

Normaliza as métricas fundamentalistas e de mercado utilizando Z-Score histórico
(janela expansível) para permitir a comparabilidade e agregação no score Q-VAL.

Input:
    - data/processed/metrics.parquet

Output:
    - data/processed/zscores.parquet
"""

import pandas as pd
import numpy as np
from pathlib import Path
from src.core.config import PROJECT_ROOT

def calculate_zscores():
    processed_dir = PROJECT_ROOT / "data" / "processed"
    input_path = processed_dir / "metrics" / "metrics.parquet"
    
    output_dir = processed_dir / "zscores"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_parquet = output_dir / "zscores.parquet"
    output_csv = output_dir / "zscores.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo {input_path} não encontrado.")

    print("Carregando métricas...")
    df = pd.read_parquet(input_path)
    df.sort_values('quarter_end', inplace=True)
    df.set_index('quarter_end', inplace=True)

    # Definição das métricas e direção
    # True = Quanto maior melhor (Z-Score normal)
    # False = Quanto menor melhor (Inverter Z-Score)
    metrics_config = {
        'earnings_yield': True,
        'ev_ebitda': False,
        'pb_ratio': False,
        'dividend_yield': True,
        'roic': True,
        'roe': True,
        'ebitda_margin': True,
        'evs': True,
        'beta': False,
        'volatility': False,
        'debt_to_equity': False,
        # 'current_ratio': True # Opcional, não listado explicitamente no schema final do roteiro mas útil
    }

    zscore_df = pd.DataFrame(index=df.index)

    print("Calculando Z-Scores (Janela Expansível)...")
    
    for metric, higher_is_better in metrics_config.items():
        if metric not in df.columns:
            print(f"Aviso: Métrica {metric} não encontrada no input. Pulando.")
            continue
            
        series = df[metric]
        
        # Janela expansível
        # Min_periods=2 para ter desvio padrão
        expanding_mean = series.expanding(min_periods=2).mean()
        expanding_std = series.expanding(min_periods=2).std()
        
        # Z-Score
        # Z = (X - Mean) / Std
        # Shiftamos mean e std para usar apenas dados PASSADOS (evitar look-ahead bias estrito)
        # Porém, a metodologia diz: "normalização histórica do próprio ativo".
        # Se usarmos expanding().mean() padrão, inclui o dado atual na média.
        # Para rigor estrito de trading, deveríamos usar shift(1).
        # O roteiro diz: "mu e sigma calculados sobre todos os períodos ANTERIORES a t".
        # Então: shift(1).
        
        hist_mean = expanding_mean.shift(1)
        hist_std = expanding_std.shift(1)
        
        z_score = (series - hist_mean) / hist_std
        
        # Inversão se necessário
        if not higher_is_better:
            z_score = -z_score
            
        zscore_df[f'z_{metric}'] = z_score

    # Limpeza
    # Os primeiros registros serão NaN devido ao shift e min_periods
    # Vamos manter os NaNs para indicar falta de histórico suficiente
    
    print(f"Gerados {len(zscore_df.columns)} Z-Scores.")
    print(f"Salvando em {output_dir}...")
    
    # Reset index para salvar quarter_end como coluna
    zscore_df.reset_index(inplace=True)
    zscore_df.to_parquet(output_parquet)
    zscore_df.to_csv(output_csv, index=False)
    print("Concluído.")

if __name__ == "__main__":
    calculate_zscores()
