"""
Helper module for accumulation strategy analysis.
Combines short-term and long-term analyses to identify truly valuable stocks.
"""

from colorama import Fore, Style

def calculate_combined_confidence(short_analysis, long_analysis):
    """
    Calcula confianza combinada (60% corto plazo + 40% largo plazo).
    Refleja que el timing importa, pero el valor fundamental es más importante.
    """
    short_conf = short_analysis.get('strategy', {}).get('confidence', 0)
    long_conf = long_analysis.get('strategy', {}).get('confidence', 0)
    
    # Asegurar que son números válidos
    if short_conf is None:
        short_conf = 0
    if long_conf is None:
        long_conf = 0
    
    short_conf = max(0, min(100, float(short_conf)))
    long_conf = max(0, min(100, float(long_conf)))
    
    combined = (short_conf * 0.6) + (long_conf * 0.4)
    return combined, short_conf, long_conf


def count_bullish_timeframes(multi_timeframe_data):
    """Cuenta cuántos timeframes (daily/weekly/monthly) muestran COMPRA."""
    try:
        if multi_timeframe_data is None:
            return 0
        
        timeframes = multi_timeframe_data.get('timeframes', {})
        if timeframes is None:
            return 0
            
        bullish_count = 0
        
        for tf_name, tf_data in timeframes.items():
            if tf_data is None:
                continue
            signal = str(tf_data.get('signal', '')).upper()
            if 'BUY' in signal or 'COMPRA' in signal:
                bullish_count += 1
        
        return int(bullish_count)
    except Exception as e:
        return 0


def evaluate_fundamental_strength(long_analysis):
    """Califica fortaleza fundamental (0-100) basada en fundamentales."""
    try:
        fundamental = long_analysis.get('fundamental', {})
        peg = fundamental.get('peg', 2.0)
        
        # Si peg es None, usar valor por defecto
        if peg is None:
            peg = 2.0
        peg = float(peg)
        
        score = 50
        
        # PEG Ratio
        if peg < 1.0:
            score += 20
        elif peg < 1.5:
            score += 10
        elif peg > 2.5:
            score -= 15
        
        # Pros y Cons
        strategy = long_analysis.get('strategy', {})
        pros_count = len(strategy.get('pros', []))
        cons_count = len(strategy.get('cons', []))
        
        score += (pros_count * 3)
        score -= (cons_count * 2)
        
        # Verdict
        verdict = strategy.get('verdict', 'HOLD').upper()
        if 'FUERTE COMPRA' in verdict or 'STRONG BUY' in verdict:
            score += 10
        elif 'VENTA' in verdict or 'SELL' in verdict:
            score -= 20
        
        return min(100, max(0, score))
    except Exception as e:
        return 50


def evaluate_insider_strength(advanced_data):
    """Califica actividad de insiders (0-100)."""
    try:
        if advanced_data is None:
            return 50
        
        insider = advanced_data.get('insider_trading', {})
        if insider is None:
            return 50
            
        sentiment = str(insider.get('sentiment', 'NEUTRAL')).upper()
        
        if 'BULLISH' in sentiment:
            return 80
        elif 'NEUTRAL' in sentiment:
            return 50
        else:
            return 20
    except Exception as e:
        return 50


def get_accumulation_rating(short_analysis, long_analysis):
    """
    Calcula "Accumulation Rating" (0-100).
    Indica cuán valiosa es la acción para acumular INDEPENDIENTEMENTE del precio.
    
    Pesos:
    - Largo Plazo Confianza (40%)
    - Fortaleza Fundamental (30%)
    - Multi-timeframe (20%)
    - Insider Activity (10%)
    """
    
    try:
        metrics = {}
        
        # 1. Largo plazo confianza (40%)
        long_conf = long_analysis.get('strategy', {}).get('confidence', 0)
        if long_conf is None:
            long_conf = 0
        try:
            metric_1 = float(long_conf)
        except (TypeError, ValueError):
            metric_1 = 0
        metric_1 = min(100, max(0, metric_1))
        metrics['long_term_confidence'] = metric_1
        
        # 2. Fortaleza fundamental (30%)
        metric_2 = evaluate_fundamental_strength(long_analysis)
        if metric_2 is None:
            metric_2 = 50
        try:
            metric_2 = float(metric_2)
        except (TypeError, ValueError):
            metric_2 = 50
        metric_2 = max(0, min(100, metric_2))
        metrics['fundamental_strength'] = metric_2
        
        # 3. Multi-timeframe (20%)
        mtf_data = long_analysis.get('advanced', {}).get('multi_timeframe', {})
        bullish_tf = count_bullish_timeframes(mtf_data)
        if bullish_tf is None:
            bullish_tf = 0
        metric_3 = (float(bullish_tf) / 3.0) * 100
        metric_3 = max(0, min(100, metric_3))
        metrics['timeframe_alignment'] = metric_3
        
        # 4. Insider (10%)
        advanced = long_analysis.get('advanced', {})
        metric_4 = evaluate_insider_strength(advanced)
        if metric_4 is None:
            metric_4 = 50
        try:
            metric_4 = float(metric_4)
        except (TypeError, ValueError):
            metric_4 = 50
        metric_4 = max(0, min(100, metric_4))
        metrics['insider_strength'] = metric_4
        
        # Rating ponderado
        accum_rating = (
            (metric_1 * 0.40) +
            (metric_2 * 0.30) +
            (metric_3 * 0.20) +
            (metric_4 * 0.10)
        )
        
        return max(0, min(100, float(accum_rating))), metrics
    
    except Exception as e:
        # Si hay error, retornar valores por defecto
        return 50, {
            'long_term_confidence': 50,
            'fundamental_strength': 50,
            'timeframe_alignment': 50,
            'insider_strength': 50
        }


def get_accumulation_decision(short_verdict, long_verdict, combined_confidence):
    """
    Retorna matriz de decisión de acumulación.
    
    Returns:
    - action: Acción recomendada (string)
    - position_size: Tamaño de posición recomendado (string)
    - priority: Prioridad (1=urgente, 5=evitar)
    """
    
    short_buy = 'COMPRA' in short_verdict.upper() or 'BUY' in short_verdict.upper()
    short_sell = 'VENTA' in short_verdict.upper() or 'SELL' in short_verdict.upper()
    long_buy = 'COMPRA' in long_verdict.upper() or 'FUERTE COMPRA' in long_verdict.upper()
    long_sell = 'VENTA' in long_verdict.upper() or 'SELL' in long_verdict.upper()
    
    if short_buy and long_buy:
        return {
            'action': f'{Fore.LIGHTGREEN_EX}✅ ACUMULAR AGRESIVA{Style.RESET_ALL}',
            'position_size': '75-100%',
            'priority': 1,
            'reasoning': 'Corto COMPRA + Largo COMPRA = Oportunidad real'
        }
    elif long_buy and not short_sell:
        return {
            'action': f'{Fore.YELLOW}🟡 ACUMULAR DCA{Style.RESET_ALL}',
            'position_size': '25-50% mensual',
            'priority': 2,
            'reasoning': 'Largo COMPRA pero timing corto plazo incierto'
        }
    elif long_buy and short_sell:
        return {
            'action': f'{Fore.YELLOW}⚠️  ESPERAR rebote{Style.RESET_ALL}',
            'position_size': '0% ahora',
            'priority': 3,
            'reasoning': 'Corrección en tendencia alcista, esperar estabilización'
        }
    elif short_buy and long_sell:
        return {
            'action': f'{Fore.RED}❌ NO COMPRAR{Style.RESET_ALL}',
            'position_size': '0%',
            'priority': 4,
            'reasoning': 'Rebote técnico en acción sin valor real'
        }
    else:  # long_sell or both neutral
        return {
            'action': f'{Fore.RED}🔴 EVITAR{Style.RESET_ALL}',
            'position_size': '0%',
            'priority': 5,
            'reasoning': 'Problemas en múltiples niveles'
        }


def format_accumulation_summary(ticker, short_analysis, long_analysis, compact=False):
    """
    Formato resumido de análisis de acumulación.
    
    Args:
        compact: Si True, una sola línea; si False, formato expandido
    """
    
    combined_conf, short_conf, long_conf = calculate_combined_confidence(short_analysis, long_analysis)
    accum_rating, metrics = get_accumulation_rating(short_analysis, long_analysis)
    
    short_verdict = short_analysis.get('strategy', {}).get('verdict', 'N/A')
    long_verdict = long_analysis.get('strategy', {}).get('verdict', 'N/A')
    
    decision = get_accumulation_decision(short_verdict, long_verdict, combined_conf)
    
    if compact:
        return f"{decision['action']} | Rating: {accum_rating:.0f}% | Conf: {combined_conf:.0f}%"
    else:
        output = f"\n{Fore.CYAN}📊 ANÁLISIS DE ACUMULACIÓN:{Style.RESET_ALL}\n"
        output += f"  Accumulation Rating: {accum_rating:.0f}%\n"
        output += f"  Confianza Combinada: {combined_conf:.0f}%\n"
        output += f"    └─ Corto Plazo: {short_conf:.0f}%\n"
        output += f"    └─ Largo Plazo: {long_conf:.0f}%\n"
        output += f"  Decisión: {decision['action']}\n"
        output += f"  Tamaño Recomendado: {decision['position_size']}\n"
        output += f"  Reasoning: {decision['reasoning']}\n"
        output += f"\n  Métricas Detalladas:\n"
        output += f"    • Long Term Confidence: {metrics['long_term_confidence']:.0f}%\n"
        output += f"    • Fundamental Strength: {metrics['fundamental_strength']:.0f}%\n"
        output += f"    • Timeframe Alignment: {metrics['timeframe_alignment']:.0f}%\n"
        output += f"    • Insider Strength: {metrics['insider_strength']:.0f}%\n"
        
        return output
