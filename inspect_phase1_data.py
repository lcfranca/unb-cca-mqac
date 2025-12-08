import pandas as pd
from src.core.config import PROJECT_ROOT

def inspect_files():
    base = PROJECT_ROOT / "data" / "processed"
    
    files = [
        base / "returns" / "returns.parquet",
        base / "zscores" / "zscores.parquet",
        base / "macro_returns.parquet"
    ]
    
    for f in files:
        if f.exists():
            print(f"\n=== {f.name} ===")
            try:
                df = pd.read_parquet(f)
                print("Columns:", df.columns.tolist())
                print("Head(2):\n", df.head(2))
                print("Tail(2):\n", df.tail(2))
            except Exception as e:
                print(f"Error reading {f.name}: {e}")
        else:
            print(f"\n=== {f.name} NOT FOUND ===")

if __name__ == "__main__":
    inspect_files()
