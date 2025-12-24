#!/usr/bin/env python3
"""
CLI para ejecutar backtests personalizados - FÁCIL DE USAR

Ejemplos:
    python backtest_cli.py --ticker AAPL --type short
    python backtest_cli.py --ticker TSLA --type long --start 2024-01-01
    python backtest_cli.py --tickers AAPL,MSFT,NVDA --type short
"""

import argparse
import sys
from datetime import datetime, timedelta
from agent_backtester import AgentBacktester
import numpy as np

def calculate_quick_metrics(daily_values):
    """Calcula métricas rápidas"""
    if len(daily_values) < 2:
        return {}
    
    initial = daily_values[0]
    final = daily_values[-1]
    total_return = (final - initial) / initial
    
    returns = np.diff(daily_values) / daily_values[:-1]
    volatility = np.std(returns) * np.sqrt(252)
    
    sharpe = 0
    if volatility > 0:
        risk_free = 0.05 / 252
        excess_returns = returns - risk_free
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    
    cummax = np.maximum.accumulate(daily_values)
    max_drawdown = np.min((daily_values - cummax) / cummax)
    
    return {
        'total_return': total_return * 100,
        'volatility': volatility * 100,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown * 100,
        'final_value': final
    }

def main():
    parser = argparse.ArgumentParser(
        description='🚀 Backtest CLI - Prueba tu agente fácilmente'
    )
    
    # Tickers
    parser.add_argument('--ticker', type=str, help='Un solo ticker (ej: AAPL)')
    parser.add_argument('--tickers', type=str, help='Múltiples tickers separados por coma (ej: AAPL,MSFT,NVDA)')
    
    # Tipo de análisis
    parser.add_argument(
        '--type',
        choices=['short', 'long'],
        default='short',
        help='short_term (6 meses) o long_term (5 años)'
    )
    
    # Fechas personalizadas
    parser.add_argument('--start', type=str, help='Fecha inicio (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='Fecha fin (YYYY-MM-DD)')
    
    # Capital inicial
    parser.add_argument('--capital', type=float, default=100000, help='Capital inicial ($) [default: $100,000]')
    
    args = parser.parse_args()
    
    # Validar tickers
    if not args.ticker and not args.tickers:
        print("❌ Error: Especifica --ticker o --tickers")
        sys.exit(1)
    
    tickers = []
    if args.ticker:
        tickers = [args.ticker]
    else:
        tickers = args.tickers.split(',')
    
    # Determinar fechas según tipo
    end_date = datetime.now().date().isoformat() if not args.end else args.end
    
    if args.type == 'short':
        analysis_type = 'short_term'
        default_start = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=180)).strftime('%Y-%m-%d')
    else:
        analysis_type = 'long_term'
        default_start = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=1254)).strftime('%Y-%m-%d')
    
    start_date = args.start if args.start else default_start
    
    # Mostrar configuración
    print("\n" + "="*80)
    print(f"{'🎯 BACKTEST CONFIGURATION':^80}")
    print("="*80)
    print(f"\n📊 Tickers:        {', '.join(tickers)}")
    print(f"📅 Período:        {start_date} → {end_date}")
    print(f"🎪 Tipo:           {analysis_type.replace('_', ' ').title()}")
    print(f"💰 Capital Inicial: ${args.capital:,.2f}")
    print(f"\n{'Iniciando backtesting...':^80}\n")
    
    # Ejecutar backtest
    try:
        backtester = AgentBacktester(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            analysis_type=analysis_type,
            initial_cash=args.capital
        )
        
        results = backtester.run_backtest()
        backtester.save_results(results)
        
        # Calcular métricas
        if not results['daily_values'].empty:
            daily_values = results['daily_values']['Portfolio Value'].values
            metrics = calculate_quick_metrics(daily_values)
            
            # Mostrar resultados
            print("="*80)
            print(f"{'✅ RESULTADOS':^80}")
            print("="*80)
            print(f"\n💰 Valor Final:       ${metrics['final_value']:,.2f}")
            print(f"📈 Retorno Total:     {metrics['total_return']:>8.2f}%")
            print(f"📊 Volatilidad:       {metrics['volatility']:>8.2f}%")
            print(f"⭐ Sharpe Ratio:      {metrics['sharpe']:>8.2f}")
            print(f"📉 Max Drawdown:      {metrics['max_drawdown']:>8.2f}%")
            print(f"🔄 Total Trades:      {len(results['transactions']):>8d}")
            
            # Winning trades
            if not results['transactions'].empty:
                winning = 0
                for _, trade in results['transactions'].iterrows():
                    if trade.get('P&L', 0) > 0:
                        winning += 1
                total = len(results['transactions'])
                win_pct = (winning / total * 100) if total > 0 else 0
                print(f"🏆 Win Rate:         {win_pct:>8.1f}%")
            
            print(f"\n📁 Reportes guardados en: backtest_results/")
            print(f"   ├─ report_agent_{analysis_type}_*.html")
            print(f"   ├─ agent_backtest_daily_*.csv")
            print(f"   └─ agent_backtest_transactions_*.csv")
            print("\n" + "="*80 + "\n")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
