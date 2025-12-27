"""
Insider Trading Activity Module
Analyzes insider buying/selling activity from SEC filings
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_insider_activity(ticker_symbol, days=90):
    """
    Get insider trading activity for a ticker
    
    Args:
        ticker_symbol: Stock ticker (e.g., 'AAPL')
        days: Look back period in days (default: 90)
        
    Returns:
        dict with insider activity analysis
    """
    
    ticker = ticker_symbol.upper()
    
    try:
        stock = yf.Ticker(ticker)
        
        # Get insider transactions
        try:
            insider_transactions = stock.get_insider_transactions()
        except:
            insider_transactions = None
        
        # Get insider purchases (more detailed)
        try:
            insider_purchases = stock.get_insider_purchases()
        except:
            insider_purchases = None
        
        # Get insider roster
        try:
            insider_roster = stock.get_insider_roster_holders()
        except:
            insider_roster = None
        
        result = {
            'available': True,
            'ticker': ticker,
            'total_transactions': 0,
            'buy_transactions': 0,
            'sell_transactions': 0,
            'net_shares': 0,
            'net_value': 0,
            'buy_value': 0,
            'sell_value': 0,
            'executive_buys': 0,
            'director_buys': 0,
            'executive_sells': 0,
            'director_sells': 0,
            'recent_large_buys': [],
            'recent_large_sells': [],
            'insider_sentiment': 'NEUTRAL',
            'confidence': 0,
            'message': ''
        }
        
        # Process insider transactions
        if insider_transactions is not None and not insider_transactions.empty:
            # Filter by date (last N days)
            cutoff_date = pd.Timestamp.now() - timedelta(days=days)
            
            # Ensure Start Date is datetime
            if 'Start Date' in insider_transactions.columns:
                insider_transactions['Start Date'] = pd.to_datetime(insider_transactions['Start Date'], errors='coerce')
                # Filter recent trades
                if pd.notna(insider_transactions['Start Date']).any():
                    recent_trades = insider_transactions[
                        (insider_transactions['Start Date'] >= cutoff_date) & 
                        (pd.notna(insider_transactions['Start Date']))
                    ]
                else:
                    # If no valid dates, use all transactions
                    recent_trades = insider_transactions
            else:
                recent_trades = insider_transactions
            
            if not recent_trades.empty:
                result['total_transactions'] = len(recent_trades)
                
                # Analyze each transaction
                for idx, trade in recent_trades.iterrows():
                    shares = trade.get('Shares', 0)
                    value = trade.get('Value', 0)
                    text = trade.get('Text', '')
                    insider_name = trade.get('Insider', '')
                    
                    # Clean up values
                    if pd.notna(shares):
                        try:
                            shares = float(shares)
                        except:
                            shares = 0
                    else:
                        shares = 0
                    
                    if pd.notna(value):
                        try:
                            value = float(value)
                        except:
                            value = 0
                    else:
                        value = 0
                    
                    # Determine if executive or director
                    insider_str = str(insider_name).lower()
                    position_str = str(trade.get('Position', '')).lower()
                    is_executive = any(title in insider_str or title in position_str for title in ['ceo', 'cfo', 'coo', 'president', 'executive', 'officer', 'counsel'])
                    is_director = 'director' in insider_str or 'director' in position_str
                    
                    # Classify transaction from Text field
                    text_lower = str(text).lower()
                    
                    if any(keyword in text_lower for keyword in ['purchase', 'buy', 'acquired', 'exercise']):
                        result['buy_transactions'] += 1
                        result['net_shares'] += shares
                        result['buy_value'] += abs(value)
                        
                        if is_executive:
                            result['executive_buys'] += 1
                        elif is_director:
                            result['director_buys'] += 1
                        
                        # Track large buys (> $100k)
                        if abs(value) > 100000:
                            result['recent_large_buys'].append({
                                'insider': insider_name,
                                'shares': shares,
                                'value': value,
                                'date': trade.get('Start Date')
                            })
                    
                    elif any(keyword in text_lower for keyword in ['sale', 'sell', 'sold', 'disposition']):
                        result['sell_transactions'] += 1
                        result['net_shares'] -= shares
                        result['sell_value'] += abs(value)
                        
                        if is_executive:
                            result['executive_sells'] += 1
                        elif is_director:
                            result['director_sells'] += 1
                        
                        # Track large sells (> $500k)
                        if abs(value) > 500000:
                            result['recent_large_sells'].append({
                                'insider': insider_name,
                                'shares': shares,
                                'value': value,
                                'date': trade.get('Start Date')
                            })
                    
                    # Note: Gifts, Awards, etc. are not counted as buys/sells
                
                # Calculate net value
                result['net_value'] = result['buy_value'] - result['sell_value']
                
                # Determine insider sentiment
                if result['buy_transactions'] > result['sell_transactions'] * 2:
                    result['insider_sentiment'] = 'BULLISH'
                    result['confidence'] = min(100, (result['buy_transactions'] / max(1, result['sell_transactions'])) * 30)
                elif result['sell_transactions'] > result['buy_transactions'] * 2:
                    result['insider_sentiment'] = 'BEARISH'
                    result['confidence'] = min(100, (result['sell_transactions'] / max(1, result['buy_transactions'])) * 30)
                else:
                    result['insider_sentiment'] = 'NEUTRAL'
                    result['confidence'] = 50
                
                # Sort large trades by value
                result['recent_large_buys'] = sorted(result['recent_large_buys'], key=lambda x: abs(x['value']), reverse=True)[:5]
                result['recent_large_sells'] = sorted(result['recent_large_sells'], key=lambda x: abs(x['value']), reverse=True)[:5]
        
        # Generate message
        messages = []
        
        if result['total_transactions'] == 0:
            messages.append(f"No insider activity in last {days} days")
        else:
            if result['buy_transactions'] > 0:
                messages.append(f"{result['buy_transactions']} insider buys")
            if result['sell_transactions'] > 0:
                messages.append(f"{result['sell_transactions']} insider sells")
            
            if result['net_value'] > 0:
                messages.append(f"Net buying: ${result['net_value']/1e6:.1f}M")
            elif result['net_value'] < 0:
                messages.append(f"Net selling: ${abs(result['net_value'])/1e6:.1f}M")
        
        result['message'] = ' | '.join(messages) if messages else 'No recent insider activity'
        
        return result
        
    except Exception as e:
        return {
            'available': False,
            'error': str(e),
            'ticker': ticker,
            'message': f'Error retrieving insider data: {str(e)}'
        }


def get_insider_summary(insider_data):
    """
    Generate human-readable summary of insider activity
    
    Args:
        insider_data: Result from get_insider_activity()
        
    Returns:
        Formatted string summary
    """
    if not insider_data.get('available'):
        return "⚠️ Insider trading data unavailable"
    
    if insider_data['total_transactions'] == 0:
        return f"\n👔 Insider Activity: No recent transactions (last 90 days)"
    
    summary = []
    summary.append(f"\n👔 Insider Activity (90 days):")
    
    # Transaction counts
    buys = insider_data['buy_transactions']
    sells = insider_data['sell_transactions']
    summary.append(f"   • Transactions: {buys} buys, {sells} sells")
    
    # Net value
    net_value = insider_data['net_value']
    if net_value > 0:
        summary.append(f"   • Net Activity: 📈 +${net_value/1e6:.1f}M buying")
    elif net_value < 0:
        summary.append(f"   • Net Activity: 📉 -${abs(net_value)/1e6:.1f}M selling")
    else:
        summary.append(f"   • Net Activity: Balanced")
    
    # Sentiment
    sentiment = insider_data['insider_sentiment']
    emoji_map = {
        'BULLISH': '🟢',
        'BEARISH': '🔴',
        'NEUTRAL': '⚪'
    }
    emoji = emoji_map.get(sentiment, '❓')
    summary.append(f"   • Sentiment: {emoji} {sentiment} ({insider_data['confidence']:.0f}% confidence)")
    
    # Executive activity
    if insider_data['executive_buys'] > 0 or insider_data['executive_sells'] > 0:
        summary.append(f"   • Executives: {insider_data['executive_buys']} buys, {insider_data['executive_sells']} sells")
    
    # Recent large buys
    if insider_data['recent_large_buys']:
        summary.append(f"\n   Recent Large Buys:")
        for i, buy in enumerate(insider_data['recent_large_buys'][:3], 1):
            summary.append(f"   {i}. {buy['insider']}: ${abs(buy['value'])/1e3:.0f}K")
    
    # Recent large sells
    if insider_data['recent_large_sells']:
        summary.append(f"\n   Recent Large Sells:")
        for i, sell in enumerate(insider_data['recent_large_sells'][:3], 1):
            summary.append(f"   {i}. {sell['insider']}: ${abs(sell['value'])/1e3:.0f}K")
    
    return "\n".join(summary)


def get_insider_confidence_adjustment(insider_data):
    """
    Calculate confidence adjustment based on insider activity
    
    Args:
        insider_data: Result from get_insider_activity()
        
    Returns:
        tuple (adjustment_pct: float, reason: str)
    """
    if not insider_data.get('available') or insider_data['total_transactions'] == 0:
        return 0, None
    
    sentiment = insider_data['insider_sentiment']
    buys = insider_data['buy_transactions']
    sells = insider_data['sell_transactions']
    net_value = insider_data['net_value']
    exec_buys = insider_data['executive_buys']
    
    # Strong insider buying
    if sentiment == 'BULLISH' and net_value > 1e6:  # > $1M net buying
        if exec_buys >= 2:  # Multiple executives buying
            return 10, f"Strong insider buying: ${net_value/1e6:.1f}M net ({exec_buys} exec buys)"
        else:
            return 5, f"Insider buying: ${net_value/1e6:.1f}M net"
    
    # Moderate insider buying
    elif sentiment == 'BULLISH' and net_value > 0:
        return 3, f"Moderate insider buying: {buys} transactions"
    
    # Strong insider selling (warning)
    elif sentiment == 'BEARISH' and net_value < -5e6:  # > $5M net selling
        return -10, f"Heavy insider selling: ${abs(net_value)/1e6:.1f}M net"
    
    # Moderate insider selling
    elif sentiment == 'BEARISH' and net_value < -1e6:
        return -5, f"Insider selling: ${abs(net_value)/1e6:.1f}M net"
    
    return 0, None


if __name__ == '__main__':
    # Test with popular tickers
    test_tickers = ['AAPL', 'NVDA', 'TSLA', 'GOOGL']
    
    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"Testing: {ticker}")
        print('='*60)
        
        insider = get_insider_activity(ticker)
        print(get_insider_summary(insider))
        
        # Check confidence adjustment
        adjustment, reason = get_insider_confidence_adjustment(insider)
        if adjustment != 0:
            print(f"\n{'🟢' if adjustment > 0 else '🔴'} Confidence adjustment: {adjustment:+.0f}% ({reason})")
