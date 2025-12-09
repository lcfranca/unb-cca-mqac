import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

def run():
    set_style()
    
    input_path = PROJECT_ROOT / "data/processed/qval/qval_timeseries.parquet"
    output_path = PROJECT_ROOT / "data/outputs/figures/qval_radar.pdf"
    
    if not input_path.exists():
        print(f"File not found: {input_path}")
        return

    df = pd.read_parquet(input_path)
    
    # Get latest date
    latest_row = df.iloc[-1]
    date_str = latest_row['quarter_end'].strftime('%Y-%m-%d')
    
    # Define categories and values
    # Mapping: (Column, Label, Invert?)
    # Invert means: High raw value is BAD, so we flip sign to make "Outward" = GOOD
    metrics = [
        # Valor (Blue)
        ('z_earnings_yield', 'E. Yield', False),
        ('z_dividend_yield', 'Div. Yield', False),
        ('z_ev_ebitda', 'EV/EBITDA', True), 
        ('z_pb_ratio', 'P/B', True),       
        
        # Qualidade (Green)
        ('z_roe', 'ROE', False),
        ('z_roic', 'ROIC', False),
        ('z_ebitda_margin', 'Margem', False),
        ('z_evs', 'Estabilidade', False), 
        
        # Risco (Red)
        ('z_debt_to_equity', 'D/E', True), 
        ('z_volatility', 'Volatilidade', True), 
        ('z_beta', 'Beta', True), 
    ]
    
    categories = [m[1] for m in metrics]
    values = []
    
    for col, label, invert in metrics:
        val = latest_row[col]
        if pd.isna(val):
            val = 0
        if invert:
            val = -val
        values.append(val)
        
    # Close the loop
    values += values[:1]
    angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
    angles += angles[:1]
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], categories, color='black', size=10)
    
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([-2, -1, 0, 1, 2], ["-2", "-1", "0", "1", "2"], color="grey", size=8)
    plt.ylim(-3, 3)
    
    # Background Colors for Dimensions
    # Value (Indices 0-3)
    # Quality (Indices 4-7)
    # Risk (Indices 8-10)
    
    # Calculate angle width per category
    width = 2 * pi / len(categories)
    
    # Shift angles to center the background slices on the axis lines? 
    # Or usually background sectors are between axes? 
    # Let's color the sectors covering the variables.
    # Angles list has the angle for each variable.
    
    # We want to cover the area corresponding to the group.
    # Value: 0 to 3. The sector should cover from angle[0]-width/2 to angle[3]+width/2?
    # Let's try simple wedges.
    
    # Value Sector (Blue)
    start_angle = angles[0] - width/2
    end_angle = angles[3] + width/2
    ax.fill_between(np.linspace(start_angle, end_angle, 100), -3, 3, color=COLORS['primary'], alpha=0.1, label='Valor')
    
    # Quality Sector (Green)
    start_angle = angles[4] - width/2
    end_angle = angles[7] + width/2
    ax.fill_between(np.linspace(start_angle, end_angle, 100), -3, 3, color=COLORS['tertiary'], alpha=0.1, label='Qualidade')
    
    # Risk Sector (Red)
    start_angle = angles[8] - width/2
    # Wrap around for the last sector if needed, but here it is contiguous 8, 9, 10.
    # 10 is the last index.
    end_angle = angles[10] + width/2
    ax.fill_between(np.linspace(start_angle, end_angle, 100), -3, 3, color=COLORS['secondary'], alpha=0.1, label='Risco')

    # Plot data
    ax.plot(angles, values, linewidth=2, linestyle='solid', color='black')
    ax.fill(angles, values, color='black', alpha=0.1) # Darker fill for the shape itself
    
    # Add Title
    plt.title(f"Radar de Fundamentos (Z-Scores) - {date_str}\n(Quanto mais externo, melhor)", size=14, color=COLORS['text'], y=1.08, fontweight='bold')
    
    # Add circle at 0 (Mean)
    ax.plot(np.linspace(0, 2*pi, 100), np.zeros(100), color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    
    # Legend for Dimensions
    # Create custom handles for legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['primary'], alpha=0.3, label='Dimensão Valor'),
        Patch(facecolor=COLORS['tertiary'], alpha=0.3, label='Dimensão Qualidade'),
        Patch(facecolor=COLORS['secondary'], alpha=0.3, label='Dimensão Risco')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    plt.tight_layout()
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    print(f"Figure saved to {output_path}")

if __name__ == "__main__":
    run()
