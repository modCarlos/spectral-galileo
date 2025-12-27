"""
Threshold Adjustment Validation Script
Tests the impact of adjusted thresholds on key tickers
"""

import agent
import pandas as pd

def test_adjusted_thresholds():
    """Test key tickers with adjusted thresholds"""
    
    test_tickers = [
        ('NVDA', 'High insider selling ($557M)', 27.4, 30),  # Expected higher
        ('WMT', 'Moderate insider + MTF', 34.7, 37),  # Expected higher
        ('AAPL', 'Moderate insider ($58M)', 26.4, 29),  # Expected higher
        ('JNJ', 'No warnings', 40.1, 40),  # Should stay same
        ('AMD', 'Was COMPRA→NEUTRAL', 22.0, 25),  # Expected to stay COMPRA
    ]
    
    print('='*70)
    print('🔧 THRESHOLD ADJUSTMENT VALIDATION')
    print('='*70)
    print('\nAdjustments Applied:')
    print('  1. Insider selling threshold: $1M→$5M (moderate), $5M→$10M (heavy)')
    print('  2. MTF_DISAGREE penalty: -15% → -10%')
    print('\n' + '='*70)
    print(f"{'Ticker':<8} {'Old Conf':<10} {'New Conf':<10} {'Change':<10} {'Status'}")
    print('='*70)
    
    results = []
    
    for ticker, desc, old_conf, expected_conf in test_tickers:
        try:
            trading_agent = agent.FinancialAgent(ticker, is_short_term=False)
            analysis = trading_agent.run_analysis()
            
            if analysis and 'strategy' in analysis:
                strategy = analysis['strategy']
                new_conf = strategy.get('confidence', 0)
                verdict = strategy.get('verdict', 'N/A')
                change = new_conf - old_conf
                
                # Check if meets expectations
                if new_conf >= expected_conf - 2:  # Allow 2% tolerance
                    status = '✅'
                else:
                    status = '⚠️'
                
                print(f"{ticker:<8} {old_conf:>6.1f}%    {new_conf:>6.1f}%    {change:>+5.1f}%    {status} {verdict}")
                
                results.append({
                    'ticker': ticker,
                    'old': old_conf,
                    'new': new_conf,
                    'change': change,
                    'verdict': verdict,
                    'expected': expected_conf
                })
            else:
                print(f"{ticker:<8} {old_conf:>6.1f}%    ERROR                ❌")
                
        except Exception as e:
            print(f"{ticker:<8} {old_conf:>6.1f}%    ERROR: {str(e)[:20]:<20} ❌")
    
    print('='*70)
    
    if results:
        avg_change = sum(r['change'] for r in results) / len(results)
        print(f'\n📊 Average confidence change: {avg_change:+.1f}%')
        print(f'✅ Successful tests: {len(results)}/{len(test_tickers)}')
        
        # Check if improvements worked
        improved = sum(1 for r in results if r['new'] >= r['old'])
        print(f'📈 Improved or maintained: {improved}/{len(results)} ({improved/len(results)*100:.0f}%)')
        
        if avg_change > 1:
            print('\n✅ ADJUSTMENTS SUCCESSFUL - Average confidence increased!')
        elif avg_change > -1:
            print('\n✅ ADJUSTMENTS NEUTRAL - Confidence maintained')
        else:
            print('\n⚠️ ADJUSTMENTS TOO AGGRESSIVE - Need fine-tuning')
    
    return results

if __name__ == '__main__':
    test_adjusted_thresholds()
