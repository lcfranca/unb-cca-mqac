"""
Coleta todos os módulos BRAPI disponíveis para o ticker principal e salva payload bruto e um resumo de estatísticas-chave.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from src.core.brapi_loader import BrapiLoader, AVAILABLE_MODULES
from src.core.config import get_config, Config

logger = logging.getLogger(__name__)


def flatten_default_keystats(raw: Dict[str, Any]) -> pd.DataFrame:
    stats = raw.get("defaultKeyStatistics") or raw.get("defaultKeyStatisticsHistory") or {}
    return pd.DataFrame([stats]) if isinstance(stats, dict) else pd.DataFrame()


def run() -> None:
    logging.basicConfig(level=logging.INFO)
    cfg: Config = get_config()
    loader = BrapiLoader(cfg)
    ticker = cfg.analysis.ticker_principal
    quote = loader.fetch_quote_with_modules(ticker=ticker, modules=AVAILABLE_MODULES)

    if not quote.raw_response:
        raise RuntimeError("Payload vazio da BRAPI")

    processed_dir = cfg.paths.data_processed
    raw_dir = cfg.paths.external_brapi
    processed_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_path = raw_dir / f"brapi_full_{ticker.replace('.SA','').lower()}.json"
    raw_path.write_text(json.dumps(quote.raw_response, ensure_ascii=False, indent=2))

    df_stats = flatten_default_keystats(quote.raw_response)
    if not df_stats.empty:
        df_stats.to_parquet(processed_dir / "brapi_stats.parquet", index=False)
        df_stats.to_csv(processed_dir / "brapi_stats.csv", index=False)
    logger.info("BRAPI full payload salvo em %s", raw_path)


if __name__ == "__main__":
    run()
