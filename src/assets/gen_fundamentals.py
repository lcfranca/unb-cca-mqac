#!/usr/bin/env python3
"""
Consolidador de Dados Fundamentalistas - PETR4

Este script consolida todos os dados fundamentalistas coletados
em um único arquivo JSON estruturado para uso no motor Q-VAL.

Artefato de saída: data/processed/fundamentals.json
"""

import json
from pathlib import Path
from datetime import datetime

# Caminhos
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EXTERNAL_BRAPI = DATA_DIR / "external" / "brapi"
PROCESSED_DIR = DATA_DIR / "processed"

def load_json(filepath: Path) -> dict:
    """Carrega arquivo JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("=" * 60)
    print("CONSOLIDAÇÃO DE DADOS FUNDAMENTALISTAS")
    print("=" * 60)
    
    # Carregar arquivos fonte
    financial_data = load_json(EXTERNAL_BRAPI / "petr4_financial_data.json")
    fundamental = load_json(EXTERNAL_BRAPI / "petr4_fundamental.json")
    balance_sheet = load_json(EXTERNAL_BRAPI / "petr4_balance_sheet.json")
    income_statement = load_json(EXTERNAL_BRAPI / "petr4_income_statement.json")
    cashflow = load_json(EXTERNAL_BRAPI / "petr4_cashflow.json")
    
    # Extrair dados principais
    fd = financial_data["results"][0]
    fund = fundamental["results"][0]
    
    # Estruturar dados consolidados
    fundamentals = {
        "metadata": {
            "ticker": "PETR4",
            "company_name": fd.get("longName", "Petróleo Brasileiro S.A. - Petrobras"),
            "sector": fd.get("summaryProfile", {}).get("sector", "Energy"),
            "industry": fd.get("summaryProfile", {}).get("industry", "Oil & Gas Integrated"),
            "currency": fd.get("currency", "BRL"),
            "generated_at": datetime.now().isoformat(),
            "data_date": financial_data.get("_metadata", {}).get("data_referencia"),
            "source": "brapi.dev"
        },
        "market_data": {
            "price": fd.get("regularMarketPrice"),
            "market_cap": fd.get("marketCap"),
            "enterprise_value": fd.get("defaultKeyStatistics", {}).get("enterpriseValue"),
            "shares_outstanding": fd.get("defaultKeyStatistics", {}).get("sharesOutstanding"),
            "52_week_high": fd.get("fiftyTwoWeekHigh"),
            "52_week_low": fd.get("fiftyTwoWeekLow"),
            "ytd_return": fd.get("defaultKeyStatistics", {}).get("ytdReturn"),
            "52_week_change": fd.get("defaultKeyStatistics", {}).get("52WeekChange")
        },
        "valuation_metrics": {
            "price_earnings": fd.get("priceEarnings"),
            "earnings_yield": 1 / fd.get("priceEarnings") if fd.get("priceEarnings") else None,
            "forward_pe": fd.get("defaultKeyStatistics", {}).get("forwardPE"),
            "price_to_book": fd.get("defaultKeyStatistics", {}).get("priceToBook"),
            "book_value_per_share": fd.get("defaultKeyStatistics", {}).get("bookValue"),
            "enterprise_to_revenue": fd.get("defaultKeyStatistics", {}).get("enterpriseToRevenue"),
            "enterprise_to_ebitda": fd.get("defaultKeyStatistics", {}).get("enterpriseToEbitda"),
            "earnings_per_share": fd.get("earningsPerShare")
        },
        "profitability_metrics": {
            "gross_margins": fd.get("financialData", {}).get("grossMargins"),
            "operating_margins": fd.get("financialData", {}).get("operatingMargins"),
            "profit_margins": fd.get("financialData", {}).get("profitMargins"),
            "ebitda_margins": fd.get("financialData", {}).get("ebitdaMargins"),
            "return_on_equity": fd.get("financialData", {}).get("returnOnEquity"),
            "return_on_assets": fd.get("financialData", {}).get("returnOnAssets")
        },
        "financial_health": {
            "current_ratio": fd.get("financialData", {}).get("currentRatio"),
            "quick_ratio": fd.get("financialData", {}).get("quickRatio"),
            "debt_to_equity": fd.get("financialData", {}).get("debtToEquity"),
            "total_debt": fd.get("financialData", {}).get("totalDebt"),
            "total_cash": fd.get("financialData", {}).get("totalCash"),
            "total_cash_per_share": fd.get("financialData", {}).get("totalCashPerShare")
        },
        "cash_flow_metrics": {
            "operating_cashflow": fd.get("financialData", {}).get("operatingCashflow"),
            "free_cashflow": fd.get("financialData", {}).get("freeCashflow")
        },
        "growth_metrics": {
            "revenue_growth": fd.get("financialData", {}).get("revenueGrowth"),
            "earnings_growth": fd.get("financialData", {}).get("earningsGrowth"),
            "earnings_annual_growth": fd.get("defaultKeyStatistics", {}).get("earningsAnnualGrowth")
        },
        "income_statement": {
            "total_revenue": fd.get("financialData", {}).get("totalRevenue"),
            "gross_profits": fd.get("financialData", {}).get("grossProfits"),
            "ebitda": fd.get("financialData", {}).get("ebitda"),
            "revenue_per_share": fd.get("financialData", {}).get("revenuePerShare")
        },
        "dividend_data": {
            "dividend_yield": fd.get("defaultKeyStatistics", {}).get("dividendYield"),
            "last_dividend_value": fd.get("defaultKeyStatistics", {}).get("lastDividendValue"),
            "last_dividend_date": fd.get("defaultKeyStatistics", {}).get("lastDividendDate"),
            "dividend_history_count": len(fund.get("dividendsData", {}).get("cashDividends", []))
        },
        "balance_sheet_summary": {
            "total_assets": fd.get("defaultKeyStatistics", {}).get("totalAssets")
        },
        "qval_inputs": {
            # Métricas de Valor (Value)
            "earnings_yield": 1 / fd.get("priceEarnings") if fd.get("priceEarnings") else None,
            "ev_ebitda": fd.get("defaultKeyStatistics", {}).get("enterpriseToEbitda"),
            "price_to_book": fd.get("defaultKeyStatistics", {}).get("priceToBook"),
            "dividend_yield": fd.get("defaultKeyStatistics", {}).get("dividendYield"),
            
            # Métricas de Qualidade (Quality)
            "roe": fd.get("financialData", {}).get("returnOnEquity"),
            "roa": fd.get("financialData", {}).get("returnOnAssets"),
            "gross_margin": fd.get("financialData", {}).get("grossMargins"),
            "operating_margin": fd.get("financialData", {}).get("operatingMargins"),
            "ebitda_margin": fd.get("financialData", {}).get("ebitdaMargins"),
            
            # Métricas de Saúde Financeira (Financial Health)
            "current_ratio": fd.get("financialData", {}).get("currentRatio"),
            "debt_to_equity": fd.get("financialData", {}).get("debtToEquity"),
            
            # Métricas de Crescimento (Growth)
            "revenue_growth": fd.get("financialData", {}).get("revenueGrowth"),
            "earnings_growth": fd.get("financialData", {}).get("earningsGrowth")
        }
    }
    
    # Salvar arquivo consolidado
    output_path = PROCESSED_DIR / "fundamentals.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(fundamentals, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Arquivo salvo: {output_path}")
    
    # Exibir resumo
    print("\n📊 RESUMO DOS DADOS CONSOLIDADOS:")
    print(f"   Ticker: {fundamentals['metadata']['ticker']}")
    print(f"   Empresa: {fundamentals['metadata']['company_name']}")
    print(f"   Setor: {fundamentals['metadata']['sector']}")
    print(f"   Indústria: {fundamentals['metadata']['industry']}")
    
    print("\n📈 Métricas de Valuation:")
    vm = fundamentals['valuation_metrics']
    print(f"   P/L: {vm['price_earnings']:.2f}x" if vm['price_earnings'] else "   P/L: N/A")
    print(f"   P/VP: {vm['price_to_book']:.2f}x" if vm['price_to_book'] else "   P/VP: N/A")
    print(f"   EV/EBITDA: {vm['enterprise_to_ebitda']:.2f}x" if vm['enterprise_to_ebitda'] else "   EV/EBITDA: N/A")
    print(f"   Earnings Yield: {vm['earnings_yield']*100:.2f}%" if vm['earnings_yield'] else "   EY: N/A")
    
    print("\n💰 Métricas de Rentabilidade:")
    pm = fundamentals['profitability_metrics']
    print(f"   ROE: {pm['return_on_equity']*100:.2f}%" if pm['return_on_equity'] else "   ROE: N/A")
    print(f"   ROA: {pm['return_on_assets']*100:.2f}%" if pm['return_on_assets'] else "   ROA: N/A")
    print(f"   Margem EBITDA: {pm['ebitda_margins']*100:.2f}%" if pm['ebitda_margins'] else "   Margem EBITDA: N/A")
    print(f"   Margem Líquida: {pm['profit_margins']*100:.2f}%" if pm['profit_margins'] else "   Margem Líquida: N/A")
    
    print("\n🏦 Saúde Financeira:")
    fh = fundamentals['financial_health']
    print(f"   Liquidez Corrente: {fh['current_ratio']:.2f}" if fh['current_ratio'] else "   Liquidez: N/A")
    print(f"   Dívida/PL: {fh['debt_to_equity']:.2f}%" if fh['debt_to_equity'] else "   D/E: N/A")
    
    print("\n📊 Dividendos:")
    dd = fundamentals['dividend_data']
    print(f"   Dividend Yield: {dd['dividend_yield']:.2f}%" if dd['dividend_yield'] else "   DY: N/A")
    print(f"   Histórico: {dd['dividend_history_count']} pagamentos registrados")
    
    print("\n" + "=" * 60)
    print("CONSOLIDAÇÃO CONCLUÍDA")
    print("=" * 60)
    
    return fundamentals

if __name__ == "__main__":
    main()
