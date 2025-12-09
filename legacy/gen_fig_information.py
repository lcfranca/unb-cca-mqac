"""
Gerador de Figuras de Análise Informacional (Asset 3.4).

Gera visualizações para a análise de eficiência informacional:
1. Scatter Plot: Q-VAL (t) vs Retorno (t+1)
2. Bar Chart: Delta R2 por Modelo
3. Line Chart: Rolling R2 (Evolução temporal do poder preditivo)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from pathlib import Path
from src.core.config import PROJECT_ROOT
from src.core.style import set_style, COLORS

def gen_fig_information():
    set_style()
    
    # Caminhos
    processed_dir = PROJECT_ROOT / "data" / "processed"
    returns_path = processed_dir / "returns" / "returns.parquet"
    qval_path = processed_dir / "qval" / "qval_timeseries.parquet"
    output_dir = PROJECT_ROOT / "data" / "outputs" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Preparar Dados
    df_ret = pd.read_parquet(returns_path)
    df_qval = pd.read_parquet(qval_path)
    
    df_qval['available_date'] = pd.to_datetime(df_qval['quarter_end']) + pd.DateOffset(months=3)
    qval_cols = ['available_date', 'qval_scaled']
    df_qval_ready = df_qval[qval_cols].sort_values('available_date')
    
    df_ret = df_ret.sort_values('date')
    df_merged = pd.merge_asof(df_ret, df_qval_ready, left_on='date', right_on='available_date', direction='backward')
    
    required_cols = ['excess_ret_petr4', 'excess_ret_ibov', 'qval_scaled']
    df_model = df_merged.dropna(subset=required_cols).copy()

    # --- Figura 1: Joint Plot Q-VAL vs Retorno (State of the Art) ---
    # Substitui scatter simples por JointPlot com densidade KDE e Regressão
    
    # Calcular correlação para anotação
    corr = df_model['qval_scaled'].corr(df_model['excess_ret_petr4'])
    
    g = sns.jointplot(x='qval_scaled', y='excess_ret_petr4', data=df_model,
                  kind='reg', height=8, ratio=5, space=0.2,
                  scatter_kws={'alpha': 0.15, 's': 10, 'color': COLORS['primary']},
                  line_kws={'color': COLORS['secondary'], 'linewidth': 2})
    
    g.plot_joint(sns.kdeplot, color=COLORS['quaternary'], zorder=0, levels=6, alpha=0.5)
    
    g.fig.suptitle('Densidade Informacional: Score Q-VAL vs Retornos Futuros', fontsize=16, fontweight='bold', y=1.02)
    g.set_axis_labels('Score Q-VAL (Lagged)', 'Retorno Excedente PETR4 (t+1)', fontsize=12)
    
    # Anotação Estatística
    g.ax_joint.text(0.05, 0.95, f'Correlação de Pearson: {corr:.3f}', 
                    transform=g.ax_joint.transAxes, fontsize=12, 
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='lightgray'))
    
    plt.tight_layout()
    plt.savefig(output_dir / "scatter_qval_returns.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Figura 1 salva (JointPlot).")

    # --- Figura 2: Bar Chart Delta R2 ---
    # Carregar resultados do JSON se existirem, ou recalcular rápido
    # Vamos recalcular para garantir consistência com o script atual
    models = {
        "M0 (CAPM)": ["excess_ret_ibov"],
        "M1 (Fator)": ["excess_ret_ibov", "qval_scaled"] # Simplificando para M3 aqui como exemplo ou usar M1 real
    }
    # Vamos usar os valores calculados anteriormente ou hardcoded do JSON para precisão
    # Mas melhor ler do JSON gerado por estimate_models.py
    json_path = PROJECT_ROOT / "data" / "outputs" / "model_comparison.json"
    if json_path.exists():
        import json
        with open(json_path, 'r') as f:
            results = json.load(f)
        
        labels = []
        deltas = []
        for key, val in results.items():
            if key == "M0_CAPM": continue
            labels.append(key)
            deltas.append(val['delta_adj_r2'])
            
        plt.figure(figsize=(8, 5))
        bars = plt.bar(labels, deltas, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        plt.title('Contribuição Marginal de Informação ($\Delta R^2$ Ajustado)')
        plt.ylabel('Aumento no $R^2$ Ajustado (vs CAPM)')
        plt.axhline(0, color='black', linewidth=0.8)
        
        # Adicionar valores nas barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.5f}',
                     ha='center', va='bottom')
                     
        plt.tight_layout()
        plt.savefig(output_dir / "bar_delta_r2.png", dpi=300)
        plt.close()
        print("Figura 2 salva.")

    # --- Figura 3: Rolling R2 ---
    print("Calculando Rolling R2...")
    window = 252 # 1 ano
    
    rolling_r2_m0 = []
    rolling_r2_m3 = []
    dates = []
    
    # Loop otimizado ou RollingOLS
    from statsmodels.regression.rolling import RollingOLS
    
    y = df_model['excess_ret_petr4']
    X0 = sm.add_constant(df_model[['excess_ret_ibov']])
    X3 = sm.add_constant(df_model[['excess_ret_ibov', 'qval_scaled']])
    
    rol_m0 = RollingOLS(y, X0, window=window).fit()
    rol_m3 = RollingOLS(y, X3, window=window).fit()
    
    # RollingOLS do statsmodels retorna params, mas não rsquared direto facilmente
    # Vamos calcular manualmente o R2 para cada janela ou usar a propriedade se existir (versões recentes)
    # rsquared não é atributo direto do RollingRegressionResults em versões antigas
    # Vamos fazer um loop manual para garantir R2 Ajustado correto
    
    # Alternativa rápida: calcular correlação ao quadrado para M0 (aprox)
    # Mas queremos R2 ajustado. Vamos fazer loop manual com step para ser mais rápido se for muito lento
    
    # Loop manual (mais seguro para métricas específicas)
    # Para 2500 obs, é rápido o suficiente
    
    r2_diff = []
    valid_dates = []
    
    for i in range(window, len(df_model), 20): # Step de 20 dias para suavizar e acelerar
        subset = df_model.iloc[i-window:i]
        if len(subset) < window: continue
        
        y_sub = subset['excess_ret_petr4']
        
        # M0
        X0_sub = sm.add_constant(subset[['excess_ret_ibov']])
        res0 = sm.OLS(y_sub, X0_sub).fit()
        
        # M3
        X3_sub = sm.add_constant(subset[['excess_ret_ibov', 'qval_scaled']])
        res3 = sm.OLS(y_sub, X3_sub).fit()
        
        r2_diff.append(res3.rsquared_adj - res0.rsquared_adj)
        valid_dates.append(subset['date'].iloc[-1])
        
    plt.figure(figsize=(12, 6))
    plt.plot(valid_dates, r2_diff, label='$\Delta R^2$ (M3 - M0)', color='purple')
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.title(f'Evolução Temporal da Contribuição Informacional (Janela Móvel {window} dias)')
    plt.ylabel('$\Delta R^2$ Ajustado')
    plt.xlabel('Data')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "rolling_r2.png", dpi=300)
    plt.close()
    print("Figura 3 salva.")

if __name__ == "__main__":
    gen_fig_information()
