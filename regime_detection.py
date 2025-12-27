"""
Market Regime Detection Module
Detects if market is in Bull, Bear, or Sideways regime and adjusts strategy accordingly
"""

import market_data
import indicators

def detect_market_regime():
    """
    Detect current market regime based on S&P 500 (SPY)
    
    Returns:
        dict with regime information
    """
    try:
        # Get SPY data (S&P 500 proxy)
        spy = market_data.get_ticker_data('SPY')
        data = market_data.get_historical_data(spy, period='1y', interval='1d')
        
        if data.empty:
            return {
                'regime': 'UNKNOWN',
                'confidence': 0,
                'description': 'Unable to determine market regime'
            }
        
        # Calculate indicators
        data = indicators.add_all_indicators(data)
        latest = data.iloc[-1]
        
        price = latest['Close']
        sma_50 = latest['SMA_50']
        sma_200 = latest['SMA_200']
        adx = latest['ADX']
        
        # Calculate price momentum (% change last 3 months)
        price_3m_ago = data['Close'].iloc[-63] if len(data) >= 63 else data['Close'].iloc[0]
        momentum_3m = ((price - price_3m_ago) / price_3m_ago) * 100
        
        # Determine regime
        bullish_indicators = 0
        bearish_indicators = 0
        
        # Price vs SMAs
        if price > sma_200:
            bullish_indicators += 2
        else:
            bearish_indicators += 2
            
        if price > sma_50:
            bullish_indicators += 1
        else:
            bearish_indicators += 1
        
        # SMA alignment (Golden Cross / Death Cross)
        if sma_50 > sma_200:
            bullish_indicators += 2
        else:
            bearish_indicators += 2
        
        # Momentum
        if momentum_3m > 5:
            bullish_indicators += 1
        elif momentum_3m < -5:
            bearish_indicators += 1
        
        # Determine regime and thresholds
        if adx < 20:
            # Weak trend = Sideways market
            regime = 'SIDEWAYS'
            description = 'Mercado lateral sin tendencia clara'
            buy_threshold = 30  # Optimized from 50 via grid search
            sell_threshold = 50
            confidence = 100 - adx * 5  # Lower ADX = higher confidence in sideways
            
        elif bullish_indicators > bearish_indicators + 1:
            # Strong bullish indicators = Bull market
            regime = 'BULL'
            description = 'Mercado alcista - tendencia positiva'
            buy_threshold = 40  # More aggressive
            sell_threshold = 60
            confidence = (bullish_indicators / (bullish_indicators + bearish_indicators)) * 100
            
        elif bearish_indicators > bullish_indicators + 1:
            # Strong bearish indicators = Bear market
            regime = 'BEAR'
            description = 'Mercado bajista - tendencia negativa'
            buy_threshold = 65  # Very conservative
            sell_threshold = 35
            confidence = (bearish_indicators / (bullish_indicators + bearish_indicators)) * 100
            
        else:
            # Mixed signals = Transition/Sideways
            regime = 'SIDEWAYS'
            description = 'Mercado en transición'
            buy_threshold = 30  # Optimized from 50 via grid search
            sell_threshold = 50
            confidence = 50
        
        return {
            'regime': regime,
            'confidence': round(confidence, 1),
            'description': description,
            'thresholds': {
                'buy': buy_threshold,
                'sell': sell_threshold
            },
            'indicators': {
                'spy_price': round(price, 2),
                'sma_50': round(sma_50, 2),
                'sma_200': round(sma_200, 2),
                'adx': round(adx, 2),
                'momentum_3m': round(momentum_3m, 2),
                'price_above_sma200': price > sma_200,
                'golden_cross': sma_50 > sma_200
            },
            'signal_counts': {
                'bullish': bullish_indicators,
                'bearish': bearish_indicators
            }
        }
        
    except Exception as e:
        return {
            'regime': 'UNKNOWN',
            'confidence': 0,
            'description': f'Error detecting regime: {str(e)}',
            'thresholds': {'buy': 50, 'sell': 50}
        }


def get_regime_adjusted_thresholds(ticker_volatility=None):
    """
    Get buy/sell thresholds adjusted for current market regime
    
    Args:
        ticker_volatility: Optional ticker-specific volatility (annual)
        
    Returns:
        dict with adjusted thresholds
    """
    regime_data = detect_market_regime()
    
    base_buy = regime_data['thresholds']['buy']
    base_sell = regime_data['thresholds']['sell']
    
    # Adjust for ticker volatility if provided
    if ticker_volatility:
        if ticker_volatility > 0.50:  # High volatility (>50% annual)
            # Be more conservative with volatile stocks
            base_buy += 5
            base_sell -= 5
        elif ticker_volatility < 0.20:  # Low volatility (<20% annual)
            # Can be more aggressive with stable stocks
            base_buy -= 3
            base_sell += 3
    
    return {
        'buy_threshold': base_buy,
        'sell_threshold': base_sell,
        'regime': regime_data['regime'],
        'regime_confidence': regime_data['confidence']
    }


def get_regime_summary():
    """
    Get human-readable market regime summary
    
    Returns:
        Formatted string
    """
    regime_data = detect_market_regime()
    
    if regime_data['regime'] == 'UNKNOWN':
        return "⚠️ Unable to determine market regime"
    
    # Emoji por régimen
    emoji_map = {
        'BULL': '🐂',
        'BEAR': '🐻',
        'SIDEWAYS': '↔️'
    }
    
    emoji = emoji_map.get(regime_data['regime'], '❓')
    
    summary = []
    summary.append(f"\n📈 Market Regime Analysis (SPY):")
    summary.append(f"   • Current Regime: {emoji} {regime_data['regime']}")
    summary.append(f"   • Confidence: {regime_data['confidence']:.1f}%")
    summary.append(f"   • {regime_data['description']}")
    summary.append(f"   • Adjusted Thresholds: BUY<{regime_data['thresholds']['buy']}, SELL>{regime_data['thresholds']['sell']}")
    
    ind = regime_data['indicators']
    summary.append(f"\n   Key Metrics:")
    summary.append(f"   • SPY Price: ${ind['spy_price']}")
    summary.append(f"   • SMA 50/200: ${ind['sma_50']:.2f} / ${ind['sma_200']:.2f}")
    summary.append(f"   • 3-Month Momentum: {ind['momentum_3m']:+.2f}%")
    summary.append(f"   • Golden Cross: {'✅ Yes' if ind['golden_cross'] else '❌ No'}")
    
    return "\n".join(summary)
