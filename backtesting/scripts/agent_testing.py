"""
Agent Testing Demo - Compare Short-Term vs Long-Term Analysis

Ejecuta backtests con el agente en dos modos:
1. Short-term (3-6 meses) - Enfoque momentum/técnico
2. Long-term (2-5 años) - Enfoque fundamental/macro

Author: Spectral Galileo
Date: 2025-12-23
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging

from agent_backtester import AgentBacktester
from advanced_metrics import AdvancedMetricsCalculator
from report_generator_v2 import ReportGeneratorV2

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_short_term_analysis():
    """
    Análisis de corto plazo: 3-6 meses
    Enfoque: Momentum, tendencias técnicas, volatilidad
    """
    print("\n" + "="*80)
    print(" "*20 + "🚀 AGENT SHORT-TERM ANALYSIS (3-6 months) 🚀")
    print("="*80)
    
    # Período: últimos 6 meses (desde hace 180 días)
    end_date = "2025-12-22"
    start_date = (pd.to_datetime(end_date) - timedelta(days=180)).strftime('%Y-%m-%d')
    
    # Tickers tech (volátiles para corto plazo)
    tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"]
    
    print(f"\n📋 Configuración")
    print(f"  Período: {start_date} → {end_date} (~180 días)")
    print(f"  Tickers: {', '.join(tickers)}")
    print(f"  Estrategia: Momentum + Señales técnicas")
    print(f"  Capital: $100,000")
    
    # Ejecutar backtest
    print(f"\n🔄 Ejecutando backtest...")
    backtester = AgentBacktester(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        initial_cash=100000,
        analysis_type="short_term"
    )
    
    results = backtester.run_backtest()
    backtester.save_results(results)
    
    # Calcular métricas
    if results and 'daily_values' in results:
        daily_values = results['daily_values']['Portfolio Value'].tolist()
        transactions = results['transactions']
        
        trades = []
        if not transactions.empty:
            for idx, row in transactions.iterrows():
                trades.append({
                    'action': row.get('Action', 'HOLD'),
                    'ticker': row.get('Ticker', ''),
                    'date': row.get('Date', ''),
                    'pnl': row.get('PnL', 0)
                })
        
        calculator = AdvancedMetricsCalculator(daily_values, trades)
        metrics = calculator.generate_summary()
        
        print(f"\n📊 RESULTADOS - CORTO PLAZO")
        print(f"{'='*80}")
        print(f"  Retorno Total: {metrics['returns']['total_return_pct']:.2f}%")
        print(f"  Retorno Anualizado: {metrics['returns']['annualized_return_pct']:.2f}%")
        print(f"  Sharpe Ratio: {metrics['risk_adjusted']['sharpe_ratio']:.2f}")
        print(f"  Máximo Drawdown: {metrics['risk']['maximum_drawdown_pct']:.2f}%")
        print(f"  Volatilidad: {metrics['risk']['volatility_pct']:.2f}%")
        print(f"  Total Trades: {metrics['trading']['total_trades']}")
        print(f"  Win Rate: {metrics['trading']['win_rate_pct']:.1f}%")
        print(f"  Profit Factor: {metrics['trading']['profit_factor']:.2f}")
        
        # Generar reporte HTML
        generator = ReportGeneratorV2()
        html_file = generator.generate_html_report(
            backtest_name="agent_short_term_AAPL_MSFT_NVDA_GOOGL_TSLA",
            metrics_summary=metrics,
            daily_values=daily_values,
            trades=trades,
            start_date=start_date,
            end_date=end_date,
            tickers=tickers
        )
        print(f"\n✓ HTML Report: {html_file}")
        
        return {
            'analysis_type': 'short_term',
            'metrics': metrics,
            'results': results,
            'html_report': html_file
        }
    
    return None


def run_long_term_analysis():
    """
    Análisis de largo plazo: 2-5 años
    Enfoque: Fundamentales, macro, estabilidad
    """
    print("\n" + "="*80)
    print(" "*20 + "📈 AGENT LONG-TERM ANALYSIS (2-5 years) 📈")
    print("="*80)
    
    # Período: 5 años completos
    end_date = "2025-12-22"
    start_date = "2020-12-24"
    
    # Tickers diversificados
    tickers = ["AAPL", "MSFT", "JPM", "JNJ", "WMT"]
    
    print(f"\n📋 Configuración")
    print(f"  Período: {start_date} → {end_date} (~1254 días)")
    print(f"  Tickers: {', '.join(tickers)}")
    print(f"  Estrategia: Análisis fundamental + Macro")
    print(f"  Capital: $100,000")
    
    # Ejecutar backtest
    print(f"\n🔄 Ejecutando backtest...")
    backtester = AgentBacktester(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        initial_cash=100000,
        analysis_type="long_term"
    )
    
    results = backtester.run_backtest()
    backtester.save_results(results)
    
    # Calcular métricas
    if results and 'daily_values' in results:
        daily_values = results['daily_values']['Portfolio Value'].tolist()
        transactions = results['transactions']
        
        trades = []
        if not transactions.empty:
            for idx, row in transactions.iterrows():
                trades.append({
                    'action': row.get('Action', 'HOLD'),
                    'ticker': row.get('Ticker', ''),
                    'date': row.get('Date', ''),
                    'pnl': row.get('PnL', 0)
                })
        
        calculator = AdvancedMetricsCalculator(daily_values, trades)
        metrics = calculator.generate_summary()
        
        print(f"\n📊 RESULTADOS - LARGO PLAZO")
        print(f"{'='*80}")
        print(f"  Retorno Total: {metrics['returns']['total_return_pct']:.2f}%")
        print(f"  Retorno Anualizado: {metrics['returns']['annualized_return_pct']:.2f}%")
        print(f"  Sharpe Ratio: {metrics['risk_adjusted']['sharpe_ratio']:.2f}")
        print(f"  Máximo Drawdown: {metrics['risk']['maximum_drawdown_pct']:.2f}%")
        print(f"  Volatilidad: {metrics['risk']['volatility_pct']:.2f}%")
        print(f"  Total Trades: {metrics['trading']['total_trades']}")
        print(f"  Win Rate: {metrics['trading']['win_rate_pct']:.1f}%")
        print(f"  Profit Factor: {metrics['trading']['profit_factor']:.2f}")
        
        # Generar reporte HTML
        generator = ReportGeneratorV2()
        html_file = generator.generate_html_report(
            backtest_name="agent_long_term_AAPL_MSFT_JPM_JNJ_WMT",
            metrics_summary=metrics,
            daily_values=daily_values,
            trades=trades,
            start_date=start_date,
            end_date=end_date,
            tickers=tickers
        )
        print(f"\n✓ HTML Report: {html_file}")
        
        return {
            'analysis_type': 'long_term',
            'metrics': metrics,
            'results': results,
            'html_report': html_file
        }
    
    return None


def compare_results(short_term_results, long_term_results):
    """Compara resultados de corto vs largo plazo."""
    print("\n" + "="*80)
    print(" "*20 + "⚖️  COMPARATIVA: CORTO vs LARGO PLAZO ⚖️")
    print("="*80)
    
    if not short_term_results or not long_term_results:
        print("  No hay suficientes datos para comparar")
        return
    
    st_metrics = short_term_results['metrics']
    lt_metrics = long_term_results['metrics']
    
    print(f"\n{'Métrica':<30} | {'Corto Plazo':<15} | {'Largo Plazo':<15}")
    print("-" * 65)
    print(f"{'Retorno Total':<30} | {st_metrics['returns']['total_return_pct']:>13.2f}% | {lt_metrics['returns']['total_return_pct']:>13.2f}%")
    print(f"{'Retorno Anualizado':<30} | {st_metrics['returns']['annualized_return_pct']:>13.2f}% | {lt_metrics['returns']['annualized_return_pct']:>13.2f}%")
    print(f"{'Sharpe Ratio':<30} | {st_metrics['risk_adjusted']['sharpe_ratio']:>13.2f} | {lt_metrics['risk_adjusted']['sharpe_ratio']:>13.2f}")
    print(f"{'Máximo Drawdown':<30} | {st_metrics['risk']['maximum_drawdown_pct']:>13.2f}% | {lt_metrics['risk']['maximum_drawdown_pct']:>13.2f}%")
    print(f"{'Volatilidad':<30} | {st_metrics['risk']['volatility_pct']:>13.2f}% | {lt_metrics['risk']['volatility_pct']:>13.2f}%")
    print(f"{'Total Trades':<30} | {st_metrics['trading']['total_trades']:>13.0f} | {lt_metrics['trading']['total_trades']:>13.0f}")
    print(f"{'Win Rate':<30} | {st_metrics['trading']['win_rate_pct']:>13.1f}% | {lt_metrics['trading']['win_rate_pct']:>13.1f}%")
    print(f"{'Profit Factor':<30} | {st_metrics['trading']['profit_factor']:>13.2f} | {lt_metrics['trading']['profit_factor']:>13.2f}")
    
    print(f"\n💡 INSIGHTS")
    print("-" * 65)
    
    # Análisis de resultados
    st_return = st_metrics['returns']['total_return_pct']
    lt_return = lt_metrics['returns']['total_return_pct']
    st_sharpe = st_metrics['risk_adjusted']['sharpe_ratio']
    lt_sharpe = lt_metrics['risk_adjusted']['sharpe_ratio']
    st_dd = st_metrics['risk']['maximum_drawdown_pct']
    lt_dd = lt_metrics['risk']['maximum_drawdown_pct']
    
    if st_return > lt_return:
        print(f"  → Corto plazo: Mejor retorno (+{st_return - lt_return:.2f}%)")
    else:
        print(f"  → Largo plazo: Mejor retorno (+{lt_return - st_return:.2f}%)")
    
    if st_sharpe > lt_sharpe:
        print(f"  → Corto plazo: Mejor risk-adjusted return (Sharpe: +{st_sharpe - lt_sharpe:.2f})")
    else:
        print(f"  → Largo plazo: Mejor risk-adjusted return (Sharpe: +{lt_sharpe - st_sharpe:.2f})")
    
    if abs(st_dd) < abs(lt_dd):
        print(f"  → Corto plazo: Menor drawdown máximo ({abs(st_dd):.2f}% vs {abs(lt_dd):.2f}%)")
    else:
        print(f"  → Largo plazo: Menor drawdown máximo ({abs(lt_dd):.2f}% vs {abs(st_dd):.2f}%)")
    
    print(f"\n📊 REPORTS GENERADOS")
    print(f"  Short-term: {short_term_results['html_report']}")
    print(f"  Long-term:  {long_term_results['html_report']}")


if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="Agent Testing - Short vs Long Term")
    parser.add_argument("--short-term", action="store_true", help="Solo análisis corto plazo")
    parser.add_argument("--long-term", action="store_true", help="Solo análisis largo plazo")
    parser.add_argument("--all", action="store_true", help="Ambos análisis + comparativa")
    
    args = parser.parse_args()
    
    short_term_results = None
    long_term_results = None
    
    if args.short_term or args.all:
        short_term_results = run_short_term_analysis()
    
    if args.long_term or args.all:
        long_term_results = run_long_term_analysis()
    
    if args.all and short_term_results and long_term_results:
        compare_results(short_term_results, long_term_results)
    
    if not (args.short_term or args.long_term or args.all):
        # Default: ambos análisis + comparativa
        print("\n" + "="*80)
        print(" "*15 + "🤖 AGENT-BASED BACKTESTING: SHORT-TERM vs LONG-TERM 🤖")
        print("="*80)
        
        short_term_results = run_short_term_analysis()
        long_term_results = run_long_term_analysis()
        
        if short_term_results and long_term_results:
            compare_results(short_term_results, long_term_results)
        
        print("\n" + "="*80)
        print("✅ Agent testing completado!")
        print("="*80 + "\n")
