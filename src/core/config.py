"""
Configuração Centralizada do Projeto Q-VAL.

Este módulo é o ÚNICO ponto de configuração para variáveis do projeto.
Todas as configurações são injetadas externamente via:
  1. Arquivo .env (credenciais e URLs de API)
  2. Notebook centralizador (variáveis de análise)

NENHUMA variável de configuração deve ser definida hardcoded nos scripts.
Os módulos em src/ devem APENAS consumir configurações deste módulo.
"""

import os
import json
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv


# =============================================================================
# DETECÇÃO DE RAIZ E CARREGAMENTO DO .ENV
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
env_path = PROJECT_ROOT / ".env"
if not env_path.exists():
    import warnings
    warnings.warn(f"Arquivo .env não encontrado em {env_path}. Usando valores padrão/ambiente.", UserWarning)

load_dotenv(env_path)
ANALYSIS_OVERRIDE_PATH = PROJECT_ROOT / "configs" / "analysis_overrides.json"


# =============================================================================
# CONFIGURAÇÕES DE AMBIENTE (LIDAS DO .ENV)
# =============================================================================

@dataclass
class EnvConfig:
    """Configurações carregadas do arquivo .env"""
    
    # Brapi (Primário)
    brapi_base_url: str = "https://brapi.dev/api"
    brapi_token: str = ""  # Vazio = sem auth (ações de teste)
    
    # Yahoo Finance (Fallback)
    yahoo_finance_enabled: bool = True
    
    # BCB
    bcb_sgs_base_url: str = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"
    
    # CVM
    cvm_base_url: str = "https://dados.cvm.gov.br/dados"
    
    # Ambiente
    environment: str = "development"
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "EnvConfig":
        """Carrega configurações do ambiente."""
        return cls(
            brapi_base_url=os.getenv("BRAPI_BASE_URL", cls.brapi_base_url),
            brapi_token=os.getenv("BRAPI_TOKEN", ""),
            yahoo_finance_enabled=os.getenv("YAHOO_FINANCE_ENABLED", "true").lower() == "true",
            bcb_sgs_base_url=os.getenv("BCB_SGS_BASE_URL", cls.bcb_sgs_base_url),
            cvm_base_url=os.getenv("CVM_BASE_URL", cls.cvm_base_url),
            environment=os.getenv("ENVIRONMENT", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def validate(self):
        """Valida configurações críticas."""
        if not self.brapi_token:
            import warnings
            warnings.warn("BRAPI_TOKEN não configurado. Acesso à API Brapi pode ser limitado.", UserWarning)
        return self


# =============================================================================
# CAMINHOS DO PROJETO
# =============================================================================

@dataclass
class ProjectPaths:
    """Caminhos padronizados do projeto."""
    
    root: Path = field(default_factory=lambda: PROJECT_ROOT)
    
    # -------------------------------------------------------------------------
    # DADOS RAW (dados locais brutos, não de APIs)
    # -------------------------------------------------------------------------
    @property
    def data_raw(self) -> Path:
        return self.root / "data" / "raw"
    
    # -------------------------------------------------------------------------
    # DADOS PROCESSED (dados processados/derivados)
    # -------------------------------------------------------------------------
    @property
    def data_processed(self) -> Path:
        return self.root / "data" / "processed"
    
    # -------------------------------------------------------------------------
    # DADOS EXTERNAL (dados brutos de APIs externas)
    # -------------------------------------------------------------------------
    @property
    def data_external(self) -> Path:
        return self.root / "data" / "external"
    
    @property
    def external_brapi(self) -> Path:
        """Dados brutos da Brapi API (fonte primária)."""
        return self.data_external / "brapi"
    
    @property
    def external_yahoo(self) -> Path:
        """Dados brutos do Yahoo Finance (fallback)."""
        return self.data_external / "yahoo_finance"
    
    @property
    def external_bcb(self) -> Path:
        """Dados brutos do BCB SGS."""
        return self.data_external / "bcb"
    
    @property
    def external_cvm(self) -> Path:
        """Dados brutos da CVM (DFP, ITR)."""
        return self.data_external / "cvm"
    
    @property
    def external_bacen(self) -> Path:
        """Dados brutos do BACEN IF.data (instituições financeiras)."""
        return self.data_external / "bacen"
    
    # -------------------------------------------------------------------------
    # OUTPUTS
    # -------------------------------------------------------------------------
    @property
    def figures(self) -> Path:
        return self.root / "data" / "outputs" / "figures"
    
    @property
    def tables(self) -> Path:
        return self.root / "data" / "outputs" / "tables"
    
    # -------------------------------------------------------------------------
    # OUTROS
    # -------------------------------------------------------------------------
    @property
    def config_yaml(self) -> Path:
        return self.root / "configs" / "params.yaml"
    
    @property
    def content(self) -> Path:
        return self.root / "content"
    
    @property
    def output(self) -> Path:
        return self.root / "output"
    
    @property
    def docs(self) -> Path:
        return self.root / "docs"
    
    def ensure_dirs(self) -> None:
        """Cria todos os diretórios necessários."""
        dirs = [
            self.data_raw,
            self.data_processed,
            self.data_external,
            self.external_brapi,
            self.external_yahoo,
            self.external_bcb,
            self.external_cvm,
            self.external_bacen,
            self.figures,
            self.tables,
            self.output,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)


# =============================================================================
# CONFIGURAÇÕES DE ANÁLISE (INJETADAS VIA NOTEBOOK)
# =============================================================================

@dataclass
class AnalysisConfig:
    """
    Configurações de análise - DEVEM SER INJETADAS VIA NOTEBOOK.
    
    Este dataclass armazena todas as variáveis configuráveis da análise.
    Os valores default são apenas placeholders - a configuração real
    deve vir do notebook centralizador.
    """
    
    # -------------------------------------------------------------------------
    # ATIVOS
    # -------------------------------------------------------------------------
    ticker_principal: str = "PETR4.SA"           # Ativo em análise
    ticker_mercado: str = "^BVSP"                 # Benchmark de mercado
    tickers_pares: List[str] = field(default_factory=lambda: [
        "PRIO3.SA", "CSAN3.SA", "RECV3.SA"
    ])
    
    # -------------------------------------------------------------------------
    # PERÍODO DE ANÁLISE
    # -------------------------------------------------------------------------
    data_inicio: str = "2016-01-01"              # Início da série
    data_fim: str = "2025-11-30"                  # Fim da série
    janela_beta_meses: int = 60                   # Janela para estimação do beta
    
    # -------------------------------------------------------------------------
    # PARÂMETROS DE MERCADO
    # -------------------------------------------------------------------------
    taxa_livre_risco: Optional[float] = None     # Deve ser obtido via API (CDI/Selic)
    premio_risco_mercado: Optional[float] = None # Deve ser calculado (Rm - Rf)
    premio_risco_pais: Optional[float] = None    # Deve ser obtido via API (EMBI+)
    
    # -------------------------------------------------------------------------
    # MÉTRICAS FUNDAMENTALISTAS (DADOS MANUAIS OU API)
    # -------------------------------------------------------------------------
    roace_atual: Optional[float] = None          # Deve ser obtido via API
    pl_atual: Optional[float] = None             # Deve ser obtido via API
    ev_ebitda_atual: Optional[float] = None      # Deve ser obtido via API
    dividend_yield: Optional[float] = None       # Deve ser obtido via API
    margem_ebitda: Optional[float] = None        # Deve ser obtido via API
    rp_ratio: Optional[float] = None             # Deve ser obtido via API
    
    # -------------------------------------------------------------------------
    # PONDERAÇÃO DO SCORE
    # -------------------------------------------------------------------------
    peso_valor: float = 0.30
    peso_qualidade: float = 0.40
    peso_risco: float = 0.30
    
    # -------------------------------------------------------------------------
    # OUTPUT
    # -------------------------------------------------------------------------
    formatos_figura: List[str] = field(default_factory=lambda: ["pdf", "png"])
    dpi: int = 300
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "ticker_principal": self.ticker_principal,
            "ticker_mercado": self.ticker_mercado,
            "tickers_pares": self.tickers_pares,
            "data_inicio": self.data_inicio,
            "data_fim": self.data_fim,
            "janela_beta_meses": self.janela_beta_meses,
            "taxa_livre_risco": self.taxa_livre_risco,
            "premio_risco_mercado": self.premio_risco_mercado,
            "premio_risco_pais": self.premio_risco_pais,
            "roace_atual": self.roace_atual,
            "pl_atual": self.pl_atual,
            "ev_ebitda_atual": self.ev_ebitda_atual,
            "dividend_yield": self.dividend_yield,
            "margem_ebitda": self.margem_ebitda,
            "rp_ratio": self.rp_ratio,
            "peso_valor": self.peso_valor,
            "peso_qualidade": self.peso_qualidade,
            "peso_risco": self.peso_risco,
        }


# =============================================================================
# SINGLETON DE CONFIGURAÇÃO GLOBAL
# =============================================================================

class Config:
    """
    Configuração global do projeto (Singleton).
    
    Uso:
        from src.core.config import Config
        
        cfg = Config()
        cfg.analysis.ticker_principal  # Acessa ticker configurado
        cfg.paths.data_processed       # Acessa caminho de dados
        cfg.env.bcb_sgs_base_url       # Acessa URL da API
    """
    
    _instance: Optional["Config"] = None
    
    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Inicializa configurações."""
        self._env = EnvConfig.from_env().validate()
        self._paths = ProjectPaths()
        self._analysis = AnalysisConfig()
        self._paths.ensure_dirs()
        self._load_analysis_overrides()
    
    @property
    def env(self) -> EnvConfig:
        """Configurações de ambiente (.env)."""
        return self._env
    
    @property
    def paths(self) -> ProjectPaths:
        """Caminhos do projeto."""
        return self._paths
    
    @property
    def analysis(self) -> AnalysisConfig:
        """Configurações de análise."""
        return self._analysis
    
    def set_analysis(self, config: AnalysisConfig) -> None:
        """
        Injeta configurações de análise.
        
        Este método deve ser chamado pelo notebook centralizador
        para definir as variáveis de análise.
        """
        self._analysis = config
    
    def update_analysis(self, **kwargs) -> None:
        """
        Atualiza configurações de análise individualmente.
        
        Exemplo:
            cfg.update_analysis(ticker_principal="PETR4.SA", data_inicio="2019-01-01")
        """
        for key, value in kwargs.items():
            if hasattr(self._analysis, key):
                setattr(self._analysis, key, value)
            else:
                raise ValueError(f"Configuração desconhecida: {key}")
    
    def reset(self) -> None:
        """Reseta para configurações default."""
        self._initialize()

    def _load_analysis_overrides(self) -> None:
        """Carrega overrides de análise a partir de arquivo JSON, se existir."""
        if not ANALYSIS_OVERRIDE_PATH.exists():
            return
        try:
            data = json.loads(ANALYSIS_OVERRIDE_PATH.read_text())
            for key, value in data.items():
                if hasattr(self._analysis, key):
                    setattr(self._analysis, key, value)
        except Exception:
            pass

    def save_analysis_overrides(self, data: Dict[str, Any]) -> None:
        """Persiste overrides de análise para uso posterior."""
        ANALYSIS_OVERRIDE_PATH.parent.mkdir(parents=True, exist_ok=True)
        ANALYSIS_OVERRIDE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# =============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# =============================================================================

def get_config() -> Config:
    """Retorna instância singleton da configuração."""
    return Config()


def get_paths() -> ProjectPaths:
    """Atalho para obter caminhos."""
    return Config().paths


def get_analysis() -> AnalysisConfig:
    """Atalho para obter configurações de análise."""
    return Config().analysis

def load_params() -> Dict[str, Any]:
    """Carrega parâmetros do arquivo params.yaml."""
    path = PROJECT_ROOT / "configs" / "params.yaml"
    if path.exists():
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    return {}
