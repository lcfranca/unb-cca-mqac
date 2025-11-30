"""
Brapi Loader - Módulo de Coleta de Dados via Brapi API.

Este módulo é a FONTE PRIMÁRIA de dados para o projeto Q-VAL.
Fornece acesso aos dados do mercado financeiro brasileiro via API Brapi.

AÇÕES DE TESTE (sem autenticação):
    - PETR4 (Petrobras PN)
    - VALE3 (Vale ON)
    - ITUB4 (Itaú Unibanco PN)
    - MGLU3 (Magazine Luiza ON)

Documentação completa: docs/Brapi.md

IMPORTANTE: Este módulo é um PIPELINE - não deve conter configurações hardcoded.
Todas as variáveis devem vir do módulo config.py que é configurado via notebook.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.core.config import Config, get_config


# =============================================================================
# CONFIGURAÇÃO DE LOGGING
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTES
# =============================================================================

# Ações de teste que não requerem autenticação
TEST_TICKERS = ["PETR4", "VALE3", "ITUB4", "MGLU3"]

# Módulos disponíveis na API
AVAILABLE_MODULES = [
    "summaryProfile",
    "financialData",
    "balanceSheetHistory",
    "balanceSheetHistoryQuarterly",
    "incomeStatementHistory",
    "incomeStatementHistoryQuarterly",
    "cashflowHistory",
    "cashflowHistoryQuarterly",
    "defaultKeyStatistics",
    "defaultKeyStatisticsHistory",
    "defaultKeyStatisticsHistoryQuarterly",
    "financialDataHistory",
    "financialDataHistoryQuarterly",
    "valueAddedHistory",
    "valueAddedHistoryQuarterly",
]

# Ranges válidos para dados históricos
VALID_RANGES = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

# Intervals válidos
VALID_INTERVALS = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class BrapiQuoteResult:
    """Container para resultado de cotação da Brapi."""
    
    symbol: str
    currency: str = "BRL"
    short_name: str = ""
    long_name: str = ""
    regular_market_price: float = 0.0
    regular_market_change: float = 0.0
    regular_market_change_percent: float = 0.0
    regular_market_time: Optional[datetime] = None
    regular_market_day_high: float = 0.0
    regular_market_day_low: float = 0.0
    regular_market_volume: int = 0
    regular_market_previous_close: float = 0.0
    regular_market_open: float = 0.0
    fifty_two_week_high: float = 0.0
    fifty_two_week_low: float = 0.0
    market_cap: int = 0
    
    # Fundamentalistas básicos (quando fundamental=true)
    price_earnings: Optional[float] = None
    earnings_per_share: Optional[float] = None
    
    # Dados históricos (quando range/interval especificados)
    historical_data: Optional[pd.DataFrame] = None
    
    # Módulos adicionais
    financial_data: Optional[Dict[str, Any]] = None
    balance_sheet_history: Optional[List[Dict]] = None
    income_statement_history: Optional[List[Dict]] = None
    cashflow_history: Optional[List[Dict]] = None
    summary_profile: Optional[Dict[str, Any]] = None
    default_key_statistics: Optional[Dict[str, Any]] = None
    dividends_data: Optional[Dict[str, Any]] = None
    
    # Metadados
    raw_response: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "BrapiQuoteResult":
        """Cria instância a partir da resposta da API."""
        # Parse historical data se existir
        historical_df = None
        if "historicalDataPrice" in data and data["historicalDataPrice"]:
            historical_df = pd.DataFrame(data["historicalDataPrice"])
            if "date" in historical_df.columns:
                historical_df["date"] = pd.to_datetime(historical_df["date"], unit="s")
        
        # Parse market time
        market_time = None
        if "regularMarketTime" in data and data["regularMarketTime"]:
            try:
                market_time = datetime.fromisoformat(
                    data["regularMarketTime"].replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                pass
        
        return cls(
            symbol=data.get("symbol", ""),
            currency=data.get("currency", "BRL"),
            short_name=data.get("shortName", ""),
            long_name=data.get("longName", ""),
            regular_market_price=data.get("regularMarketPrice", 0.0),
            regular_market_change=data.get("regularMarketChange", 0.0),
            regular_market_change_percent=data.get("regularMarketChangePercent", 0.0),
            regular_market_time=market_time,
            regular_market_day_high=data.get("regularMarketDayHigh", 0.0),
            regular_market_day_low=data.get("regularMarketDayLow", 0.0),
            regular_market_volume=data.get("regularMarketVolume", 0),
            regular_market_previous_close=data.get("regularMarketPreviousClose", 0.0),
            regular_market_open=data.get("regularMarketOpen", 0.0),
            fifty_two_week_high=data.get("fiftyTwoWeekHigh", 0.0),
            fifty_two_week_low=data.get("fiftyTwoWeekLow", 0.0),
            market_cap=data.get("marketCap", 0),
            price_earnings=data.get("priceEarnings"),
            earnings_per_share=data.get("earningsPerShare"),
            historical_data=historical_df,
            financial_data=data.get("financialData"),
            balance_sheet_history=data.get("balanceSheetHistory"),
            income_statement_history=data.get("incomeStatementHistory"),
            cashflow_history=data.get("cashflowHistory"),
            summary_profile=data.get("summaryProfile"),
            default_key_statistics=data.get("defaultKeyStatistics"),
            dividends_data=data.get("dividendsData"),
            raw_response=data,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário (exclui DataFrames e raw_response)."""
        return {
            "symbol": self.symbol,
            "currency": self.currency,
            "short_name": self.short_name,
            "long_name": self.long_name,
            "regular_market_price": self.regular_market_price,
            "regular_market_change": self.regular_market_change,
            "regular_market_change_percent": self.regular_market_change_percent,
            "regular_market_day_high": self.regular_market_day_high,
            "regular_market_day_low": self.regular_market_day_low,
            "regular_market_volume": self.regular_market_volume,
            "regular_market_previous_close": self.regular_market_previous_close,
            "regular_market_open": self.regular_market_open,
            "fifty_two_week_high": self.fifty_two_week_high,
            "fifty_two_week_low": self.fifty_two_week_low,
            "market_cap": self.market_cap,
            "price_earnings": self.price_earnings,
            "earnings_per_share": self.earnings_per_share,
        }


# =============================================================================
# BRAPI LOADER
# =============================================================================

class BrapiLoader:
    """
    Carregador de dados da Brapi API.
    
    Fonte primária para dados do mercado financeiro brasileiro.
    
    Exemplo:
        loader = BrapiLoader()
        
        # Cotação simples
        quote = loader.fetch_quote("PETR4")
        
        # Com dados históricos
        quote = loader.fetch_quote("PETR4", range="1y", interval="1d")
        
        # Com módulos fundamentalistas
        quote = loader.fetch_quote_with_modules(
            "PETR4", 
            modules=["financialData", "balanceSheetHistory"]
        )
    
    Attributes:
        config: Configuração centralizada do projeto.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Inicializa o loader.
        
        Args:
            config: Configuração do projeto. Se não fornecida, usa singleton.
        """
        self.config = config or get_config()
        self.base_url = self.config.env.brapi_base_url
        self.token = self.config.env.brapi_token
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Cria sessão HTTP com retry automático."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _requires_auth(self, tickers: List[str]) -> bool:
        """
        Verifica se a requisição requer autenticação.
        
        Requisições com apenas ações de teste não requerem token.
        """
        tickers_clean = [t.replace(".SA", "").upper() for t in tickers]
        return not all(t in TEST_TICKERS for t in tickers_clean)
    
    def _build_url(
        self,
        endpoint: str,
        tickers: Optional[List[str]] = None,
        **params
    ) -> str:
        """Constrói URL com parâmetros."""
        url = f"{self.base_url}/{endpoint}"
        
        if tickers:
            tickers_str = ",".join(t.replace(".SA", "") for t in tickers)
            url = f"{url}/{tickers_str}"
        
        # Adicionar token se necessário
        if tickers and self._requires_auth(tickers) and self.token:
            params["token"] = self.token
        
        # Construir query string
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if query:
                url = f"{url}?{query}"
        
        return url
    
    def _request(
        self,
        endpoint: str,
        tickers: Optional[List[str]] = None,
        **params
    ) -> Dict[str, Any]:
        """
        Faz requisição à API.
        
        Args:
            endpoint: Endpoint da API (ex: "quote").
            tickers: Lista de tickers.
            **params: Parâmetros adicionais.
            
        Returns:
            Resposta JSON da API.
            
        Raises:
            requests.HTTPError: Se a requisição falhar.
        """
        url = self._build_url(endpoint, tickers, **params)
        
        logger.debug(f"Requisição: {url}")
        
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    # -------------------------------------------------------------------------
    # COTAÇÕES
    # -------------------------------------------------------------------------
    
    def fetch_quote(
        self,
        ticker: Optional[str] = None,
        range: Optional[str] = None,
        interval: Optional[str] = None,
        fundamental: bool = False,
        dividends: bool = False,
    ) -> BrapiQuoteResult:
        """
        Obtém cotação detalhada de um ativo.
        
        Args:
            ticker: Código do ativo (ex: "PETR4.SA"). 
                   Default: ticker_principal da config.
            range: Período histórico (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
            interval: Intervalo dos dados (1d, 1wk, 1mo).
            fundamental: Incluir dados fundamentalistas básicos (P/L, LPA).
            dividends: Incluir dados de dividendos.
            
        Returns:
            BrapiQuoteResult com dados da cotação.
        """
        ticker = ticker or self.config.analysis.ticker_principal
        ticker_clean = ticker.replace(".SA", "")
        
        logger.info(f"Buscando cotação de {ticker_clean} via Brapi")
        
        params = {}
        if range:
            params["range"] = range
        if interval:
            params["interval"] = interval
        if fundamental:
            params["fundamental"] = "true"
        if dividends:
            params["dividends"] = "true"
        
        response = self._request("quote", [ticker_clean], **params)
        
        if "results" not in response or not response["results"]:
            logger.warning(f"Nenhum resultado para {ticker_clean}")
            return BrapiQuoteResult(symbol=ticker_clean)
        
        result = BrapiQuoteResult.from_api_response(response["results"][0])
        logger.info(f"Cotação obtida: {result.symbol} @ R${result.regular_market_price:.2f}")
        
        return result
    
    def fetch_quote_with_modules(
        self,
        ticker: Optional[str] = None,
        modules: Optional[List[str]] = None,
        range: Optional[str] = None,
        interval: Optional[str] = None,
        fundamental: bool = True,
        dividends: bool = True,
    ) -> BrapiQuoteResult:
        """
        Obtém cotação com módulos de dados adicionais.
        
        Args:
            ticker: Código do ativo. Default: ticker_principal.
            modules: Lista de módulos a incluir. Default: financialData.
            range: Período histórico.
            interval: Intervalo dos dados.
            fundamental: Incluir dados fundamentalistas básicos.
            dividends: Incluir dados de dividendos.
            
        Returns:
            BrapiQuoteResult com dados completos.
            
        Módulos disponíveis:
            - summaryProfile: Perfil da empresa
            - financialData: Dados financeiros TTM
            - balanceSheetHistory: Balanço Patrimonial anual
            - balanceSheetHistoryQuarterly: Balanço Patrimonial trimestral
            - incomeStatementHistory: DRE anual
            - incomeStatementHistoryQuarterly: DRE trimestral
            - cashflowHistory: DFC anual
            - cashflowHistoryQuarterly: DFC trimestral
            - defaultKeyStatistics: Estatísticas-chave
        """
        ticker = ticker or self.config.analysis.ticker_principal
        ticker_clean = ticker.replace(".SA", "")
        modules = modules or ["financialData"]
        
        logger.info(f"Buscando {ticker_clean} com módulos: {modules}")
        
        params = {
            "modules": ",".join(modules),
        }
        if range:
            params["range"] = range
        if interval:
            params["interval"] = interval
        if fundamental:
            params["fundamental"] = "true"
        if dividends:
            params["dividends"] = "true"
        
        response = self._request("quote", [ticker_clean], **params)
        
        if "results" not in response or not response["results"]:
            logger.warning(f"Nenhum resultado para {ticker_clean}")
            return BrapiQuoteResult(symbol=ticker_clean)
        
        result = BrapiQuoteResult.from_api_response(response["results"][0])
        logger.info(f"Dados obtidos para {result.symbol}")
        
        return result
    
    def fetch_multiple(
        self,
        tickers: Optional[List[str]] = None,
        fundamental: bool = True,
    ) -> List[BrapiQuoteResult]:
        """
        Obtém cotações de múltiplos ativos.
        
        Args:
            tickers: Lista de códigos. Default: ticker_principal + pares.
            fundamental: Incluir dados fundamentalistas.
            
        Returns:
            Lista de BrapiQuoteResult.
        """
        if tickers is None:
            analysis = self.config.analysis
            tickers = [analysis.ticker_principal] + analysis.tickers_pares
        
        tickers_clean = [t.replace(".SA", "") for t in tickers]
        
        logger.info(f"Buscando cotações: {tickers_clean}")
        
        params = {}
        if fundamental:
            params["fundamental"] = "true"
        
        response = self._request("quote", tickers_clean, **params)
        
        results = []
        for data in response.get("results", []):
            results.append(BrapiQuoteResult.from_api_response(data))
        
        logger.info(f"Obtidas {len(results)} cotações")
        return results
    
    # -------------------------------------------------------------------------
    # DADOS HISTÓRICOS
    # -------------------------------------------------------------------------
    
    def fetch_historical_data(
        self,
        ticker: Optional[str] = None,
        range: str = "1y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Obtém série histórica de preços.
        
        Args:
            ticker: Código do ativo. Default: ticker_principal.
            range: Período (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
            interval: Intervalo (1d, 5d, 1wk, 1mo).
            
        Returns:
            DataFrame com colunas: date, open, high, low, close, volume, adjustedClose.
        """
        quote = self.fetch_quote(ticker, range=range, interval=interval)
        
        if quote.historical_data is None or quote.historical_data.empty:
            logger.warning(f"Nenhum dado histórico para {quote.symbol}")
            return pd.DataFrame()
        
        df = quote.historical_data.copy()
        df["ticker"] = quote.symbol
        
        logger.info(f"Obtidos {len(df)} registros históricos para {quote.symbol}")
        return df
    
    def fetch_returns(
        self,
        ticker: Optional[str] = None,
        range: str = "5y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Calcula retornos a partir dos dados históricos.
        
        Args:
            ticker: Código do ativo.
            range: Período histórico.
            interval: Intervalo dos dados.
            
        Returns:
            DataFrame com colunas: date, price, return, log_return.
        """
        df = self.fetch_historical_data(ticker, range, interval)
        
        if df.empty:
            return pd.DataFrame()
        
        # Usar adjustedClose se disponível, senão close
        price_col = "adjustedClose" if "adjustedClose" in df.columns else "close"
        
        result = pd.DataFrame({
            "date": df["date"],
            "price": df[price_col],
            "ticker": df["ticker"],
        })
        
        result["return"] = result["price"].pct_change()
        result["log_return"] = (result["price"] / result["price"].shift(1)).apply(
            lambda x: float("nan") if pd.isna(x) or x <= 0 else pd.np.log(x)
        )
        
        return result.dropna()
    
    # -------------------------------------------------------------------------
    # ANÁLISE Q-VAL
    # -------------------------------------------------------------------------
    
    def fetch_analysis_data(
        self,
        save_external: bool = True,
    ) -> Dict[str, Any]:
        """
        Obtém todos os dados necessários para análise Q-VAL.
        
        Busca:
        - Ativo principal com módulos completos
        - Benchmark de mercado (histórico)
        - Ativos pares
        
        Args:
            save_external: Se True, salva dados brutos em data/external/brapi/
            
        Returns:
            Dicionário com:
                - "principal": BrapiQuoteResult do ativo em análise
                - "mercado": DataFrame com histórico do benchmark
                - "pares": Lista de BrapiQuoteResult dos peers
                - "returns": DataFrame com retornos consolidados
        """
        analysis = self.config.analysis
        
        # 1. Ativo principal com todos os módulos
        logger.info(f"Carregando ativo principal: {analysis.ticker_principal}")
        principal = self.fetch_quote_with_modules(
            modules=[
                "financialData",
                "balanceSheetHistory",
                "incomeStatementHistory",
                "cashflowHistory",
                "summaryProfile",
                "defaultKeyStatistics",
            ],
            range="5y",
            interval="1d",
            dividends=True,
        )
        
        # 2. Benchmark de mercado
        logger.info(f"Carregando benchmark: {analysis.ticker_mercado}")
        mercado = self.fetch_historical_data(
            analysis.ticker_mercado,
            range="5y",
            interval="1d",
        )
        
        # 3. Ativos pares
        logger.info(f"Carregando pares: {analysis.tickers_pares}")
        pares = self.fetch_multiple(analysis.tickers_pares, fundamental=True)
        
        # 4. Calcular retornos para CAPM
        returns_principal = self.fetch_returns(analysis.ticker_principal, range="5y")
        returns_mercado = self.fetch_returns(analysis.ticker_mercado, range="5y")
        
        # Merge de retornos
        returns = pd.DataFrame()
        if not returns_principal.empty and not returns_mercado.empty:
            returns = returns_principal[["date", "return"]].copy()
            returns.columns = ["date", "return_stock"]
            
            ret_m = returns_mercado[["date", "return"]].copy()
            ret_m.columns = ["date", "return_market"]
            
            returns = returns.merge(ret_m, on="date", how="inner")
        
        # 5. Salvar dados brutos
        if save_external:
            self._save_analysis_external(principal, mercado, pares)
        
        return {
            "principal": principal,
            "mercado": mercado,
            "pares": pares,
            "returns": returns,
        }
    
    def _save_analysis_external(
        self,
        principal: BrapiQuoteResult,
        mercado: pd.DataFrame,
        pares: List[BrapiQuoteResult],
    ) -> None:
        """Salva dados de análise em data/external/brapi/."""
        external_dir = self.config.paths.external_brapi
        external_dir.mkdir(parents=True, exist_ok=True)
        
        # Principal (JSON completo)
        principal_path = external_dir / "quote_principal.json"
        with open(principal_path, "w", encoding="utf-8") as f:
            json.dump(principal.raw_response, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"Salvo: {principal_path}")
        
        # Histórico principal
        if principal.historical_data is not None and not principal.historical_data.empty:
            hist_path = external_dir / "historical_principal.csv"
            principal.historical_data.to_csv(hist_path, index=False)
            logger.info(f"Salvo: {hist_path}")
        
        # Mercado
        if not mercado.empty:
            mercado_path = external_dir / "historical_mercado.csv"
            mercado.to_csv(mercado_path, index=False)
            logger.info(f"Salvo: {mercado_path}")
        
        # Pares
        pares_data = [p.to_dict() for p in pares]
        pares_path = external_dir / "quotes_pares.json"
        with open(pares_path, "w", encoding="utf-8") as f:
            json.dump(pares_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Salvo: {pares_path}")
    
    # -------------------------------------------------------------------------
    # SALVAMENTO
    # -------------------------------------------------------------------------
    
    def save_to_external(
        self,
        data: Union[BrapiQuoteResult, pd.DataFrame, Dict],
        filename: str,
    ) -> Path:
        """
        Salva dados brutos em data/external/brapi/.
        
        Args:
            data: Dados a salvar (BrapiQuoteResult, DataFrame ou Dict).
            filename: Nome do arquivo (sem extensão).
            
        Returns:
            Path do arquivo salvo.
        """
        output_dir = self.config.paths.external_brapi
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(data, BrapiQuoteResult):
            path = output_dir / f"{filename}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data.raw_response, f, ensure_ascii=False, indent=2, default=str)
        elif isinstance(data, pd.DataFrame):
            path = output_dir / f"{filename}.csv"
            data.to_csv(path, index=False)
        else:
            path = output_dir / f"{filename}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Salvo (external): {path}")
        return path
    
    def save_to_processed(
        self,
        data: Union[pd.DataFrame, Dict],
        filename: str,
    ) -> Path:
        """
        Salva dados processados em data/processed/.
        
        Args:
            data: DataFrame ou Dict a salvar.
            filename: Nome do arquivo (sem extensão).
            
        Returns:
            Path do arquivo salvo.
        """
        output_dir = self.config.paths.data_processed
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(data, pd.DataFrame):
            path = output_dir / f"{filename}.csv"
            data.to_csv(path, index=False)
        else:
            path = output_dir / f"{filename}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Salvo (processed): {path}")
        return path


# =============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# =============================================================================

def get_brapi_loader(config: Optional[Config] = None) -> BrapiLoader:
    """Factory function para criar BrapiLoader."""
    return BrapiLoader(config)


def fetch_quote(ticker: str = None, **kwargs) -> BrapiQuoteResult:
    """Wrapper conveniente para buscar cotação."""
    loader = BrapiLoader()
    return loader.fetch_quote(ticker, **kwargs)


def fetch_historical(ticker: str = None, **kwargs) -> pd.DataFrame:
    """Wrapper conveniente para buscar dados históricos."""
    loader = BrapiLoader()
    return loader.fetch_historical_data(ticker, **kwargs)


def fetch_fundamentals(ticker: str = None) -> BrapiQuoteResult:
    """Wrapper conveniente para buscar dados fundamentalistas."""
    loader = BrapiLoader()
    return loader.fetch_quote_with_modules(
        ticker,
        modules=["financialData", "balanceSheetHistory", "summaryProfile"],
        fundamental=True,
    )


def is_test_ticker(ticker: str) -> bool:
    """Verifica se ticker é de teste (não requer autenticação)."""
    ticker_clean = ticker.replace(".SA", "").upper()
    return ticker_clean in TEST_TICKERS
