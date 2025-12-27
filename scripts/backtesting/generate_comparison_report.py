"""
Comparison Report Generator
Compares results from OLD (main branch) vs NEW (with improvements)
"""

import pandas as pd
import sys

def generate_comparison_report(old_file='backtesting_comparison_old.csv', 
                               new_file='backtesting_comparison_new.csv',
                               output_file='backtesting_comparison_report.md'):
    """
    Generate markdown report comparing old vs new results
    """
    
    try:
        df_old = pd.read_csv(old_file)
        print(f"✅ Loaded OLD results: {old_file} ({len(df_old)} tickers)")
    except FileNotFoundError:
        print(f"❌ OLD file not found: {old_file}")
        print("   Run this script on main branch first:")
        print("   git stash && git checkout main && python backtesting_comparison.py")
        return
    
    try:
        df_new = pd.read_csv(new_file)
        print(f"✅ Loaded NEW results: {new_file} ({len(df_new)} tickers)")
    except FileNotFoundError:
        print(f"❌ NEW file not found: {new_file}")
        print("   Run backtesting_comparison.py first on feature branch")
        return
    
    # Merge dataframes
    df_old = df_old.add_prefix('old_')
    df_new = df_new.add_prefix('new_')
    
    df = pd.concat([df_old.set_index('old_ticker'), df_new.set_index('new_ticker')], axis=1)
    df = df.reset_index()
    df = df.rename(columns={'index': 'ticker'})
    
    # Calculate deltas
    df['confidence_delta'] = df['new_confidence'] - df['old_confidence']
    df['verdict_changed'] = df['old_verdict'] != df['new_verdict']
    
    # Generate report
    report = []
    report.append("# Backtesting Comparison Report")
    report.append(f"\n**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"\n**Tickers Analyzed**: {len(df)}")
    report.append("\n---\n")
    
    # Summary Statistics
    report.append("## 📊 Summary Statistics\n")
    
    old_success = len(df[df['old_error'].isna()])
    new_success = len(df[df['new_error'].isna()])
    
    report.append(f"### Success Rate")
    report.append(f"- **OLD**: {old_success}/{len(df)} ({old_success/len(df)*100:.1f}%)")
    report.append(f"- **NEW**: {new_success}/{len(df)} ({new_success/len(df)*100:.1f}%)")
    
    # Verdicts comparison
    report.append(f"\n### Verdict Distribution\n")
    
    old_verdicts = df[df['old_error'].isna()]['old_verdict'].value_counts()
    new_verdicts = df[df['new_error'].isna()]['new_verdict'].value_counts()
    
    report.append("| Verdict | OLD | NEW | Change |")
    report.append("|---------|-----|-----|--------|")
    
    all_verdicts = set(old_verdicts.index) | set(new_verdicts.index)
    for verdict in sorted(all_verdicts):
        old_count = old_verdicts.get(verdict, 0)
        new_count = new_verdicts.get(verdict, 0)
        delta = new_count - old_count
        delta_str = f"{delta:+d}" if delta != 0 else "0"
        report.append(f"| {verdict} | {old_count} | {new_count} | {delta_str} |")
    
    # Confidence analysis
    report.append(f"\n### Confidence Analysis\n")
    
    df_valid = df[(df['old_error'].isna()) & (df['new_error'].isna())]
    
    avg_old = df_valid['old_confidence'].mean()
    avg_new = df_valid['new_confidence'].mean()
    avg_delta = avg_new - avg_old
    
    report.append(f"- **Average OLD Confidence**: {avg_old:.1f}%")
    report.append(f"- **Average NEW Confidence**: {avg_new:.1f}%")
    report.append(f"- **Average Delta**: {avg_delta:+.1f}%")
    
    # Warnings analysis
    report.append(f"\n### Warnings Detected (NEW Version)\n")
    
    warnings_count = len(df_valid[df_valid['new_warnings'] != 'NONE'])
    report.append(f"- **Tickers with Warnings**: {warnings_count}/{len(df_valid)} ({warnings_count/len(df_valid)*100:.0f}%)")
    
    # Count specific warnings
    mtf_disagree = len(df_valid[df_valid['new_warnings'].str.contains('MTF_DISAGREE', na=False)])
    insider_selling = len(df_valid[df_valid['new_warnings'].str.contains('INSIDER_SELLING', na=False)])
    pre_earnings = len(df_valid[df_valid['new_warnings'].str.contains('PRE_EARNINGS', na=False)])
    
    report.append(f"- **Multi-Timeframe Disagreements**: {mtf_disagree}")
    report.append(f"- **Insider Selling Detected**: {insider_selling}")
    report.append(f"- **Pre-Earnings Warnings**: {pre_earnings}")
    
    # Top changes
    report.append(f"\n## 🔄 Top Confidence Changes\n")
    
    report.append(f"\n### Biggest Confidence Drops (More Conservative)\n")
    top_drops = df_valid.nsmallest(10, 'confidence_delta')[['ticker', 'old_verdict', 'new_verdict', 'old_confidence', 'new_confidence', 'confidence_delta', 'new_warnings']]
    report.append("\n| Ticker | OLD Verdict | NEW Verdict | OLD Conf | NEW Conf | Delta | Warnings |")
    report.append("|--------|-------------|-------------|----------|----------|-------|----------|")
    for _, row in top_drops.iterrows():
        report.append(f"| {row['ticker']} | {row['old_verdict']} | {row['new_verdict']} | {row['old_confidence']:.0f}% | {row['new_confidence']:.0f}% | {row['confidence_delta']:.0f}% | {row['new_warnings'].replace('|', ', ')} |")
    
    report.append(f"\n### Biggest Confidence Increases\n")
    top_increases = df_valid.nlargest(10, 'confidence_delta')[['ticker', 'old_verdict', 'new_verdict', 'old_confidence', 'new_confidence', 'confidence_delta', 'new_warnings']]
    report.append("\n| Ticker | OLD Verdict | NEW Verdict | OLD Conf | NEW Conf | Delta | Warnings |")
    report.append("|--------|-------------|-------------|----------|----------|-------|----------|")
    for _, row in top_increases.iterrows():
        report.append(f"| {row['ticker']} | {row['old_verdict']} | {row['new_verdict']} | {row['old_confidence']:.0f}% | {row['new_confidence']:.0f}% | {row['confidence_delta']:.0f}% | {row['new_warnings'].replace('|', ', ')} |")
    
    # Verdict changes
    verdict_changes = df_valid[df_valid['verdict_changed']]
    if len(verdict_changes) > 0:
        report.append(f"\n## ⚡ Verdict Changes ({len(verdict_changes)} tickers)\n")
        report.append("\n| Ticker | OLD → NEW | Conf Delta | Warnings |")
        report.append("|--------|-----------|------------|----------|")
        for _, row in verdict_changes.iterrows():
            report.append(f"| {row['ticker']} | {row['old_verdict']} → {row['new_verdict']} | {row['confidence_delta']:.0f}% | {row['new_warnings'].replace('|', ', ')} |")
    
    # New features impact
    report.append(f"\n## 🆕 New Features Impact\n")
    
    # Reddit sentiment
    reddit_activity = len(df_valid[df_valid['new_reddit_mentions'] > 0])
    report.append(f"\n### Reddit Sentiment")
    report.append(f"- **Tickers with Reddit Activity**: {reddit_activity}/{len(df_valid)}")
    if reddit_activity > 0:
        reddit_bullish = len(df_valid[df_valid['new_reddit_sentiment'] == 'BULLISH'])
        reddit_bearish = len(df_valid[df_valid['new_reddit_sentiment'] == 'BEARISH'])
        report.append(f"- **Bullish**: {reddit_bullish}, **Bearish**: {reddit_bearish}")
    
    # Earnings
    earnings_beating = len(df_valid[df_valid['new_earnings_trend'] == 'BEATING'])
    earnings_missing = len(df_valid[df_valid['new_earnings_trend'] == 'MISSING'])
    report.append(f"\n### Earnings Trends")
    report.append(f"- **BEATING estimates**: {earnings_beating}")
    report.append(f"- **MISSING estimates**: {earnings_missing}")
    
    # Insider trading
    insider_buying = len(df_valid[df_valid['new_insider_sentiment'] == 'BULLISH'])
    insider_selling = len(df_valid[df_valid['new_insider_sentiment'] == 'BEARISH'])
    report.append(f"\n### Insider Trading")
    report.append(f"- **Insider Buying detected**: {insider_buying}")
    report.append(f"- **Insider Selling detected**: {insider_selling}")
    
    # Full comparison table
    report.append(f"\n## 📋 Full Comparison Table\n")
    report.append("\n| Ticker | OLD | NEW | Δ Conf | Warnings | MTF | Reddit | Earnings | Insider |")
    report.append("|--------|-----|-----|--------|----------|-----|--------|----------|---------|")
    
    for _, row in df_valid.iterrows():
        warnings_short = row['new_warnings'].replace('|', ',')[:20] if row['new_warnings'] != 'NONE' else '-'
        report.append(f"| {row['ticker']} | {row['old_verdict'][:10]} {row['old_confidence']:.0f}% | {row['new_verdict'][:10]} {row['new_confidence']:.0f}% | {row['confidence_delta']:+.0f}% | {warnings_short} | {row['new_mtf_signal']} | {row['new_reddit_sentiment'][:4] if pd.notna(row['new_reddit_sentiment']) else '-'} | {row['new_earnings_trend'][:4] if pd.notna(row['new_earnings_trend']) else '-'} | {row['new_insider_sentiment'][:4] if pd.notna(row['new_insider_sentiment']) else '-'} |")
    
    # Save report
    report_text = "\n".join(report)
    with open(output_file, 'w') as f:
        f.write(report_text)
    
    print(f"\n{'='*60}")
    print(f"✅ Comparison report generated!")
    print(f"📄 Saved to: {output_file}")
    print(f"{'='*60}\n")
    
    # Also save detailed CSV
    df.to_csv('backtesting_comparison_detailed.csv', index=False)
    print(f"📊 Detailed CSV saved to: backtesting_comparison_detailed.csv\n")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("📊 BACKTESTING COMPARISON REPORT GENERATOR")
    print("="*60 + "\n")
    
    generate_comparison_report()
