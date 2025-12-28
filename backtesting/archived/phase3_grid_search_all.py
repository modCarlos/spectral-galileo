#!/usr/bin/env python3
"""
Phase 3: Complete Grid Search Optimization for all ticker categories
Tests parameter combinations for each risk category and finds optimal thresholds
"""

import sys
import logging
import os
from datetime import datetime
from parameter_optimizer import ParameterOptimizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_category_grid_search():
    """
    Run grid search optimization for all ticker categories
    """
    
    # Define ticker categories (from agent.py)
    tickers_by_category = {
        'ultra_conservative': ['META', 'AMZN'],
        'conservative': ['MSFT', 'NVDA'],
        'normal': ['AAPL', 'GOOGL'],
        'aggressive': ['PLTR', 'TSLA']
    }
    
    print("\n" + "="*80)
    print("PHASE 3: COMPLETE GRID SEARCH OPTIMIZATION")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Setup optimizer
    optimizer = ParameterOptimizer(
        strategy_name='agent_backtester',
        results_dir='./optimization_results'
    )
    
    print(f"\nTickers by Category:")
    for cat, tickers in tickers_by_category.items():
        print(f"  {cat}: {', '.join(tickers)}")
    
    print("\n🔍 Starting grid search optimization...")
    
    try:
        # Run category-based grid search
        results = optimizer.grid_search_by_category(tickers_by_category)
        
        # Print results
        print("\n" + "="*80)
        print("GRID SEARCH RESULTS - OPTIMAL PARAMETERS BY CATEGORY")
        print("="*80)
        
        if results:
            for category, params in results.items():
                print(f"\n{category.upper()}:")
                print(f"  Buy Threshold: {params.get('buy_threshold', 'N/A')}")
                print(f"  Sell Threshold: {params.get('sell_threshold', 'N/A')}")
                if isinstance(params, dict):
                    for key, value in params.items():
                        if key not in ['buy_threshold', 'sell_threshold']:
                            print(f"  {key}: {value}")
        
        print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print("✅ Grid search complete!")
        print("="*80)
        
        return results
        
    except Exception as e:
        print(f"❌ Error during grid search: {str(e)}")
        logger.error("Grid search failed", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        results = run_category_grid_search()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n❌ Grid search interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Grid search failed: {str(e)}")
        logger.error("Grid search failed", exc_info=True)
        sys.exit(1)
