#!/usr/bin/env python3
"""
Análise de Cenários - Fase 7
============================

Implementa análise de cenários para PETR4:
- Cenário Base: Premissas atuais
- Cenário Otimista: Margem Equatorial produzindo
- Cenário Pessimista: Stranded assets

Saída:
- data/processed/scenario_results.json
- data/outputs/tables/cenarios_valuation.tex
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from copy import deepcopy

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
# DEFINIÇÃO DE CENÁRIOS
# =============================================================================

SCENARIOS = {
    "base": {
        "name": "Base",
        "description": "Premissas atuais de mercado",
        "assumptions": {
            "brent_price": 75.0,           # US$/bbl
            "production": 2.8,              # MMboe/d
            "reserves_change": 0.0,         # % change
            "erp": 0.055,                   # Equity Risk Premium
            "rf_adjustment": 0.0,           # Ajuste na taxa livre de risco
            "beta_adjustment": 0.0,         # Ajuste no beta
            "margin_adjustment": 0.0,       # Ajuste na margem EBITDA
            "growth_adjustment": 0.0,       # Ajuste no crescimento
        },
    },
    "optimistic": {
        "name": "Otimista",
        "description": "Margem Equatorial produzindo, Brent alto",
        "assumptions": {
            "brent_price": 90.0,           # US$/bbl (+20%)
            "production": 3.5,              # MMboe/d (+25%)
            "reserves_change": 0.30,        # +30% reservas (5 Bboe adicionais)
            "erp": 0.045,                   # ERP menor (menor risco país)
            "rf_adjustment": -0.005,        # -50 bps (queda Selic)
            "beta_adjustment": -0.10,       # Beta menor (diversificação)
            "margin_adjustment": 0.05,      # +5pp margem EBITDA
            "growth_adjustment": 0.03,      # +3% crescimento
        },
    },
    "pessimistic": {
        "name": "Pessimista",
        "description": "Stranded assets, bloqueio Margem Equatorial",
        "assumptions": {
            "brent_price": 50.0,           # US$/bbl (-33%)
            "production": 2.5,              # MMboe/d (-11%)
            "reserves_change": -0.20,       # -20% write-down
            "erp": 0.070,                   # ERP maior (maior risco)
            "rf_adjustment": 0.01,          # +100 bps (alta Selic)
            "beta_adjustment": 0.15,        # Beta maior
            "margin_adjustment": -0.10,     # -10pp margem EBITDA
            "growth_adjustment": -0.05,     # -5% (contração)
        },
    },
}

# Benchmarks setoriais para Z-Score
SECTOR_BENCHMARKS = {
    "earnings_yield": {"mean": 0.10, "std": 0.05, "lower_is_better": False},
    "ev_ebitda": {"mean": 4.5, "std": 1.5, "lower_is_better": True},
    "price_to_book": {"mean": 1.2, "std": 0.4, "lower_is_better": True},
    "roe": {"mean": 0.12, "std": 0.06, "lower_is_better": False},
    "roace": {"mean": 0.10, "std": 0.04, "lower_is_better": False},
    "ebitda_margin": {"mean": 0.35, "std": 0.10, "lower_is_better": False},
    "beta": {"mean": 1.0, "std": 0.3, "lower_is_better": True},
    "volatility": {"mean": 0.35, "std": 0.10, "lower_is_better": True},
    "evs": {"mean": 0.0, "std": 0.05, "lower_is_better": False},
}

WEIGHTS = {"valor": 0.30, "qualidade": 0.40, "risco": 0.30}


def load_data():
    """Carrega dados base."""
    with open(PROCESSED_DIR / "fundamentals.json", "r") as f:
        fundamentals = json.load(f)
    
    with open(PROCESSED_DIR / "capm_results.json", "r") as f:
        capm = json.load(f)
    
    with open(PROCESSED_DIR / "qval_results.json", "r") as f:
        qval = json.load(f)
    
    with open(PROCESSED_DIR / "valuation_results.json", "r") as f:
        valuation = json.load(f)
    
    returns = pd.read_csv(PROCESSED_DIR / "returns.csv", parse_dates=["date"])
    
    return fundamentals, capm, qval, valuation, returns


def calculate_z_score(value: float, benchmark: dict) -> float:
    """Calcula Z-Score normalizado."""
    z = (value - benchmark["mean"]) / benchmark["std"] if benchmark["std"] > 0 else 0
    if benchmark["lower_is_better"]:
        z = -z
    return z


def scale_to_100(raw_score: float) -> float:
    """Escala score bruto para 0-100."""
    return max(0, min(100, 50 + 10 * raw_score))


def classify_score(score: float) -> tuple:
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


def calculate_scenario(scenario_key: str, fundamentals: dict, capm: dict, 
                       returns: pd.DataFrame) -> dict:
    """
    Calcula métricas para um cenário específico.
    """
    scenario = SCENARIOS[scenario_key]
    assumptions = scenario["assumptions"]
    
    # Dados base
    qval_inputs = fundamentals["qval_inputs"]
    base_beta = capm["beta"]
    base_rf = capm["rf_annual"]
    base_volatility = returns["r_petr4"].std() * np.sqrt(252)
    
    # Ajustes de cenário
    # 1. Beta ajustado
    beta = base_beta + assumptions["beta_adjustment"]
    
    # 2. Taxa livre de risco ajustada
    rf = base_rf + assumptions["rf_adjustment"]
    
    # 3. ERP do cenário
    erp = assumptions["erp"]
    
    # 4. Ke recalculado
    ke = rf + beta * erp
    
    # 5. Métricas de valor ajustadas
    # Impacto do preço do Brent nas métricas
    brent_factor = assumptions["brent_price"] / 75.0  # Base = 75
    production_factor = assumptions["production"] / 2.8  # Base = 2.8
    
    # Earnings Yield ajustado (maior Brent = maior lucro = maior EY)
    earnings_yield = qval_inputs["earnings_yield"] * brent_factor * production_factor
    earnings_yield = min(0.40, earnings_yield)  # Cap em 40%
    
    # EV/EBITDA ajustado (maior lucro = menor múltiplo se preço constante)
    ev_ebitda = qval_inputs["ev_ebitda"] / (brent_factor * production_factor)
    ev_ebitda = max(1.0, ev_ebitda)  # Floor em 1.0x
    
    # P/VP ajustado (reservas impactam book value)
    price_to_book = qval_inputs["price_to_book"] * (1 - assumptions["reserves_change"] * 0.5)
    
    # 6. Métricas de qualidade ajustadas
    # ROE ajustado
    roe = qval_inputs["roe"] * brent_factor * production_factor
    roe = min(0.30, max(0.02, roe))  # Limites
    
    # ROACE estimado (ajustado pelo Brent)
    roace = 0.15 * brent_factor * production_factor
    roace = min(0.35, max(0.03, roace))
    
    # Margem EBITDA ajustada
    ebitda_margin = qval_inputs["ebitda_margin"] + assumptions["margin_adjustment"]
    ebitda_margin = min(0.60, max(0.15, ebitda_margin))
    
    # 7. Métricas de risco
    # Volatilidade (aumenta em cenários extremos)
    if scenario_key == "pessimistic":
        volatility = base_volatility * 1.20
    elif scenario_key == "optimistic":
        volatility = base_volatility * 0.90
    else:
        volatility = base_volatility
    
    # EVS
    evs = roace - ke
    
    # 8. Calcular Z-Scores
    metrics = {
        "earnings_yield": {"value": earnings_yield, "z_score": calculate_z_score(earnings_yield, SECTOR_BENCHMARKS["earnings_yield"])},
        "ev_ebitda": {"value": ev_ebitda, "z_score": calculate_z_score(ev_ebitda, SECTOR_BENCHMARKS["ev_ebitda"])},
        "price_to_book": {"value": price_to_book, "z_score": calculate_z_score(price_to_book, SECTOR_BENCHMARKS["price_to_book"])},
        "roe": {"value": roe, "z_score": calculate_z_score(roe, SECTOR_BENCHMARKS["roe"])},
        "roace": {"value": roace, "z_score": calculate_z_score(roace, SECTOR_BENCHMARKS["roace"])},
        "ebitda_margin": {"value": ebitda_margin, "z_score": calculate_z_score(ebitda_margin, SECTOR_BENCHMARKS["ebitda_margin"])},
        "beta": {"value": beta, "z_score": calculate_z_score(beta, SECTOR_BENCHMARKS["beta"])},
        "volatility": {"value": volatility, "z_score": calculate_z_score(volatility, SECTOR_BENCHMARKS["volatility"])},
        "evs": {"value": evs, "z_score": calculate_z_score(evs, SECTOR_BENCHMARKS["evs"])},
    }
    
    # 9. Calcular scores por dimensão
    z_valor = np.mean([metrics["earnings_yield"]["z_score"], 
                       metrics["ev_ebitda"]["z_score"], 
                       metrics["price_to_book"]["z_score"]])
    
    z_qualidade = np.mean([metrics["roe"]["z_score"], 
                           metrics["roace"]["z_score"], 
                           metrics["ebitda_margin"]["z_score"]])
    
    z_risco = np.mean([metrics["beta"]["z_score"], 
                       metrics["volatility"]["z_score"], 
                       metrics["evs"]["z_score"]])
    
    # 10. Score final
    score_raw = (WEIGHTS["valor"] * z_valor + 
                 WEIGHTS["qualidade"] * z_qualidade + 
                 WEIGHTS["risco"] * z_risco)
    
    score_final = scale_to_100(score_raw)
    recommendation, emoji = classify_score(score_final)
    
    # 11. Valuation ajustado (Gordon simplificado)
    dy = fundamentals["dividend_data"]["dividend_yield"] / 100
    g = max(0, assumptions["growth_adjustment"])
    current_price = fundamentals["market_data"]["price"]
    
    d1 = current_price * dy * (1 + g)
    if ke > g:
        fair_value = d1 / (ke - g)
    else:
        fair_value = d1 / 0.10
    
    upside = (fair_value / current_price - 1) * 100
    
    # ICC
    icc = (d1 / current_price) + g
    spread = icc - ke
    
    return {
        "scenario_key": scenario_key,
        "scenario_name": scenario["name"],
        "description": scenario["description"],
        "assumptions": assumptions,
        "capm": {
            "beta": beta,
            "rf": rf,
            "erp": erp,
            "ke": ke,
        },
        "metrics": metrics,
        "dimension_scores": {
            "z_valor": z_valor,
            "z_qualidade": z_qualidade,
            "z_risco": z_risco,
        },
        "qval": {
            "score_raw": score_raw,
            "score_final": score_final,
            "recommendation": recommendation,
            "emoji": emoji,
        },
        "valuation": {
            "fair_value": fair_value,
            "current_price": current_price,
            "upside_percent": upside,
            "icc": icc,
            "spread_icc_ke": spread,
        },
    }


def generate_tex_scenarios(results: dict, output_path: Path):
    """Gera tabela LaTeX comparativa de cenários."""
    
    base = results["base"]
    opt = results["optimistic"]
    pess = results["pessimistic"]
    
    tex = r"""\begin{table}[htbp]
\centering
\caption{Análise de Cenários -- PETR4}
\label{tab:cenarios_valuation}
\begin{tabular}{lrrr}
\toprule
\textbf{Métrica} & \textbf{Base} & \textbf{Otimista} & \textbf{Pessimista} \\
\midrule
\multicolumn{4}{l}{\textit{Premissas}} \\
Brent (US\$/bbl) & """ + f"{base['assumptions']['brent_price']:.0f}" + r""" & """ + f"{opt['assumptions']['brent_price']:.0f}" + r""" & """ + f"{pess['assumptions']['brent_price']:.0f}" + r""" \\
Produção (MMboe/d) & """ + f"{base['assumptions']['production']:.1f}" + r""" & """ + f"{opt['assumptions']['production']:.1f}" + r""" & """ + f"{pess['assumptions']['production']:.1f}" + r""" \\
Reservas (\% var.) & """ + f"{base['assumptions']['reserves_change']*100:+.0f}" + r"""\% & """ + f"{opt['assumptions']['reserves_change']*100:+.0f}" + r"""\% & """ + f"{pess['assumptions']['reserves_change']*100:+.0f}" + r"""\% \\
ERP & """ + f"{base['assumptions']['erp']*100:.1f}" + r"""\% & """ + f"{opt['assumptions']['erp']*100:.1f}" + r"""\% & """ + f"{pess['assumptions']['erp']*100:.1f}" + r"""\% \\
\midrule
\multicolumn{4}{l}{\textit{CAPM}} \\
Beta & """ + f"{base['capm']['beta']:.2f}" + r""" & """ + f"{opt['capm']['beta']:.2f}" + r""" & """ + f"{pess['capm']['beta']:.2f}" + r""" \\
Rf & """ + f"{base['capm']['rf']*100:.2f}" + r"""\% & """ + f"{opt['capm']['rf']*100:.2f}" + r"""\% & """ + f"{pess['capm']['rf']*100:.2f}" + r"""\% \\
Ke & """ + f"{base['capm']['ke']*100:.2f}" + r"""\% & """ + f"{opt['capm']['ke']*100:.2f}" + r"""\% & """ + f"{pess['capm']['ke']*100:.2f}" + r"""\% \\
\midrule
\multicolumn{4}{l}{\textit{Valuation}} \\
Valor Justo (R\$) & """ + f"{base['valuation']['fair_value']:.2f}" + r""" & """ + f"{opt['valuation']['fair_value']:.2f}" + r""" & """ + f"{pess['valuation']['fair_value']:.2f}" + r""" \\
Upside/Downside & """ + f"{base['valuation']['upside_percent']:+.1f}" + r"""\% & """ + f"{opt['valuation']['upside_percent']:+.1f}" + r"""\% & """ + f"{pess['valuation']['upside_percent']:+.1f}" + r"""\% \\
ICC & """ + f"{base['valuation']['icc']*100:.2f}" + r"""\% & """ + f"{opt['valuation']['icc']*100:.2f}" + r"""\% & """ + f"{pess['valuation']['icc']*100:.2f}" + r"""\% \\
\midrule
\multicolumn{4}{l}{\textit{Q-VAL Score}} \\
Score (0-100) & """ + f"{base['qval']['score_final']:.1f}" + r""" & """ + f"{opt['qval']['score_final']:.1f}" + r""" & """ + f"{pess['qval']['score_final']:.1f}" + r""" \\
Recomendação & """ + base['qval']['recommendation'] + r""" & """ + opt['qval']['recommendation'] + r""" & """ + pess['qval']['recommendation'] + r""" \\
\bottomrule
\end{tabular}
\end{table}
"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tex)


def main():
    """Executa análise de cenários."""
    print("=" * 60)
    print("ANÁLISE DE CENÁRIOS - PETR4")
    print("=" * 60)
    
    # Carregar dados
    fundamentals, capm, qval, valuation, returns = load_data()
    
    # Calcular cenários
    results = {}
    for scenario_key in ["base", "optimistic", "pessimistic"]:
        print(f"\n📊 Calculando cenário: {SCENARIOS[scenario_key]['name']}...")
        results[scenario_key] = calculate_scenario(
            scenario_key, fundamentals, capm, returns
        )
    
    # Consolidar resultados
    output = {
        "metadata": {
            "ticker": "PETR4",
            "generated_at": datetime.now().isoformat(),
            "current_price": fundamentals["market_data"]["price"],
        },
        "scenarios": results,
        "sensitivity": {
            "score_range": {
                "min": results["pessimistic"]["qval"]["score_final"],
                "base": results["base"]["qval"]["score_final"],
                "max": results["optimistic"]["qval"]["score_final"],
            },
            "fair_value_range": {
                "min": results["pessimistic"]["valuation"]["fair_value"],
                "base": results["base"]["valuation"]["fair_value"],
                "max": results["optimistic"]["valuation"]["fair_value"],
            },
        },
    }
    
    # Salvar JSON
    output_json = PROCESSED_DIR / "scenario_results.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Resultados salvos: {output_json}")
    
    # Gerar tabela LaTeX
    generate_tex_scenarios(results, OUTPUTS_DIR / "tables" / "cenarios_valuation.tex")
    print(f"✓ Tabela gerada: cenarios_valuation.tex")
    
    # Sumário
    print("\n" + "=" * 60)
    print("COMPARATIVO DE CENÁRIOS")
    print("=" * 60)
    
    for key in ["base", "optimistic", "pessimistic"]:
        r = results[key]
        print(f"\n{'📊' if key == 'base' else '🚀' if key == 'optimistic' else '⚠️'} {r['scenario_name'].upper()}")
        print(f"   {r['description']}")
        print(f"   Brent: US$ {r['assumptions']['brent_price']:.0f}/bbl | Produção: {r['assumptions']['production']:.1f} MMboe/d")
        print(f"   Ke: {r['capm']['ke']*100:.2f}% | Fair Value: R$ {r['valuation']['fair_value']:.2f}")
        print(f"   Score Q-VAL: {r['qval']['score_final']:.1f}/100 → {r['qval']['emoji']} {r['qval']['recommendation']}")
        print(f"   Upside: {r['valuation']['upside_percent']:+.1f}%")
    
    print("\n" + "-" * 60)
    print("FAIXA DE SENSIBILIDADE")
    print("-" * 60)
    print(f"   Score Q-VAL:  {output['sensitivity']['score_range']['min']:.1f} — {output['sensitivity']['score_range']['base']:.1f} — {output['sensitivity']['score_range']['max']:.1f}")
    print(f"   Fair Value:   R$ {output['sensitivity']['fair_value_range']['min']:.2f} — R$ {output['sensitivity']['fair_value_range']['base']:.2f} — R$ {output['sensitivity']['fair_value_range']['max']:.2f}")
    print("-" * 60)
    
    return output


if __name__ == "__main__":
    main()
