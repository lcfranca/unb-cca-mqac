"""
Fundamentals Loader - Coleta de Dados Fundamentais via Yahoo Finance

Este módulo fornece funcionalidades para coletar e processar dados
fundamentais de ações brasileiras via Yahoo Finance API.

NOTA: Instituições financeiras no Brasil não reportam DFP à CVM.
      Bancos reportam ao BACEN via sistema IF.data.
      Portanto, usamos Yahoo Finance para dados fundamentais.

Author: Q-VAL Analysis Pipeline
Date: 2025
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from .config import Config, get_config


@dataclass
class FundamentalsData:
    """Container para dados fundamentais de uma ação."""
    
    ticker: str
    info: dict[str, Any]
    balance_sheet: pd.DataFrame
    income_stmt: pd.DataFrame
    cashflow: pd.DataFrame
    
    @property
    def nome(self) -> str:
        return self.info.get('longName', self.info.get('shortName', self.ticker))
    
    @property
    def setor(self) -> str:
        return self.info.get('sector', 'N/A')
    
    @property
    def market_cap(self) -> float:
        return self.info.get('marketCap', 0)
    
    @property
    def price(self) -> float:
        return self.info.get('currentPrice', 0)
    
    @property
    def pl_trailing(self) -> float | None:
        return self.info.get('trailingPE')
    
    @property
    def pl_forward(self) -> float | None:
        return self.info.get('forwardPE')
    
    @property
    def pvp(self) -> float | None:
        return self.info.get('priceToBook')
    
    @property
    def roe(self) -> float | None:
        return self.info.get('returnOnEquity')
    
    @property
    def roa(self) -> float | None:
        return self.info.get('returnOnAssets')
    
    @property
    def dividend_yield(self) -> float | None:
        return self.info.get('dividendYield')
    
    @property
    def eps_trailing(self) -> float | None:
        return self.info.get('trailingEps')
    
    @property
    def book_value(self) -> float | None:
        return self.info.get('bookValue')
    
    @property
    def target_price_mean(self) -> float | None:
        return self.info.get('targetMeanPrice')
    
    @property
    def recommendation(self) -> str:
        return self.info.get('recommendationKey', 'N/A')
    
    def to_dict(self) -> dict[str, Any]:
        """Converte dados para dicionário para serialização."""
        return {
            'ticker': self.ticker,
            'nome': self.nome,
            'setor': self.setor,
            'industria': self.info.get('industry'),
            'market_cap': self.market_cap,
            'enterprise_value': self.info.get('enterpriseValue'),
            'price': self.price,
            'pl_trailing': self.pl_trailing,
            'pl_forward': self.pl_forward,
            'pvp': self.pvp,
            'ev_ebitda': self.info.get('enterpriseToEbitda'),
            'dividend_yield': self.dividend_yield,
            'dividend_rate': self.info.get('dividendRate'),
            'payout_ratio': self.info.get('payoutRatio'),
            'roe': self.roe,
            'roa': self.roa,
            'margem_liquida': self.info.get('profitMargins'),
            'margem_operacional': self.info.get('operatingMargins'),
            'crescimento_lucro_5a': self.info.get('earningsQuarterlyGrowth'),
            'crescimento_receita': self.info.get('revenueGrowth'),
            'eps_trailing': self.eps_trailing,
            'eps_forward': self.info.get('forwardEps'),
            'book_value': self.book_value,
            'shares_outstanding': self.info.get('sharesOutstanding'),
            'float_shares': self.info.get('floatShares'),
            'target_price_mean': self.target_price_mean,
            'target_price_low': self.info.get('targetLowPrice'),
            'target_price_high': self.info.get('targetHighPrice'),
            'recommendation': self.recommendation,
        }


class FundamentalsLoader:
    """
    Carregador de dados fundamentais via Yahoo Finance.
    
    Coleta dados de:
    - Informações gerais (nome, setor, market cap)
    - Métricas de valor (P/L, P/VP, EV/EBITDA)
    - Rentabilidade (ROE, ROA, margens)
    - Dividendos (yield, payout ratio)
    - Demonstrativos financeiros (balanço, DRE, DFC)
    
    Attributes:
        config: Configuração centralizada do projeto
    """
    
    def __init__(self, config: Config | None = None):
        """
        Inicializa o loader de dados fundamentais.
        
        Args:
            config: Configuração do projeto. Se None, usa singleton.
        """
        self.config = config or get_config()
        
    def fetch_fundamentals(self, ticker: str) -> FundamentalsData:
        """
        Obtém dados fundamentais completos de uma ação.
        
        Args:
            ticker: Código do ticker (ex: "PETR4.SA")
            
        Returns:
            FundamentalsData com todos os dados fundamentais
        """
        yf_ticker = yf.Ticker(ticker)
        
        return FundamentalsData(
            ticker=ticker,
            info=yf_ticker.info,
            balance_sheet=yf_ticker.quarterly_balance_sheet,
            income_stmt=yf_ticker.quarterly_income_stmt,
            cashflow=yf_ticker.quarterly_cashflow,
        )
    
    def fetch_multiple(self, tickers: list[str]) -> dict[str, FundamentalsData]:
        """
        Obtém dados fundamentais de múltiplos tickers.
        
        Args:
            tickers: Lista de códigos de ticker
            
        Returns:
            Dicionário mapeando ticker -> FundamentalsData
        """
        results = {}
        for ticker in tickers:
            try:
                results[ticker] = self.fetch_fundamentals(ticker)
            except Exception as e:
                print(f"Erro ao obter dados de {ticker}: {e}")
        return results
    
    def fetch_peer_comparison(
        self,
        principal: str,
        peers: list[str]
    ) -> pd.DataFrame:
        """
        Cria tabela comparativa entre ação principal e pares.
        
        Args:
            principal: Ticker da ação principal
            peers: Lista de tickers dos pares
            
        Returns:
            DataFrame com comparação de métricas
        """
        all_tickers = [principal] + peers
        all_data = self.fetch_multiple(all_tickers)
        
        comparison_data = []
        for ticker, data in all_data.items():
            comparison_data.append({
                'ticker': ticker,
                'nome': data.nome,
                'market_cap_bi': data.market_cap / 1e9,
                'price': data.price,
                'pl': data.pl_trailing,
                'pvp': data.pvp,
                'roe': (data.roe or 0) * 100,
                'dividend_yield': (data.dividend_yield or 0) * 100,
                'eps': data.eps_trailing,
                'book_value': data.book_value,
                'recommendation': data.recommendation,
            })
        
        df = pd.DataFrame(comparison_data)
        return df.set_index('ticker')
    
    def save_to_external(
        self,
        data: FundamentalsData,
        prefix: str = ""
    ) -> dict[str, Path]:
        """
        Salva demonstrativos financeiros em data/external/yahoo_finance/.
        
        Args:
            data: Dados fundamentais a salvar
            prefix: Prefixo para nomes de arquivo (padrão: ticker)
            
        Returns:
            Dicionário com caminhos dos arquivos salvos
        """
        ticker_clean = data.ticker.replace('.SA', '').lower()
        prefix = prefix or ticker_clean
        
        output_dir = self.config.paths.external_yahoo
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        # Balanço Patrimonial
        if not data.balance_sheet.empty:
            path = output_dir / f"balance_sheet_{prefix}.csv"
            data.balance_sheet.to_csv(path)
            saved_files['balance_sheet'] = path
        
        # DRE
        if not data.income_stmt.empty:
            path = output_dir / f"income_stmt_{prefix}.csv"
            data.income_stmt.to_csv(path)
            saved_files['income_stmt'] = path
        
        # Fluxo de Caixa
        if not data.cashflow.empty:
            path = output_dir / f"cashflow_{prefix}.csv"
            data.cashflow.to_csv(path)
            saved_files['cashflow'] = path
        
        return saved_files
    
    def save_to_processed(
        self,
        data: FundamentalsData,
        filename: str | None = None
    ) -> Path:
        """
        Salva dados fundamentais consolidados em data/processed/.
        
        Args:
            data: Dados fundamentais a salvar
            filename: Nome do arquivo (padrão: fundamentals_{ticker}.csv)
            
        Returns:
            Caminho do arquivo salvo
        """
        ticker_clean = data.ticker.replace('.SA', '').lower()
        filename = filename or f"fundamentals_{ticker_clean}.csv"
        
        output_dir = self.config.paths.data_processed
        output_dir.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame([data.to_dict()])
        output_path = output_dir / filename
        df.to_csv(output_path, index=False)
        
        return output_path
    
    def save_peer_comparison(
        self,
        df_peers: pd.DataFrame,
        filename: str = "fundamentals_peers.csv"
    ) -> Path:
        """
        Salva comparação com pares em data/processed/.
        
        Args:
            df_peers: DataFrame com dados dos pares
            filename: Nome do arquivo
            
        Returns:
            Caminho do arquivo salvo
        """
        output_dir = self.config.paths.data_processed
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / filename
        df_peers.to_csv(output_path)
        
        return output_path
    
    def analyze_relative_position(
        self,
        df_peers: pd.DataFrame,
        principal_ticker: str
    ) -> dict[str, dict[str, Any]]:
        """
        Analisa posição relativa da ação principal vs pares.
        
        Args:
            df_peers: DataFrame com dados dos pares
            principal_ticker: Ticker da ação principal
            
        Returns:
            Dicionário com análise de cada métrica
        """
        metrics = {
            'P/L': 'pl',
            'P/VP': 'pvp',
            'ROE (%)': 'roe',
        }
        
        analysis = {}
        for metric_name, col in metrics.items():
            principal_val = df_peers.loc[principal_ticker, col]
            peers_mean = df_peers.drop(principal_ticker)[col].mean()
            
            if peers_mean != 0:
                diff_pct = ((principal_val - peers_mean) / peers_mean) * 100
            else:
                diff_pct = 0
            
            # Determinar status
            if diff_pct < -10:
                status = 'BARATO'
            elif diff_pct > 10:
                status = 'CARO'
            else:
                status = 'NEUTRO'
            
            analysis[metric_name] = {
                'principal': principal_val,
                'peers_mean': peers_mean,
                'diff_pct': diff_pct,
                'status': status,
            }
        
        return analysis


def get_fundamentals_loader(config: Config | None = None) -> FundamentalsLoader:
    """
    Factory function para criar FundamentalsLoader.
    
    Args:
        config: Configuração do projeto (opcional)
        
    Returns:
        Instância de FundamentalsLoader
    """
    return FundamentalsLoader(config)
