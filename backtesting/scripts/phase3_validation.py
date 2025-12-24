#!/usr/bin/env python3
"""
PHASE 3: Quick Validation Script

Tests Risk Management and Parameter Optimization implementations
without requiring full backtests.

Usage:
    python phase3_validation.py --test risk_management
    python phase3_validation.py --test parameter_optimization
    python phase3_validation.py --test all
"""

import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

class Phase3Validator:
    """Validates Phase 3 implementations"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        
    def test_risk_management(self):
        """Test Risk Management functions"""
        print("\n" + "="*60)
        print("TESTING: Risk Management Functions (Option A)")
        print("="*60)
        
        try:
            from agent_backtester import AgentBacktester
            bt = AgentBacktester()
            
            # Test 1: ATR Calculation
            print("\n[1/8] Testing _calculate_atr()...")
            ticker = 'AAPL'
            try:
                atr = bt._calculate_atr(ticker, periods=14)
                assert isinstance(atr, (int, float)), "ATR must be numeric"
                assert atr > 0, "ATR must be positive"
                print(f"  ✅ ATR for {ticker}: ${atr:.2f}")
                self.results['atr_calculation'] = 'PASS'
            except Exception as e:
                print(f"  ❌ ATR calculation failed: {e}")
                self.errors.append(f"ATR: {e}")
                self.results['atr_calculation'] = 'FAIL'
            
            # Test 2: Position Sizing
            print("\n[2/8] Testing _calculate_position_size()...")
            try:
                atr = bt._calculate_atr(ticker)
                position_size = bt._calculate_position_size(
                    entry_price=100.0,
                    volatility=0.02,
                    atr=atr,
                    max_risk_pct=0.02,
                    account_size=100000
                )
                assert isinstance(position_size, (int, float)), "Position size must be numeric"
                assert position_size > 0, "Position size must be positive"
                print(f"  ✅ Position Size: {position_size:.0f} shares")
                self.results['position_sizing'] = 'PASS'
            except Exception as e:
                print(f"  ❌ Position sizing failed: {e}")
                self.errors.append(f"Position Sizing: {e}")
                self.results['position_sizing'] = 'FAIL'
            
            # Test 3: Stop Loss Calculation
            print("\n[3/8] Testing _get_stop_loss_price()...")
            try:
                atr = bt._calculate_atr(ticker)
                sl_price = bt._get_stop_loss_price(
                    entry_price=100.0,
                    atr=atr,
                    volatility=0.02,
                    ticker=ticker
                )
                assert isinstance(sl_price, (int, float)), "SL price must be numeric"
                assert sl_price < 100.0, "SL should be below entry price"
                print(f"  ✅ Stop Loss Price: ${sl_price:.2f} (from entry $100.00)")
                self.results['stop_loss_calc'] = 'PASS'
            except Exception as e:
                print(f"  ❌ Stop loss calculation failed: {e}")
                self.errors.append(f"Stop Loss: {e}")
                self.results['stop_loss_calc'] = 'FAIL'
            
            # Test 4: Take Profit Calculation
            print("\n[4/8] Testing _get_take_profit_price()...")
            try:
                tp_price = bt._get_take_profit_price(
                    entry_price=100.0,
                    ticker=ticker,
                    volatility=0.02
                )
                assert isinstance(tp_price, (int, float)), "TP price must be numeric"
                assert tp_price > 100.0, "TP should be above entry price"
                print(f"  ✅ Take Profit Price: ${tp_price:.2f} (from entry $100.00)")
                self.results['take_profit_calc'] = 'PASS'
            except Exception as e:
                print(f"  ❌ Take profit calculation failed: {e}")
                self.errors.append(f"Take Profit: {e}")
                self.results['take_profit_calc'] = 'FAIL'
            
            # Test 5: Stop Loss Check
            print("\n[5/8] Testing _check_stop_loss()...")
            try:
                should_exit, reason = bt._check_stop_loss(
                    ticker=ticker,
                    current_price=95.0,  # Below SL
                    stop_loss_price=96.0
                )
                assert should_exit == True, "Should exit when below SL"
                assert isinstance(reason, str), "Reason must be string"
                print(f"  ✅ SL Check: {reason}")
                self.results['stop_loss_check'] = 'PASS'
            except Exception as e:
                print(f"  ❌ Stop loss check failed: {e}")
                self.errors.append(f"SL Check: {e}")
                self.results['stop_loss_check'] = 'FAIL'
            
            # Test 6: Take Profit Check
            print("\n[6/8] Testing _check_take_profit()...")
            try:
                should_exit, reason = bt._check_take_profit(
                    ticker=ticker,
                    current_price=105.0,  # Above TP
                    take_profit_price=104.0
                )
                assert should_exit == True, "Should exit when above TP"
                assert isinstance(reason, str), "Reason must be string"
                print(f"  ✅ TP Check: {reason}")
                self.results['take_profit_check'] = 'PASS'
            except Exception as e:
                print(f"  ❌ Take profit check failed: {e}")
                self.errors.append(f"TP Check: {e}")
                self.results['take_profit_check'] = 'FAIL'
            
            # Test 7: Max Drawdown
            print("\n[7/8] Testing _calculate_max_drawdown()...")
            try:
                max_dd, dd_date = bt._calculate_max_drawdown()
                assert isinstance(max_dd, (int, float)), "Max DD must be numeric"
                assert max_dd >= 0, "Max DD must be non-negative"
                assert isinstance(dd_date, str), "DD date must be string"
                print(f"  ✅ Max Drawdown: {max_dd:.2f}% on {dd_date}")
                self.results['max_drawdown'] = 'PASS'
            except Exception as e:
                print(f"  ❌ Max drawdown calculation failed: {e}")
                self.errors.append(f"Max Drawdown: {e}")
                self.results['max_drawdown'] = 'FAIL'
            
            # Test 8: Calmar Ratio
            print("\n[8/8] Testing _calculate_calmar_ratio()...")
            try:
                calmar = bt._calculate_calmar_ratio(returns_annual=0.15)
                assert isinstance(calmar, (int, float)), "Calmar must be numeric"
                print(f"  ✅ Calmar Ratio: {calmar:.2f}")
                self.results['calmar_ratio'] = 'PASS'
            except Exception as e:
                print(f"  ❌ Calmar ratio calculation failed: {e}")
                self.errors.append(f"Calmar: {e}")
                self.results['calmar_ratio'] = 'FAIL'
            
            # Summary
            passed = sum(1 for v in self.results.values() if v == 'PASS')
            total = len(self.results)
            print(f"\n✅ Risk Management Tests: {passed}/{total} PASSED")
            
            return passed == total
            
        except ImportError as e:
            print(f"❌ Could not import agent_backtester: {e}")
            return False
    
    def test_parameter_optimization(self):
        """Test Parameter Optimization functions"""
        print("\n" + "="*60)
        print("TESTING: Parameter Optimization Framework (Option D)")
        print("="*60)
        
        try:
            from parameter_optimizer import ParameterOptimizer
            
            optimizer = ParameterOptimizer(strategy_name="phase3_test")
            
            # Test 1: Grid Search Thresholds
            print("\n[1/4] Testing grid_search_thresholds()...")
            try:
                result = optimizer.grid_search_thresholds(
                    buy_range=(35, 45, 5),    # 35, 40, 45
                    sell_range=(55, 65, 5),   # 55, 60, 65
                    ticker='AAPL'
                )
                assert 'best_params' in result, "Should return best_params"
                assert 'top_10' in result, "Should return top_10 results"
                assert len(result['top_10']) > 0, "Should have results"
                print(f"  ✅ Grid Search: Found {len(result['top_10'])} parameter sets")
                print(f"     Best Parameters: Buy={result['best_params']['buy_threshold']}, "
                      f"Sell={result['best_params']['sell_threshold']}")
                self.results['grid_search'] = 'PASS'
            except Exception as e:
                print(f"  ❌ Grid search failed: {e}")
                self.errors.append(f"Grid Search: {e}")
                self.results['grid_search'] = 'FAIL'
            
            # Test 2: Category-Based Optimization
            print("\n[2/4] Testing grid_search_by_category()...")
            try:
                result = optimizer.grid_search_by_category({
                    'ultra_conservative': ['META'],
                    'conservative': ['MSFT'],
                    'aggressive': ['TSLA'],
                    'normal': ['AAPL']
                })
                assert 'ultra_conservative' in result, "Should have ultra_conservative"
                assert 'conservative' in result, "Should have conservative"
                assert 'aggressive' in result, "Should have aggressive"
                assert 'normal' in result, "Should have normal"
                print(f"  ✅ Category Optimization: Found parameters for 4 categories")
                for cat, params in result.items():
                    print(f"     {cat.upper()}: Buy={params.get('buy_threshold')}, "
                          f"Sell={params.get('sell_threshold')}")
                self.results['category_optimization'] = 'PASS'
            except Exception as e:
                print(f"  ❌ Category optimization failed: {e}")
                self.errors.append(f"Category Optimization: {e}")
                self.results['category_optimization'] = 'FAIL'
            
            # Test 3: Walk-Forward Validation
            print("\n[3/4] Testing walk_forward_test()...")
            try:
                result = optimizer.walk_forward_test(
                    start_date='2024-06-26',
                    end_date='2025-12-23',
                    optimization_window=60,
                    step_size=20,  # Larger step for fewer iterations
                    ticker='AAPL'
                )
                assert isinstance(result, list), "Should return list of iterations"
                assert len(result) > 0, "Should have iterations"
                
                # Check structure
                first_iter = result[0]
                assert 'in_sample_return' in first_iter, "Should have in_sample_return"
                assert 'out_sample_return' in first_iter, "Should have out_sample_return"
                
                print(f"  ✅ Walk-Forward Test: {len(result)} iterations completed")
                avg_is = np.mean([r['in_sample_return'] for r in result])
                avg_oos = np.mean([r['out_sample_return'] for r in result])
                print(f"     In-Sample Avg: {avg_is:.2%}")
                print(f"     Out-of-Sample Avg: {avg_oos:.2%}")
                self.results['walk_forward'] = 'PASS'
            except Exception as e:
                print(f"  ❌ Walk-forward test failed: {e}")
                self.errors.append(f"Walk-Forward: {e}")
                self.results['walk_forward'] = 'FAIL'
            
            # Test 4: Sensitivity Analysis
            print("\n[4/4] Testing sensitivity_analysis()...")
            try:
                result = optimizer.sensitivity_analysis(
                    base_parameters={'buy_threshold': 40, 'sell_threshold': 60},
                    parameter_ranges={
                        'buy_threshold': [35, 40, 45],
                        'sell_threshold': [55, 60, 65]
                    },
                    ticker='AAPL'
                )
                assert isinstance(result, dict), "Should return dict"
                assert 'buy_threshold' in result, "Should have buy_threshold sensitivity"
                assert 'sell_threshold' in result, "Should have sell_threshold sensitivity"
                print(f"  ✅ Sensitivity Analysis: Analyzed {len(result)} parameters")
                self.results['sensitivity_analysis'] = 'PASS'
            except Exception as e:
                print(f"  ❌ Sensitivity analysis failed: {e}")
                self.errors.append(f"Sensitivity: {e}")
                self.results['sensitivity_analysis'] = 'FAIL'
            
            # Summary
            passed = sum(1 for v in self.results.values() if v == 'PASS')
            total = len(self.results)
            print(f"\n✅ Parameter Optimization Tests: {passed}/{total} PASSED")
            
            return passed == total
            
        except ImportError as e:
            print(f"❌ Could not import parameter_optimizer: {e}")
            return False
    
    def test_syntax(self):
        """Check Python syntax for both files"""
        print("\n" + "="*60)
        print("CHECKING: Python Syntax")
        print("="*60)
        
        import py_compile
        
        files_to_check = [
            'agent_backtester.py',
            'parameter_optimizer.py'
        ]
        
        all_valid = True
        for filepath in files_to_check:
            full_path = f'/Users/carlosfuentes/GitHub/spectral-galileo/{filepath}'
            try:
                py_compile.compile(full_path, doraise=True)
                print(f"  ✅ {filepath}: Syntax OK")
                self.results[f'{filepath}_syntax'] = 'PASS'
            except py_compile.PyCompileError as e:
                print(f"  ❌ {filepath}: Syntax Error")
                print(f"     {e}")
                self.results[f'{filepath}_syntax'] = 'FAIL'
                all_valid = False
        
        return all_valid
    
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)
        
        passed = sum(1 for v in self.results.values() if v == 'PASS')
        total = len(self.results)
        pct = (passed / total * 100) if total > 0 else 0
        
        print(f"\nSummary: {passed}/{total} tests passed ({pct:.0f}%)")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        print(f"\nDetailed Results:")
        for test_name, result in self.results.items():
            status = "✅" if result == 'PASS' else "❌"
            print(f"  {status} {test_name}: {result}")
        
        # Overall status
        print("\n" + "="*60)
        if pct >= 80:
            print("✅ VALIDATION SUCCESSFUL - Ready for integration!")
        else:
            print("❌ VALIDATION FAILED - Review errors above")
        print("="*60)
        
        return pct >= 80

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Phase 3 Validation Script')
    parser.add_argument(
        '--test',
        choices=['syntax', 'risk_management', 'parameter_optimization', 'all'],
        default='all',
        help='Which tests to run'
    )
    
    args = parser.parse_args()
    
    validator = Phase3Validator()
    
    print("\n" + "="*60)
    print("PHASE 3: IMPLEMENTATION VALIDATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run requested tests
    if args.test in ['syntax', 'all']:
        validator.test_syntax()
    
    if args.test in ['risk_management', 'all']:
        validator.test_risk_management()
    
    if args.test in ['parameter_optimization', 'all']:
        validator.test_parameter_optimization()
    
    # Generate report
    success = validator.generate_report()
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
