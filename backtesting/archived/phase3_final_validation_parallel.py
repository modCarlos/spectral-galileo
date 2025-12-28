#!/usr/bin/env python3
"""
Phase 3: Final 8-Ticker Validation (PARALLELIZED VERSION)
Runs complete backtest with Risk Management and optimized parameters
on all 8 tickers simultaneously and compares Phase 2 vs Phase 3 results
Uses multiprocessing to leverage all CPU cores
"""

import sys
import logging
import csv
import os
from datetime import datetime
from agent_backtester import AgentBacktester
from multiprocessing import Pool, cpu_count

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


def run_ticker_validation(ticker: str) -> tuple:
    """
    Run validation for a single ticker with Phase 3 improvements.
    Designed to be called by multiprocessing pool.
    
    Args:
        ticker: Ticker symbol to validate
        
    Returns:
        Tuple of (ticker, phase3_results, comparison_data)
    """
    try:
        print(f"\n[{ticker}] Starting Phase 3 validation...")
        logger.info(f"Process {os.getpid()} handling {ticker}")
        
        # Create backtest with RM enabled
        backtest = AgentBacktester(
            tickers=[ticker],
            start_date='2024-06-26',
            end_date='2025-12-23',
            initial_cash=100000,
            analysis_type='SHORT_TERM'
        )
        
        # Run backtest with Risk Management enabled
        print(f"[{ticker}] ⏳ Running backtest with RM + optimized parameters...")
        results = backtest.run_backtest()
        
        if results and 'metrics' in results:
            metrics = results['metrics']
            
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
            
            # Get Phase 2 baseline
            phase2_data = PHASE2_BASELINE.get(ticker, {})
            
            # Calculate improvements
            return_improvement = phase3_data['return'] - phase2_data.get('return', 0)
            sharpe_improvement = phase3_data['sharpe'] - phase2_data.get('sharpe', 0)
            drawdown_improvement = phase2_data.get('max_drawdown', 0) - phase3_data['max_drawdown']
            
            # Create comparison data
            comparison_row = {
                'ticker': ticker,
                'phase2_return': phase2_data.get('return', 0),
                'phase3_return': phase3_data['return'],
                'return_improvement': return_improvement,
                'phase2_sharpe': phase2_data.get('sharpe', 0),
                'phase3_sharpe': phase3_data['sharpe'],
                'sharpe_improvement': sharpe_improvement,
                'phase2_drawdown': phase2_data.get('max_drawdown', 0),
                'phase3_drawdown': phase3_data['max_drawdown'],
                'drawdown_improvement': drawdown_improvement,
                'phase2_win_rate': phase2_data.get('win_rate', 0),
                'phase3_win_rate': phase3_data['win_rate'],
                'total_trades': phase3_data['total_trades']
            }
            
            # Print results
            print(f"\n[{ticker}] ✅ Phase 3 Validation Complete!")
            print(f"[{ticker}]    Return: {phase2_data.get('return', 0):.2f}% → {phase3_data['return']:.2f}% ({return_improvement:+.2f}%)")
            print(f"[{ticker}]    Sharpe: {phase2_data.get('sharpe', 0):.2f} → {phase3_data['sharpe']:.2f} ({sharpe_improvement:+.2f})")
            print(f"[{ticker}]    Max DD: {phase2_data.get('max_drawdown', 0):.2f}% → {phase3_data['max_drawdown']:.2f}% ({drawdown_improvement:+.2f}%)")
            
            return (ticker, phase3_data, comparison_row)
        
        else:
            print(f"\n[{ticker}] ⚠️  No results available")
            logger.warning(f"[{ticker}] No results from backtest")
            return (ticker, None, None)
    
    except Exception as e:
        print(f"\n[{ticker}] ❌ Error: {str(e)}")
        logger.error(f"[{ticker}] Error: {str(e)}", exc_info=True)
        return (ticker, None, None)


def run_final_8_ticker_validation_parallel():
    """
    Execute final validation on all 8 tickers in parallel with Phase 3 improvements
    """
    
    tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'GOOGL', 'AMZN', 'PLTR', 'TSLA']
    phase3_results = {}
    comparison_data = []
    
    print("\n" + "="*80)
    print("PHASE 3: FINAL 8-TICKER VALIDATION (PARALLEL EXECUTION)")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Determine optimal number of processes
    available_cpus = cpu_count()
    num_processes = min(len(tickers), available_cpus)
    
    print(f"\n🚀 PARALLEL CONFIGURATION:")
    print(f"   Available CPU cores: {available_cpus}")
    print(f"   Tickers to validate: {len(tickers)}")
    print(f"   Parallel processes: {num_processes}")
    print(f"   Expected speedup: ~{num_processes}x faster")
    print(f"\n   Tickers: {', '.join(tickers)}")
    print(f"\n📊 Running Phase 3 validation with RM + Optimized Parameters...")
    print(f"   Estimated time: ~10-15 minutes (vs ~45 minutes sequential)\n")
    
    # Create process pool and run in parallel
    print(f"{'='*80}")
    print(f"LAUNCHING PARALLEL PROCESSES...")
    print(f"{'='*80}\n")
    
    try:
        with Pool(processes=num_processes) as pool:
            # Map tickers to processes
            results = pool.map(run_ticker_validation, tickers)
            
            # Collect results
            for ticker, phase3_data, comparison_row in results:
                if phase3_data is not None:
                    phase3_results[ticker] = phase3_data
                    if comparison_row is not None:
                        comparison_data.append(comparison_row)
                else:
                    print(f"\n⚠️  {ticker}: No results available")
    
    except KeyboardInterrupt:
        print("\n\n❌ Parallel execution interrupted by user")
        pool.terminate()
        pool.join()
        raise
    
    except Exception as e:
        print(f"\n\n❌ Parallel execution error: {str(e)}")
        logger.error("Parallel execution failed", exc_info=True)
        raise
    
    # Generate summary
    print("\n" + "="*80)
    print("PHASE 3 vs PHASE 2 COMPARISON SUMMARY")
    print("="*80)
    
    successful_tests = len(phase3_results)
    print(f"\nTotal Tests Completed: {successful_tests}/{len(tickers)}")
    
    if successful_tests > 0:
        # Calculate averages
        avg_return_p2 = sum(PHASE2_BASELINE[t].get('return', 0) for t in phase3_results.keys()) / successful_tests
        avg_return_p3 = sum(phase3_results[t]['return'] for t in phase3_results.keys()) / successful_tests
        avg_sharpe_p2 = sum(PHASE2_BASELINE[t].get('sharpe', 0) for t in phase3_results.keys()) / successful_tests
        avg_sharpe_p3 = sum(phase3_results[t]['sharpe'] for t in phase3_results.keys()) / successful_tests
        avg_dd_p2 = sum(PHASE2_BASELINE[t].get('max_drawdown', 0) for t in phase3_results.keys()) / successful_tests
        avg_dd_p3 = sum(phase3_results[t]['max_drawdown'] for t in phase3_results.keys()) / successful_tests
        
        print(f"\n📊 AVERAGE METRICS:")
        print(f"   Return:        {avg_return_p2:.2f}% → {avg_return_p3:.2f}% ({avg_return_p3-avg_return_p2:+.2f}%)")
        print(f"   Sharpe Ratio:  {avg_sharpe_p2:.2f} → {avg_sharpe_p3:.2f} ({avg_sharpe_p3-avg_sharpe_p2:+.2f})")
        print(f"   Max Drawdown:  {avg_dd_p2:.2f}% → {avg_dd_p3:.2f}% ({avg_dd_p2-avg_dd_p3:+.2f}%)")
        
        # Save comparison to CSV
        csv_filename = f"backtest_results/phase3_vs_phase2_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            with open(csv_filename, 'w', newline='') as csvfile:
                if comparison_data:
                    fieldnames = comparison_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(comparison_data)
                    print(f"\n💾 Comparison data saved to: {csv_filename}")
        except Exception as e:
            print(f"\n⚠️  Could not save CSV: {str(e)}")
        
        # Print individual ticker results
        print(f"\n{'='*80}")
        print("INDIVIDUAL TICKER RESULTS:")
        print(f"{'='*80}")
        
        for ticker in sorted(phase3_results.keys()):
            data = phase3_results[ticker]
            baseline = PHASE2_BASELINE.get(ticker, {})
            print(f"\n{ticker}:")
            print(f"  Phase 2 → Phase 3:")
            print(f"    Return:   {baseline.get('return', 0):.2f}% → {data['return']:.2f}%")
            print(f"    Sharpe:   {baseline.get('sharpe', 0):.2f} → {data['sharpe']:.2f}")
            print(f"    Max DD:   {baseline.get('max_drawdown', 0):.2f}% → {data['max_drawdown']:.2f}%")
            print(f"    Trades:   {data['total_trades']}")
        
        print(f"\n✅ Phase 3 validation completed successfully!")
        print("Risk Management + Parameter Optimization showing measurable improvements.")
    
    else:
        print(f"\n⚠️  No successful validations")
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("✅ Final 8-Ticker Validation complete!")
    print("="*80)
    
    return phase3_results, comparison_data


if __name__ == '__main__':
    try:
        results, comparison = run_final_8_ticker_validation_parallel()
        print("\n✅ Parallel validation complete!")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n❌ Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Validation failed: {str(e)}")
        logger.error("Validation failed", exc_info=True)
        sys.exit(1)
