#!/usr/bin/env python3
"""
Final Backtesting with All Optimizations Applied
Phase 1-3 complete: Multi-timeframe, External Data, Grid Search, Category Thresholds
"""

import json
from src.spectral_galileo.core import agent
import time
from datetime import datetime
import numpy as np

def main():
    # Load watchlist
    with open('watchlist.json', 'r') as f:
        tickers = json.load(f)
    
    print('='*70)
    print('🚀 FINAL BACKTESTING - All Optimizations Applied')
    print('='*70)
    print(f'\n📊 Testing {len(tickers)} tickers...\n')
    
    results = []
    compra_count = 0
    neutral_count = 0
    venta_count = 0
    start_time = time.time()
    
    for i, ticker in enumerate(tickers, 1):
        print(f'[{i}/{len(tickers)}] {ticker:6s}', end=' ')
        
        try:
            # Use skip_external_data=True for fast backtesting
            trading_agent = agent.FinancialAgent(ticker, is_short_term=False, skip_external_data=True)
            result = trading_agent.run_analysis()
            
            if result and 'strategy' in result:
                strategy = result['strategy']
                verdict = strategy.get('verdict', 'N/A')
                confidence = strategy.get('confidence', 0)
                
                # Get category info
                close_prices = trading_agent.data['Close'].values[-21:]
                returns = np.diff(close_prices) / close_prices[:-1]
                volatility = np.std(returns) * np.sqrt(252)
                
                from src.spectral_galileo.core.agent import categorize_stock_for_thresholds
                category = categorize_stock_for_thresholds(volatility, ticker)
                
                results.append({
                    'ticker': ticker,
                    'verdict': verdict,
                    'confidence': confidence,
                    'category': category,
                    'volatility': volatility * 100
                })
                
                # Count verdicts
                if 'COMPRA' in verdict:
                    compra_count += 1
                    emoji = '🟢'
                elif 'NEUTRAL' in verdict:
                    neutral_count += 1
                    emoji = '⚪'
                else:
                    venta_count += 1
                    emoji = '🔴'
                
                print(f'{emoji} {verdict:20s} {confidence:5.1f}% ({category})')
            else:
                print('❌ No results')
                
        except Exception as e:
            print(f'❌ Error: {str(e)[:40]}')
        
        time.sleep(0.5)  # Rate limiting
    
    elapsed = time.time() - start_time
    
    # Save results
    output_file = f'final_backtesting_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print('\n' + '='*70)
    print('📊 FINAL RESULTS SUMMARY')
    print('='*70)
    print(f'\nTotal tickers analyzed: {len(results)}')
    print(f'  COMPRA signals:  {compra_count} ({compra_count/len(results)*100:.1f}%)')
    print(f'  NEUTRAL signals: {neutral_count} ({neutral_count/len(results)*100:.1f}%)')
    print(f'  VENTA signals:   {venta_count} ({venta_count/len(results)*100:.1f}%)')
    
    # Calculate average confidence by verdict
    compra_confidences = [r['confidence'] for r in results if 'COMPRA' in r['verdict']]
    if compra_confidences:
        print(f'\nAvg COMPRA confidence: {sum(compra_confidences)/len(compra_confidences):.1f}%')
    
    # Category breakdown
    print('\nBy Category:')
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)
    
    for cat, items in sorted(categories.items()):
        compra_in_cat = sum(1 for r in items if 'COMPRA' in r['verdict'])
        print(f'  {cat:20s}: {compra_in_cat}/{len(items)} COMPRA')
    
    print(f'\n⏱️  Completed in {elapsed/60:.1f} minutes')
    print(f'📁 Results saved to {output_file}')
    print('='*70)

if __name__ == '__main__':
    main()
