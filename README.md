# UnB CCA - Métodos Quantitativos em Contabilidade (MQC)
## Pipeline de Análise de Eficiência Informacional e Valuation (Q-VAL)

Este documento técnico descreve a arquitetura, instalação e operação do pipeline de análise de dados desenvolvido para a disciplina de Métodos Quantitativos em Contabilidade da Universidade de Brasília (UnB).

O projeto implementa um framework reprodutível para testar a Hipótese dos Mercados Eficientes (EMH) contra estratégias fundamentalistas estruturadas, utilizando a Petrobras (PETR4) como estudo de caso empírico.

---

## 1. Visão Geral do Projeto

### 1.1 Objetivo Científico
O objetivo central deste trabalho é quantificar a contribuição marginal da análise fundamentalista na explicação dos retornos de ativos financeiros. A investigação responde à seguinte questão de pesquisa:

> "A incorporação de métricas fundamentalistas estruturadas (Score Q-VAL) em modelos de precificação resulta em ganho estatisticamente significativo de poder explicativo e capacidade preditiva em relação aos modelos de mercado tradicionais?"

### 1.2 Metodologia
A abordagem metodológica baseia-se na estimação de modelos econométricos aninhados (Nested Models), variando do Random Walk (M0) até modelos de Machine Learning com fatores macroeconômicos e fundamentalistas (M5). O diferencial é a construção do **Score Q-VAL**, um indicador sintético que agrega dimensões de Valor, Qualidade e Risco.

---

## 2. Arquitetura do Sistema

O sistema foi projetado seguindo o padrão de arquitetura **"Data as Interface"**, priorizando a reprodutibilidade, auditabilidade e desacoplamento de componentes.

### 2.1 Princípios de Design
1.  **Imutabilidade dos Dados Brutos**: Os dados originais (`data/raw`) são preservados em estado de leitura ("read-only") para garantir a integridade da fonte.
2.  **Desacoplamento via Sistema de Arquivos**: Módulos de processamento não compartilham memória. A comunicação entre etapas ocorre exclusivamente através de arquivos serializados (Parquet/JSON) em disco.
3.  **Orquestração Declarativa**: Todo o fluxo de trabalho, desde a ingestão de dados até a compilação do documento final, é definido e gerenciado via `GNU Make`.
4.  **Idempotência**: A execução repetida do pipeline produz resultados determinísticos e idênticos.

### 2.2 Estrutura de Diretórios

```plaintext
unb-cca-mqac/
├── configs/                # Arquivos de configuração (YAML) e parâmetros globais
├── content/                # Código-fonte do texto da Nota Técnica (Markdown)
├── data/                   # Camada de persistência de dados
│   ├── external/           # Dados obtidos via API (Yahoo Finance, BCB)
│   ├── raw/                # Dados brutos locais (Demonstrações Financeiras)
│   ├── processed/          # Dados transformados e limpos (Parquet)
│   └── outputs/            # Artefatos finais (Tabelas, Figuras, Modelos)
├── docs/                   # Documentação técnica e roteiros de pesquisa
├── src/                    # Código-fonte da aplicação
│   ├── analysis/           # Motores de inferência e modelagem estatística
│   ├── assets/             # Geradores de artefatos visuais (1 script = 1 asset)
│   ├── core/               # Bibliotecas compartilhadas e utilitários
│   └── processing/         # Pipelines de ETL e engenharia de features
├── templates/              # Templates LaTeX para formatação ABNT
├── Makefile                # Arquivo de orquestração de build
├── pyproject.toml          # Definição de dependências e metadados do projeto
└── README.md               # Documentação principal
```

---

## 3. Requisitos do Sistema

Para garantir a execução correta do pipeline, o ambiente de desenvolvimento deve atender aos seguintes requisitos de software.

### 3.1 Dependências de Sistema (Nível OS)

O projeto depende de ferramentas de compilação e processamento de texto que devem ser instaladas no nível do sistema operacional.

#### Linux (Debian/Ubuntu)
```bash
sudo apt-get update
sudo apt-get install -y make python3-venv python3-pip pandoc texlive-full
```

#### macOS (via Homebrew)
```bash
brew install make pandoc basictex
# Recomendado instalar pacotes LaTeX completos via MacTeX se necessário
```

#### Windows
Recomenda-se a utilização do **WSL2 (Windows Subsystem for Linux)** com Ubuntu para garantir compatibilidade total com o `Makefile`. Caso utilize Windows nativo:
1.  Instalar Python 3.10+.
2.  Instalar `Make` via Chocolatey (`choco install make`).
3.  Instalar Pandoc (`choco install pandoc`).
4.  Instalar MiKTeX ou TeX Live.

### 3.2 Dependências Python
O projeto requer **Python 3.10** ou superior. As bibliotecas Python são gerenciadas via `pip` e isoladas em um ambiente virtual.

Principais bibliotecas utilizadas:
-   **Análise de Dados**: `pandas`, `numpy`, `scipy`
-   **Econometria e ML**: `statsmodels`, `scikit-learn`, `xgboost`
-   **Visualização**: `matplotlib`, `seaborn`
-   **Infraestrutura**: `pyarrow` (Parquet), `pyyaml`, `python-dotenv`

---

## 4. Guia de Instalação e Execução

Siga este roteiro passo-a-passo para configurar o ambiente e executar o pipeline completo.

### Passo 1: Clonagem do Repositório

Obtenha o código-fonte através do sistema de controle de versão:

```bash
git clone https://github.com/seu-usuario/unb-cca-mqac.git
cd unb-cca-mqac
```

### Passo 2: Configuração do Ambiente Virtual

Crie um ambiente isolado para evitar conflitos de dependências:

```bash
# Criação do ambiente virtual no diretório .venv
python3 -m venv .venv

# Ativação do ambiente
source .venv/bin/activate
```

### Passo 3: Instalação de Pacotes

Instale o projeto em modo editável (`-e`), o que permite que alterações no código sejam refletidas imediatamente sem necessidade de reinstalação:

```bash
pip install -e .
```

### Passo 4: Execução do Pipeline (Build)

O projeto utiliza o `Make` para automatizar todo o processo. O comando abaixo executará sequencialmente:
1.  Verificação e processamento de dados.
2.  Treinamento dos modelos (M0 a M5).
3.  Geração de figuras e tabelas.
4.  Compilação do documento final em PDF.

```bash
make all
```

**Nota**: A primeira execução pode levar alguns minutos devido ao treinamento dos modelos de Machine Learning e compilação do LaTeX.

---

## 5. Comandos de Operação (Makefile)

A tabela abaixo detalha os alvos disponíveis no `Makefile` para operações granulares.

| Comando | Descrição Técnica | Artefatos Gerados |
| :--- | :--- | :--- |
| `make all` | **Execução Completa.** Orquestra todo o fluxo de trabalho. | `output/nota-tecnica.pdf` |
| `make data` | **ETL.** Processa dados brutos e calcula indicadores. | `data/processed/*.parquet` |
| `make analysis` | **Modelagem.** Executa scripts de regressão e ML. | `data/outputs/*.json`, `*.parquet` |
| `make figures` | **Visualização.** Gera gráficos vetoriais e estáticos. | `data/outputs/figures/*.pdf` |
| `make tables` | **Tabulação.** Gera tabelas em formato LaTeX. | `data/outputs/tables/*.tex` |
| `make pdf` | **Compilação.** Converte Markdown/LaTeX para PDF. | `output/nota-tecnica.pdf` |
| `make clean` | **Limpeza.** Remove todos os artefatos gerados. | *N/A* |

---

## 6. Detalhamento dos Modelos (Roadmap de Pesquisa)

O pipeline implementa uma estratégia de **comparação de modelos aninhados**, permitindo isolar o efeito marginal de cada grupo de variáveis.

### M0: Benchmarks Naïve
-   **M0_RW (Random Walk)**: Previsão baseada no último preço ($P_{t+1} = P_t$).
-   **M0_Mean (Média Histórica)**: Previsão baseada na média incondicional dos retornos.

### M1: Modelo de Mercado (CAPM Estático)
-   Regressão linear simples dos retornos do ativo contra o prêmio de risco de mercado.
-   $R_i - R_f = \alpha + \beta(R_m - R_f) + \epsilon$

### M2: CAPM Dinâmico (Time-Varying Beta)
-   Extensão do M1 utilizando **Rolling OLS** (Janela móvel de 252 dias).
-   Captura a natureza variante no tempo do risco sistemático.

### M3: Modelo Fundamentalista (Q-VAL)
-   Incorpora o **Score Q-VAL** como fator explicativo adicional.
-   Testa a hipótese de que fundamentos contábeis contêm informação não precificada pelo Beta.

### M4: Modelo Macroeconômico
-   Adiciona variáveis de controle exógenas: Petróleo Brent, Taxa de Câmbio (USD/BRL) e Risco País (EMBI+).

### M5: Síntese e Machine Learning
-   **M5_Linear**: Modelo linear irrestrito com todas as variáveis.
-   **M5_ML (XGBoost)**: Modelo não-linear para capturar interações complexas entre fundamentos e macroeconomia.

---

**Universidade de Brasília (UnB)**
Departamento de Ciências Contábeis e Atuariais (CCA)
*Disciplina: Métodos Quantitativos em Contabilidade*
