#!/usr/bin/env python3
"""
Análise de Valuation e Mispricing - Fase 6
==========================================

Implementa:
- Múltiplos relativos (histórico e setor)
- Modelo de Gordon (Dividend Discount Model)
- Implied Cost of Capital (ICC)
- Diagnóstico de Mispricing

Saída:
- data/processed/valuation_results.json
- data/outputs/tables/valuation_multiplos.tex
- data/outputs/tables/diagnostico_mispricing.tex
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

paths = get_paths()
PROCESSED_DIR = paths.data_processed
OUTPUTS_DIR = paths.root / "data" / "outputs"

# =============================================================================
# BENCHMARKS HISTÓRICOS E SETORIAIS
# =============================================================================

# Múltiplos históricos PETR4 (média 5 anos - 2020-2024)
# Fonte: Economatica, Bloomberg
HISTORICAL_MULTIPLES = {
    "price_earnings": {"mean": 6.5, "std": 3.2, "min": 2.8, "max": 12.5},
    "ev_ebitda": {"mean": 3.8, "std": 1.2, "min": 1.9, "max": 6.2},
    "price_to_book": {"mean": 1.1, "std": 0.3, "min": 0.6, "max": 1.8},
    "dividend_yield": {"mean": 12.0, "std": 8.0, "min": 2.5, "max": 35.0},
}

# Múltiplos setoriais (Oil & Gas Integrated - Brasil, 2024)
SECTOR_MULTIPLES = {
    "price_earnings": {"mean": 8.0, "std": 4.0},
    "ev_ebitda": {"mean": 4.5, "std": 1.5},
    "price_to_book": {"mean": 1.2, "std": 0.4},
    "dividend_yield": {"mean": 8.0, "std": 5.0},
}


def load_data():
    """Carrega dados necessários."""
    with open(PROCESSED_DIR / "fundamentals.json", "r") as f:
        fundamentals = json.load(f)
    
    with open(PROCESSED_DIR / "capm_results.json", "r") as f:
        capm = json.load(f)
    
    with open(PROCESSED_DIR / "qval_results.json", "r") as f:
        qval = json.load(f)
    
    return fundamentals, capm, qval


def analyze_multiples(fundamentals: dict) -> dict:
    """
    Analisa múltiplos atuais vs. histórico e setor.
    """
    valuation = fundamentals["valuation_metrics"]
    dividend = fundamentals["dividend_data"]
    
    current = {
        "price_earnings": valuation["price_earnings"],
        "ev_ebitda": valuation["enterprise_to_ebitda"],
        "price_to_book": valuation["price_to_book"],
        "dividend_yield": dividend["dividend_yield"],
    }
    
    analysis = {}
    for metric, value in current.items():
        hist = HISTORICAL_MULTIPLES[metric]
        sect = SECTOR_MULTIPLES[metric]
        
        # Z-score vs histórico
        z_hist = (value - hist["mean"]) / hist["std"] if hist["std"] > 0 else 0
        
        # Z-score vs setor
        z_sect = (value - sect["mean"]) / sect["std"] if sect["std"] > 0 else 0
        
        # Prêmio/desconto percentual
        premium_hist = (value / hist["mean"] - 1) * 100 if hist["mean"] > 0 else 0
        premium_sect = (value / sect["mean"] - 1) * 100 if sect["mean"] > 0 else 0
        
        analysis[metric] = {
            "current": value,
            "historical_mean": hist["mean"],
            "sector_mean": sect["mean"],
            "z_historical": z_hist,
            "z_sector": z_sect,
            "premium_vs_historical": premium_hist,
            "premium_vs_sector": premium_sect,
        }
    
    return analysis


def gordon_model(fundamentals: dict, capm: dict) -> dict:
    """
    Implementa o Modelo de Gordon (DDM).
    P0 = D1 / (Ke - g)
    """
    dividend = fundamentals["dividend_data"]
    profitability = fundamentals["profitability_metrics"]
    market = fundamentals["market_data"]
    
    # Último dividendo por ação
    last_dividend = dividend["last_dividend_value"]
    current_price = market["price"]
    dy = dividend["dividend_yield"] / 100  # Converter para decimal
    
    # Taxa de crescimento (g) - Método 1: ROE × (1 - Payout)
    roe = profitability["return_on_equity"]
    
    # Estimativa de payout ratio
    # Payout ≈ DY × P/E
    pe = fundamentals["valuation_metrics"]["price_earnings"]
    payout_ratio = min(0.95, dy * pe)  # Limitar a 95%
    
    g_roe = roe * (1 - payout_ratio)
    
    # Taxa de crescimento (g) - Método 2: Crescimento histórico de earnings
    earnings_growth = fundamentals["growth_metrics"]["earnings_growth"]
    g_earnings = max(-0.10, min(0.15, earnings_growth))  # Limitar entre -10% e 15%
    
    # Usar média dos dois métodos, com piso em 0%
    g = max(0.0, (g_roe + g_earnings) / 2)
    
    # Ke do CAPM
    ke = capm["ke_capm"]
    
    # D1 = D0 × (1 + g)
    # Usar DY atual para estimar D0 por ação
    d0_per_share = current_price * dy
    d1 = d0_per_share * (1 + g)
    
    # Valor justo pelo Gordon
    if ke > g:
        fair_value = d1 / (ke - g)
    else:
        # Se g >= ke, modelo não é válido, usar múltiplo de DY
        fair_value = d1 / 0.10  # Assumir 10% de yield justo
    
    # Upside/Downside
    upside = (fair_value / current_price - 1) * 100
    
    return {
        "last_dividend": last_dividend,
        "dividend_yield": dy,
        "payout_ratio": payout_ratio,
        "growth_rate_roe": g_roe,
        "growth_rate_earnings": g_earnings,
        "growth_rate_avg": g,
        "ke": ke,
        "d1": d1,
        "fair_value": fair_value,
        "current_price": current_price,
        "upside_percent": upside,
    }


def calculate_icc(fundamentals: dict, gordon: dict) -> dict:
    """
    Calcula Implied Cost of Capital (ICC).
    ICC = (D1/P0) + g = DY × (1+g) + g
    """
    market = fundamentals["market_data"]
    current_price = market["price"]
    
    d1 = gordon["d1"]
    g = gordon["growth_rate_avg"]
    
    # Método 1: ICC via Gordon reverso
    icc_gordon = (d1 / current_price) + g
    
    # Método 2: ICC via Earnings Yield + g
    ey = fundamentals["valuation_metrics"]["earnings_yield"]
    icc_ey = ey + g
    
    # Média ponderada (Gordon tem mais peso por ser baseado em fluxos)
    icc = 0.6 * icc_gordon + 0.4 * icc_ey
    
    return {
        "icc_gordon": icc_gordon,
        "icc_earnings_yield": icc_ey,
        "icc_weighted": icc,
        "components": {
            "dividend_yield_adjusted": d1 / current_price,
            "growth_rate": g,
            "earnings_yield": ey,
        }
    }


def diagnose_mispricing(capm: dict, icc: dict, gordon: dict, qval: dict) -> dict:
    """
    Diagnóstico consolidado de mispricing.
    """
    ke = capm["ke_capm"]
    icc_val = icc["icc_weighted"]
    
    # Spread ICC vs Ke
    spread = icc_val - ke
    spread_bps = spread * 10000  # Em basis points
    
    # Classificação
    if spread > 0.02:  # > 200 bps
        classification = "Fortemente Subprecificado"
        signal = "Compra Forte"
        emoji = "🟢🟢"
    elif spread > 0.005:  # > 50 bps
        classification = "Subprecificado"
        signal = "Compra"
        emoji = "🟢"
    elif spread > -0.005:  # Entre -50 e +50 bps
        classification = "Precificação Justa"
        signal = "Neutro"
        emoji = "🟡"
    elif spread > -0.02:  # Entre -200 e -50 bps
        classification = "Sobreprecificado"
        signal = "Venda"
        emoji = "🔴"
    else:
        classification = "Fortemente Sobreprecificado"
        signal = "Venda Forte"
        emoji = "🔴🔴"
    
    # Integração com Q-VAL
    qval_score = qval["score_final"]
    qval_signal = qval["recommendation"]
    
    # Sinal consolidado (média de múltiplas metodologias)
    # 1 = Compra Forte, 0.5 = Compra, 0 = Neutro, -0.5 = Venda, -1 = Venda Forte
    signal_map = {
        "Compra Forte": 1.0,
        "Compra": 0.5,
        "Neutro": 0.0,
        "Venda": -0.5,
        "Venda Forte": -1.0,
    }
    
    icc_signal_val = signal_map.get(signal, 0)
    qval_signal_val = signal_map.get(qval_signal, 0)
    gordon_signal_val = 0.5 if gordon["upside_percent"] > 10 else (-0.5 if gordon["upside_percent"] < -10 else 0)
    
    consolidated_signal = (icc_signal_val + qval_signal_val + gordon_signal_val) / 3
    
    if consolidated_signal > 0.4:
        final_recommendation = "Compra"
        final_emoji = "🟢"
    elif consolidated_signal > -0.4:
        final_recommendation = "Neutro"
        final_emoji = "🟡"
    else:
        final_recommendation = "Venda"
        final_emoji = "🔴"
    
    return {
        "ke_capm": ke,
        "icc": icc_val,
        "spread": spread,
        "spread_bps": spread_bps,
        "classification": classification,
        "icc_signal": signal,
        "icc_emoji": emoji,
        "gordon_upside": gordon["upside_percent"],
        "qval_score": qval_score,
        "qval_signal": qval_signal,
        "consolidated_signal_value": consolidated_signal,
        "final_recommendation": final_recommendation,
        "final_emoji": final_emoji,
    }


def generate_tex_multiples(analysis: dict, output_path: Path):
    """Gera tabela LaTeX de múltiplos."""
    
    tex = r"""\begin{table}[htbp]
\centering
\caption{Análise de Múltiplos -- PETR4}
\label{tab:valuation_multiplos}
\begin{tabular}{lrrrr}
\toprule
\textbf{Múltiplo} & \textbf{Atual} & \textbf{Histórico} & \textbf{Setor} & \textbf{Prêmio/Desc.} \\
\midrule
"""
    
    metric_names = {
        "price_earnings": "P/L",
        "ev_ebitda": "EV/EBITDA",
        "price_to_book": "P/VP",
        "dividend_yield": "Dividend Yield",
    }
    
    for metric, data in analysis.items():
        name = metric_names[metric]
        current = data["current"]
        hist = data["historical_mean"]
        sect = data["sector_mean"]
        premium = data["premium_vs_historical"]
        
        if metric == "dividend_yield":
            tex += f"{name} & {current:.2f}\\% & {hist:.2f}\\% & {sect:.2f}\\% & {premium:+.1f}\\% \\\\\n"
        else:
            tex += f"{name} & {current:.2f}x & {hist:.2f}x & {sect:.2f}x & {premium:+.1f}\\% \\\\\n"
    
    tex += r"""\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item Prêmio/Desconto calculado vs. média histórica 5 anos.
\item Valores negativos indicam desconto (ativo mais barato que histórico).
\end{tablenotes}
\end{table}
"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tex)


def generate_tex_mispricing(diagnosis: dict, gordon: dict, output_path: Path):
    """Gera tabela LaTeX de diagnóstico de mispricing."""
    
    tex = r"""\begin{table}[htbp]
\centering
\caption{Diagnóstico de Mispricing -- PETR4}
\label{tab:diagnostico_mispricing}
\begin{tabular}{lr}
\toprule
\textbf{Métrica} & \textbf{Valor} \\
\midrule
\multicolumn{2}{l}{\textit{Modelo de Gordon (DDM)}} \\
Taxa de Crescimento (g) & """ + f"{gordon['growth_rate_avg']*100:.2f}" + r"""\% \\
Custo de Capital (Ke) & """ + f"{gordon['ke']*100:.2f}" + r"""\% \\
Valor Justo Estimado & R\$ """ + f"{gordon['fair_value']:.2f}" + r""" \\
Preço Atual & R\$ """ + f"{gordon['current_price']:.2f}" + r""" \\
Upside/Downside & """ + f"{gordon['upside_percent']:+.1f}" + r"""\% \\
\midrule
\multicolumn{2}{l}{\textit{Implied Cost of Capital (ICC)}} \\
ICC (ponderado) & """ + f"{diagnosis['icc']*100:.2f}" + r"""\% \\
Ke (CAPM) & """ + f"{diagnosis['ke_capm']*100:.2f}" + r"""\% \\
Spread (ICC - Ke) & """ + f"{diagnosis['spread']*100:+.2f}" + r"""\% \\
\midrule
\multicolumn{2}{l}{\textit{Diagnóstico Consolidado}} \\
Classificação & """ + diagnosis['classification'] + r""" \\
Sinal ICC & """ + diagnosis['icc_signal'] + r""" \\
Score Q-VAL & """ + f"{diagnosis['qval_score']:.1f}" + r"""/100 \\
Sinal Q-VAL & """ + diagnosis['qval_signal'] + r""" \\
\textbf{Recomendação Final} & \textbf{""" + diagnosis['final_recommendation'] + r"""} \\
\bottomrule
\end{tabular}
\end{table}
"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tex)


def main():
    """Executa análise de valuation."""
    print("=" * 60)
    print("ANÁLISE DE VALUATION E MISPRICING - PETR4")
    print("=" * 60)
    
    # Carregar dados
    fundamentals, capm, qval = load_data()
    
    # 1. Análise de Múltiplos
    print("\n📊 Analisando múltiplos...")
    multiples = analyze_multiples(fundamentals)
    
    # 2. Modelo de Gordon
    print("📈 Calculando valor justo (Gordon DDM)...")
    gordon = gordon_model(fundamentals, capm)
    
    # 3. Implied Cost of Capital
    print("💹 Calculando ICC...")
    icc = calculate_icc(fundamentals, gordon)
    
    # 4. Diagnóstico de Mispricing
    print("🔍 Diagnosticando mispricing...")
    diagnosis = diagnose_mispricing(capm, icc, gordon, qval)
    
    # Consolidar resultados
    results = {
        "metadata": {
            "ticker": "PETR4",
            "generated_at": datetime.now().isoformat(),
        },
        "multiples_analysis": multiples,
        "gordon_model": gordon,
        "implied_cost_of_capital": icc,
        "mispricing_diagnosis": diagnosis,
    }
    
    # Salvar JSON
    output_json = PROCESSED_DIR / "valuation_results.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Resultados salvos: {output_json}")
    
    # Gerar tabelas LaTeX
    generate_tex_multiples(multiples, OUTPUTS_DIR / "tables" / "valuation_multiplos.tex")
    print(f"✓ Tabela gerada: valuation_multiplos.tex")
    
    generate_tex_mispricing(diagnosis, gordon, OUTPUTS_DIR / "tables" / "diagnostico_mispricing.tex")
    print(f"✓ Tabela gerada: diagnostico_mispricing.tex")
    
    # Sumário
    print("\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    
    print("\n📊 MÚLTIPLOS (vs. Histórico 5 anos)")
    for metric, data in multiples.items():
        premium = data["premium_vs_historical"]
        signal = "📉 Desconto" if premium < -10 else ("📈 Prêmio" if premium > 10 else "➡️ Em linha")
        print(f"   {metric:20s}: {data['current']:6.2f} vs {data['historical_mean']:6.2f} ({premium:+.1f}%) {signal}")
    
    print(f"\n💰 MODELO DE GORDON (DDM)")
    print(f"   Taxa de crescimento (g): {gordon['growth_rate_avg']*100:.2f}%")
    print(f"   Custo de capital (Ke):   {gordon['ke']*100:.2f}%")
    print(f"   Valor Justo:             R$ {gordon['fair_value']:.2f}")
    print(f"   Preço Atual:             R$ {gordon['current_price']:.2f}")
    print(f"   Upside/Downside:         {gordon['upside_percent']:+.1f}%")
    
    print(f"\n💹 IMPLIED COST OF CAPITAL (ICC)")
    print(f"   ICC (Gordon):            {icc['icc_gordon']*100:.2f}%")
    print(f"   ICC (Earnings Yield):    {icc['icc_earnings_yield']*100:.2f}%")
    print(f"   ICC (Ponderado):         {icc['icc_weighted']*100:.2f}%")
    print(f"   Ke (CAPM):               {capm['ke_capm']*100:.2f}%")
    print(f"   Spread (ICC - Ke):       {diagnosis['spread']*100:+.2f}%")
    
    print("\n" + "-" * 60)
    print(f"🎯 DIAGNÓSTICO: {diagnosis['classification']}")
    print(f"📌 SINAL ICC:   {diagnosis['icc_emoji']} {diagnosis['icc_signal']}")
    print(f"📊 SCORE Q-VAL: {diagnosis['qval_score']:.1f}/100 ({diagnosis['qval_signal']})")
    print(f"\n🏆 RECOMENDAÇÃO FINAL: {diagnosis['final_emoji']} {diagnosis['final_recommendation']}")
    print("-" * 60)
    
    return results


if __name__ == "__main__":
    main()
