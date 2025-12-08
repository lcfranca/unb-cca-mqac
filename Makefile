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
NESTED_RESULTS := $(OUTPUT_DIR)/nested_models_results.json
M5_PREDICTIONS := $(OUTPUT_DIR)/m5_predictions.parquet
BACKTEST_RESULTS := $(OUTPUT_DIR)/backtest_results.json

# Arquivos de saída (Assets)
FIGURES := $(FIGURES_DIR)/r2_evolution.pdf \
           $(FIGURES_DIR)/backtest_equity_curve.pdf

TABLES := $(TABLES_DIR)/tabela_performance_modelos.tex

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
analysis: $(NESTED_RESULTS) $(M5_PREDICTIONS) $(BACKTEST_RESULTS)

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

$(NESTED_RESULTS):
	@echo "Executando estimativa de modelos aninhados (M0-M5)..."
	$(PYTHON) -m src.analysis.estimate_nested_models

$(M5_PREDICTIONS):
	@echo "Treinando modelos M5 (Linear e ML)..."
	$(PYTHON) -m src.analysis.train_m5_models

$(BACKTEST_RESULTS): $(M5_PREDICTIONS)
	@echo "Executando backtest M5..."
	$(PYTHON) -m src.analysis.backtest_m5

# ==============================================================================
# GERADORES DE FIGURAS
# ==============================================================================

$(FIGURES_DIR)/r2_evolution.pdf: $(NESTED_RESULTS)
	@echo "Gerando gráfico de evolução do R2..."
	$(PYTHON) -m src.assets.gen_fig_r2_evolution

$(FIGURES_DIR)/backtest_equity_curve.pdf: $(BACKTEST_RESULTS)
	@echo "Gerando gráfico de backtest..."
	# O script backtest_m5 já gera a figura, mas definimos a dependência aqui
	@echo "Figura de backtest atualizada."

# ==============================================================================
# GERADORES DE TABELAS
# ==============================================================================

$(TABLES_DIR)/tabela_performance_modelos.tex: $(NESTED_RESULTS)
	@echo "Gerando tabela de performance dos modelos..."
	$(PYTHON) -m src.assets.gen_table_model_performance

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
