# ==============================================================================
# Makefile - Automação do projeto MQC
# ==============================================================================
#
# Uso:
#   make all        - Gera dados, análise, assets e PDF
#   make data       - Gera dados simulados
#   make analysis   - Executa análise CAPM
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

# Arquivos de dados intermediários
RETURNS_CSV := $(PROCESSED_DIR)/returns.csv
CAPM_JSON := $(PROCESSED_DIR)/capm_results.json
STATS_JSON := $(PROCESSED_DIR)/statistics.json

# Arquivos de saída
FIGURES := $(FIGURES_DIR)/regressao_beta.pdf \
           $(FIGURES_DIR)/sml_capm.pdf \
           $(FIGURES_DIR)/distribuicao_retornos.pdf \
           $(FIGURES_DIR)/correlacao.pdf

TABLES := $(TABLES_DIR)/estatisticas_descritivas.tex \
          $(TABLES_DIR)/resultados_capm.tex

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

## data: Gera dados simulados
data: $(RETURNS_CSV)

## analysis: Executa análise CAPM
analysis: $(CAPM_JSON) $(STATS_JSON)

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
# GERADORES DE DADOS
# ==============================================================================

# returns.csv é gerado pelo notebook 01_data_ingestion.ipynb
# Não há target para gerá-lo via make, execute o notebook primeiro

$(CAPM_JSON): $(RETURNS_CSV)
	@echo "Executando análise CAPM..."
	$(PYTHON) -m src.assets.gen_capm_analysis

$(STATS_JSON): $(RETURNS_CSV)
	@echo "Calculando estatísticas..."
	$(PYTHON) -m src.assets.gen_table_statistics

# ==============================================================================
# GERADORES DE FIGURAS
# ==============================================================================

$(FIGURES_DIR)/regressao_beta.pdf: $(CAPM_JSON)
	@echo "Gerando figura: Regressão Beta..."
	$(PYTHON) -m src.assets.gen_fig_regression

$(FIGURES_DIR)/sml_capm.pdf: $(CAPM_JSON)
	@echo "Gerando figura: SML..."
	$(PYTHON) -m src.assets.gen_fig_sml

$(FIGURES_DIR)/distribuicao_retornos.pdf: $(RETURNS_CSV)
	@echo "Gerando figura: Distribuição..."
	$(PYTHON) -m src.assets.gen_fig_distribution

$(FIGURES_DIR)/correlacao.pdf: $(RETURNS_CSV)
	@echo "Gerando figura: Correlação..."
	$(PYTHON) -m src.assets.gen_fig_correlation

# ==============================================================================
# GERADORES DE TABELAS
# ==============================================================================

$(TABLES_DIR)/estatisticas_descritivas.tex: $(RETURNS_CSV)
	@echo "Gerando tabela: Estatísticas..."
	$(PYTHON) -m src.assets.gen_table_statistics

$(TABLES_DIR)/resultados_capm.tex: $(CAPM_JSON)
	@echo "Gerando tabela: Resultados CAPM..."
	$(PYTHON) -m src.assets.gen_table_results

# ==============================================================================
# UTILITÁRIOS
# ==============================================================================

## clean: Remove artefatos gerados
clean:
	@echo "Limpando artefatos..."
	rm -rf $(PROCESSED_DIR)/*.csv $(PROCESSED_DIR)/*.json
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

## reproduce: Limpa e reproduz tudo do zero
reproduce: clean all

## help: Mostra esta ajuda
help:
	@echo "Comandos disponíveis:"
	@echo ""
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## /  /'
	@echo ""
	@echo "Geradores individuais (run as Python modules):"
	@echo "  python -m src.assets.gen_sample_data"
	@echo "  python -m src.assets.gen_capm_analysis"
	@echo "  python -m src.assets.gen_fig_regression"
	@echo "  python -m src.assets.gen_fig_sml"
	@echo "  python -m src.assets.gen_fig_distribution"
	@echo "  python -m src.assets.gen_fig_correlation"
	@echo "  python -m src.assets.gen_table_statistics"
	@echo "  python -m src.assets.gen_table_results"
