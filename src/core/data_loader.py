"""
Módulo de Coleta de Dados do Projeto Q-VAL.

Este módulo é responsável por toda a coleta de dados de fontes externas:
  - Yahoo Finance (preços de ações)
  - BCB SGS (taxas de juros e indicadores macroeconômicos)

Todas as variáveis devem vir do módulo config.py.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

import pandas as pd
import numpy as np

from src.core.config import get_config, Config


# =============================================================================
# CONFIGURAÇÃO DE LOGGING
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# YAHOO FINANCE DATA LOADER
# =============================================================================

class YahooFinanceLoader:
    """
    Carregador de dados do Yahoo Finance.
    
    Utiliza a biblioteca yfinance para obter dados históricos de preços.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Inicializa o loader.
        
        Args:
            config: Configuração do projeto. Se não fornecida, usa singleton.
        """
        self.config = config or get_config()
        self._yf = None
    
    @property
    def yf(self):
        """Importa yfinance sob demanda."""
        if self._yf is None:
            try:
                import yfinance as yf
                self._yf = yf
            except ImportError:
                raise ImportError(
                    "yfinance não está instalado. "
                    "Execute: pip install yfinance"
                )
        return self._yf
    
    def fetch_prices(
        self,
        ticker: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Obtém preços históricos de um ativo.
        
        Args:
            ticker: Código do ativo (ex: "PETR4.SA").
            start: Data inicial (YYYY-MM-DD). Default: config.data_inicio.
            end: Data final (YYYY-MM-DD). Default: config.data_fim.
            interval: Intervalo dos dados ("1d", "1wk", "1mo").
            
        Returns:
            DataFrame com colunas: Date, Open, High, Low, Close, Volume, Adj Close.
        """
        analysis = self.config.analysis
        start = start or analysis.data_inicio
        end = end or analysis.data_fim
        
        logger.info(f"Buscando dados de {ticker} de {start} a {end}")
        
        stock = self.yf.Ticker(ticker)
        df = stock.history(start=start, end=end, interval=interval)
        
        if df.empty:
            logger.warning(f"Nenhum dado retornado para {ticker}")
            return pd.DataFrame()
        
        # Reset index para ter Date como coluna
        df = df.reset_index()
        df["Ticker"] = ticker
        
        logger.info(f"Obtidos {len(df)} registros para {ticker}")
        
        return df
    
    def fetch_multiple(
        self,
        tickers: List[str],
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Obtém preços de múltiplos ativos.
        
        Args:
            tickers: Lista de códigos de ativos.
            start: Data inicial.
            end: Data final.
            
        Returns:
            DataFrame concatenado com coluna 'Ticker' identificando cada ativo.
        """
        dfs = []
        for ticker in tickers:
            df = self.fetch_prices(ticker, start, end)
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        return pd.concat(dfs, ignore_index=True)
    
    def fetch_returns(
        self,
        ticker: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        period: str = "daily",
    ) -> pd.DataFrame:
        """
        Calcula retornos de um ativo.
        
        Args:
            ticker: Código do ativo.
            start: Data inicial.
            end: Data final.
            period: Tipo de retorno ("daily", "monthly").
            
        Returns:
            DataFrame com colunas: Date, Price, Return.
        """
        df = self.fetch_prices(ticker, start, end)
        
        if df.empty:
            return pd.DataFrame()
        
        # Usar Adj Close para retornos (ajustado por dividendos/splits)
        # yfinance retorna 'Close' já ajustado na versão mais recente
        price_col = "Close"
        
        if period == "monthly":
            df["YearMonth"] = df["Date"].dt.to_period("M")
            df = df.groupby("YearMonth").last().reset_index()
            df["Date"] = df["YearMonth"].dt.to_timestamp()
        
        df["Return"] = df[price_col].pct_change()
        df["LogReturn"] = np.log(df[price_col] / df[price_col].shift(1))
        
        result = df[["Date", price_col, "Return", "LogReturn"]].copy()
        result.columns = ["Date", "Price", "Return", "LogReturn"]
        result["Ticker"] = ticker
        
        return result.dropna()
    
    def fetch_analysis_data(self, save_external: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Obtém todos os dados necessários para a análise CAPM.
        
        Usa as configurações do notebook para buscar:
          - Ativo principal
          - Benchmark de mercado
          - Ativos pares
          
        Args:
            save_external: Se True, salva dados brutos em data/external/yahoo_finance/
          
        Returns:
            Dicionário com DataFrames:
              - "principal": dados do ativo em análise
              - "mercado": dados do benchmark
              - "pares": dados dos peers
              - "returns": retornos consolidados (processado)
        """
        analysis = self.config.analysis
        
        # Ativo principal
        logger.info(f"Carregando ativo principal: {analysis.ticker_principal}")
        principal = self.fetch_prices(analysis.ticker_principal)
        
        # Mercado
        logger.info(f"Carregando benchmark: {analysis.ticker_mercado}")
        mercado = self.fetch_prices(analysis.ticker_mercado)
        
        # Pares
        logger.info(f"Carregando pares: {analysis.tickers_pares}")
        pares = self.fetch_multiple(analysis.tickers_pares)
        
        # Salvar dados brutos em external/yahoo_finance/
        if save_external:
            external_dir = self.config.paths.external_yahoo
            external_dir.mkdir(parents=True, exist_ok=True)
            
            if not principal.empty:
                principal.to_csv(external_dir / "prices_principal.csv", index=False)
            if not mercado.empty:
                mercado.to_csv(external_dir / "prices_mercado.csv", index=False)
            if not pares.empty:
                pares.to_csv(external_dir / "prices_pares.csv", index=False)
            
            logger.info(f"Dados brutos salvos em {external_dir}")
        
        # Retornos para CAPM (dado processado/derivado)
        ret_principal = self.fetch_returns(analysis.ticker_principal)
        ret_mercado = self.fetch_returns(analysis.ticker_mercado)
        
        # Merge de retornos
        if not ret_principal.empty and not ret_mercado.empty:
            returns = ret_principal[["Date", "Return"]].copy()
            returns.columns = ["Date", "Return_Stock"]
            
            ret_m = ret_mercado[["Date", "Return"]].copy()
            ret_m.columns = ["Date", "Return_Market"]
            
            returns = returns.merge(ret_m, on="Date", how="inner")
        else:
            returns = pd.DataFrame()
        
        return {
            "principal": principal,
            "mercado": mercado,
            "pares": pares,
            "returns": returns,
        }
    
    def save_to_external(
        self,
        data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        filename: str,
    ) -> Path:
        """
        Salva dados brutos em data/external/yahoo_finance/.
        
        Args:
            data: DataFrame ou dicionário de DataFrames.
            filename: Nome do arquivo (sem extensão).
            
        Returns:
            Path do arquivo salvo.
        """
        output_dir = self.config.paths.external_yahoo
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(data, dict):
            paths = []
            for name, df in data.items():
                if isinstance(df, pd.DataFrame) and not df.empty:
                    path = output_dir / f"{filename}_{name}.csv"
                    df.to_csv(path, index=False)
                    logger.info(f"Salvo (external): {path}")
                    paths.append(path)
            return paths[0] if paths else None
        else:
            path = output_dir / f"{filename}.csv"
            data.to_csv(path, index=False)
            logger.info(f"Salvo (external): {path}")
            return path
    
    def save_to_processed(
        self,
        data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        filename: str,
    ) -> Path:
        """
        Salva dados em data/processed/.
        
        Args:
            data: DataFrame ou dicionário de DataFrames.
            filename: Nome do arquivo (sem extensão).
            
        Returns:
            Path do arquivo salvo.
        """
        output_dir = self.config.paths.data_processed
        
        if isinstance(data, dict):
            # Salva cada DataFrame separadamente
            paths = []
            for name, df in data.items():
                if isinstance(df, pd.DataFrame) and not df.empty:
                    path = output_dir / f"{filename}_{name}.csv"
                    df.to_csv(path, index=False)
                    logger.info(f"Salvo: {path}")
                    paths.append(path)
            return paths[0] if paths else None
        else:
            path = output_dir / f"{filename}.csv"
            data.to_csv(path, index=False)
            logger.info(f"Salvo: {path}")
            return path


# =============================================================================
# BCB DATA LOADER
# =============================================================================

class BCBLoader:
    """
    Carregador de dados do Banco Central (SGS).
    
    Códigos úteis do SGS:
      - 432: Taxa Selic (% a.a.)
      - 433: Taxa Selic acumulada no mês (%)
      - 4189: Taxa Selic Meta (% a.a.)
      - 21619: IPCA acumulado 12 meses (%)
    """
    
    # Códigos de séries comuns
    SERIES_CODES = {
        "selic_meta": 432,
        "selic_acumulada": 433,
        "selic_target": 4189,
        "ipca_12m": 21619,
        "pib_mensal": 4380,
        "cambio_venda": 1,
    }
    
    def __init__(self, config: Optional[Config] = None):
        """Inicializa o loader."""
        self.config = config or get_config()
        self._bcb = None
    
    @property
    def bcb(self):
        """Importa python-bcb sob demanda."""
        if self._bcb is None:
            try:
                from bcb import sgs
                self._bcb = sgs
            except ImportError:
                raise ImportError(
                    "python-bcb não está instalado. "
                    "Execute: pip install python-bcb"
                )
        return self._bcb
    
    def fetch_series(
        self,
        code: Union[int, str],
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Obtém série temporal do SGS.
        
        Args:
            code: Código numérico ou nome da série (ver SERIES_CODES).
            start: Data inicial.
            end: Data final.
            
        Returns:
            DataFrame com a série.
        """
        if isinstance(code, str):
            code = self.SERIES_CODES.get(code, code)
        
        analysis = self.config.analysis
        start = start or analysis.data_inicio
        end = end or analysis.data_fim
        
        logger.info(f"Buscando série SGS {code} de {start} a {end}")
        
        df = self.bcb.get(code, start=start, end=end)
        
        if isinstance(df, pd.Series):
            df = df.to_frame(name="Value")
        
        df = df.reset_index()
        df.columns = ["Date", "Value"]
        df["SeriesCode"] = code
        
        return df
    
    def fetch_selic_atual(self) -> float:
        """
        Obtém a taxa Selic meta atual.
        
        Returns:
            Taxa Selic em formato decimal (ex: 0.1175 para 11.75%).
        """
        df = self.fetch_series("selic_target")
        
        if df.empty:
            logger.warning("Não foi possível obter Selic, usando valor da config")
            return self.config.analysis.taxa_livre_risco
        
        # Último valor disponível
        selic = df["Value"].iloc[-1] / 100  # Converter de % para decimal
        logger.info(f"Selic atual: {selic:.4f} ({selic*100:.2f}%)")
        
        return selic


# =============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# =============================================================================

def load_yahoo_data() -> Dict[str, pd.DataFrame]:
    """
    Carrega todos os dados do Yahoo Finance usando configuração atual.
    
    Returns:
        Dicionário com DataFrames dos ativos.
    """
    loader = YahooFinanceLoader()
    return loader.fetch_analysis_data()


def load_stock_prices(ticker: str, **kwargs) -> pd.DataFrame:
    """
    Carrega preços de um ativo.
    
    Args:
        ticker: Código do ativo.
        **kwargs: Argumentos adicionais (start, end, interval).
        
    Returns:
        DataFrame com preços.
    """
    loader = YahooFinanceLoader()
    return loader.fetch_prices(ticker, **kwargs)


def load_returns(ticker: str, **kwargs) -> pd.DataFrame:
    """
    Carrega retornos de um ativo.
    
    Args:
        ticker: Código do ativo.
        **kwargs: Argumentos adicionais.
        
    Returns:
        DataFrame com retornos.
    """
    loader = YahooFinanceLoader()
    return loader.fetch_returns(ticker, **kwargs)


def load_selic() -> float:
    """
    Obtém taxa Selic atual.
    
    Returns:
        Taxa em formato decimal.
    """
    loader = BCBLoader()
    return loader.fetch_selic_atual()
