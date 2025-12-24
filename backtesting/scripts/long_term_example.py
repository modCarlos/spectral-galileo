"""
Complete Long-Term Backtest Example - Fase 3 Demonstration

Integra:
1. Data loading (5 años de datos)
2. Backtester (generación de señales y trades)
3. Advanced Metrics (cálculo de métricas)
4. Report Generator (generación de reportes HTML)

Author: Spectral Galileo
Date: 2025-12-23
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

from backtest_data_manager import BacktestDataManager
from backtester import Backtester
from advanced_metrics import AdvancedMetricsCalculator
from report_generator_v2 import ReportGeneratorV2

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_long_term_backtest_example():
    """
    Ejecuta backtest de largo plazo (5 años) con métricas avanzadas y reportes.
    """
    
    print("\n" + "="*80)
    print(" "*15 + "🚀 FASE 3: LONG-TERM BACKTEST WITH ADVANCED METRICS 🚀")
    print("="*80)
    
    # =====================================================================
    # PASO 1: Configurar parámetros del backtest
    # =====================================================================
    print("\n📋 Configuración del Backtest")
    print("-" * 80)
    
    # Usar datos de 5 años: 2020-12-24 a 2025-12-22
    start_date = "2020-12-24"
    end_date = "2025-12-22"
    initial_cash = 100000
    
    # Tickers para diversificación
    tickers = [
        "AAPL", "MSFT", "NVDA", "GOOGL", "META"  # Tech
    ]
    
    print(f"  Período: {start_date} → {end_date} (5 años)")
    print(f"  Capital Inicial: ${initial_cash:,.0f}")
    print(f"  Tickers: {', '.join(tickers)} ({len(tickers)} activos)")
    print(f"  Estrategia: RSI(14) + MA(20) basada en momentum")
    
    # =====================================================================
    # PASO 2: Ejecutar backtest
    # =====================================================================
    print("\n🔄 Ejecutando Backtest...")
    print("-" * 80)
    
    backtester = Backtester(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        initial_cash=initial_cash
    )
    
    try:
        results = backtester.run_backtest()
        print(f"✓ Backtest completado exitosamente")
    except Exception as e:
        logger.error(f"Error ejecutando backtest: {e}")
        return
    
    # =====================================================================
    # PASO 3: Calcular métricas avanzadas
    # =====================================================================
    print("\n📊 Calculando Métricas Avanzadas...")
    print("-" * 80)
    
    daily_values = results['daily_values']['Portfolio Value'].tolist()
    transactions_df = results.get('transactions', pd.DataFrame())
    
    # Convertir transacciones a formato que espera AdvancedMetricsCalculator
    trades = []
    if not transactions_df.empty:
        for idx, row in transactions_df.iterrows():
            trades.append({
                'action': row.get('Action', 'HOLD'),
                'ticker': row.get('Ticker', ''),
                'date': row.get('Date', ''),
                'pnl': row.get('PnL', 0)
            })
    
    metrics_calculator = AdvancedMetricsCalculator(
        daily_values=daily_values,
        trades=trades,
        risk_free_rate=0.04
    )
    
    metrics_summary = metrics_calculator.generate_summary()
    
    # Mostrar métricas
    metrics_calculator.print_summary()
    
    # =====================================================================
    # PASO 4: Generar reporte HTML
    # =====================================================================
    print("\n🎨 Generando Reporte HTML...")
    print("-" * 80)
    
    report_generator = ReportGeneratorV2(output_dir="./backtest_results")
    
    report_file = report_generator.generate_html_report(
        backtest_name=f"long_term_{'-'.join(tickers)}",
        metrics_summary=metrics_summary,
        daily_values=daily_values,
        trades=trades,
        start_date=start_date,
        end_date=end_date,
        tickers=tickers
    )
    
    print(f"✓ Reporte HTML generado: {report_file}")
    
    # =====================================================================
    # PASO 5: Guardar resultados detallados
    # =====================================================================
    print("\n💾 Guardando Resultados...")
    print("-" * 80)
    
    # Guardar métricas como JSON
    metrics_file = Path("backtest_results") / f"metrics_long_term_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics_summary, f, indent=2)
    print(f"✓ Métricas guardadas: {metrics_file}")
    
    # Guardar resultados del backtest
    backtester.save_results(results)
    print(f"✓ Resultados del backtest guardados")
    
    # =====================================================================
    # PASO 6: Resumen final
    # =====================================================================
    print("\n" + "="*80)
    print(" "*25 + "✅ BACKTEST COMPLETADO EXITOSAMENTE ✅")
    print("="*80)
    
    print("\n📈 RESUMEN DE RESULTADOS")
    print("-" * 80)
    print(f"  Período: {start_date} → {end_date}")
    print(f"  Capital Inicial: ${initial_cash:,.0f}")
    print(f"  Capital Final: ${daily_values[-1]:,.2f}")
    print(f"  Retorno Total: {metrics_summary['returns']['total_return_pct']:.2f}%")
    print(f"  Retorno Anualizado: {metrics_summary['returns']['annualized_return_pct']:.2f}%")
    print(f"  Sharpe Ratio: {metrics_summary['risk_adjusted']['sharpe_ratio']:.2f}")
    print(f"  Máximo Drawdown: {metrics_summary['risk']['maximum_drawdown_pct']:.2f}%")
    print(f"  Volatilidad: {metrics_summary['risk']['volatility_pct']:.2f}%")
    print(f"  Total de Trades: {metrics_summary['trading']['total_trades']}")
    print(f"  Win Rate: {metrics_summary['trading']['win_rate_pct']:.1f}%")
    print(f"  Profit Factor: {metrics_summary['trading']['profit_factor']:.2f}")
    
    print("\n📁 ARCHIVOS GENERADOS")
    print("-" * 80)
    print(f"  1. HTML Report: {report_file}")
    print(f"  2. Metrics JSON: {metrics_file}")
    print(f"  3. Backtest Results: backtest_results/backtest_summary_*.txt")
    print(f"  4. Daily Values: backtest_results/backtest_daily_*.csv")
    print(f"  5. Transactions: backtest_results/backtest_transactions_*.csv")
    
    print("\n🔗 PRÓXIMOS PASOS")
    print("-" * 80)
    print("  1. Abre el HTML report en navegador para ver gráficos interactivos")
    print("  2. Revisa el JSON de métricas para análisis detallado")
    print("  3. Compara resultados entre diferentes períodos de tiempo")
    print("  4. Experimenta con diferentes parámetros de señales")
    print("  5. Prueba con diferentes combinaciones de tickers")
    
    print("\n" + "="*80 + "\n")
    
    return {
        'metrics': metrics_summary,
        'report_file': report_file,
        'results': results
    }


def run_multi_period_analysis():
    """
    Ejecuta backtests en múltiples períodos de tiempo para análisis exhaustivo.
    """
    
    print("\n" + "="*80)
    print(" "*15 + "📊 ANÁLISIS MULTI-PERÍODO (3-5 AÑOS) 📊")
    print("="*80)
    
    # Definir períodos
    periods = {
        'full_5_years': {
            'start': "2020-12-24",
            'end': "2025-12-22",
            'description': "Período completo (5 años)"
        },
        'last_2_years': {
            'start': "2023-12-22",
            'end': "2025-12-22",
            'description': "Últimos 2 años"
        },
        'last_year': {
            'start': "2024-12-23",
            'end': "2025-12-22",
            'description': "Último año"
        }
    }
    
    # Tickers
    tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "META"]
    
    results_by_period = {}
    
    for period_key, period_info in periods.items():
        print(f"\n🔄 Analizando: {period_info['description']}")
        print(f"   Período: {period_info['start']} → {period_info['end']}")
        print("-" * 80)
        
        backtester = Backtester(
            tickers=tickers,
            start_date=period_info['start'],
            end_date=period_info['end'],
            initial_cash=100000
        )
        
        try:
            results = backtester.run_backtest()
            
            # Calcular métricas
            calculator = AdvancedMetricsCalculator(
                daily_values=results['daily_values'],
                trades=results['trades']
            )
            
            metrics = calculator.generate_summary()
            results_by_period[period_key] = {
                'period': period_info['description'],
                'metrics': metrics,
                'results': results
            }
            
            print(f"  ✓ Retorno Total: {metrics['returns']['total_return_pct']:.2f}%")
            print(f"  ✓ Sharpe Ratio: {metrics['risk_adjusted']['sharpe_ratio']:.2f}")
            print(f"  ✓ Max Drawdown: {metrics['risk']['maximum_drawdown_pct']:.2f}%")
            print(f"  ✓ Trades: {metrics['trading']['total_trades']} (Win Rate: {metrics['trading']['win_rate_pct']:.1f}%)")
            
        except Exception as e:
            logger.error(f"Error en período {period_key}: {e}")
    
    # Comparativa
    print("\n" + "="*80)
    print(" "*25 + "📊 COMPARATIVA DE PERÍODOS 📊")
    print("="*80)
    
    print(f"\n{'Período':<20} | {'Retorno %':<12} | {'Sharpe':<8} | {'Max DD %':<10} | {'Trades':<8}")
    print("-" * 80)
    
    for period_key, period_data in results_by_period.items():
        m = period_data['metrics']
        print(f"{period_data['period']:<20} | {m['returns']['total_return_pct']:>10.2f}% | "
              f"{m['risk_adjusted']['sharpe_ratio']:>6.2f} | {m['risk']['maximum_drawdown_pct']:>8.2f}% | "
              f"{m['trading']['total_trades']:>6.0f}")
    
    print("\n" + "="*80 + "\n")
    
    return results_by_period


if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="Long-Term Backtest Example - Fase 3")
    parser.add_argument("--long-term", action="store_true", help="Ejecutar backtest de largo plazo")
    parser.add_argument("--multi-period", action="store_true", help="Ejecutar análisis multi-período")
    parser.add_argument("--all", action="store_true", help="Ejecutar todos los análisis")
    
    args = parser.parse_args()
    
    if args.long_term or args.all:
        run_long_term_backtest_example()
    
    if args.multi_period or args.all:
        run_multi_period_analysis()
    
    if not (args.long_term or args.multi_period or args.all):
        # Default: ejecutar backtest de largo plazo
        run_long_term_backtest_example()
