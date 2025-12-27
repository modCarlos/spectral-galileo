#!/usr/bin/env python3
"""
Phase 4A Integration Test
Test ST scoring with real tickers to validate:
1. RSI correction (oversold = BUY)
2. Optimized weights (50/35/15)
3. Dynamic thresholds by category
4. Confidence score
"""

import sys
from src.spectral_galileo.core.agent import FinancialAgent

def test_ticker(ticker: str, is_short_term: bool = True):
    print(f"\n{'='*60}")
    print(f"Testing {ticker} ({'SHORT-TERM' if is_short_term else 'LONG-TERM'})")
    print(f"{'='*60}")
    
    try:
        agent = FinancialAgent(ticker, is_short_term=is_short_term)
        result = agent.run_analysis()
        
        if "error" in result:
            print(f"❌ ERROR: {result['error']}")
            return
        
        # Extract key metrics
        verdict = result.get('strategy', {}).get('verdict', 'N/A')
        confidence = result.get('strategy', {}).get('confidence', 'N/A')
        
        print(f"\n📊 RESULTADO:")
        print(f"   Veredicto: {verdict}")
        print(f"   Confidence: {confidence:.1f}%" if isinstance(confidence, (int, float)) else f"   Confidence: {confidence}")
        
        # Display technical breakdown if available
        tech_summary = result.get('technical_summary', {})
        if tech_summary and isinstance(tech_summary, dict):
            print(f"\n🔧 TECHNICAL BREAKDOWN:")
            for key, value in tech_summary.items():
                print(f"   {key}: {value}")
        
        # Show pros/cons
        pros = result.get('pros', [])
        cons = result.get('cons', [])
        
        if pros:
            print(f"\n✅ PROS ({len(pros)}):")
            for pro in pros[:5]:  # Show top 5
                print(f"   • {pro}")
        
        if cons:
            print(f"\n⚠️  CONS ({len(cons)}):")
            for con in cons[:5]:  # Show top 5
                print(f"   • {con}")
        
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🚀 PHASE 4A INTEGRATION TEST")
    print("Testing optimized ST scoring with real market data\n")
    
    # Test different stock categories
    test_cases = [
        ("PLTR", True),   # High volatility (threshold 43/57)
        ("META", True),   # Ultra-conservative (threshold 35/65)
        ("AAPL", True),   # Normal (threshold 42/58)
    ]
    
    for ticker, is_st in test_cases:
        test_ticker(ticker, is_st)
    
    print("\n✅ Phase 4A integration test complete!")
