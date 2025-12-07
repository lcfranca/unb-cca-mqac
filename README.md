# UnB CCA - Projeto Pivotado (Q-VAL / Eficiência Informacional)

Este repositório está em fase de pivotagem para implementar a análise descrita em `docs/ROTEIRO_PIVOT_INFORMACAO.md` e `docs/roteiro-resultados.md`, focando na eficiência informacional das métricas fundamentalistas (Q-VAL) para PETR4.

## Estado atual
- Artefatos legados e scripts de assets antigos foram removidos.
- Diretórios vazios criados para o novo pipeline:
  - `src/data`, `src/processing`, `src/models`, `src/analysis`, `src/outputs`.
- `Makefile` é um stub com alvos `data`, `process`, `models`, `analysis`, `outputs` (a implementar).
- Dependências atualizadas em `pyproject.toml` para uso de Parquet (`pyarrow`), requisições (`requests`), e variáveis de ambiente (`python-dotenv`).
- Notebooks legados arquivados em `notebooks/legacy/`.

## Estrutura (pivot)
```
unb-cca-mqac/
├── content/                # Nota técnica (Markdown)
├── configs/                # Parâmetros de execução
├── data/                   # Interface entre módulos (camadas)
│   ├── external/           # Coletas brutas (limpo no momento)
│   ├── processed/          # Intermediários (.parquet/.json)
│   ├── outputs/            # Tabelas/Figuras finais
│   └── raw/                # Dados imutáveis (não alterar manualmente)
├── docs/                   # Roteiros e especificações
├── notebooks/legacy/       # Notebooks antigos (apenas referência)
├── src/
│   ├── data/               # Coleta (a criar)
│   ├── processing/         # Processamento (a criar)
│   ├── models/             # Estimação de modelos (a criar)
│   ├── analysis/           # Análises derivadas (a criar)
│   └── outputs/            # Geração de tabelas/figuras (a criar)
├── templates/              # Templates LaTeX/ABNT (manter)
├── Makefile                # Stub do novo pipeline
├── pyproject.toml          # Dependências e metadata
└── README.md
```

## Próximos passos (resumo do roteiro)
1) Implementar coleta (`src/data/*`): preços PETR4, Ibovespa, CDI (BCB), fundamentals BRAPI.
2) Implementar processamento (`src/processing/*`): retornos, métricas, z-score histórico, série Q-VAL.
3) Modelos (`src/models/*`): CAPM (M0) e modelos M1–M3; comparação e testes.
4) Análises (`src/analysis/*`): estatísticas descritivas, R² rolling, validação OOS.
5) Outputs (`src/outputs/*`): tabelas e figuras da Seção 5.
6) Atualizar `Makefile` com os novos alvos concretos quando os scripts estiverem prontos.

## Como instalar dependências
```bash
pip install -e .
```

## Referências
- `docs/ROTEIRO_PIVOT_INFORMACAO.md`
- `docs/roteiro-resultados.md`# UnB CCA - Métodos Quantitativos em Contabilidade (MQC)

Template para elaboração de **Nota Técnica** da disciplina MQC do Departamento de Ciências Contábeis e Atuariais da Universidade de Brasília.

**Formatação conforme ABNT NBR 14724:2011** (Trabalhos Acadêmicos)

## Estrutura do Projeto

```
unb-cca-mqac/
├── 📝 content/                    # WORKLOAD PRINCIPAL
│   └── nota-tecnica.md            # Documento editável (Markdown)
│
├── 📊 src/                        # Código fonte
│   ├── core/                      # Módulos compartilhados
│   │   ├── config.py              # Configuração e caminhos
│   │   ├── io.py                  # Input/Output de dados
│   │   ├── analysis.py            # Funções de análise
│   │   └── plotting.py            # Estilo de plots
│   └── assets/                    # Geradores de assets (1 arquivo = 1 output)
│       ├── gen_sample_data.py     # → data/processed/returns.csv
│       ├── gen_capm_analysis.py   # → data/processed/capm_results.json
│       ├── gen_fig_regression.py  # → data/outputs/figures/regressao_beta.pdf
│       ├── gen_fig_sml.py         # → data/outputs/figures/sml_capm.pdf
│       ├── gen_fig_distribution.py# → data/outputs/figures/distribuicao_retornos.pdf
│       ├── gen_fig_correlation.py # → data/outputs/figures/correlacao.pdf
│       ├── gen_table_statistics.py# → data/outputs/tables/estatisticas_descritivas.tex
│       └── gen_table_results.py   # → data/outputs/tables/resultados_capm.tex
│
├── 📁 data/                       # Camada de dados (toda comunicação via arquivos)
│   ├── external/                  # Dados de APIs (Yahoo, BCB, etc.)
│   ├── raw/                       # Dados brutos locais (imutáveis)
│   ├── processed/                 # Dados intermediários (CSV, JSON)
│   └── outputs/                   # Assets finais
│       ├── figures/               # Figuras (PDF, PNG)
│       └── tables/                # Tabelas LaTeX (.tex)
│
├── ⚙️ configs/
│   └── params.yaml                # Parâmetros do modelo
│
├── 📄 templates/                  # Templates LaTeX ABNT
│   ├── preamble.tex
│   ├── titlepage.tex
│   ├── authorities.tex
│   ├── headings.tex
│   └── toc.tex
│
├── 🧪 tests/                      # Testes unitários
├── 📤 output/                     # PDF final
│   └── nota-tecnica.pdf
│
├── Makefile                       # Automação
├── pyproject.toml                 # Dependências Python
├── metadata.yaml                  # Metadados do documento
├── defaults.yaml                  # Config Pandoc
├── pdf.yaml                       # Config saída PDF
├── template.tex                   # Template principal
└── references.bib                 # Bibliografia
```

## Princípios de Design

### 1. Dados como Interface

**Toda comunicação entre módulos é via arquivos em `data/`.**

```
src/assets/gen_sample_data.py  →  data/processed/returns.csv
                                        ↓
src/assets/gen_capm_analysis.py  →  data/processed/capm_results.json
                                        ↓
src/assets/gen_fig_regression.py  →  data/outputs/figures/regressao_beta.pdf
```

- Nenhum dado é gerado dentro do código (hardcoded)
- Todos os dados intermediários são persistidos
- Facilita debugging e reprodutibilidade

### 2. Um Arquivo = Um Output

Cada gerador em `src/assets/` produz exatamente um asset:

| Gerador | Output |
|---------|--------|
| `gen_sample_data.py` | `data/processed/returns.csv` |
| `gen_capm_analysis.py` | `data/processed/capm_results.json` |
| `gen_fig_regression.py` | `data/outputs/figures/regressao_beta.pdf` |
| `gen_fig_sml.py` | `data/outputs/figures/sml_capm.pdf` |
| `gen_fig_distribution.py` | `data/outputs/figures/distribuicao_retornos.pdf` |
| `gen_fig_correlation.py` | `data/outputs/figures/correlacao.pdf` |
| `gen_table_statistics.py` | `data/outputs/tables/estatisticas_descritivas.tex` |
| `gen_table_results.py` | `data/outputs/tables/resultados_capm.tex` |

Execute individualmente:
```bash
python -m src.assets.gen_fig_regression
```

### 3. Camadas de Dados

| Camada | Propósito | Exemplo |
|--------|-----------|---------|
| `data/external/` | APIs externas | Yahoo Finance, BCB |
| `data/raw/` | Dados brutos (imutáveis) | CSVs originais |
| `data/processed/` | Dados intermediários | `returns.csv`, `capm_results.json` |
| `data/outputs/` | Assets finais | PDFs, tabelas .tex |

## Início Rápido

### 1. Instalar Dependências

```bash
# Python
pip install -e .

# Sistema (Ubuntu/Debian)
sudo apt install pandoc texlive-full
```

### 2. Executar Pipeline Completo

```bash
make all
```

Ou passo a passo:

```bash
make data       # Gera dados simulados
make analysis   # Executa análise CAPM
make figures    # Gera todas as figuras
make tables     # Gera todas as tabelas
make pdf        # Compila PDF
```

### 3. Executar Geradores Individualmente

```bash
# Via VS Code: abra o arquivo e clique "Run Python File"
# Ou via terminal:
python -m src.assets.gen_fig_sml
```

## Configuração

Edite `configs/params.yaml`:

```yaml
model:
  rf: 0.0525        # Taxa livre de risco (Selic)
  rm: 0.12          # Retorno do mercado (Ibovespa)
  beta_true: 1.15   # Beta para simulação

data:
  n_periods: 24     # Meses
  seed: 42          # Reprodutibilidade
  source: "simulated"  # ou "yahoo", "bcb", "csv"
```

## Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────────────┐
│                        configs/params.yaml                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  gen_sample_data.py  ──────────►  data/processed/returns.csv        │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  gen_capm_analysis.py  ────────►  data/processed/capm_results.json  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ gen_fig_*.py    │    │ gen_table_*.py  │    │ nota-tecnica.md │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ figures/*.pdf   │    │ tables/*.tex    │    │  pandoc/latex   │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┴──────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │ output/nota-tecnica │
                    │        .pdf         │
                    └─────────────────────┘
```

## Comandos Make

| Comando | Descrição |
|---------|-----------|
| `make all` | Pipeline completo |
| `make data` | Gera dados simulados |
| `make analysis` | Executa análise CAPM |
| `make figures` | Gera todas as figuras |
| `make tables` | Gera todas as tabelas |
| `make pdf` | Compila PDF |
| `make clean` | Remove artefatos |
| `make reproduce` | Limpa e reproduz tudo |
| `make help` | Mostra ajuda |

## Uso no Documento

### Figuras

```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.70\textwidth]{data/outputs/figures/regressao_beta.pdf}
\caption{Estimação do Beta}
\label{fig:regressao_beta}
\end{figure}
```

### Tabelas

```latex
\input{data/outputs/tables/estatisticas_descritivas.tex}
```

## Padrões ABNT Implementados

| Elemento | Especificação ABNT |
|----------|-------------------|
| Fonte | Times New Roman (TeX Gyre Termes) |
| Tamanho | 12pt |
| Margens | Superior/Esquerda: 3cm, Inferior/Direita: 2cm |
| Espaçamento | 1,5 entre linhas |
| Recuo | 1,25cm para parágrafos |
| Seções | Numeração progressiva (NBR 6024:2012) |
| Sumário | Conforme NBR 6027:2012 |

## Autor

**Lucas Coelho França**  
Universidade de Brasília (UnB)  
Departamento de Ciências Contábeis e Atuariais (CCA)
