# GitHub Copilot Instructions for UNB-CCA-MQAC

This repository implements a reproducible data analysis pipeline for generating a Technical Note (Nota Técnica) for the "Métodos Quantitativos em Contabilidade" course. It combines Python for analysis and Pandoc/LaTeX for document generation.

## 🏗 Project Architecture & Philosophy

### 1. Data as Interface (Crucial)
- **Strict Separation**: Modules communicate **exclusively** via files in the `data/` directory.
- **No In-Memory Passing**: Never pass large dataframes between scripts in memory. One script writes to disk, the next reads from disk.
- **Data Layers**:
  - `data/external/`: API data (Yahoo, BCB).
  - `data/raw/`: Immutable local raw data.
  - `data/processed/`: Cleaned intermediate data (CSV, JSON).
  - `data/outputs/`: Final assets for the report (Figures, Tables).

### 2. One File = One Output
- Scripts in `src/assets/` are "generators". Each script is responsible for creating **one specific artifact** (or a tightly coupled set).
- **Naming Convention**: `gen_<artifact_type>_<name>.py` (e.g., `gen_fig_regression.py`, `gen_table_statistics.py`).
- **Execution**: Scripts are designed to be run as modules: `python -m src.assets.gen_fig_regression`.

## 🛠 Development Workflow

### Build & Run
- **Automation**: Use `make` for all high-level tasks.
  - `make all`: Run full pipeline (Data -> Analysis -> Assets -> PDF).
  - `make data`: Generate/fetch data.
  - `make analysis`: Run CAPM/statistical models.
  - `make figures` / `make tables`: Generate visual assets.
  - `make pdf`: Compile the final document.
- **Python Execution**: Always run scripts from the project root using the module syntax:
  ```bash
  python -m src.assets.gen_capm_analysis
  ```

### Configuration
- **Parameters**: Model parameters (Rf, Rm, Beta) are in `configs/params.yaml`. **Never hardcode these values.**
- **Environment**: API keys and paths are managed in `src/core/config.py` (loading from `.env`).
- **Usage**:
  ```python
  from src.core.config import settings
  # Use settings.brapi_token, etc.
  ```

## 💻 Coding Standards

### Python
- **Paths**: Always use `pathlib.Path`. Use `src.core.config.PROJECT_ROOT` to resolve absolute paths.
- **Typing**: Use Python type hints (`typing`) for all function signatures.
- **Libraries**:
  - Data: `pandas`, `numpy`
  - Stats: `statsmodels`, `scipy`
  - Plotting: `matplotlib`, `seaborn` (use `src.core.style` for consistent theming)
- **Docstrings**: Include docstrings for all modules and functions.

### LaTeX / Markdown
- **Content**: Write text in `content/nota-tecnica.md`.
- **References**: Use BibTeX in `references.bib`.
- **Templating**: LaTeX templates are in `templates/`.

## ⚠️ Common Pitfalls
- **Do not** modify `data/raw/` manually.
- **Do not** hardcode file paths. Use `src.core.config` or relative paths from `data/`.
- **Do not** commit large files in `data/` (check `.gitignore`).
- Ensure `requirements.txt` or `pyproject.toml` is updated when adding dependencies.
