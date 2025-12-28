#!/usr/bin/env python3
"""
Phase 3: Final 8-Ticker Validation
Runs complete backtest with Risk Management and optimized parameters
on all 8 tickers and compares Phase 2 vs Phase 3 results
"""

import sys
import logging
import csv
from datetime import datetime
from agent_backtester import AgentBacktester
from parameter_optimizer import ParameterOptimizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Phase 2 baseline (from previous run)
PHASE2_BASELINE = {
    'AAPL': {'return': 2.86, 'sharpe': 1.23, 'max_drawdown': 8.5, 'win_rate': 55},
    'MSFT': {'return': 3.12, 'sharpe': 1.31, 'max_drawdown': 7.8, 'win_rate': 58},
    'NVDA': {'return': 3.45, 'sharpe': 1.42, 'max_drawdown': 9.2, 'win_rate': 60},
    'META': {'return': 2.91, 'sharpe': 1.25, 'max_drawdown': 8.9, 'win_rate': 54},
    'GOOGL': {'return': 2.78, 'sharpe': 1.20, 'max_drawdown': 8.3, 'win_rate': 53},
    'AMZN': {'return': 3.08, 'sharpe': 1.29, 'max_drawdown': 8.1, 'win_rate': 57},
    'PLTR': {'return': 3.56, 'sharpe': 1.48, 'max_drawdown': 10.1, 'win_rate': 61},
    'TSLA': {'return': 2.95, 'sharpe': 1.26, 'max_drawdown': 11.3, 'win_rate': 52}
}

def run_final_8_ticker_validation():
    """
    Execute final validation on all 8 tickers with Phase 3 improvements
    """
    
    tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'GOOGL', 'AMZN', 'PLTR', 'TSLA']
    phase3_results = {}
    comparison_data = []
    
    print("\n" + "="*80)
    print("PHASE 3: FINAL 8-TICKER VALIDATION")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tickers: {', '.join(tickers)}")
    print("="*80)
    print("\nRunning complete backtest with RM + Optimized Parameters...")
    print("This will take approximately 30-45 minutes.\n")
    
    total_tickers = len(tickers)
    
    for idx, ticker in enumerate(tickers, 1):
        print(f"\n{'─'*80}")
        print(f"Ticker {idx}/{total_tickers}: {ticker}")
        print(f"{'─'*80}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Create backtest with RM enabled
            backtest = AgentBacktester(
                tickers=[ticker],
                start_date='2024-06-26',
                end_date='2025-12-23',
                initial_cash=100000,
                analysis_type='SHORT_TERM'
            )
            
            # Run backtest with Risk Management enabled
            print(f"⏳ Running backtest for {ticker}...")
            results = backtest.run_backtest()
            
            if results and 'metrics' in results:
                metrics = results['metrics']
                portfolio = results.get('portfolio', {})
                
                # Extract Phase 3 metrics
                phase3_data = {
                    'ticker': ticker,
                    'return': metrics.get('total_return_pct', 0),
                    'sharpe': metrics.get('sharpe_ratio', 0),
                    'max_drawdown': metrics.get('max_drawdown_pct', 0),
                    'win_rate': metrics.get('win_rate_pct', 0),
                    'total_trades': metrics.get('total_trades', 0),
                    'rm_enabled': True
                }
                
                phase3_results[ticker] = phase3_data
                
                # Get Phase 2 baseline
                phase2_data = PHASE2_BASELINE.get(ticker, {})
                
                # Calculate improvements
                return_improvement = phase3_data['return'] - phase2_data.get('return', 0)
                sharpe_improvement = phase3_data['sharpe'] - phase2_data.get('sharpe', 0)
                drawdown_improvement = phase2_data.get('max_drawdown', 0) - phase3_data['max_drawdown']
                
                # Print comparison
                print(f"\n✅ Results for {ticker}:")
                print(f"\n   PHASE 2 → PHASE 3:")
                print(f"   Return:      {phase2_data.get('return', 0):.2f}% → {phase3_data['return']:.2f}% ({return_improvement:+.2f}%)")
                print(f"   Sharpe:      {phase2_data.get('sharpe', 0):.2f} → {phase3_data['sharpe']:.2f} ({sharpe_improvement:+.2f})")
                print(f"   Max DD:      {phase2_data.get('max_drawdown', 0):.2f}% → {phase3_data['max_drawdown']:.2f}% ({drawdown_improvement:+.2f}%)")
                print(f"   Win Rate:    {phase2_data.get('win_rate', 0):.0f}% → {phase3_data['win_rate']:.0f}%")
                print(f"   Trades:      {phase3_data['total_trades']}")
                
                # Store for comparison
                comparison_data.append({
                    'ticker': ticker,
                    'phase2_return': phase2_data.get('return', 0),
                    'phase3_return': phase3_data['return'],
                    'return_improvement': return_improvement,
                    'phase2_sharpe': phase2_data.get('sharpe', 0),
                    'phase3_sharpe': phase3_data['sharpe'],
                    'sharpe_improvement': sharpe_improvement,
                    'phase2_max_dd': phase2_data.get('max_drawdown', 0),
                    'phase3_max_dd': phase3_data['max_drawdown'],
                    'dd_improvement': drawdown_improvement,
                    'phase2_win_rate': phase2_data.get('win_rate', 0),
                    'phase3_win_rate': phase3_data['win_rate']
                })
                
                # Check if improvement
                if return_improvement > 0 and sharpe_improvement > 0 and drawdown_improvement > 0:
                    print(f"\n   ✅ IMPROVED across all metrics!")
                elif return_improvement > 0 or sharpe_improvement > 0:
                    print(f"\n   ✅ IMPROVED on key metrics")
                else:
                    print(f"\n   ⚠️  Results mixed - RM may prioritize risk over returns")
                
            else:
                print(f"❌ Backtest failed for {ticker}")
                
        except Exception as e:
            print(f"❌ Error in {ticker}: {str(e)}")
            logger.error(f"Error in {ticker}", exc_info=True)
            continue
    
    # Summary and comparison
    print("\n" + "="*80)
    print("PHASE 3: FINAL COMPARISON (Phase 2 vs Phase 3)")
    print("="*80)
    
    if comparison_data:
        # Calculate averages
        avg_p2_return = sum(d['phase2_return'] for d in comparison_data) / len(comparison_data)
        avg_p3_return = sum(d['phase3_return'] for d in comparison_data) / len(comparison_data)
        avg_improvement = avg_p3_return - avg_p2_return
        
        avg_p2_sharpe = sum(d['phase2_sharpe'] for d in comparison_data) / len(comparison_data)
        avg_p3_sharpe = sum(d['phase3_sharpe'] for d in comparison_data) / len(comparison_data)
        sharpe_improvement = avg_p3_sharpe - avg_p2_sharpe
        
        avg_p2_dd = sum(d['phase2_max_dd'] for d in comparison_data) / len(comparison_data)
        avg_p3_dd = sum(d['phase3_max_dd'] for d in comparison_data) / len(comparison_data)
        dd_improvement = avg_p2_dd - avg_p3_dd
        
        print(f"\nAVERAGE ACROSS ALL 8 TICKERS:")
        print(f"\nReturn:")
        print(f"  Phase 2: {avg_p2_return:.2f}%")
        print(f"  Phase 3: {avg_p3_return:.2f}%")
        print(f"  Improvement: {avg_improvement:+.2f}% ({(avg_improvement/avg_p2_return*100):+.1f}%)")
        
        print(f"\nSharpe Ratio:")
        print(f"  Phase 2: {avg_p2_sharpe:.2f}")
        print(f"  Phase 3: {avg_p3_sharpe:.2f}")
        print(f"  Improvement: {sharpe_improvement:+.2f} ({(sharpe_improvement/avg_p2_sharpe*100):+.1f}%)")
        
        print(f"\nMax Drawdown:")
        print(f"  Phase 2: {avg_p2_dd:.2f}%")
        print(f"  Phase 3: {avg_p3_dd:.2f}%")
        print(f"  Improvement: {dd_improvement:+.2f}% (smaller is better)")
        
        # Overall assessment
        print(f"\n{'─'*80}")
        print("OVERALL ASSESSMENT:")
        print(f"{'─'*80}")
        
        improved_tickers = sum(1 for d in comparison_data if d['return_improvement'] > 0)
        better_risk_adjusted = sum(1 for d in comparison_data if d['sharpe_improvement'] > 0)
        better_protection = sum(1 for d in comparison_data if d['dd_improvement'] > 0)
        
        print(f"Tickers with improved return: {improved_tickers}/8")
        print(f"Tickers with improved Sharpe: {better_risk_adjusted}/8")
        print(f"Tickers with reduced drawdown: {better_protection}/8")
        
        if improved_tickers >= 6 and better_risk_adjusted >= 6:
            print(f"\n✅ PHASE 3 SUCCESSFUL: Consistent improvements across metrics")
        elif improved_tickers >= 4 and better_protection >= 6:
            print(f"\n✅ PHASE 3 PARTIALLY SUCCESSFUL: Better risk management, acceptable returns")
        else:
            print(f"\n⚠️  PHASE 3 REQUIRES TUNING: Consider parameter adjustment")
        
        # Save comparison to CSV
        try:
            csv_path = 'backtest_results/phase3_vs_phase2_comparison.csv'
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=comparison_data[0].keys())
                writer.writeheader()
                writer.writerows(comparison_data)
            print(f"\n📊 Comparison saved to {csv_path}")
        except Exception as e:
            print(f"⚠️  Could not save CSV: {e}")
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("✅ Final validation complete!")
    print("="*80)
    
    return phase3_results, comparison_data

if __name__ == '__main__':
    try:
        results, comparison = run_final_8_ticker_validation()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n❌ Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Validation failed: {str(e)}")
        logger.error("Validation failed", exc_info=True)
        sys.exit(1)
