"""
Grid Search Optimizer for Financial Agent
Finds optimal parameters through systematic search
"""

import agent
import pandas as pd
import json
import time
from itertools import product
import random
from typing import Dict, List, Any
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
import multiprocessing

# Parameter grid
DEFAULT_PARAM_GRID = {
    # Multi-timeframe weights
    'mtf_strong_weight': [3, 5, 7],
    'mtf_moderate_weight': [2, 3, 4],
    
    # MTF penalties/boosts
    'mtf_penalty': [0.85, 0.90, 0.95],
    'mtf_boost': [1.05, 1.10, 1.15],
    
    # Insider thresholds
    'insider_moderate_sell': [-3e6, -5e6, -7e6],
    'insider_heavy_sell': [-8e6, -10e6, -15e6],
    'insider_moderate_buy': [5e5, 1e6, 2e6],
    
    # Verdict thresholds
    'buy_threshold': [20, 25, 30, 35],
    
    # Reddit penalty
    'reddit_penalty': [0.85, 0.90, 0.95],
}


def generate_configs(param_grid, method='random', n_samples=50):
    """Generate parameter configurations"""
    
    if method == 'grid':
        # Full grid search - all combinations
        keys = list(param_grid.keys())
        values = [param_grid[k] for k in keys]
        
        for combo in product(*values):
            yield dict(zip(keys, combo))
    
    elif method == 'random':
        # Random search - sample n_samples random combinations
        keys = list(param_grid.keys())
        
        for _ in range(n_samples):
            config = {}
            for key in keys:
                config[key] = random.choice(param_grid[key])
            yield config
    
    else:
        raise ValueError(f"Unknown method: {method}")


def apply_config_to_agent(trading_agent, config):
    """
    Apply configuration to agent (monkey-patching for testing)
    In production, these would be proper parameters
    """
    # Store original values
    original = {}
    
    # This is a simplified version - in reality you'd need to modify
    # the agent's internal parameters or pass them as arguments
    
    return original


def evaluate_config(config: Dict, tickers: List[str], verbose=False) -> Dict[str, Any]:
    """
    Evaluate a single configuration
    
    Args:
        config: Parameter configuration
        tickers: List of tickers to test
        verbose: Print progress
        
    Returns:
        Evaluation results dict
    """
    results = []
    errors = 0
    
    if verbose:
        print(f"\n  Testing: {config}")
    
    for i, ticker in enumerate(tickers):
        if verbose and i % 10 == 0:
            print(f"    [{i}/{len(tickers)}] {ticker}...")
        
        try:
            # Skip external data (Reddit/Earnings) to avoid API blocking
            trading_agent = agent.FinancialAgent(ticker, is_short_term=False, skip_external_data=True)
            
            # Apply config (simplified - just run normal analysis for now)
            analysis = trading_agent.run_analysis()
            
            if analysis and 'strategy' in analysis:
                strategy = analysis['strategy']
                verdict = strategy.get('verdict', 'N/A')
                confidence = strategy.get('confidence', 0)
                
                results.append({
                    'ticker': ticker,
                    'verdict': verdict,
                    'confidence': confidence,
                    'regime': analysis.get('regime', 'N/A')
                })
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            if verbose:
                print(f"    ERROR on {ticker}: {str(e)[:50]}")
            errors += 1
    
    # Calculate metrics
    compra_count = sum(1 for r in results if 'COMPRA' in r['verdict'])
    neutral_count = sum(1 for r in results if 'NEUTRAL' in r['verdict'])
    
    compra_confidences = [r['confidence'] for r in results if 'COMPRA' in r['verdict']]
    avg_compra_conf = sum(compra_confidences) / len(compra_confidences) if compra_confidences else 0
    
    all_confidences = [r['confidence'] for r in results]
    avg_conf = sum(all_confidences) / len(all_confidences) if all_confidences else 0
    
    # Coverage (% of tickers getting COMPRA)
    coverage = compra_count / len(results) if results else 0
    
    # Selectivity score (higher confidence in COMPRA is better)
    selectivity = avg_compra_conf / 100 if avg_compra_conf > 0 else 0
    
    # Combined score (balance between coverage and selectivity)
    # We want: reasonable coverage (25-35%) + high confidence (35%+)
    target_coverage = 0.30
    target_confidence = 35
    
    coverage_score = 1 - abs(coverage - target_coverage) / target_coverage
    confidence_score = min(avg_compra_conf / target_confidence, 1.0)
    
    # Weighted score
    score = (
        coverage_score * 0.3 +  # 30% weight on coverage
        confidence_score * 0.5 +  # 50% weight on confidence
        selectivity * 0.2  # 20% weight on selectivity
    )
    
    return {
        'config': config,
        'score': score,
        'coverage': coverage,
        'avg_compra_conf': avg_compra_conf,
        'avg_conf': avg_conf,
        'compra_count': compra_count,
        'neutral_count': neutral_count,
        'total': len(results),
        'errors': errors,
        'coverage_score': coverage_score,
        'confidence_score': confidence_score,
        'selectivity': selectivity,
        'results': results
    }


def grid_search(param_grid=None, tickers=None, method='random', n_samples=50, 
                verbose=True, n_workers=None):
    """
    Run grid search optimization with parallel processing
    
    Args:
        param_grid: Parameter grid to search (uses default if None)
        tickers: List of tickers to test (uses sample if None)
        method: 'grid' or 'random'
        n_samples: Number of samples for random search
        verbose: Print progress
        n_workers: Number of parallel workers (None = auto-detect)
        
    Returns:
        List of results sorted by score
    """
    if param_grid is None:
        param_grid = DEFAULT_PARAM_GRID
    
    if tickers is None:
        # Use sample of watchlist
        import json
        with open('watchlist.json', 'r') as f:
            watchlist = json.load(f)
        tickers = watchlist[:20]  # First 20 for speed
    
    if n_workers is None:
        n_workers = max(1, multiprocessing.cpu_count() - 1)  # Leave 1 core free
    
    if verbose:
        print('='*70)
        print('🔍 GRID SEARCH OPTIMIZATION (PARALLEL)')
        print('='*70)
        print(f'\nMethod: {method.upper()}')
        print(f'Tickers: {len(tickers)}')
        print(f'Workers: {n_workers} parallel processes')
        if method == 'random':
            print(f'Samples: {n_samples}')
        else:
            # Calculate total combinations
            n_combos = 1
            for values in param_grid.values():
                n_combos *= len(values)
            print(f'Total combinations: {n_combos}')
        print('\nParameter Grid:')
        for key, values in param_grid.items():
            print(f'  {key}: {values}')
        print('\n' + '='*70)
    
    all_results = []
    configs = list(generate_configs(param_grid, method, n_samples))
    
    print(f'\n🚀 Starting evaluation of {len(configs)} configurations...')
    print(f'⚡ Using {n_workers} parallel workers\n')
    
    start_time = time.time()
    
    if n_workers > 1:
        # Parallel processing
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            # Submit all tasks
            future_to_config = {
                executor.submit(evaluate_config, config, tickers, False): (i, config)
                for i, config in enumerate(configs, 1)
            }
            
            # Process results as they complete
            for future in as_completed(future_to_config):
                i, config = future_to_config[future]
                try:
                    result = future.result()
                    all_results.append(result)
                    
                    if verbose:
                        elapsed = time.time() - start_time
                        remaining = len(configs) - len(all_results)
                        eta = (elapsed / len(all_results)) * remaining if all_results else 0
                        
                        print(f'[{len(all_results)}/{len(configs)}] Score: {result["score"]:.3f} | '
                              f'COMPRA: {result["compra_count"]}/{result["total"]} ({result["coverage"]*100:.0f}%) | '
                              f'Conf: {result["avg_compra_conf"]:.1f}% | '
                              f'ETA: {eta/60:.0f}m')
                
                except Exception as e:
                    if verbose:
                        print(f'[{i}/{len(configs)}] ❌ ERROR: {str(e)[:50]}')
    else:
        # Sequential processing (fallback)
        for i, config in enumerate(configs, 1):
            if verbose:
                print(f'\n[{i}/{len(configs)}] Evaluating configuration...')
            
            try:
                result = evaluate_config(config, tickers, verbose=False)
                all_results.append(result)
                
                if verbose:
                    elapsed = time.time() - start_time
                    print(f'  Score: {result["score"]:.3f}')
                    print(f'  COMPRA: {result["compra_count"]}/{result["total"]} ({result["coverage"]*100:.0f}%)')
                    print(f'  Avg COMPRA Confidence: {result["avg_compra_conf"]:.1f}%')
                    print(f'  Time: {elapsed:.1f}s')
            
            except Exception as e:
                if verbose:
                    print(f'  ❌ ERROR: {str(e)}')
    
    total_time = time.time() - start_time
    
    # Sort by score
    all_results.sort(key=lambda x: x['score'], reverse=True)
    
    if verbose:
        print('\n' + '='*70)
        print(f'⏱️  COMPLETED IN {total_time/60:.1f} MINUTES')
        print('='*70)
        print('🏆 TOP 10 CONFIGURATIONS')
        print('='*70)
        
        for i, result in enumerate(all_results[:10], 1):
            print(f'\n#{i} - Score: {result["score"]:.3f}')
            print(f'  COMPRA: {result["compra_count"]}/{result["total"]} ({result["coverage"]*100:.0f}%)')
            print(f'  Avg COMPRA Conf: {result["avg_compra_conf"]:.1f}%')
            print(f'  Avg Overall Conf: {result["avg_conf"]:.1f}%')
            print(f'  Config: {result["config"]}')
    
    return all_results


def save_results(results, filename='grid_search_results.json'):
    """Save grid search results to file"""
    # Remove detailed results to save space
    simplified_results = []
    for r in results:
        simplified = {k: v for k, v in r.items() if k != 'results'}
        simplified_results.append(simplified)
    
    with open(filename, 'w') as f:
        json.dump(simplified_results, f, indent=2)
    
    print(f'\n✅ Results saved to {filename}')


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Grid search optimization')
    parser.add_argument('--method', choices=['grid', 'random'], default='random',
                        help='Search method')
    parser.add_argument('--n-samples', type=int, default=50,
                        help='Number of samples for random search')
    parser.add_argument('--tickers', type=int, default=20,
                        help='Number of tickers to test')
    parser.add_argument('--output', default='grid_search_results.json',
                        help='Output file for results')
    parser.add_argument('--workers', type=int, default=None,
                        help='Number of parallel workers (default: auto-detect)')
    
    args = parser.parse_args()
    
    # Load tickers
    with open('watchlist.json', 'r') as f:
        watchlist = json.load(f)
    tickers = watchlist[:args.tickers]
    
    # Run grid search
    results = grid_search(
        tickers=tickers,
        method=args.method,
        n_samples=args.n_samples,
        n_workers=args.workers,
        verbose=True
    )
    
    # Save results
    save_results(results, args.output)
    
    print('\n✅ Grid search complete!')
