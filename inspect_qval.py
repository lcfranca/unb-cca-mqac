import pandas as pd
from src.core.config import PROJECT_ROOT

path = PROJECT_ROOT / "data/processed/qval/qval_timeseries.parquet"
try:
    df = pd.read_parquet(path)
    print(df.columns.tolist())
except Exception as e:
    print(e)
