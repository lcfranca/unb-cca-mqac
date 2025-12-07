"""
Coleta preços históricos diários da PETR4 via Brapi com fallback Yahoo.

- Fonte primária: Brapi `/quote/{ticker}?range=10y&interval=1d`
- Fallback: yfinance (quando habilitado via `.env`)
- Saídas:
    - data/processed/prices_petr4.parquet (ajustado e filtrado pelo período da análise)
    - data/external/{brapi|yahoo_finance}/prices_petr4_*.parquet (cópia bruta para auditoria)

Execute a partir da raiz do projeto:
    python -m src.data.fetch_prices
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple

import pandas as pd

from src.core.brapi_loader import BrapiLoader
from src.core.config import get_config, Config
from src.core.data_loader import YahooFinanceLoader

logger = logging.getLogger(__name__)


def _standardize_prices(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Normaliza colunas e tipos do DataFrame de preços."""
    if df.empty:
        return df

    working = df.copy()
    date_col = "date" if "date" in working.columns else "Date"
    working[date_col] = pd.to_datetime(working[date_col]).dt.tz_localize(None).dt.normalize()

    rename_map = {
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adjusted_close",
        "Adj_Close": "adjusted_close",
        "AdjClose": "adjusted_close",
        "Volume": "volume",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "adjustedClose": "adjusted_close",
        "volume": "volume",
    }

    working = working.rename(columns=rename_map)

    # Garante coluna adjusted_close presente
    if "adjusted_close" not in working.columns and "close" in working.columns:
        working["adjusted_close"] = working["close"]

    cols = [
        "date",
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "volume",
    ]
    available_cols = [c for c in cols if c in working.columns]
    working = working[available_cols]
    working["ticker"] = ticker.replace(".SA", "").upper()

    return working.sort_values("date").reset_index(drop=True)


def _validate_coverage(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> dict:
    """Valida cobertura temporal e identifica lacunas em dias úteis."""
    if df.empty:
        return {"row_count": 0, "missing_business_days": None}

    expected = pd.date_range(start=start, end=end, freq="B")
    missing = expected.difference(df["date"])

    return {
        "row_count": len(df),
        "first_date": df["date"].min(),
        "last_date": df["date"].max(),
        "missing_business_days": len(missing),
    }


def fetch_prices(range_: str = "10y", interval: str = "1d") -> Tuple[pd.DataFrame, str]:
    """Tenta coletar preços via Brapi, caindo para Yahoo se necessário."""
    config: Config = get_config()
    ticker = config.analysis.ticker_principal

    # Tentativa primária: Brapi
    try:
        brapi_loader = BrapiLoader(config)
        df_brapi = brapi_loader.fetch_historical_data(
            ticker=ticker,
            range=range_,
            interval=interval,
        )
        if not df_brapi.empty:
            logger.info("Preços obtidos via Brapi")
            return df_brapi, "brapi"
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falha na Brapi: %s", exc)

    # Fallback: Yahoo Finance
    if not config.env.yahoo_finance_enabled:
        raise RuntimeError("Brapi falhou e fallback Yahoo está desabilitado")

    yahoo_loader = YahooFinanceLoader(config)
    df_yahoo = yahoo_loader.fetch_prices(
        ticker=ticker,
        start=config.analysis.data_inicio,
        end=config.analysis.data_fim,
        interval=interval,
    )
    if df_yahoo.empty:
        raise RuntimeError("Nenhuma fonte retornou dados de preços")

    logger.info("Preços obtidos via Yahoo Finance")
    return df_yahoo, "yahoo_finance"


def save_outputs(df: pd.DataFrame, source: str, processed_name: str = "prices_petr4") -> Path:
    """Salva dataset processado e cópia bruta na área external."""
    config = get_config()
    
    # Output directory
    output_dir = config.paths.data_processed / "prices"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    processed_parquet = output_dir / f"{processed_name}.parquet"
    processed_csv = output_dir / f"{processed_name}.csv"
    
    df.to_parquet(processed_parquet, index=False)
    df.to_csv(processed_csv, index=False)

    raw_dir = config.paths.external_brapi if source == "brapi" else config.paths.external_yahoo
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_parquet = raw_dir / f"{processed_name}_{source}.parquet"
    raw_csv = raw_dir / f"{processed_name}_{source}.csv"
    df.to_parquet(raw_parquet, index=False)
    df.to_csv(raw_csv, index=False)

    return raw_parquet


def run() -> None:
    """Executa a coleta e persistência de preços."""
    logging.basicConfig(level=logging.INFO)
    config = get_config()
    start = pd.to_datetime(config.analysis.data_inicio)
    end = pd.to_datetime(config.analysis.data_fim)

    raw_df, source = fetch_prices()
    standardized = _standardize_prices(raw_df, config.analysis.ticker_principal)
    standardized = standardized[(standardized["date"] >= start) & (standardized["date"] <= end)]

    coverage = _validate_coverage(standardized, start, end)
    save_outputs(standardized, source)

    logger.info(
        "Cobertura: %s linhas, %s a %s, %s dias úteis faltantes",
        coverage.get("row_count"),
        coverage.get("first_date"),
        coverage.get("last_date"),
        coverage.get("missing_business_days"),
    )


if __name__ == "__main__":
    run()
