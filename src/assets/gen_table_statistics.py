"""
Tabela: Estatísticas Descritivas
================================

Gera tabela LaTeX com estatísticas descritivas dos retornos.
Salva em data/outputs/tables/estatisticas_descritivas.tex
"""

import json
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

def main():
    base_path = Path(__file__).resolve().parents[2]
    
    returns_path = base_path / "data" / "processed" / "returns.csv"
    stats_path = base_path / "data" / "processed" / "statistics.json"
    output_path = base_path / "data" / "outputs" / "tables" / "estatisticas_descritivas.tex"
    
    df = pd.read_csv(returns_path, parse_dates=["date"])
    df = df.dropna(subset=["r_petr4", "r_ibov"])
    
    def calc_stats(series, name):
        return {
            "name": name,
            "n": len(series),
            "mean": series.mean(),
            "std": series.std(),
            "min": series.min(),
            "q25": series.quantile(0.25),
            "median": series.median(),
            "q75": series.quantile(0.75),
            "max": series.max(),
            "skewness": stats.skew(series),
            "kurtosis": stats.kurtosis(series),
            "mean_annual": (1 + series.mean()) ** 252 - 1,
            "std_annual": series.std() * np.sqrt(252)
        }
    
    petr4_stats = calc_stats(df["r_petr4"], "PETR4")
    ibov_stats = calc_stats(df["r_ibov"], "IBOVESPA")
    
    statistics = {
        "period_start": df["date"].min().strftime("%Y-%m-%d"),
        "period_end": df["date"].max().strftime("%Y-%m-%d"),
        "n_observations": len(df),
        "petr4": petr4_stats,
        "ibov": ibov_stats,
        "correlation": df["r_petr4"].corr(df["r_ibov"])
    }
    
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(statistics, f, indent=2, ensure_ascii=False)
    
    latex = r"""\begin{table}[H]
\centering
\caption{Estatísticas Descritivas dos Retornos Diários}
\label{tab:estatisticas_descritivas}
\begin{tabular}{lrr}
\toprule
\textbf{Estatística} & \textbf{PETR4} & \textbf{IBOVESPA} \\
\midrule
Observações & """ + f"{petr4_stats['n']:,}".replace(",", ".") + r""" & """ + f"{ibov_stats['n']:,}".replace(",", ".") + r""" \\
Média diária (\%) & """ + f"{petr4_stats['mean']*100:.4f}" + r""" & """ + f"{ibov_stats['mean']*100:.4f}" + r""" \\
Desvio-padrão diário (\%) & """ + f"{petr4_stats['std']*100:.4f}" + r""" & """ + f"{ibov_stats['std']*100:.4f}" + r""" \\
Mínimo (\%) & """ + f"{petr4_stats['min']*100:.2f}" + r""" & """ + f"{ibov_stats['min']*100:.2f}" + r""" \\
1º Quartil (\%) & """ + f"{petr4_stats['q25']*100:.4f}" + r""" & """ + f"{ibov_stats['q25']*100:.4f}" + r""" \\
Mediana (\%) & """ + f"{petr4_stats['median']*100:.4f}" + r""" & """ + f"{ibov_stats['median']*100:.4f}" + r""" \\
3º Quartil (\%) & """ + f"{petr4_stats['q75']*100:.4f}" + r""" & """ + f"{ibov_stats['q75']*100:.4f}" + r""" \\
Máximo (\%) & """ + f"{petr4_stats['max']*100:.2f}" + r""" & """ + f"{ibov_stats['max']*100:.2f}" + r""" \\
Assimetria & """ + f"{petr4_stats['skewness']:.4f}" + r""" & """ + f"{ibov_stats['skewness']:.4f}" + r""" \\
Curtose (excesso) & """ + f"{petr4_stats['kurtosis']:.4f}" + r""" & """ + f"{ibov_stats['kurtosis']:.4f}" + r""" \\
\midrule
Retorno anualizado (\%) & """ + f"{petr4_stats['mean_annual']*100:.2f}" + r""" & """ + f"{ibov_stats['mean_annual']*100:.2f}" + r""" \\
Volatilidade anualizada (\%) & """ + f"{petr4_stats['std_annual']*100:.2f}" + r""" & """ + f"{ibov_stats['std_annual']*100:.2f}" + r""" \\
\midrule
Correlação & \multicolumn{2}{c}{""" + f"{statistics['correlation']:.4f}" + r"""} \\
\bottomrule
\end{tabular}
\par\medskip\footnotesize
Nota: Período de """ + statistics['period_start'] + r""" a """ + statistics['period_end'] + r""". Retornos calculados em base logarítmica.
\end{table}
"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex)
    
    print(f"✓ Tabela salva em: {output_path}")
    print(f"✓ Estatísticas salvas em: {stats_path}")

if __name__ == "__main__":
    main()
