"""
Coleta dados fundamentalistas trimestrais da PETR4 via Brapi.

Módulos usados:
- defaultKeyStatisticsHistoryQuarterly
- incomeStatementHistoryQuarterly
- balanceSheetHistoryQuarterly
- financialDataHistoryQuarterly

Saídas:
    - data/processed/fundamentals_petr4.parquet (tabela tidy por trimestre)
    - data/external/brapi/fundamentals_petr4_brapi.json (payload bruto)

Execute a partir da raiz do projeto:
    python -m src.data.fetch_fundamentals
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd

from src.core.brapi_loader import BrapiLoader
from src.core.config import get_config, Config

logger = logging.getLogger(__name__)

MODULES = [
    "defaultKeyStatisticsHistoryQuarterly",
    "incomeStatementHistoryQuarterly",
    "balanceSheetHistoryQuarterly",
    "financialDataHistoryQuarterly",
    "cashflowHistoryQuarterly",
]

TARGET_COLUMNS = [
    "quarter_end",
    "pe_ratio",
    "pb_ratio",
    "roe",
    "roa",
    "ev_ebitda",
    "dividend_yield",
    "revenue",
    "ebitda",
    "net_income",
    "total_debt",
    "equity",
    "total_assets",
    "current_assets",
    "current_liabilities",
    "inventory",
    "current_ratio",
    "quick_ratio",
    "debt_to_equity",
    "net_margin",
    "asset_turnover",
    "tax_provision",
    "pre_tax_income",
]


def _parse_date(value: object) -> Optional[pd.Timestamp]:
    """Converte campo de data em Timestamp, tratando ints em epoch."""
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return pd.to_datetime(value, unit="s")
        return pd.to_datetime(value)
    except Exception:  # noqa: BLE001
        return None


def _ingest_module(
    entries: Iterable[Dict],
    mapping: Dict[str, str],
    container: Dict[pd.Timestamp, Dict[str, float]],
) -> None:
    """Mescla métricas de um módulo em container por trimestre."""
    for entry in entries or []:
        date_field = (
            entry.get("date")
            or entry.get("endDate")
            or entry.get("period")
            or entry.get("mostRecentQuarter")
            or entry.get("updatedAt")
        )
        dt = _parse_date(date_field)
        if dt is None:
            continue
        dt = dt.tz_localize(None)
        record = container.setdefault(dt, {})
        for source_field, target_field in mapping.items():
            value = entry.get(source_field)
            if value is None:
                continue
            # Não sobrescreve valores já preenchidos
            record.setdefault(target_field, value)


def _normalize_brapi_payload(raw: Dict) -> pd.DataFrame:
    """Extrai séries trimestrais do payload bruto da Brapi."""
    quarter_data: Dict[pd.Timestamp, Dict[str, float]] = {}

    _ingest_module(
        raw.get("defaultKeyStatisticsHistoryQuarterly"),
        {
            "priceToEarnings": "pe_ratio",
            "trailingPE": "pe_ratio",
            "forwardPE": "pe_ratio",
            "priceToBook": "pb_ratio",
            "returnOnEquity": "roe",
            "enterpriseToEbitda": "ev_ebitda",
            "dividendYield": "dividend_yield",
        },
        quarter_data,
    )

    _ingest_module(
        raw.get("financialDataHistoryQuarterly"),
        {
            "totalRevenue": "revenue",
            "ebitda": "ebitda",
            "totalDebt": "total_debt",
        },
        quarter_data,
    )

    _ingest_module(
        raw.get("incomeStatementHistoryQuarterly"),
        {
            "netIncome": "net_income",
            "totalRevenue": "revenue",
            "operatingIncome": "operating_income",
            "incomeTaxExpense": "tax_provision",
            "incomeBeforeTax": "pre_tax_income",
        },
        quarter_data,
    )

    _ingest_module(
        raw.get("cashflowHistoryQuarterly"),
        {
            "netIncome": "net_income",
            "depreciation": "depreciation",
        },
        quarter_data,
    )

    _ingest_module(
        raw.get("balanceSheetHistoryQuarterly"),
        {
            "totalStockholderEquity": "equity",
            "shareholdersEquity": "equity",
            "totalDebt": "total_debt",
            "shortLongTermDebt": "debt_short",
            "longTermDebt": "debt_long",
            "totalAssets": "total_assets",
            "totalCurrentAssets": "current_assets",
            "totalCurrentLiabilities": "current_liabilities",
            "inventory": "inventory",
        },
        quarter_data,
    )

    # Post-processing: Calculate derived fields if missing
    for _date, record in quarter_data.items():
        # Calculate Total Debt if missing
        if record.get("total_debt") is None:
            d_short = record.get("debt_short")
            d_long = record.get("debt_long")
            if d_short is not None or d_long is not None:
                record["total_debt"] = (d_short or 0) + (d_long or 0)
        
        # Calculate EBITDA if missing (EBIT + Depreciation)
        if record.get("ebitda") is None:
            op_inc = record.get("operating_income")
            dep = record.get("depreciation")
            if op_inc is not None and dep is not None:
                record["ebitda"] = op_inc + dep
        
        # --- Imputation for Missing Values (Forward Fill Logic) ---
        # Note: This is a simple imputation for critical fields to ensure continuity.
        # In a production pipeline, more sophisticated imputation (e.g., interpolation) might be used.
        # Here we rely on the fact that balance sheet items (Equity, Debt, Assets) are stocks
        # and tend to be stable, while flow items (Revenue, Income) are more volatile.
        
        # For now, we leave gaps as None to be handled by the analysis pipeline (e.g. ffill there).
        # The focus here is on calculating derived metrics where components exist.

        # --- Derived Metrics Calculations ---
        
        # ROE: Net Income / Equity
        if record.get("roe") is None:
            ni = record.get("net_income")
            eq = record.get("equity")
            if ni is not None and eq is not None and eq != 0:
                record["roe"] = ni / eq

        # ROA: Net Income / Total Assets
        if record.get("roa") is None:
            ni = record.get("net_income")
            ta = record.get("total_assets")
            if ni is not None and ta is not None and ta != 0:
                record["roa"] = ni / ta

        # Current Ratio: Current Assets / Current Liabilities
        if record.get("current_ratio") is None:
            ca = record.get("current_assets")
            cl = record.get("current_liabilities")
            if ca is not None and cl is not None and cl != 0:
                record["current_ratio"] = ca / cl

        # Quick Ratio: (Current Assets - Inventory) / Current Liabilities
        if record.get("quick_ratio") is None:
            ca = record.get("current_assets")
            inv = record.get("inventory")
            cl = record.get("current_liabilities")
            if ca is not None and cl is not None and cl != 0:
                inv_val = inv if inv is not None else 0
                record["quick_ratio"] = (ca - inv_val) / cl

        # Debt to Equity: Total Debt / Equity
        if record.get("debt_to_equity") is None:
            td = record.get("total_debt")
            eq = record.get("equity")
            if td is not None and eq is not None and eq != 0:
                record["debt_to_equity"] = td / eq

        # Net Margin: Net Income / Revenue
        if record.get("net_margin") is None:
            ni = record.get("net_income")
            rev = record.get("revenue")
            if ni is not None and rev is not None and rev != 0:
                record["net_margin"] = ni / rev

        # Asset Turnover: Revenue / Total Assets
        if record.get("asset_turnover") is None:
            rev = record.get("revenue")
            ta = record.get("total_assets")
            if rev is not None and ta is not None and ta != 0:
                record["asset_turnover"] = rev / ta

    if not quarter_data:
        return pd.DataFrame(columns=TARGET_COLUMNS)

    df = pd.DataFrame.from_dict(quarter_data, orient="index").reset_index()
    df = df.rename(columns={"index": "quarter_end"})
    df["quarter_end"] = pd.to_datetime(df["quarter_end"]).dt.tz_localize(None)

    for col in TARGET_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df = df[TARGET_COLUMNS].sort_values("quarter_end").reset_index(drop=True)
    return df


def save_outputs(df: pd.DataFrame, raw_payload: Dict, processed_name: str = "fundamentals_petr4") -> Path:
    """Salva dataset processado e payload bruto."""
    config = get_config()
    
    # Output directory
    output_dir = config.paths.data_processed / "fundamentals"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    processed_path_parquet = output_dir / f"{processed_name}.parquet"
    processed_path_csv = output_dir / f"{processed_name}.csv"
    
    df.to_parquet(processed_path_parquet, index=False)
    df.to_csv(processed_path_csv, index=False)

    raw_dir = config.paths.external_brapi
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{processed_name}_brapi.json"
    raw_path.write_text(json.dumps(raw_payload, ensure_ascii=False, indent=2))

    return processed_path_parquet


def fetch_fundamentals() -> pd.DataFrame:
    """Coleta dados fundamentalistas trimestrais via Brapi."""
    config: Config = get_config()
    loader = BrapiLoader(config)

    quote = loader.fetch_quote_with_modules(
        ticker=config.analysis.ticker_principal,
        modules=MODULES,
    )

    if not quote.raw_response:
        raise RuntimeError("Payload vazio retornado pela Brapi")

    df = _normalize_brapi_payload(quote.raw_response)
    if df.empty:
        raise RuntimeError("Nenhum dado fundamentalista encontrado no payload")

    save_outputs(df, quote.raw_response)
    return df


def run() -> None:
    """Executa a coleta e persistência de fundamentos."""
    logging.basicConfig(level=logging.INFO)
    df = fetch_fundamentals()
    logger.info(
        "Fundamentos carregados: %s linhas, %s a %s",
        len(df),
        df["quarter_end"].min(),
        df["quarter_end"].max(),
    )


if __name__ == "__main__":
    run()
