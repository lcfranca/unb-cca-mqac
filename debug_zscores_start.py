import pandas as pd
from src.core.config import PROJECT_ROOT

def inspect_zscores_validity():
    zscores_path = PROJECT_ROOT / "data" / "processed" / "zscores" / "zscores.parquet"
    df = pd.read_parquet(zscores_path).sort_values('quarter_end')
    
    print(f"Total rows: {len(df)}")
    print(f"Date Range: {df['quarter_end'].min()} to {df['quarter_end'].max()}")
    
    cols_to_check = ['z_beta', 'z_volatility', 'z_dividend_yield', 'z_earnings_yield']
    
    for col in cols_to_check:
        if col in df.columns:
            first_valid = df[col].first_valid_index()
            if first_valid is not None:
                print(f"\nColumn: {col}")
                print(f"First valid index: {first_valid}")
                print(f"First valid date: {df.loc[first_valid, 'quarter_end']}")
                print(f"Null count: {df[col].isna().sum()}")
            else:
                print(f"\nColumn: {col} is ALL NULL")

if __name__ == "__main__":
    inspect_zscores_validity()
