"""
Backtesting Comparison Script
Compares agent performance BEFORE (main branch) vs AFTER (with Phase 1+2 improvements)
"""

import json
import pandas as pd
from datetime import datetime
from src.spectral_galileo.core import agent
import sys
import time

def run_watchlist_analysis(output_file='backtesting_comparison_new.csv'):
    """
    Run agent analysis on entire watchlist and save results
    """
    
    # Load watchlist
    with open('watchlist.json', 'r') as f:
        tickers = json.load(f)
    
    print(f"🔍 Analyzing {len(tickers)} tickers from watchlist...")
    print(f"📊 This will take approximately {len(tickers) * 10 / 60:.1f} minutes\n")
    
    results = []
    
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] Analyzing {ticker}...")
        
        try:
            # Run agent
            trading_agent = agent.FinancialAgent(ticker, is_short_term=False)
            analysis = trading_agent.run_analysis()
            
            if 'error' in analysis:
                print(f"  ❌ Error: {analysis['error']}")
                results.append({
                    'ticker': ticker,
                    'error': str(analysis['error']),
                    'verdict': 'ERROR',
                    'confidence': 0,
                    'regime': None,
                    'mtf_signal': None,
                    'mtf_confluence': 0,
                    'reddit_mentions': 0,
                    'reddit_sentiment': None,
                    'earnings_trend': None,
                    'earnings_beat_streak': 0,
                    'insider_sentiment': None,
                    'insider_net_value': 0,
                    'confluence_score': 0,
                    'warnings': ''
                })
                continue
            
            # Extract key metrics
            strategy = analysis.get('strategy', {})
            advanced = analysis.get('advanced', {})
            
            verdict = strategy.get('verdict', 'N/A')
            confidence = strategy.get('confidence', 0)
            pros = strategy.get('pros', [])
            cons = strategy.get('cons', [])
            
            # Multi-timeframe
            mtf = advanced.get('multi_timeframe', {})
            mtf_confluence = mtf.get('confluence', {})
            mtf_signal = mtf_confluence.get('overall_signal', 'N/A') if mtf_confluence else 'N/A'
            mtf_score = mtf_confluence.get('score', 0) if mtf_confluence else 0
            
            # Market regime
            regime = advanced.get('market_regime', {})
            regime_state = regime.get('regime', 'N/A') if regime else 'N/A'
            
            # Reddit
            reddit = advanced.get('reddit_sentiment', {})
            reddit_mentions = reddit.get('mentions', 0) if reddit else 0
            reddit_sentiment = reddit.get('sentiment', 'N/A') if reddit else 'N/A'
            
            # Earnings
            earnings = advanced.get('earnings_calendar', {})
            earnings_trend = earnings.get('earnings_trend', 'N/A') if earnings else 'N/A'
            earnings_beat_streak = earnings.get('beat_streak', 0) if earnings else 0
            days_to_earnings = earnings.get('days_to_earnings', None) if earnings else None
            
            # Insider
            insider = advanced.get('insider_trading', {})
            insider_sentiment = insider.get('insider_sentiment', 'N/A') if insider else 'N/A'
            insider_net_value = insider.get('net_value', 0) if insider else 0
            
            # Confluence
            confluence_score = advanced.get('confluence_score', 0)
            
            # Collect warnings
            warnings = []
            for con in cons:
                if 'Timeframes en desacuerdo' in con:
                    warnings.append('MTF_DISAGREE')
                if 'Earnings en' in con and 'días' in con:
                    warnings.append('PRE_EARNINGS')
                if 'insider selling' in con.lower():
                    warnings.append('INSIDER_SELLING')
                if 'Bear Market' in con:
                    warnings.append('BEAR_MARKET')
                if 'Death Cross' in con:
                    warnings.append('DEATH_CROSS')
                if 'Reddit' in con and 'BEARISH' in con:
                    warnings.append('REDDIT_BEARISH')
            
            result = {
                'ticker': ticker,
                'error': None,
                'verdict': verdict,
                'confidence': round(confidence, 1),
                'regime': regime_state,
                'mtf_signal': mtf_signal,
                'mtf_confluence': round(mtf_score, 0),
                'reddit_mentions': reddit_mentions,
                'reddit_sentiment': reddit_sentiment,
                'earnings_trend': earnings_trend,
                'earnings_beat_streak': earnings_beat_streak,
                'days_to_earnings': days_to_earnings,
                'insider_sentiment': insider_sentiment,
                'insider_net_value_millions': round(insider_net_value / 1e6, 1) if insider_net_value else 0,
                'confluence_score': round(confluence_score, 0) if confluence_score else 0,
                'warnings': '|'.join(warnings) if warnings else 'NONE',
                'pros_count': len(pros),
                'cons_count': len(cons)
            }
            
            results.append(result)
            print(f"  ✅ {verdict} ({confidence:.0f}%) | Warnings: {len(warnings)}")
            
            # Small delay to avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            results.append({
                'ticker': ticker,
                'error': str(e),
                'verdict': 'EXCEPTION',
                'confidence': 0,
                'regime': None,
                'mtf_signal': None,
                'mtf_confluence': 0,
                'reddit_mentions': 0,
                'reddit_sentiment': None,
                'earnings_trend': None,
                'earnings_beat_streak': 0,
                'days_to_earnings': None,
                'insider_sentiment': None,
                'insider_net_value_millions': 0,
                'confluence_score': 0,
                'warnings': 'EXCEPTION',
                'pros_count': 0,
                'cons_count': 0
            })
    
    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Analysis complete!")
    print(f"📊 Results saved to: {output_file}")
    print(f"{'='*60}\n")
    
    # Summary statistics
    successful = len([r for r in results if not r['error']])
    errors = len(results) - successful
    
    print("📈 SUMMARY:")
    print(f"  • Total tickers: {len(results)}")
    print(f"  • Successful: {successful}")
    print(f"  • Errors: {errors}")
    
    if successful > 0:
        verdicts = df[df['error'].isna()]['verdict'].value_counts()
        print(f"\n  Verdicts:")
        for verdict, count in verdicts.items():
            print(f"    - {verdict}: {count}")
        
        avg_confidence = df[df['error'].isna()]['confidence'].mean()
        print(f"\n  Average Confidence: {avg_confidence:.1f}%")
        
        warnings_total = len([r for r in results if r['warnings'] not in ['NONE', 'EXCEPTION', '']])
        print(f"  Tickers with Warnings: {warnings_total} ({warnings_total/successful*100:.0f}%)")
        
        print(f"\n  Multi-Timeframe Disagreements: {len([r for r in results if 'MTF_DISAGREE' in r['warnings']])}")
        print(f"  Insider Selling Detected: {len([r for r in results if 'INSIDER_SELLING' in r['warnings']])}")
        print(f"  Pre-Earnings Warnings: {len([r for r in results if 'PRE_EARNINGS' in r['warnings']])}")
    
    return df


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 WATCHLIST BACKTESTING - NEW VERSION (with improvements)")
    print("="*60 + "\n")
    
    df = run_watchlist_analysis('backtesting_comparison_new.csv')
    
    print("\n✨ Next step: Checkout to main branch and run again to compare")
    print("   Command: git stash && git checkout main && python backtesting_comparison.py")
