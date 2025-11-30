#!/usr/bin/env python3
"""
Q-VAL Scoring Engine - Motor de Métricas e Comprabilidade
=========================================================

Calcula o score Q-VAL para PETR4 baseado em três dimensões:
- Valor (30%): EY, EV/EBITDA, P/VP
- Qualidade (40%): ROE, ROACE, Margem EBITDA
- Risco (30%): Beta, Volatilidade, EVS

Saída:
- data/processed/qval_results.json
- data/outputs/tables/metricas_fundamentalistas.tex
- data/outputs/tables/score_comprabilidade.tex
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# Configuração de caminhos
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import get_paths

# Obter caminhos
paths = get_paths()
PROCESSED_DATA_DIR = paths.data_processed
OUTPUTS_DIR = paths.root / "data" / "outputs"

# =============================================================================
# BENCHMARKS SETORIAIS (Oil & Gas Integrated - Brasil)
# =============================================================================
# Referências: Bloomberg, Economatica, Relatórios Setoriais 2024
# Nota: Na ausência de dados de pares sem auth, usamos benchmarks de mercado

SECTOR_BENCHMARKS = {
    # Métricas de Valor (menor = melhor para EV/EBITDA e P/VP)
    "earnings_yield": {"mean": 0.10, "std": 0.05, "lower_is_better": False},
    "ev_ebitda": {"mean": 4.5, "std": 1.5, "lower_is_better": True},
    "price_to_book": {"mean": 1.2, "std": 0.4, "lower_is_better": True},
    
    # Métricas de Qualidade (maior = melhor)
    "roe": {"mean": 0.12, "std": 0.06, "lower_is_better": False},
    "roace": {"mean": 0.10, "std": 0.04, "lower_is_better": False},
    "ebitda_margin": {"mean": 0.35, "std": 0.10, "lower_is_better": False},
    
    # Métricas de Risco (menor = melhor para beta e vol)
    "beta": {"mean": 1.0, "std": 0.3, "lower_is_better": True},
    "volatility": {"mean": 0.35, "std": 0.10, "lower_is_better": True},
    "evs": {"mean": 0.0, "std": 0.05, "lower_is_better": False},  # EVS > 0 = criação de valor
}

# Pesos das dimensões
WEIGHTS = {
    "valor": 0.30,
    "qualidade": 0.40,
    "risco": 0.30,
}


def load_data():
    """Carrega dados de fundamentals e CAPM."""
    with open(PROCESSED_DATA_DIR / "fundamentals.json", "r") as f:
        fundamentals = json.load(f)
    
    with open(PROCESSED_DATA_DIR / "capm_results.json", "r") as f:
        capm = json.load(f)
    
    # Carregar returns para calcular volatilidade
    returns = pd.read_csv(PROCESSED_DATA_DIR / "returns.csv", parse_dates=["date"])
    
    return fundamentals, capm, returns


def calculate_roace(fundamentals: dict) -> float:
    """
    Calcula ROACE (Return on Average Capital Employed).
    ROACE = EBIT / Capital Empregado
    Capital Empregado = Total Assets - Current Liabilities
    
    Nota: Usando aproximação via dados disponíveis.
    """
    # EBIT não está diretamente disponível, usar proxy: EBITDA * (1 - D&A/EBITDA)
    # Ou usar Operating Income se disponível
    ebitda = fundamentals["income_statement"]["ebitda"]
    total_assets = fundamentals["balance_sheet_summary"]["total_assets"]
    
    # Estimativa de Current Liabilities via Current Ratio
    # Current Ratio = Current Assets / Current Liabilities
    # Aproximação: Current Assets ≈ Cash + 30% * Revenue (simplificação)
    current_ratio = fundamentals["financial_health"]["current_ratio"]
    total_cash = fundamentals["financial_health"]["total_cash"]
    revenue = fundamentals["income_statement"]["total_revenue"]
    
    # Estimativa conservadora de current assets
    current_assets_est = total_cash + 0.15 * revenue
    current_liabilities_est = current_assets_est / current_ratio if current_ratio > 0 else current_assets_est
    
    # Capital Empregado
    capital_employed = total_assets - current_liabilities_est
    
    # EBIT aproximado (EBITDA * 0.75 como proxy para D&A médio de O&G)
    ebit_est = ebitda * 0.75
    
    roace = ebit_est / capital_employed if capital_employed > 0 else 0
    
    return roace


def calculate_evs(roace: float, ke: float) -> float:
    """
    Calcula Economic Value Spread.
    EVS = ROACE - Ke
    EVS > 0 indica criação de valor econômico.
    """
    return roace - ke


def calculate_z_score(value: float, benchmark: dict) -> float:
    """
    Calcula Z-Score normalizado.
    Para métricas onde menor é melhor, inverte o sinal.
    """
    z = (value - benchmark["mean"]) / benchmark["std"] if benchmark["std"] > 0 else 0
    
    # Inverter sinal para métricas onde menor é melhor
    if benchmark["lower_is_better"]:
        z = -z
    
    return z


def calculate_dimension_score(metrics: dict, dimension_metrics: list) -> float:
    """Calcula score médio de uma dimensão."""
    z_scores = []
    for metric_name in dimension_metrics:
        if metric_name in metrics:
            z_scores.append(metrics[metric_name]["z_score"])
    
    return np.mean(z_scores) if z_scores else 0


def scale_to_100(raw_score: float) -> float:
    """
    Escala score bruto para 0-100.
    Score = 50 + 10 * Z (limitado a 0-100)
    """
    scaled = 50 + 10 * raw_score
    return max(0, min(100, scaled))


def classify_score(score: float) -> tuple[str, str]:
    """Classifica score em recomendação."""
    if score >= 70:
        return "Compra Forte", "🟢🟢"
    elif score >= 55:
        return "Compra", "🟢"
    elif score >= 45:
        return "Neutro", "🟡"
    elif score >= 30:
        return "Venda", "🔴"
    else:
        return "Venda Forte", "🔴🔴"


def generate_tex_metricas(metrics: dict, output_path: Path):
    """Gera tabela LaTeX com métricas fundamentalistas."""
    
    tex_content = r"""\begin{table}[htbp]
\centering
\caption{Métricas Fundamentalistas -- PETR4}
\label{tab:metricas_fundamentalistas}
\begin{tabular}{llrrr}
\toprule
\textbf{Dimensão} & \textbf{Métrica} & \textbf{Valor} & \textbf{Benchmark} & \textbf{Z-Score} \\
\midrule
"""
    
    # Métricas de Valor
    tex_content += r"\multirow{3}{*}{\textbf{Valor}}" + "\n"
    tex_content += f"    & Earnings Yield & {metrics['earnings_yield']['value']*100:.2f}\\% & {SECTOR_BENCHMARKS['earnings_yield']['mean']*100:.2f}\\% & {metrics['earnings_yield']['z_score']:+.2f} \\\\\n"
    tex_content += f"    & EV/EBITDA & {metrics['ev_ebitda']['value']:.2f}x & {SECTOR_BENCHMARKS['ev_ebitda']['mean']:.2f}x & {metrics['ev_ebitda']['z_score']:+.2f} \\\\\n"
    tex_content += f"    & P/VP & {metrics['price_to_book']['value']:.2f}x & {SECTOR_BENCHMARKS['price_to_book']['mean']:.2f}x & {metrics['price_to_book']['z_score']:+.2f} \\\\\n"
    tex_content += r"\midrule" + "\n"
    
    # Métricas de Qualidade
    tex_content += r"\multirow{3}{*}{\textbf{Qualidade}}" + "\n"
    tex_content += f"    & ROE & {metrics['roe']['value']*100:.2f}\\% & {SECTOR_BENCHMARKS['roe']['mean']*100:.2f}\\% & {metrics['roe']['z_score']:+.2f} \\\\\n"
    tex_content += f"    & ROACE & {metrics['roace']['value']*100:.2f}\\% & {SECTOR_BENCHMARKS['roace']['mean']*100:.2f}\\% & {metrics['roace']['z_score']:+.2f} \\\\\n"
    tex_content += f"    & Margem EBITDA & {metrics['ebitda_margin']['value']*100:.2f}\\% & {SECTOR_BENCHMARKS['ebitda_margin']['mean']*100:.2f}\\% & {metrics['ebitda_margin']['z_score']:+.2f} \\\\\n"
    tex_content += r"\midrule" + "\n"
    
    # Métricas de Risco
    tex_content += r"\multirow{3}{*}{\textbf{Risco}}" + "\n"
    tex_content += f"    & Beta & {metrics['beta']['value']:.2f} & {SECTOR_BENCHMARKS['beta']['mean']:.2f} & {metrics['beta']['z_score']:+.2f} \\\\\n"
    tex_content += f"    & Volatilidade & {metrics['volatility']['value']*100:.2f}\\% & {SECTOR_BENCHMARKS['volatility']['mean']*100:.2f}\\% & {metrics['volatility']['z_score']:+.2f} \\\\\n"
    tex_content += f"    & EVS & {metrics['evs']['value']*100:.2f}\\% & {SECTOR_BENCHMARKS['evs']['mean']*100:.2f}\\% & {metrics['evs']['z_score']:+.2f} \\\\\n"
    
    tex_content += r"""\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item Nota: Z-Score positivo indica performance superior ao benchmark setorial.
\item EVS = Economic Value Spread (ROACE - Ke). EVS > 0 indica criação de valor.
\end{tablenotes}
\end{table}
"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tex_content)


def generate_tex_score(results: dict, output_path: Path):
    """Gera tabela LaTeX com score de comprabilidade."""
    
    recommendation, _ = classify_score(results["score_final"])
    
    tex_content = r"""\begin{table}[htbp]
\centering
\caption{Score de Comprabilidade Q-VAL -- PETR4}
\label{tab:score_comprabilidade}
\begin{tabular}{lrr}
\toprule
\textbf{Dimensão} & \textbf{Z-Score Médio} & \textbf{Peso} \\
\midrule
"""
    
    tex_content += f"Valor & {results['z_valor']:+.2f} & {WEIGHTS['valor']*100:.0f}\\% \\\\\n"
    tex_content += f"Qualidade & {results['z_qualidade']:+.2f} & {WEIGHTS['qualidade']*100:.0f}\\% \\\\\n"
    tex_content += f"Risco & {results['z_risco']:+.2f} & {WEIGHTS['risco']*100:.0f}\\% \\\\\n"
    
    tex_content += r"""\midrule
\textbf{Score Bruto} & \multicolumn{2}{c}{""" + f"{results['score_raw']:+.2f}" + r"""} \\
\textbf{Score Final (0-100)} & \multicolumn{2}{c}{\textbf{""" + f"{results['score_final']:.1f}" + r"""}} \\
\textbf{Recomendação} & \multicolumn{2}{c}{\textbf{""" + recommendation + r"""}} \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item Escala de classificação: $<$30 Venda Forte; 30-45 Venda; 45-55 Neutro; 55-70 Compra; $>$70 Compra Forte.
\end{tablenotes}
\end{table}
"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tex_content)


def main():
    """Executa o motor Q-VAL."""
    print("=" * 60)
    print("Q-VAL SCORING ENGINE - PETR4")
    print("=" * 60)
    
    # Carregar dados
    fundamentals, capm, returns = load_data()
    
    # Extrair métricas brutas
    qval_inputs = fundamentals["qval_inputs"]
    
    # Calcular métricas derivadas
    roace = calculate_roace(fundamentals)
    ke = capm["ke_capm"]
    evs = calculate_evs(roace, ke)
    
    # Volatilidade anualizada
    volatility = returns["r_petr4"].std() * np.sqrt(252)
    
    # Construir dicionário de métricas com Z-Scores
    metrics = {
        # Valor
        "earnings_yield": {
            "value": qval_inputs["earnings_yield"],
            "z_score": calculate_z_score(qval_inputs["earnings_yield"], SECTOR_BENCHMARKS["earnings_yield"]),
        },
        "ev_ebitda": {
            "value": qval_inputs["ev_ebitda"],
            "z_score": calculate_z_score(qval_inputs["ev_ebitda"], SECTOR_BENCHMARKS["ev_ebitda"]),
        },
        "price_to_book": {
            "value": qval_inputs["price_to_book"],
            "z_score": calculate_z_score(qval_inputs["price_to_book"], SECTOR_BENCHMARKS["price_to_book"]),
        },
        # Qualidade
        "roe": {
            "value": qval_inputs["roe"],
            "z_score": calculate_z_score(qval_inputs["roe"], SECTOR_BENCHMARKS["roe"]),
        },
        "roace": {
            "value": roace,
            "z_score": calculate_z_score(roace, SECTOR_BENCHMARKS["roace"]),
        },
        "ebitda_margin": {
            "value": qval_inputs["ebitda_margin"],
            "z_score": calculate_z_score(qval_inputs["ebitda_margin"], SECTOR_BENCHMARKS["ebitda_margin"]),
        },
        # Risco
        "beta": {
            "value": capm["beta"],
            "z_score": calculate_z_score(capm["beta"], SECTOR_BENCHMARKS["beta"]),
        },
        "volatility": {
            "value": volatility,
            "z_score": calculate_z_score(volatility, SECTOR_BENCHMARKS["volatility"]),
        },
        "evs": {
            "value": evs,
            "z_score": calculate_z_score(evs, SECTOR_BENCHMARKS["evs"]),
        },
    }
    
    # Calcular scores por dimensão
    z_valor = calculate_dimension_score(metrics, ["earnings_yield", "ev_ebitda", "price_to_book"])
    z_qualidade = calculate_dimension_score(metrics, ["roe", "roace", "ebitda_margin"])
    z_risco = calculate_dimension_score(metrics, ["beta", "volatility", "evs"])
    
    # Score bruto ponderado
    score_raw = (
        WEIGHTS["valor"] * z_valor +
        WEIGHTS["qualidade"] * z_qualidade +
        WEIGHTS["risco"] * z_risco
    )
    
    # Score final (0-100)
    score_final = scale_to_100(score_raw)
    recommendation, emoji = classify_score(score_final)
    
    # Resultados consolidados
    results = {
        "metadata": {
            "ticker": "PETR4",
            "generated_at": datetime.now().isoformat(),
            "model_version": "Q-VAL v1.0",
        },
        "metrics": {k: {"value": v["value"], "z_score": v["z_score"]} for k, v in metrics.items()},
        "dimension_scores": {
            "valor": z_valor,
            "qualidade": z_qualidade,
            "risco": z_risco,
        },
        "weights": WEIGHTS,
        "z_valor": z_valor,
        "z_qualidade": z_qualidade,
        "z_risco": z_risco,
        "score_raw": score_raw,
        "score_final": score_final,
        "recommendation": recommendation,
        "derived_metrics": {
            "roace": roace,
            "evs": evs,
            "ke": ke,
            "volatility_annual": volatility,
        },
    }
    
    # Salvar JSON
    output_json = PROCESSED_DATA_DIR / "qval_results.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"✓ Resultados salvos: {output_json}")
    
    # Gerar tabelas LaTeX
    generate_tex_metricas(metrics, OUTPUTS_DIR / "tables" / "metricas_fundamentalistas.tex")
    print(f"✓ Tabela gerada: metricas_fundamentalistas.tex")
    
    generate_tex_score(results, OUTPUTS_DIR / "tables" / "score_comprabilidade.tex")
    print(f"✓ Tabela gerada: score_comprabilidade.tex")
    
    # Sumário
    print("\n" + "=" * 60)
    print("RESULTADOS Q-VAL")
    print("=" * 60)
    print(f"\n📊 MÉTRICAS DE VALOR (peso: {WEIGHTS['valor']*100:.0f}%)")
    print(f"   Earnings Yield: {metrics['earnings_yield']['value']*100:.2f}% (Z={metrics['earnings_yield']['z_score']:+.2f})")
    print(f"   EV/EBITDA:      {metrics['ev_ebitda']['value']:.2f}x (Z={metrics['ev_ebitda']['z_score']:+.2f})")
    print(f"   P/VP:           {metrics['price_to_book']['value']:.2f}x (Z={metrics['price_to_book']['z_score']:+.2f})")
    print(f"   → Z médio Valor: {z_valor:+.2f}")
    
    print(f"\n📈 MÉTRICAS DE QUALIDADE (peso: {WEIGHTS['qualidade']*100:.0f}%)")
    print(f"   ROE:            {metrics['roe']['value']*100:.2f}% (Z={metrics['roe']['z_score']:+.2f})")
    print(f"   ROACE:          {metrics['roace']['value']*100:.2f}% (Z={metrics['roace']['z_score']:+.2f})")
    print(f"   Margem EBITDA:  {metrics['ebitda_margin']['value']*100:.2f}% (Z={metrics['ebitda_margin']['z_score']:+.2f})")
    print(f"   → Z médio Qualidade: {z_qualidade:+.2f}")
    
    print(f"\n⚠️  MÉTRICAS DE RISCO (peso: {WEIGHTS['risco']*100:.0f}%)")
    print(f"   Beta:           {metrics['beta']['value']:.2f} (Z={metrics['beta']['z_score']:+.2f})")
    print(f"   Volatilidade:   {metrics['volatility']['value']*100:.2f}% (Z={metrics['volatility']['z_score']:+.2f})")
    print(f"   EVS:            {metrics['evs']['value']*100:.2f}% (Z={metrics['evs']['z_score']:+.2f})")
    print(f"   → Z médio Risco: {z_risco:+.2f}")
    
    print("\n" + "-" * 60)
    print(f"📌 SCORE BRUTO:  {score_raw:+.2f}")
    print(f"📌 SCORE FINAL:  {score_final:.1f}/100")
    print(f"📌 RECOMENDAÇÃO: {emoji} {recommendation}")
    print("-" * 60)
    
    return results


if __name__ == "__main__":
    main()
