import pandas as pd
from src.core.config import PROJECT_ROOT

def inspect_data():
    # 1. Check Q-VAL for Radar Chart
    qval_path = PROJECT_ROOT / "data" / "processed" / "qval" / "qval_timeseries.parquet"
    try:
        df_qval = pd.read_parquet(qval_path)
        print("=== Q-VAL TAIL ===")
        print(df_qval.tail(3).T)
        
        last_row = df_qval.iloc[-1]
        print("\n=== LAST ROW VALUES ===")
        print(f"Score Valor: {last_row.get('score_valor')}")
        print(f"Score Qualidade: {last_row.get('score_qualidade')}")
        print(f"Score Risco: {last_row.get('score_risco')}")
    except Exception as e:
        print(f"Error reading Q-VAL: {e}")

    # 2. Check Rolling R2 Columns
    r2_path = PROJECT_ROOT / "data" / "outputs" / "rolling_r2.parquet"
    try:
        df_r2 = pd.read_parquet(r2_path)
        print("\n=== ROLLING R2 COLUMNS ===")
        print(df_r2.columns.tolist())
        print("\n=== ROLLING R2 TAIL ===")
        print(df_r2.tail(3))
    except Exception as e:
        print(f"Error reading Rolling R2: {e}")

if __name__ == "__main__":
    inspect_data()
