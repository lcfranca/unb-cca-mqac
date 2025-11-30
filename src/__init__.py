"""
Q-VAL - Módulo de Análise Quantitativa de Valor
================================================

Este pacote implementa o framework Q-VAL para análise de comprabilidade
de ações, combinando CAPM com métricas fundamentalistas.

Arquitetura:
    - core/: Módulos centrais (config, data_loader, scoring, capm)
    - assets/: Geradores de figuras e tabelas

Uso:
    from src.core.config import get_config, AnalysisConfig
    from src.core.data_loader import YahooFinanceLoader
"""

from src.core.config import (
    Config,
    AnalysisConfig,
    ProjectPaths,
    get_config,
    get_paths,
    get_analysis,
)

__all__ = [
    "Config",
    "AnalysisConfig",
    "ProjectPaths",
    "get_config",
    "get_paths",
    "get_analysis",
]
