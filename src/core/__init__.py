"""
Core - Módulos Centrais do Q-VAL
================================

Módulos de infraestrutura e lógica de negócio para análise Q-VAL.

Módulos disponíveis:
    - config: Configuração centralizada (singleton)
    - brapi_loader: Coleta de dados via Brapi API (PRIMÁRIO)
    - data_loader: Coleta de dados de preços (Yahoo Finance - FALLBACK, BCB)
    - fundamentals_loader: Coleta de dados fundamentais (Yahoo Finance - FALLBACK)
    - cvm_loader: Coleta de dados da CVM (DFP, ITR)

Hierarquia de fontes de dados:
    1. Brapi API (primário) - ações de teste sem autenticação
    2. Yahoo Finance (fallback) - quando Brapi não disponível
    3. BCB SGS (complementar) - taxas e indicadores macro
    4. CVM (complementar) - demonstrações financeiras oficiais
"""

from src.core.config import (
    Config,
    AnalysisConfig,
    ProjectPaths,
    EnvConfig,
    get_config,
    get_paths,
    get_analysis,
)

from src.core.brapi_loader import (
    BrapiLoader,
    BrapiQuoteResult,
    get_brapi_loader,
    fetch_quote,
    fetch_historical,
    fetch_fundamentals,
    is_test_ticker,
    TEST_TICKERS,
    AVAILABLE_MODULES,
)

from src.core.data_loader import (
    YahooFinanceLoader,
    BCBLoader,
    load_yahoo_data,
    load_stock_prices,
    load_returns,
    load_selic,
)

from src.core.fundamentals_loader import (
    FundamentalsLoader,
    FundamentalsData,
    get_fundamentals_loader,
)

from src.core.cvm_loader import (
    CVMLoader,
    download_all_dfps,
    get_company_cvm_code,
    CVM_CODES,
)

__all__ = [
    # Config
    "Config",
    "AnalysisConfig",
    "ProjectPaths",
    "EnvConfig",
    "get_config",
    "get_paths",
    "get_analysis",
    # Brapi Loader (PRIMÁRIO) - Dados B3
    "BrapiLoader",
    "BrapiQuoteResult",
    "get_brapi_loader",
    "fetch_quote",
    "fetch_historical",
    "fetch_fundamentals",
    "is_test_ticker",
    "TEST_TICKERS",
    "AVAILABLE_MODULES",
    # Data Loader (Yahoo, BCB - FALLBACK) - Preços
    "YahooFinanceLoader",
    "BCBLoader",
    "load_yahoo_data",
    "load_stock_prices",
    "load_returns",
    "load_selic",
    # Fundamentals Loader - Dados Fundamentais
    "FundamentalsLoader",
    "FundamentalsData",
    "get_fundamentals_loader",
    # CVM Loader - Demonstrações Financeiras
    "CVMLoader",
    "download_all_dfps",
    "get_company_cvm_code",
    "CVM_CODES",
]
