"""
Earnings Calendar & Surprises Module
Tracks upcoming earnings dates and historical earnings surprises
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def get_earnings_info(ticker_symbol):
    """
    Get earnings calendar and historical surprises for a ticker
    
    Args:
        ticker_symbol: Stock ticker (e.g., 'AAPL')
        
    Returns:
        dict with earnings information
    """
    
    ticker = ticker_symbol.upper()
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get earnings dates and history
        try:
            earnings_dates = stock.get_earnings_dates(limit=12)
        except:
            earnings_dates = None
        
        try:
            earnings_history = stock.get_earnings_history()
        except:
            earnings_history = None
        
        result = {
            'available': True,
            'ticker': ticker,
            'next_earnings_date': None,
            'days_to_earnings': None,
            'last_earnings_date': None,
            'last_eps_actual': None,
            'last_eps_estimate': None,
            'last_surprise_pct': None,
            'avg_surprise_last_4q': None,
            'beat_streak': 0,
            'earnings_trend': 'UNKNOWN',
            'message': ''
        }
        
        # Try to get next earnings date from info
        if 'earningsTimestamp' in info and info['earningsTimestamp']:
            try:
                result['next_earnings_date'] = pd.to_datetime(info['earningsTimestamp'], unit='s')
                days_diff = (result['next_earnings_date'] - pd.Timestamp.now()).days
                result['days_to_earnings'] = days_diff
            except:
                pass
        
        # Alternative: try earningsDate from info
        if result['next_earnings_date'] is None and 'mostRecentQuarter' in info:
            try:
                # Estimate next earnings (typically 90 days after last quarter)
                last_quarter = pd.to_datetime(info['mostRecentQuarter'], unit='s')
                estimated_next = last_quarter + timedelta(days=90)
                if estimated_next > pd.Timestamp.now():
                    result['next_earnings_date'] = estimated_next
                    result['days_to_earnings'] = (estimated_next - pd.Timestamp.now()).days
            except:
                pass
        
        # Parse earnings history from earnings_dates DataFrame
        if earnings_dates is not None and not earnings_dates.empty:
            try:
                # earnings_dates is a DataFrame with EPS Estimate and Reported EPS
                history_sorted = earnings_dates.sort_index(ascending=False)
                
                surprises = []
                beat_count = 0
                
                for i, (date, row) in enumerate(history_sorted.iterrows()):
                    if i >= 4:  # Only look at last 4 quarters
                        break
                    
                    actual = row.get('Reported EPS')
                    estimate = row.get('EPS Estimate')
                    
                    if i == 0:  # Most recent
                        result['last_earnings_date'] = date
                        result['last_eps_actual'] = actual
                        result['last_eps_estimate'] = estimate
                    
                    if pd.notna(actual) and pd.notna(estimate) and estimate != 0:
                        surprise = ((actual - estimate) / abs(estimate)) * 100
                        surprises.append(surprise)
                        
                        if i == 0:
                            result['last_surprise_pct'] = round(surprise, 2)
                        
                        if surprise > 0:
                            beat_count += 1
                
                if surprises:
                    result['avg_surprise_last_4q'] = round(sum(surprises) / len(surprises), 2)
                    result['beat_streak'] = beat_count
                    
                    # Determine trend
                    if result['avg_surprise_last_4q'] > 5:
                        result['earnings_trend'] = 'BEATING'
                    elif result['avg_surprise_last_4q'] < -5:
                        result['earnings_trend'] = 'MISSING'
                    else:
                        result['earnings_trend'] = 'MEETING'
                        
            except Exception as e:
                # Fallback: use earnings_history if available
                pass
        
        # Try earnings_history as fallback
        if earnings_history is not None and not earnings_history.empty and result['last_surprise_pct'] is None:
            try:
                history_sorted = earnings_history.sort_index(ascending=False)
                
                surprises = []
                beat_count = 0
                
                for i in range(min(4, len(history_sorted))):
                    row = history_sorted.iloc[i]
                    actual = row.get('epsActual')
                    estimate = row.get('epsEstimate')
                    
                    if i == 0:
                        result['last_earnings_date'] = history_sorted.index[i]
                        result['last_eps_actual'] = actual
                        result['last_eps_estimate'] = estimate
                    
                    if pd.notna(actual) and pd.notna(estimate) and estimate != 0:
                        surprise = ((actual - estimate) / abs(estimate)) * 100
                        surprises.append(surprise)
                        
                        if i == 0:
                            result['last_surprise_pct'] = round(surprise, 2)
                        
                        if surprise > 0:
                            beat_count += 1
                
                if surprises:
                    result['avg_surprise_last_4q'] = round(sum(surprises) / len(surprises), 2)
                    result['beat_streak'] = beat_count
                    
                    if result['avg_surprise_last_4q'] > 5:
                        result['earnings_trend'] = 'BEATING'
                    elif result['avg_surprise_last_4q'] < -5:
                        result['earnings_trend'] = 'MISSING'
                    else:
                        result['earnings_trend'] = 'MEETING'
                        
            except Exception as e:
                pass
        
        # Generate message
        messages = []
        
        if result['days_to_earnings'] is not None:
            if result['days_to_earnings'] < 0:
                messages.append(f"Earnings ya reportados (hace {abs(result['days_to_earnings'])} días)")
            elif result['days_to_earnings'] == 0:
                messages.append("⚠️ EARNINGS HOY")
            elif result['days_to_earnings'] <= 7:
                messages.append(f"⚠️ Earnings en {result['days_to_earnings']} días")
            elif result['days_to_earnings'] <= 30:
                messages.append(f"Earnings en {result['days_to_earnings']} días")
        
        if result['last_surprise_pct'] is not None:
            if result['last_surprise_pct'] > 10:
                messages.append(f"Último earnings: BEAT +{result['last_surprise_pct']:.1f}%")
            elif result['last_surprise_pct'] < -10:
                messages.append(f"Último earnings: MISS {result['last_surprise_pct']:.1f}%")
        
        if result['earnings_trend'] == 'BEATING':
            messages.append(f"Tendencia: Beating estimates consistentemente ({result['beat_streak']}/4)")
        elif result['earnings_trend'] == 'MISSING':
            messages.append("Tendencia: Missing estimates")
        
        result['message'] = ' | '.join(messages) if messages else 'No earnings data available'
        
        return result
        
    except Exception as e:
        return {
            'available': False,
            'error': str(e),
            'ticker': ticker,
            'message': f'Error retrieving earnings data: {str(e)}'
        }


def get_earnings_summary(earnings_data):
    """
    Generate human-readable summary of earnings data
    
    Args:
        earnings_data: Result from get_earnings_info()
        
    Returns:
        Formatted string summary
    """
    if not earnings_data.get('available'):
        return "⚠️ Earnings data unavailable"
    
    summary = []
    summary.append(f"\n📅 Earnings Calendar:")
    
    # Next earnings date
    if earnings_data['days_to_earnings'] is not None:
        days = earnings_data['days_to_earnings']
        if days < 0:
            summary.append(f"   • Next Report: Ya reportado (hace {abs(days)} días)")
        elif days == 0:
            summary.append(f"   • Next Report: ⚠️ HOY")
        elif days <= 7:
            summary.append(f"   • Next Report: ⚠️ En {days} días")
        elif days <= 30:
            summary.append(f"   • Next Report: En {days} días")
        else:
            summary.append(f"   • Next Report: En {days} días")
    else:
        summary.append(f"   • Next Report: No disponible")
    
    # Last earnings surprise
    if earnings_data['last_surprise_pct'] is not None:
        surprise = earnings_data['last_surprise_pct']
        emoji = "✅" if surprise > 0 else "❌"
        summary.append(f"   • Último EPS: {emoji} {surprise:+.1f}% vs estimate")
    
    # Earnings trend
    if earnings_data['earnings_trend'] != 'UNKNOWN':
        trend = earnings_data['earnings_trend']
        emoji_map = {
            'BEATING': '📈',
            'MISSING': '📉',
            'MEETING': '➡️'
        }
        emoji = emoji_map.get(trend, '❓')
        
        summary.append(f"   • Tendencia: {emoji} {trend}")
        
        if earnings_data['avg_surprise_last_4q'] is not None:
            avg = earnings_data['avg_surprise_last_4q']
            summary.append(f"   • Avg 4Q: {avg:+.1f}%")
        
        if earnings_data['beat_streak'] > 0:
            summary.append(f"   • Beat Streak: {earnings_data['beat_streak']}/4 quarters")
    
    return "\n".join(summary)


def should_reduce_confidence_pre_earnings(earnings_data, days_threshold=7):
    """
    Check if confidence should be reduced due to upcoming earnings
    
    Args:
        earnings_data: Result from get_earnings_info()
        days_threshold: Days before earnings to start reducing confidence
        
    Returns:
        tuple (should_reduce: bool, reduction_factor: float)
    """
    if not earnings_data.get('available'):
        return False, 1.0
    
    days = earnings_data.get('days_to_earnings')
    
    if days is None or days < 0:
        return False, 1.0
    
    if days <= days_threshold:
        # Reduce confidence more as earnings approach
        if days == 0:
            return True, 0.70  # -30% on earnings day
        elif days <= 2:
            return True, 0.80  # -20% within 2 days
        elif days <= 7:
            return True, 0.90  # -10% within 7 days
    
    return False, 1.0


def get_earnings_confidence_boost(earnings_data):
    """
    Calculate confidence boost based on earnings track record
    
    Args:
        earnings_data: Result from get_earnings_info()
        
    Returns:
        tuple (boost_pct: float, reason: str)
    """
    if not earnings_data.get('available'):
        return 0, None
    
    # Check if far from earnings (no volatility concerns)
    days = earnings_data.get('days_to_earnings')
    if days is not None and days <= 7:
        return 0, None  # Don't boost near earnings
    
    # Strong earnings momentum
    avg_surprise = earnings_data.get('avg_surprise_last_4q')
    beat_streak = earnings_data.get('beat_streak', 0)
    last_surprise = earnings_data.get('last_surprise_pct')
    
    if avg_surprise is not None and avg_surprise > 10 and beat_streak >= 3:
        return 10, f"Strong earnings momentum ({beat_streak}/4 beats, avg +{avg_surprise:.1f}%)"
    
    if last_surprise is not None and last_surprise > 15:
        return 5, f"Last earnings beat +{last_surprise:.1f}%"
    
    return 0, None


if __name__ == '__main__':
    # Test with popular tickers
    test_tickers = ['AAPL', 'NVDA', 'TSLA', 'GOOGL']
    
    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"Testing: {ticker}")
        print('='*60)
        
        earnings = get_earnings_info(ticker)
        print(get_earnings_summary(earnings))
        
        # Check pre-earnings reduction
        should_reduce, factor = should_reduce_confidence_pre_earnings(earnings)
        if should_reduce:
            print(f"\n⚠️ Pre-earnings reduction: {(1-factor)*100:.0f}%")
        
        # Check earnings boost
        boost, reason = get_earnings_confidence_boost(earnings)
        if boost > 0:
            print(f"\n✨ Earnings boost: +{boost}% ({reason})")
