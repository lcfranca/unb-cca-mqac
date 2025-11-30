"""
Módulo de Coleta de Dados da CVM (Comissão de Valores Mobiliários).

Este módulo baixa e processa DFPs (Demonstrações Financeiras Padronizadas)
diretamente do portal dados.cvm.gov.br.

Fontes:
    - DFP: Demonstrações Financeiras Padronizadas (anuais)
    - ITR: Informações Trimestrais (trimestrais)

IMPORTANTE: Este módulo é um PIPELINE - não deve conter configurações hardcoded.
Todas as variáveis devem vir do módulo config.py que é configurado via notebook.
"""

import io
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.core.config import Config, get_config


# =============================================================================
# CONFIGURAÇÃO DE LOGGING
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTES E MAPEAMENTOS
# =============================================================================

# Códigos CVM de empresas relevantes
CVM_CODES = {
    "PETR4": 9512,    # Petrobras
    "PETR3": 9512,    # Petrobras ON
    "PRIO3": 24295,   # PetroRio
    "CSAN3": 19836,   # Cosan
    "RECV3": 25607,   # PetroRecôncavo
    "VALE3": 4170,    # Vale (alternativa)
}

# Tipos de documentos disponíveis
DOC_TYPES = {
    "BPA": "Balanço Patrimonial Ativo",
    "BPP": "Balanço Patrimonial Passivo",
    "DRE": "Demonstração de Resultado",
    "DFC_MI": "Demonstração de Fluxo de Caixa (Método Indireto)",
    "DFC_MD": "Demonstração de Fluxo de Caixa (Método Direto)",
    "DVA": "Demonstração de Valor Adicionado",
    "DMPL": "Demonstração de Mutações do Patrimônio Líquido",
}

# Contas contábeis relevantes para bancos (códigos IFRS)
CONTAS_RELEVANTES = {
    # Balanço Patrimonial Ativo (BPA)
    "1": "Ativo Total",
    "1.01": "Ativo Circulante",
    "1.02": "Ativo Não Circulante",
    
    # Balanço Patrimonial Passivo (BPP)
    "2": "Passivo Total",
    "2.01": "Passivo Circulante",
    "2.02": "Passivo Não Circulante",
    "2.03": "Patrimônio Líquido Consolidado",
    
    # DRE
    "3.01": "Receita de Intermediação Financeira",
    "3.02": "Despesas de Intermediação Financeira",
    "3.03": "Resultado Bruto Intermediação Financeira",
    "3.04": "Outras Receitas/Despesas Operacionais",
    "3.05": "Resultado Antes dos Tributos",
    "3.06": "Imposto de Renda e CSLL",
    "3.07": "Lucro/Prejuízo do Período",
    "3.09": "Lucro por Ação",
}


# =============================================================================
# CVM DATA LOADER
# =============================================================================

class CVMLoader:
    """
    Carregador de dados da CVM.
    
    Baixa e processa DFPs (Demonstrações Financeiras Padronizadas)
    diretamente do portal dados.cvm.gov.br.
    
    Exemplo:
        loader = CVMLoader()
        df = loader.fetch_financial_history(cvm_code=1023, start_year=2014)
    """
    
    BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC"
    
    def __init__(self, config: Optional[Config] = None):
        """
        Inicializa o loader.
        
        Args:
            config: Configuração do projeto. Se não fornecida, usa singleton.
        """
        self.config = config or get_config()
        self.cache_dir = self.config.paths.external_cvm
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar sessão HTTP com retry
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Cria sessão HTTP com retry automático."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    # -------------------------------------------------------------------------
    # DOWNLOAD
    # -------------------------------------------------------------------------
    
    def download_dfp(self, year: int, force: bool = False) -> Path:
        """
        Baixa arquivo ZIP do DFP de um ano específico.
        
        Args:
            year: Ano do DFP (ex: 2024).
            force: Se True, baixa mesmo se já existir em cache.
            
        Returns:
            Path do arquivo ZIP baixado.
        """
        filename = f"dfp_cia_aberta_{year}.zip"
        cache_path = self.cache_dir / filename
        
        # Verificar cache
        if cache_path.exists() and not force:
            logger.info(f"Usando cache: {cache_path}")
            return cache_path
        
        # URL do arquivo
        url = f"{self.BASE_URL}/DFP/DADOS/{filename}"
        logger.info(f"Baixando DFP {year} de {url}")
        
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            # Salvar em cache
            cache_path.write_bytes(response.content)
            logger.info(f"Salvo em: {cache_path} ({len(response.content) / 1024 / 1024:.1f} MB)")
            
            return cache_path
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"DFP {year} não encontrado (404)")
                raise FileNotFoundError(f"DFP {year} não disponível na CVM")
            raise
    
    def download_itr(self, year: int, force: bool = False) -> Path:
        """
        Baixa arquivo ZIP do ITR (trimestral) de um ano.
        
        Args:
            year: Ano do ITR.
            force: Se True, força redownload.
            
        Returns:
            Path do arquivo ZIP.
        """
        filename = f"itr_cia_aberta_{year}.zip"
        cache_path = self.cache_dir / filename
        
        if cache_path.exists() and not force:
            logger.info(f"Usando cache: {cache_path}")
            return cache_path
        
        url = f"{self.BASE_URL}/ITR/DADOS/{filename}"
        logger.info(f"Baixando ITR {year} de {url}")
        
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            cache_path.write_bytes(response.content)
            logger.info(f"Salvo em: {cache_path}")
            
            return cache_path
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise FileNotFoundError(f"ITR {year} não disponível")
            raise
    
    # -------------------------------------------------------------------------
    # EXTRAÇÃO E PARSING
    # -------------------------------------------------------------------------
    
    def extract_company(
        self,
        zip_path: Path,
        cvm_code: int,
        doc_types: Optional[List[str]] = None,
        consolidated: bool = True,
    ) -> Dict[str, pd.DataFrame]:
        """
        Extrai dados de uma empresa específica do ZIP.
        
        Args:
            zip_path: Caminho do arquivo ZIP.
            cvm_code: Código CVM da empresa (ex: 1023 para BB).
            doc_types: Lista de tipos de documento (ex: ['BPA', 'DRE']).
                      Se None, extrai BPA, BPP e DRE.
            consolidated: Se True, usa demonstrações consolidadas (_con_).
            
        Returns:
            Dicionário {tipo_doc: DataFrame} com os dados filtrados.
        """
        doc_types = doc_types or ["BPA", "BPP", "DRE"]
        suffix = "_con_" if consolidated else "_ind_"
        
        results = {}
        
        with zipfile.ZipFile(zip_path, "r") as zf:
            for doc_type in doc_types:
                # Encontrar arquivo correspondente
                pattern = f"dfp_cia_aberta_{doc_type}{suffix}"
                matching = [f for f in zf.namelist() if pattern.lower() in f.lower()]
                
                if not matching:
                    logger.warning(f"Documento {doc_type} não encontrado no ZIP")
                    continue
                
                csv_name = matching[0]
                logger.debug(f"Extraindo {csv_name}")
                
                # Ler CSV do ZIP
                with zf.open(csv_name) as f:
                    df = pd.read_csv(
                        f,
                        sep=";",
                        encoding="latin-1",
                        dtype={"CD_CVM": str, "CD_CONTA": str},
                    )
                
                # Filtrar por código CVM
                df["CD_CVM"] = df["CD_CVM"].astype(str).str.strip()
                df_company = df[df["CD_CVM"] == str(cvm_code)].copy()
                
                if df_company.empty:
                    logger.warning(f"Nenhum dado para CD_CVM={cvm_code} em {doc_type}")
                    continue
                
                # Limpar e padronizar
                df_company = self._clean_dataframe(df_company)
                results[doc_type] = df_company
                
                logger.info(f"Extraídos {len(df_company)} registros de {doc_type}")
        
        return results
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa e padroniza DataFrame extraído."""
        # Converter datas
        if "DT_REFER" in df.columns:
            df["DT_REFER"] = pd.to_datetime(df["DT_REFER"], errors="coerce")
        if "DT_FIM_EXERC" in df.columns:
            df["DT_FIM_EXERC"] = pd.to_datetime(df["DT_FIM_EXERC"], errors="coerce")
        
        # Converter valores numéricos
        if "VL_CONTA" in df.columns:
            df["VL_CONTA"] = pd.to_numeric(
                df["VL_CONTA"].astype(str).str.replace(",", "."),
                errors="coerce"
            )
        
        # Extrair ano
        if "DT_REFER" in df.columns:
            df["ANO"] = df["DT_REFER"].dt.year
        
        return df
    
    # -------------------------------------------------------------------------
    # PROCESSAMENTO DE HISTÓRICO
    # -------------------------------------------------------------------------
    
    def fetch_financial_history(
        self,
        cvm_code: int = 9512,
        start_year: int = 2014,
        end_year: Optional[int] = None,
        doc_types: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Obtém histórico completo de demonstrações financeiras.
        
        Args:
            cvm_code: Código CVM da empresa (default: 9512 = Petrobras).
            start_year: Ano inicial (default: 2014).
            end_year: Ano final (default: ano atual).
            doc_types: Tipos de documento a extrair.
            
        Returns:
            DataFrame consolidado com histórico financeiro.
        """
        end_year = end_year or datetime.now().year
        doc_types = doc_types or ["BPA", "BPP", "DRE"]
        
        all_data = {doc: [] for doc in doc_types}
        
        for year in range(start_year, end_year + 1):
            try:
                zip_path = self.download_dfp(year)
                year_data = self.extract_company(zip_path, cvm_code, doc_types)
                
                for doc_type, df in year_data.items():
                    if not df.empty:
                        all_data[doc_type].append(df)
                        
            except FileNotFoundError:
                logger.warning(f"DFP {year} não disponível, pulando...")
                continue
            except Exception as e:
                logger.error(f"Erro ao processar DFP {year}: {e}")
                continue
        
        # Concatenar todos os anos
        result = {}
        for doc_type, dfs in all_data.items():
            if dfs:
                result[doc_type] = pd.concat(dfs, ignore_index=True)
        
        # Consolidar em DataFrame único com métricas calculadas
        return self._consolidate_financials(result)
    
    def _consolidate_financials(
        self,
        data: Dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        """
        Consolida demonstrações em DataFrame com métricas calculadas.
        
        Args:
            data: Dicionário {tipo_doc: DataFrame}.
            
        Returns:
            DataFrame com métricas por ano.
        """
        if not data:
            return pd.DataFrame()
        
        # Extrair métricas de cada demonstração
        metrics = []
        
        # Anos disponíveis
        years = set()
        for df in data.values():
            if "ANO" in df.columns:
                years.update(df["ANO"].dropna().unique())
        
        for year in sorted(years):
            row = {"ano": int(year)}
            
            # BPA - Ativo Total
            if "BPA" in data:
                bpa = data["BPA"]
                bpa_year = bpa[bpa["ANO"] == year]
                
                # Ativo Total (código 1)
                ativo = bpa_year[bpa_year["CD_CONTA"] == "1"]
                if not ativo.empty:
                    row["ativo_total"] = ativo["VL_CONTA"].iloc[-1]
            
            # BPP - Patrimônio Líquido e Passivo
            if "BPP" in data:
                bpp = data["BPP"]
                bpp_year = bpp[bpp["ANO"] == year]
                
                # Patrimônio Líquido (código 2.03)
                pl = bpp_year[bpp_year["CD_CONTA"].str.startswith("2.03")]
                if not pl.empty:
                    row["patrimonio_liquido"] = pl["VL_CONTA"].iloc[-1]
                
                # Passivo Total (código 2)
                passivo = bpp_year[bpp_year["CD_CONTA"] == "2"]
                if not passivo.empty:
                    row["passivo_total"] = passivo["VL_CONTA"].iloc[-1]
            
            # DRE - Lucro Líquido e Receitas
            if "DRE" in data:
                dre = data["DRE"]
                dre_year = dre[dre["ANO"] == year]
                
                # Lucro Líquido (código 3.07 ou 3.11)
                lucro = dre_year[
                    dre_year["CD_CONTA"].str.startswith("3.07") |
                    dre_year["CD_CONTA"].str.startswith("3.11")
                ]
                if not lucro.empty:
                    row["lucro_liquido"] = lucro["VL_CONTA"].iloc[-1]
                
                # Receita Total (código 3.01)
                receita = dre_year[dre_year["CD_CONTA"].str.startswith("3.01")]
                if not receita.empty:
                    row["receita_total"] = receita["VL_CONTA"].iloc[-1]
            
            metrics.append(row)
        
        # Criar DataFrame
        df = pd.DataFrame(metrics)
        
        if df.empty:
            return df
        
        # Calcular métricas derivadas
        if "lucro_liquido" in df.columns and "patrimonio_liquido" in df.columns:
            df["roe"] = df["lucro_liquido"] / df["patrimonio_liquido"]
        
        if "lucro_liquido" in df.columns and "ativo_total" in df.columns:
            df["roa"] = df["lucro_liquido"] / df["ativo_total"]
        
        if "lucro_liquido" in df.columns and "receita_total" in df.columns:
            df["margem_liquida"] = df["lucro_liquido"] / df["receita_total"]
        
        return df.sort_values("ano").reset_index(drop=True)
    
    # -------------------------------------------------------------------------
    # SALVAMENTO
    # -------------------------------------------------------------------------
    
    def save_raw_data(
        self,
        data: Dict[str, pd.DataFrame],
        company_ticker: str = "petr4",
    ) -> Dict[str, Path]:
        """
        Salva dados brutos extraídos em external/cvm/.
        
        Args:
            data: Dicionário {tipo_doc: DataFrame}.
            company_ticker: Ticker da empresa para nome dos arquivos.
            
        Returns:
            Dicionário {tipo_doc: Path} dos arquivos salvos.
        """
        output_dir = self.cache_dir / f"dfp_{company_ticker}_raw"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        paths = {}
        for doc_type, df in data.items():
            if not df.empty:
                path = output_dir / f"{doc_type.lower()}.csv"
                df.to_csv(path, index=False)
                paths[doc_type] = path
                logger.info(f"Salvo: {path}")
        
        return paths
    
    def save_processed(
        self,
        df: pd.DataFrame,
        filename: str = "financials_petr4.csv",
    ) -> Path:
        """
        Salva dados processados em data/processed/.
        
        Args:
            df: DataFrame consolidado.
            filename: Nome do arquivo.
            
        Returns:
            Path do arquivo salvo.
        """
        output_path = self.config.paths.data_processed / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Salvo: {output_path}")
        return output_path


# =============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# =============================================================================

def load_petr4_financials(
    start_year: int = 2014,
    end_year: Optional[int] = None,
) -> pd.DataFrame:
    """
    Carrega histórico financeiro da Petrobras.
    
    Wrapper conveniente para análise Q-VAL.
    
    Args:
        start_year: Ano inicial.
        end_year: Ano final (default: ano atual).
        
    Returns:
        DataFrame com métricas financeiras históricas.
    """
    loader = CVMLoader()
    return loader.fetch_financial_history(
        cvm_code=9512,  # Petrobras
        start_year=start_year,
        end_year=end_year,
    )


def download_all_dfps(
    start_year: int = 2014,
    end_year: Optional[int] = None,
) -> List[Path]:
    """
    Baixa todos os DFPs de um período.
    
    Útil para pré-cache antes de análises.
    
    Args:
        start_year: Ano inicial.
        end_year: Ano final.
        
    Returns:
        Lista de paths dos ZIPs baixados.
    """
    end_year = end_year or datetime.now().year
    loader = CVMLoader()
    
    paths = []
    for year in range(start_year, end_year + 1):
        try:
            path = loader.download_dfp(year)
            paths.append(path)
        except FileNotFoundError:
            logger.warning(f"DFP {year} não disponível")
    
    return paths


def get_company_cvm_code(ticker: str) -> Optional[int]:
    """
    Retorna código CVM de um ticker.
    
    Args:
        ticker: Código do ativo (ex: "PETR4").
        
    Returns:
        Código CVM ou None se não encontrado.
    """
    return CVM_CODES.get(ticker.upper())
