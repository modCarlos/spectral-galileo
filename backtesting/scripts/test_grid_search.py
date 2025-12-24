#!/usr/bin/env python3
"""
PHASE 3: Paso 3 - Grid Search Test
Tests parameter optimization on AAPL ticker
"""

from parameter_optimizer import ParameterOptimizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("PHASE 3: Paso 3 - Grid Search Optimization Test")
print("="*80)

try:
    print("\n📊 Initializing Parameter Optimizer...")
    optimizer = ParameterOptimizer(strategy_name="phase3_grid_search")
    
    print("\n🔍 Running grid search on AAPL (small ranges for quick test)...")
    print("   Buy Range: 35-45 (step 5) → 3 values")
    print("   Sell Range: 55-65 (step 5) → 3 values")
    print("   Total Combinations: 9 tests")
    print("   Expected Time: 5-10 minutes")
    
    # Run grid search with small ranges for quick testing
    results = optimizer.grid_search_thresholds(
        buy_range=(35, 45, 5),      # 35, 40, 45
        sell_range=(55, 65, 5),     # 55, 60, 65
        ticker='AAPL'
    )
    
    if results and 'best_params' in results:
        print("\n✅ GRID SEARCH COMPLETED SUCCESSFULLY")
        
        best = results['best_params']
        print(f"\n🏆 Best Parameters Found:")
        print(f"   Buy Threshold: {best.get('buy_threshold', 'N/A')}")
        print(f"   Sell Threshold: {best.get('sell_threshold', 'N/A')}")
        print(f"   Return: {best.get('return', 0):.2%}")
        print(f"   Sharpe Ratio: {best.get('sharpe', 0):.2f}")
        print(f"   Max Drawdown: {best.get('max_drawdown', 0):.2%}")
        
        if 'top_10' in results and len(results['top_10']) > 0:
            print(f"\n📊 Top 10 Parameter Sets:")
            print(f"   {'Rank':<6} {'Buy':<6} {'Sell':<6} {'Return':<10} {'Sharpe':<8} {'Drawdown':<10}")
            print(f"   {'-'*50}")
            
            for i, params in enumerate(results['top_10'][:5], 1):
                buy = params.get('buy_threshold', 'N/A')
                sell = params.get('sell_threshold', 'N/A')
                ret = params.get('return', 0)
                sharpe = params.get('sharpe', 0)
                dd = params.get('max_drawdown', 0)
                print(f"   {i:<6} {buy:<6} {sell:<6} {ret:<10.2%} {sharpe:<8.2f} {dd:<10.2%}")
        
        print("\n✅ VALIDATION PASSED")
        print("\nNext Steps:")
        print("  1. ✅ Parameter Optimizer connected")
        print("  2. ✅ Grid Search working")
        print("  3. Next: Run full grid search on all 4 categories")
        print("  4. Then: Walk-forward validation")
        print("  5. Finally: Full testing on 8 tickers")
    else:
        print("\n⚠️  Grid search returned unexpected format")
        print(f"Results keys: {results.keys() if results else 'None'}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
