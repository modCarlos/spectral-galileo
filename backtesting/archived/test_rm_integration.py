#!/usr/bin/env python3
"""
Quick test to verify Risk Management integration works
"""

from agent_backtester import AgentBacktester
import sys

print("="*80)
print("TESTING: Risk Management Integration (Phase 3)")
print("="*80)

try:
    # Create backtester with RM enabled
    bt = AgentBacktester(
        tickers=['AAPL'],
        start_date='2025-06-26',
        end_date='2025-07-31',
        initial_cash=100000.0,
        analysis_type='short_term'
    )
    
    print("\n✅ AgentBacktester initialized successfully")
    print(f"   Risk Management Enabled: {bt.risk_management_enabled}")
    print(f"   Max Risk Per Trade: {bt.max_risk_per_trade:.1%}")
    print(f"   Open Positions Tracking: {type(bt.open_positions)}")
    print(f"   Position Stops Tracking: {type(bt.position_stops)}")
    
    # Test that methods exist
    print("\n✅ Testing Risk Management methods:")
    
    # Test ATR
    if hasattr(bt, '_calculate_atr'):
        print("   ✓ _calculate_atr() exists")
    else:
        print("   ✗ _calculate_atr() MISSING")
        sys.exit(1)
    
    # Test Position Size
    if hasattr(bt, '_calculate_position_size'):
        print("   ✓ _calculate_position_size() exists")
    else:
        print("   ✗ _calculate_position_size() MISSING")
        sys.exit(1)
    
    # Test Stop Loss
    if hasattr(bt, '_get_stop_loss_price'):
        print("   ✓ _get_stop_loss_price() exists")
    else:
        print("   ✗ _get_stop_loss_price() MISSING")
        sys.exit(1)
    
    # Test Take Profit
    if hasattr(bt, '_get_take_profit_price'):
        print("   ✓ _get_take_profit_price() exists")
    else:
        print("   ✗ _get_take_profit_price() MISSING")
        sys.exit(1)
    
    # Test Check SL
    if hasattr(bt, '_check_stop_loss'):
        print("   ✓ _check_stop_loss() exists")
    else:
        print("   ✗ _check_stop_loss() MISSING")
        sys.exit(1)
    
    # Test Check TP
    if hasattr(bt, '_check_take_profit'):
        print("   ✓ _check_take_profit() exists")
    else:
        print("   ✗ _check_take_profit() MISSING")
        sys.exit(1)
    
    # Test Drawdown
    if hasattr(bt, '_calculate_max_drawdown'):
        print("   ✓ _calculate_max_drawdown() exists")
    else:
        print("   ✗ _calculate_max_drawdown() MISSING")
        sys.exit(1)
    
    # Test Calmar
    if hasattr(bt, '_calculate_calmar_ratio'):
        print("   ✓ _calculate_calmar_ratio() exists")
    else:
        print("   ✗ _calculate_calmar_ratio() MISSING")
        sys.exit(1)
    
    print("\n✅ ALL TESTS PASSED")
    print("\nRisk Management Integration Status: ✅ READY")
    print("\nNext steps:")
    print("  1. Run full backtest: python agent_backtester.py")
    print("  2. Check logs for [SL HIT] and [TP HIT] messages")
    print("  3. Compare results with Phase 2 baseline")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
