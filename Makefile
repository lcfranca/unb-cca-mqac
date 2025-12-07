# ==============================================================================
# Makefile - Automação do projeto MQC
# ==============================================================================
#
# Uso:
#   make all        - Gera dados, análise, assets e PDF
#   make data       - Gera dados simulados (se necessário)
#   make analysis   - Executa scripts de análise
#   make figures    - Gera todas as figuras
#   make tables     - Gera todas as tabelas
#   make pdf        - Compila documento PDF
#   make clean      - Remove artefatos gerados
#
# ==============================================================================

PYTHON := .venv/bin/python
PANDOC := pandoc

# Diretórios
DATA_DIR := data
PROCESSED_DIR := $(DATA_DIR)/processed
OUTPUT_DIR := $(DATA_DIR)/outputs
FIGURES_DIR := $(OUTPUT_DIR)/figures
TABLES_DIR := $(OUTPUT_DIR)/tables

# Arquivos de dados intermediários (Inputs para os assets)
RETURNS_PARQUET := $(PROCESSED_DIR)/returns/returns.parquet
QVAL_PARQUET := $(PROCESSED_DIR)/qval/qval_timeseries.parquet
METRICS_PARQUET := $(PROCESSED_DIR)/metrics/metrics.parquet
OOS_RESULTS := $(OUTPUT_DIR)/oos_results.json
ROLLING_R2 := $(OUTPUT_DIR)/rolling_r2.parquet

# Arquivos de saída (Assets)
FIGURES := $(FIGURES_DIR)/sml_dynamic.pdf \
           $(FIGURES_DIR)/radar_chart.pdf \
           $(FIGURES_DIR)/learning_curve.pdf \
           $(FIGURES_DIR)/rolling_r2.pdf \
           $(FIGURES_DIR)/scatter_pred_actual.pdf \
           $(FIGURES_DIR)/residuals_hist.pdf

TABLES := $(TABLES_DIR)/estatisticas_descritivas.tex \
          $(TABLES_DIR)/resultados_capm.tex \
          $(TABLES_DIR)/score_comprabilidade.tex \
          $(TABLES_DIR)/comparacao_modelos.tex \
          $(TABLES_DIR)/criterios_informacao.tex

PDF := output/nota-tecnica.pdf

# ==============================================================================
# TARGETS PRINCIPAIS
# ==============================================================================

.PHONY: all data analysis figures tables pdf clean install check help

## all: Pipeline completo (dados → análise → assets → PDF)
all: pdf
	@echo ""
	@echo "✓ Pipeline completo executado com sucesso!"
	@echo "  PDF gerado em: output/nota-tecnica.pdf"

## data: Verifica existência dos dados processados
data:
	@if [ ! -f $(RETURNS_PARQUET) ]; then echo "Erro: $(RETURNS_PARQUET) não encontrado. Execute os notebooks de ingestão."; exit 1; fi
	@echo "✓ Dados processados encontrados."

## analysis: Executa scripts de análise (se necessário)
analysis: $(OOS_RESULTS) $(ROLLING_R2)

## figures: Gera todas as figuras
figures: $(FIGURES)

## tables: Gera todas as tabelas
tables: $(TABLES)

## pdf: Compila documento PDF
pdf: figures tables
	@echo "Compilando PDF..."
	@mkdir -p output
	$(PANDOC) --defaults=defaults.yaml --defaults=pdf.yaml
	@echo "✓ PDF gerado em: output/nota-tecnica.pdf"

# ==============================================================================
# REGRAS DE ANÁLISE
# ==============================================================================

$(OOS_RESULTS):
	@echo "Executando validação Out-of-Sample..."
	$(PYTHON) -m src.analysis.oos_validation

$(ROLLING_R2):
	@echo "Calculando Rolling R2..."
	$(PYTHON) -m src.analysis.rolling_r2

# ==============================================================================
# GERADORES DE FIGURAS
# ==============================================================================

# Agrupando figuras geradas pelo mesmo script para evitar múltiplas execuções
$(FIGURES_DIR)/sml_dynamic.pdf $(FIGURES_DIR)/radar_chart.pdf $(FIGURES_DIR)/learning_curve.pdf:
	@echo "Gerando figuras avançadas (SML, Radar, Learning Curve)..."
	$(PYTHON) -m src.assets.gen_advanced_figures

$(FIGURES_DIR)/rolling_r2.pdf $(FIGURES_DIR)/scatter_pred_actual.pdf $(FIGURES_DIR)/residuals_hist.pdf:
	@echo "Gerando figuras de diagnóstico..."
	$(PYTHON) -m src.assets.gen_fig_model_diagnostics

# ==============================================================================
# GERADORES DE TABELAS
# ==============================================================================

$(TABLES_DIR)/estatisticas_descritivas.tex:
	@echo "Gerando tabela: Estatísticas Descritivas..."
	$(PYTHON) -m src.assets.gen_table_descriptive

$(TABLES_DIR)/resultados_capm.tex:
	@echo "Gerando tabela: Resultados CAPM..."
	$(PYTHON) -m src.assets.gen_table_capm

$(TABLES_DIR)/score_comprabilidade.tex:
	@echo "Gerando tabela: Score Q-VAL..."
	$(PYTHON) -m src.assets.gen_table_qval_score

$(TABLES_DIR)/comparacao_modelos.tex:
	@echo "Gerando tabela: Comparação de Modelos..."
	$(PYTHON) -m src.assets.gen_table_model_comparison

$(TABLES_DIR)/criterios_informacao.tex:
	@echo "Gerando tabela: Critérios de Informação..."
	$(PYTHON) -m src.assets.gen_table_aic_bic

# ==============================================================================
# UTILITÁRIOS
# ==============================================================================

## clean: Remove artefatos gerados
clean:
	@echo "Limpando artefatos..."
	rm -rf $(FIGURES_DIR)/*.pdf $(FIGURES_DIR)/*.png
	rm -rf $(TABLES_DIR)/*.tex
	rm -rf output/*.pdf
	@echo "✓ Artefatos removidos"

## install: Instala dependências Python
install:
	pip install -e .
	@echo "✓ Dependências instaladas"

## check: Verifica dependências do sistema
check:
	@echo "Verificando dependências..."
	@which $(PYTHON) > /dev/null && echo "✓ Python: $(shell $(PYTHON) --version)" || echo "✗ Python não encontrado"
	@which $(PANDOC) > /dev/null && echo "✓ Pandoc: $(shell $(PANDOC) --version | head -1)" || echo "✗ Pandoc não encontrado"
	@which pdflatex > /dev/null && echo "✓ pdflatex instalado" || echo "✗ pdflatex não encontrado"

## help: Mostra esta ajuda
help:
	@echo "Comandos disponíveis:"
	@echo ""
	@grep -E "^## " $(MAKEFILE_LIST) | sed "s/## /  /"
