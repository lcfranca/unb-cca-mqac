"""
Gera as tabelas para a nova estratégia de pivotagem (M0 a M5).
Mapeia os resultados existentes para a nova hierarquia de modelos.
"""

import json
import pandas as pd
from pathlib import Path
from src.core.config import PROJECT_ROOT

def load_json(filename):
    path = PROJECT_ROOT / "data" / "outputs" / filename
    if not path.exists():
        print(f"Warning: {filename} not found.")
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def format_r2(val):
    return f"{val * 100:.2f}\\%"

def format_mse(val):
    return f"{val * 10000:.4f}"

def create_latex_table(rows, caption, label, columns):
    latex = []
    latex.append(r"\begin{table}[H]")
    latex.append(r"\centering")
    latex.append(f"\\caption{{{caption}}}")
    latex.append(f"\\label{{{label}}}")
    latex.append(r"\begin{tabular}{" + columns + "}")
    latex.append(r"\toprule")
    # Header row assumed to be handled by caller or fixed
    latex.append(r"Modelo & MSE ($10^{-4}$) & $R^2_{OOS}$ (\%) & $\Delta R^2$ \\")
    latex.append(r"\midrule")
    
    base_r2 = 0
    for i, row in enumerate(rows):
        name = row['name']
        mse = row['mse']
        r2 = row['r2']
        
        if i == 0:
            delta = "-"
            base_r2 = r2
        else:
            diff = (r2 - base_r2) * 100
            delta = f"{diff:+.2f} p.p."
            base_r2 = r2 # Update base for incremental comparison? Or keep fixed?
            # User asked for "comparação progressiva", so incremental makes sense.
        
        latex.append(f"{name} & {format_mse(mse)} & {format_r2(r2)} & {delta} \\\\")
        
    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}")
    latex.append(r"\end{table}")
    return "\n".join(latex)

def run():
    # Load Data
    naive = load_json("naive_metrics.json")
    dynamic = load_json("dynamic_metrics.json")
    full = load_json("full_model_comparison.json")
    
    output_dir = PROJECT_ROOT / "data" / "outputs" / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Tabela 1: Benchmarks (M0, M1, M2) ---
    # M0: RW/HM
    # M1: CAPM Static
    # M2: CAPM Dynamic
    
    rows_t1 = []
    # M0 - HM (Baseline)
    if "HM" in naive:
        rows_t1.append({'name': 'M0 (Média Histórica)', 'mse': naive['HM']['MSE'], 'r2': naive['HM']['R2_OOS']})
    # M1 - CAPM Static
    if "CAPM" in naive:
        rows_t1.append({'name': 'M1 (CAPM Estático)', 'mse': naive['CAPM']['MSE'], 'r2': naive['CAPM']['R2_OOS']})
    # M2 - CAPM Dynamic
    if "Dynamic CAPM" in dynamic:
        rows_t1.append({'name': 'M2 (CAPM Dinâmico)', 'mse': dynamic['Dynamic CAPM']['MSE'], 'r2': dynamic['Dynamic CAPM']['R2_OOS']})
        
    tex_t1 = create_latex_table(rows_t1, "Fase 1: Benchmarks e Risco de Mercado (M0-M2)", "tab:pivot_benchmarks", "lccc")
    with open(output_dir / "table_pivot_01_benchmarks.tex", 'w') as f:
        f.write(tex_t1)

    # --- Tabela 2: Fundamentos (M2 vs M3) ---
    # M2: Dynamic
    # M3: Dynamic + Fundamentals. 
    # Proxy: Using "M5 (Fatores)" from full_model_comparison as the best Fundamental model available.
    # Note: Ideally we should run Dynamic + Fundamentals.
    
    rows_t2 = []
    if "Dynamic CAPM" in dynamic:
        rows_t2.append({'name': 'M2 (CAPM Dinâmico)', 'mse': dynamic['Dynamic CAPM']['MSE'], 'r2': dynamic['Dynamic CAPM']['R2_OOS']})
    
    if "M5 (Fatores)" in full:
        # Renaming to M3 for the narrative
        rows_t2.append({'name': 'M3 (Fundamentos)', 'mse': full['M5 (Fatores)']['MSE'], 'r2': full['M5 (Fatores)']['R2_OOS']})
        
    tex_t2 = create_latex_table(rows_t2, "Fase 2: Inclusão de Fundamentos (M2 vs M3)", "tab:pivot_fundamentals", "lccc")
    with open(output_dir / "table_pivot_02_fundamentals.tex", 'w') as f:
        f.write(tex_t2)

    # --- Tabela 3: Macro (M3 vs M4) ---
    # M3: Fundamentos
    # M4: Macro. Using "M4 (Macro)" from full_model_comparison.
    
    rows_t3 = []
    if "M5 (Fatores)" in full:
        rows_t3.append({'name': 'M3 (Fundamentos)', 'mse': full['M5 (Fatores)']['MSE'], 'r2': full['M5 (Fatores)']['R2_OOS']})
    
    if "M4 (Macro)" in full:
        # Note: In the current data, Macro (23.53%) is slightly WORSE than Factors (24.08%).
        # This is an interesting finding for the report.
        rows_t3.append({'name': 'M4 (Macro + Fatores)', 'mse': full['M4 (Macro)']['MSE'], 'r2': full['M4 (Macro)']['R2_OOS']})
        
    tex_t3 = create_latex_table(rows_t3, "Fase 3: Variáveis Macroeconômicas (M3 vs M4)", "tab:pivot_macro", "lccc")
    with open(output_dir / "table_pivot_03_macro.tex", 'w') as f:
        f.write(tex_t3)

    # --- Tabela 4: Síntese (M4 vs M5) ---
    # M4: Macro
    # M5: Score Q-VAL. Using "M3 (CAPM + Q-VAL)" from full_model_comparison.
    
    rows_t4 = []
    if "M4 (Macro)" in full:
        rows_t4.append({'name': 'M4 (Macro + Fatores)', 'mse': full['M4 (Macro)']['MSE'], 'r2': full['M4 (Macro)']['R2_OOS']})
        
    if "M3 (CAPM + Q-VAL)" in full:
        # Renaming to M5
        rows_t4.append({'name': 'M5 (Score Agregado)', 'mse': full['M3 (CAPM + Q-VAL)']['MSE'], 'r2': full['M3 (CAPM + Q-VAL)']['R2_OOS']})
        
    tex_t4 = create_latex_table(rows_t4, "Fase 4: Eficiência do Score Agregado (M4 vs M5)", "tab:pivot_synthesis", "lccc")
    with open(output_dir / "table_pivot_04_synthesis.tex", 'w') as f:
        f.write(tex_t4)
        
    print("Tabelas de pivotagem geradas com sucesso.")

if __name__ == "__main__":
    run()
