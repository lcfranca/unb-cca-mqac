"""
Assets — Geradores de Figuras e Tabelas
=======================================

Cada arquivo neste módulo gera um asset específico (figura ou tabela).
Execute individualmente com: python -m src.assets.<nome>

Fluxo de dados:
    notebooks/01_data_ingestion.ipynb → data/processed/returns.csv
    data/processed/returns.csv → análise CAPM → capm_results.json
    data/processed/*.json → figuras e tabelas
"""

from pathlib import Path

GENERATORS = [
    "gen_capm_analysis",     # Executa análise CAPM
    "gen_fig_regression",    # Figura: regressão beta
    "gen_fig_sml",           # Figura: Security Market Line
    "gen_fig_distribution",  # Figura: distribuição retornos
    "gen_fig_correlation",   # Figura: heatmap correlação
    "gen_table_statistics",  # Tabela: estatísticas descritivas
    "gen_table_results",     # Tabela: resultados CAPM
]

__all__ = GENERATORS
