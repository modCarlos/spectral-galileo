"""
Multi-Timeframe Analysis Module
Analyzes price action across multiple timeframes to confirm signals
"""

import pandas as pd
import market_data
import indicators
import signal
from contextlib import contextmanager

class TimeoutException(Exception):
    """Exception raised when an operation times out"""
    pass

@contextmanager
def time_limit(seconds):
    """Context manager to enforce time limit on operations"""
    def signal_handler(signum, frame):
        raise TimeoutException(f"Operation timed out after {seconds} seconds")
    
    old_handler = signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def analyze_timeframe(ticker_symbol, period, interval):
    """
    Analyze a single timeframe with timeout protection
    
    Args:
        ticker_symbol: Stock symbol
        period: Historical period (1y, 2y, 5y)
        interval: Data interval (1d, 1wk, 1mo)
        
    Returns:
        dict with timeframe analysis or None on timeout/error
    """
    try:
        # Add 10-second timeout for each timeframe analysis
        with time_limit(10):
            # Get data
            ticker = market_data.get_ticker_data(ticker_symbol)
            data = market_data.get_historical_data(ticker, period=period, interval=interval)
        
        if data.empty or len(data) < 50:
            return None
        
        # Calculate indicators
        data = indicators.add_all_indicators(data)
        latest = data.iloc[-1]
        
        # Extract key metrics
        price = latest['Close']
        rsi = latest['RSI']
        macd = latest['MACD']
        macd_signal = latest['MACD_Signal']
        sma_50 = latest['SMA_50']
        sma_200 = latest['SMA_200']
        adx = latest['ADX']
        
        # Determine trend
        if price > sma_200:
            trend = 'bullish'
        elif price < sma_200:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        # Determine momentum
        if rsi > 50 and macd > macd_signal:
            momentum = 'bullish'
        elif rsi < 50 and macd < macd_signal:
            momentum = 'bearish'
        else:
            momentum = 'neutral'
        
        # Overall signal
        bullish_signals = 0
        bearish_signals = 0
        
        if price > sma_50: bullish_signals += 1
        else: bearish_signals += 1
        
        if price > sma_200: bullish_signals += 1
        else: bearish_signals += 1
        
        if rsi < 30: bullish_signals += 2  # Oversold = buy opportunity
        elif rsi > 70: bearish_signals += 2  # Overbought = sell signal
        
        if macd > macd_signal: bullish_signals += 1
        else: bearish_signals += 1
        
        if adx > 25:  # Strong trend
            if trend == 'bullish': bullish_signals += 1
            elif trend == 'bearish': bearish_signals += 1
        
        # Determine signal
        if bullish_signals > bearish_signals + 1:
            signal = 'BUY'
        elif bearish_signals > bullish_signals + 1:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        return {
            'interval': interval,
            'trend': trend,
            'momentum': momentum,
            'signal': signal,
            'rsi': rsi,
            'adx': adx,
            'price_vs_sma50': 'above' if price > sma_50 else 'below',
            'price_vs_sma200': 'above' if price > sma_200 else 'below',
            'bullish_signals': bullish_signals,
            'bearish_signals': bearish_signals,
            'confidence': abs(bullish_signals - bearish_signals) / (bullish_signals + bearish_signals) * 100
        }
        
    except TimeoutException as e:
        print(f"⚠️  Timeframe analysis timeout for {ticker_symbol} ({period}, {interval})")
        return None
    except Exception as e:
        return None


def analyze_multiple_timeframes(ticker_symbol):
    """
    Analyze multiple timeframes and determine confluence
    
    Args:
        ticker_symbol: Stock symbol
        
    Returns:
        dict with multi-timeframe analysis and confluence score
    """
    
    timeframes = [
        {'name': 'Daily', 'period': '1y', 'interval': '1d'},
        {'name': 'Weekly', 'period': '2y', 'interval': '1wk'},
        {'name': 'Monthly', 'period': '5y', 'interval': '1mo'}
    ]
    
    results = {}
    signals = []
    
    for tf in timeframes:
        analysis = analyze_timeframe(ticker_symbol, tf['period'], tf['interval'])
        if analysis:
            results[tf['name']] = analysis
            signals.append(analysis['signal'])
    
    # Calculate confluence
    if len(signals) < 2:
        return {
            'timeframes': results,
            'confluence': None,
            'message': 'Insufficient data for multi-timeframe analysis'
        }
    
    buy_count = signals.count('BUY')
    sell_count = signals.count('SELL')
    hold_count = signals.count('HOLD')
    
    # Determine overall signal based on confluence
    if buy_count >= 2:
        overall_signal = 'BUY'
        confluence_strength = 'STRONG' if buy_count == 3 else 'MODERATE'
    elif sell_count >= 2:
        overall_signal = 'SELL'
        confluence_strength = 'STRONG' if sell_count == 3 else 'MODERATE'
    else:
        overall_signal = 'HOLD'
        confluence_strength = 'WEAK'
    
    # Calculate confluence score (0-100)
    max_agreement = max(buy_count, sell_count, hold_count)
    confluence_score = (max_agreement / len(signals)) * 100
    
    # Generate message
    if confluence_strength == 'STRONG':
        message = f"✅ Strong multi-timeframe confirmation: All {max_agreement} timeframes agree"
    elif confluence_strength == 'MODERATE':
        message = f"⚠️ Moderate confluence: {max_agreement}/{len(signals)} timeframes agree"
    else:
        message = f"❌ Weak confluence: Timeframes disagree (BUY:{buy_count}, SELL:{sell_count}, HOLD:{hold_count})"
    
    return {
        'timeframes': results,
        'signals': {
            'daily': results.get('Daily', {}).get('signal'),
            'weekly': results.get('Weekly', {}).get('signal'),
            'monthly': results.get('Monthly', {}).get('signal')
        },
        'confluence': {
            'overall_signal': overall_signal,
            'strength': confluence_strength,
            'score': round(confluence_score, 1),
            'buy_count': buy_count,
            'sell_count': sell_count,
            'hold_count': hold_count
        },
        'message': message
    }


def get_timeframe_summary(mtf_analysis):
    """
    Generate human-readable summary of multi-timeframe analysis
    
    Args:
        mtf_analysis: Result from analyze_multiple_timeframes()
        
    Returns:
        Formatted string summary
    """
    if not mtf_analysis or not mtf_analysis.get('confluence'):
        return "Multi-timeframe analysis unavailable"
    
    conf = mtf_analysis['confluence']
    signals = mtf_analysis['signals']
    
    summary = []
    summary.append(f"📊 Multi-Timeframe Analysis:")
    summary.append(f"   • Daily: {signals['daily']}")
    summary.append(f"   • Weekly: {signals['weekly']}")
    summary.append(f"   • Monthly: {signals['monthly']}")
    summary.append(f"   • Confluence: {conf['score']}% ({conf['strength']})")
    summary.append(f"   • Overall: {conf['overall_signal']}")
    
    return "\n".join(summary)
