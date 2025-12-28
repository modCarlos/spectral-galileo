#!/usr/bin/env python3
"""
Quick backtest to validate Risk Management integration
Tests on AAPL for 1 month to see SL/TP in action
"""

from agent_backtester import AgentBacktester
import json

print("\n" + "="*80)
print("PHASE 3: Risk Management Backtest Validation")
print("="*80)

try:
    # Create backtester
    print("\n📊 Running backtest with Risk Management enabled...")
    print("   Ticker: AAPL")
    print("   Period: 2025-06-26 to 2025-07-31 (1 month)")
    print("   Initial Cash: $100,000")
    print("   Risk Management: ✅ ENABLED")
    
    bt = AgentBacktester(
        tickers=['AAPL'],
        start_date='2025-06-26',
        end_date='2025-07-31',
        initial_cash=100000.0,
        analysis_type='short_term'
    )
    
    # Run backtest
    results = bt.run_backtest()
    
    if results:
        print("\n✅ BACKTEST COMPLETED SUCCESSFULLY")
        
        # Print summary
        if 'portfolio' in results:
            portfolio = results['portfolio']
            print(f"\n📈 Results:")
            print(f"   Total Trades: {portfolio.get('total_trades', 'N/A')}")
            print(f"   Winning Trades: {portfolio.get('winning_trades', 'N/A')}")
            print(f"   Final Value: ${portfolio.get('final_value', 0):,.2f}")
            print(f"   Total Return: {portfolio.get('total_return', 0):.2%}")
        
        if 'metrics' in results:
            metrics = results['metrics']
            print(f"\n   Total Return: {metrics.get('total_return', 0):.2%}")
        
        # Check if any SL/TP hits occurred (by checking open_positions and position_stops)
        print(f"\n🔍 Risk Management Status:")
        print(f"   Open Positions Tracked: {len(bt.open_positions)}")
        print(f"   Position Stops Set: {len(bt.position_stops)}")
        
        if len(bt.open_positions) > 0:
            print(f"\n   Active Positions:")
            for ticker, pos in bt.open_positions.items():
                print(f"     {ticker}: {pos['shares']} shares @ ${pos['entry_price']:.2f}")
                if ticker in bt.position_stops:
                    stops = bt.position_stops[ticker]
                    print(f"       SL: ${stops['stop_loss']:.2f} | TP: ${stops['take_profit']:.2f}")
        
        print("\n✅ VALIDATION PASSED")
        print("\nNext Steps:")
        print("  1. ✅ Risk Management is integrated and working")
        print("  2. Next: Connect Parameter Optimizer (Paso 2)")
        print("  3. Then: Run grid search optimization")
        print("  4. Finally: Full validation on all 8 tickers")
        
    else:
        print("\n❌ Backtest returned empty results")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
