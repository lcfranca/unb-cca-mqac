"""
Coleta CDI diário (série 4389 - Taxa DI) do BCB/SGS.

Saídas:
    - data/processed/cdi.parquet (cdi_annual, cdi_daily)
    - data/external/bcb/cdi_raw.parquet

Execute a partir da raiz do projeto:
    python -m src.data.fetch_cdi
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple, Optional

import pandas as pd
import requests

from src.core.config import get_config, Config

logger = logging.getLogger(__name__)

# Ordem de tentativa para séries CDI/DI no SGS
CDI_SERIES_ORDER = [4389, 12, 11, 4391]  # 4391 = Selic diária como último recurso


def _fetch_sgs_series(series_code: int, start: str, end: str) -> pd.DataFrame:
    """Busca série do SGS em formato JSON e converte para DataFrame."""
    config = get_config()
    base_url = config.env.bcb_sgs_base_url
    url = (
        f"{base_url}.{series_code}/dados"
        f"?formato=json&dataInicial={start}&dataFinal={end}"
    )
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)
    return df


def fetch_cdi(preferred_series: Optional[int] = None) -> Tuple[pd.DataFrame, int]:
    """Obtém CDI (ou proxy) do BCB SGS entre as datas da análise.

    Tenta séries em ordem CDI_SERIES_ORDER até obter sucesso.
    """
    config: Config = get_config()
    start = pd.to_datetime(config.analysis.data_inicio)
    end = pd.to_datetime(config.analysis.data_fim)

    series_candidates = [preferred_series] if preferred_series else []
    series_candidates.extend([code for code in CDI_SERIES_ORDER if code not in series_candidates])

    last_error: Exception | None = None
    df_raw: pd.DataFrame | None = None
    used_code: int | None = None

    for code in series_candidates:
        if code is None:
            continue
        try:
            df_raw = _fetch_sgs_series(
                code,
                start.strftime("%d/%m/%Y"),
                end.strftime("%d/%m/%Y"),
            )
            if not df_raw.empty:
                used_code = code
                logger.info("CDI carregado via SGS série %s", code)
                break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning("Falha ao buscar série %s: %s", code, exc)

    if df_raw is None or df_raw.empty or used_code is None:
        raise RuntimeError("Nenhum dado retornado pelo SGS", last_error)

    df_raw["data"] = pd.to_datetime(df_raw["data"], format="%d/%m/%Y")
    df_raw["valor"] = df_raw["valor"].str.replace(",", ".", regex=False).astype(float)

    df_raw = df_raw.rename(columns={"data": "date", "valor": "rate_percent"})
    df_raw["cdi_annual"] = df_raw["rate_percent"] / 100.0
    df_raw["cdi_daily"] = (1 + df_raw["cdi_annual"]) ** (1 / 252) - 1

    cols = ["date", "cdi_annual", "cdi_daily", "rate_percent"]
    df_raw = df_raw[cols]

    business_days = pd.date_range(start=start, end=end, freq="B")
    raw_unique = df_raw["date"].nunique()
    df_raw = df_raw.set_index("date").reindex(business_days).ffill().bfill().reset_index()
    df_raw = df_raw.rename(columns={"index": "date"})
    df_raw["missing_business_days_raw"] = len(business_days) - raw_unique
    df_raw["missing_business_days_after_ffill"] = df_raw["cdi_daily"].isna().sum()

    return df_raw.sort_values("date").reset_index(drop=True), used_code


def save_outputs(df: pd.DataFrame, processed_name: str = "cdi") -> Tuple[Path, Path]:
    """Salva dataset processado e cópia bruta na área external."""
    config = get_config()
    
    # Output directory
    output_dir = config.paths.data_processed / "cdi"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    processed_path_parquet = output_dir / f"{processed_name}.parquet"
    processed_path_csv = output_dir / f"{processed_name}.csv"
    
    df[["date", "cdi_annual", "cdi_daily"]].to_parquet(processed_path_parquet, index=False)
    df[["date", "cdi_annual", "cdi_daily"]].to_csv(processed_path_csv, index=False)

    raw_dir = config.paths.external_bcb
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path_parquet = raw_dir / f"{processed_name}_raw.parquet"
    raw_path_csv = raw_dir / f"{processed_name}_raw.csv"
    df.to_parquet(raw_path_parquet, index=False)
    df.to_csv(raw_path_csv, index=False)

    return processed_path_parquet, raw_path_parquet


def run() -> None:
    """Executa a coleta e persistência do CDI."""
    logging.basicConfig(level=logging.INFO)
    df_cdi, used_code = fetch_cdi()
    save_outputs(df_cdi)
    logger.info(
        "CDI carregado (série %s): %s linhas, %s a %s, gaps brutos: %s, gaps pós-ffill: %s",
        used_code,
        len(df_cdi),
        df_cdi["date"].min(),
        df_cdi["date"].max(),
        int(df_cdi["missing_business_days_raw"].iloc[0]),
        int(df_cdi["missing_business_days_after_ffill"].iloc[0]),
    )


if __name__ == "__main__":
    run()
