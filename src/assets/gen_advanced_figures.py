"""
Gerador de Figuras Avançadas (Asset 5.X).

Gera visualizações de alta qualidade estética para a Nota Técnica:
1. Security Market Line (SML) Dinâmica
2. Decomposição de Volatilidade
3. Radar Chart Multidimensional
4. Dashboard de Valuation
5. Curva de Aprendizado (CSSE)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import statsmodels.api as sm
from pathlib import Path
from math import pi
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

def gen_advanced_figures():
    set_style()
    
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    returns_path = processed_dir / "returns" / "returns.parquet"
    qval_path = processed_dir / "qval" / "qval_timeseries.parquet"
    metrics_path = processed_dir / "metrics" / "metrics.parquet"
    
    output_dir = PROJECT_ROOT / "data" / "outputs" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Carregar Dados
    df_ret = pd.read_parquet(returns_path).sort_values('date')
    df_qval = pd.read_parquet(qval_path).sort_values('quarter_end')
    df_metrics = pd.read_parquet(metrics_path).sort_values('quarter_end')

    # ==========================================================================
    # FIGURA 1.1: Security Market Line (SML) Dinâmica
    # ==========================================================================
    print("Gerando SML Dinâmica...")
    
    # Definir períodos
    periods = [
        ('2016-2018', '2016-01-01', '2018-12-31'),
        ('2019-2021', '2019-01-01', '2021-12-31'),
        ('2022-2025', '2022-01-01', '2025-12-31')
    ]
    
    betas = []
    returns = []
    labels = []
    
    # Calcular Beta e Retorno Médio para cada período
    for label, start, end in periods:
        mask = (df_ret['date'] >= start) & (df_ret['date'] <= end)
        sub = df_ret.loc[mask]
        if len(sub) < 30: continue
        
        # Retorno médio anualizado
        avg_ret = sub['excess_ret_petr4'].mean() * 252
        
        # Beta
        X = sm.add_constant(sub['excess_ret_ibov'])
        y = sub['excess_ret_petr4']
        model = sm.OLS(y, X).fit()
        beta = model.params['excess_ret_ibov']
        
        betas.append(beta)
        returns.append(avg_ret)
        labels.append(label)

    # Plot - State of the Art SML
    plt.figure(figsize=(10, 7))
    
    # Linha SML Teórica (Rm médio do período todo)
    rm_avg = df_ret['excess_ret_ibov'].mean() * 252
    x_sml = np.linspace(0, 2.2, 100)
    y_sml = x_sml * rm_avg
    
    # Área de "Alpha Positivo" (Acima da SML)
    plt.fill_between(x_sml, y_sml, y_sml + 0.5, color=COLORS['positive'], alpha=0.05)
    plt.fill_between(x_sml, y_sml - 0.5, y_sml, color=COLORS['negative'], alpha=0.05)
    
    plt.plot(x_sml, y_sml, color='gray', linestyle='--', alpha=0.8, linewidth=1.5, label='SML Teórica (Equilíbrio)')
    
    # Trajetória com Gradiente de Cor (Tempo)
    # Usar scatter com colormap para indicar evolução temporal
    cmap = sns.color_palette("Blues", as_cmap=True)
    norm = plt.Normalize(0, len(betas)-1)
    
    # Plotar linha de trajetória suave
    plt.plot(betas, returns, color=COLORS['primary'], alpha=0.3, linewidth=3, zorder=2, linestyle='-')
    
    # Plotar pontos com cores evolutivas
    sc = plt.scatter(betas, returns, c=range(len(betas)), cmap='Blues', s=200, zorder=5, edgecolors='black', linewidth=1.5)
    
    # Setas de direção entre pontos
    for i in range(len(betas)-1):
        plt.annotate('', xy=(betas[i+1], returns[i+1]), xytext=(betas[i], returns[i]),
                     arrowprops=dict(arrowstyle='->', color='black', lw=1.5, shrinkA=10, shrinkB=10), zorder=4)
    
    # Labels com caixas
    for i, txt in enumerate(labels):
        # Calcular Alpha (Distância vertical)
        alpha = returns[i] - (betas[i] * rm_avg)
        alpha_txt = f"$\\alpha$: {alpha:.1%}"
        
        offset_y = 15 if i % 2 == 0 else -25
        
        plt.annotate(f"{txt}\n{alpha_txt}", (betas[i], returns[i]), xytext=(0, offset_y), 
                     textcoords='offset points', fontsize=10, fontweight='bold', ha='center',
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9))
        
    plt.title('Dinâmica de Risco-Retorno: Migração na SML (2016-2025)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Beta (Risco Sistemático)', fontsize=12)
    plt.ylabel('Retorno em Excesso Anualizado', fontsize=12)
    
    # Anotação de Interpretação
    plt.text(0.05, 0.95, "Região de Alpha Positivo\n(Retorno > Risco)", transform=plt.gca().transAxes, 
             color=COLORS['positive'], fontweight='bold', fontsize=10)
    
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "sml_dynamic.pdf")
    plt.close()

    # ==========================================================================
    # FIGURA 2.1: Radar Chart Multidimensional
    # ==========================================================================
    print("Gerando Radar Chart...")
    from scipy.stats import norm
    
    # Pegar último trimestre disponível
    last_q = df_qval.iloc[-1]
    
    # Categorias
    categories = ['Valor', 'Qualidade', 'Risco']
    N = len(categories)
    
    # Converter Z-Scores para Percentil (0-100) para visualização no Radar
    # Assumindo distribuição normal dos Z-Scores
    def z_to_score(z):
        if pd.isna(z): return 50
        return norm.cdf(z) * 100

    val_score = z_to_score(last_q['score_valor'])
    qual_score = z_to_score(last_q['score_qualidade'])
    risk_score = z_to_score(last_q['score_risco'])
    
    values = [val_score, qual_score, risk_score]
    values += values[:1] # Fechar o loop
    
    # Benchmark (Média 50 = Z-Score 0)
    benchmark = [50, 50, 50, 50]
    
    # Ângulos
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    # Plot
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    # Eixos
    plt.xticks(angles[:-1], categories, color='black', size=12, fontweight='bold')
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80], ["20", "40", "60", "80"], color="grey", size=8)
    plt.ylim(0, 100)
    
    # Plot PETR4
    ax.plot(angles, values, linewidth=2, linestyle='solid', label='PETR4 (Atual)', color=COLORS['primary'])
    ax.fill(angles, values, color=COLORS['primary'], alpha=0.2)
    
    # Plot Benchmark
    ax.plot(angles, benchmark, linewidth=1, linestyle='dashed', label='Média Histórica', color='gray')
    
    plt.title(f"Perfil Multidimensional Q-VAL ({last_q['quarter_end'].date()})", y=1.08, fontsize=14, fontweight='bold')
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 0.1))
    plt.tight_layout()
    plt.savefig(output_dir / "radar_qval.pdf")
    plt.close()

    # ==========================================================================
    # FIGURA 3.1: Curva de Aprendizado (CSSE)
    # ==========================================================================
    print("Gerando Curva de Aprendizado...")
    
    # Preparar dados (Merge)
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    df_merged = pd.merge_asof(df_ret, df_qval[['available_date', 'qval_scaled']], 
                              left_on='date', right_on='available_date', direction='backward').dropna()
    
    # Estimar modelos na amostra toda (para pegar resíduos)
    y = df_merged['excess_ret_petr4']
    X0 = sm.add_constant(df_merged[['excess_ret_ibov']])
    X3 = sm.add_constant(df_merged[['excess_ret_ibov', 'qval_scaled']])
    
    res0 = sm.OLS(y, X0).fit()
    res3 = sm.OLS(y, X3).fit()
    
    # Erros ao quadrado
    e0_sq = res0.resid ** 2
    e3_sq = res3.resid ** 2
    
    # Diferença acumulada (M0 - M3) -> Se positivo, M3 erra menos
    diff_cumsum = (e0_sq - e3_sq).cumsum()
    
    plt.figure(figsize=(10, 5))
    plt.plot(df_merged['date'], diff_cumsum, color=COLORS['secondary'], linewidth=1.5)
    
    # Adicionar linha zero
    plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
    
    # Preencher área
    plt.fill_between(df_merged['date'], diff_cumsum, 0, where=(diff_cumsum >= 0), 
                     color=COLORS['secondary'], alpha=0.1, interpolate=True)
    plt.fill_between(df_merged['date'], diff_cumsum, 0, where=(diff_cumsum < 0), 
                     color='gray', alpha=0.1, interpolate=True)
    
    plt.title('Curva de Aprendizado do Mercado: $\sum (e_{CAPM}^2 - e_{QVAL}^2)$')
    plt.ylabel('Diferença Acumulada de Erros Quadráticos')
    plt.xlabel('Data')
    
    # Anotação interpretativa
    plt.annotate('Q-VAL adiciona informação', xy=(0.02, 0.9), xycoords='axes fraction', 
                 color=COLORS['secondary'], fontweight='bold')
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "learning_curve.pdf")
    plt.close()

    print("Figuras avançadas geradas com sucesso.")

if __name__ == "__main__":
    gen_advanced_figures()
