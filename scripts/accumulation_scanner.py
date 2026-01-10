#!/usr/bin/env python3
"""
🎯 Accumulation Scanner - Identifica acciones verdaderamente valiosas
que merecen acumulación independientemente del precio de entrada.

Combina:
- Análisis Corto Plazo (momentum, oportunidad operativa)
- Análisis Largo Plazo (fundamentales, valor intrínseco)
- Confluencia Multi-Timeframe
- Sentimiento y Actividad de Insiders
"""

import sys
import os

# Setup path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from src.spectral_galileo.core.agent import FinancialAgent
from colorama import Fore, Style
import json
from datetime import datetime

def calculate_combined_confidence(short_analysis, long_analysis):
    """
    Calcula confianza combinada (60% corto plazo + 40% largo plazo)
    Refleja que el timing importa, pero el valor fundamental es más importante.
    """
    short_conf = short_analysis.get('strategy', {}).get('confidence', 0)
    long_conf = long_analysis.get('strategy', {}).get('confidence', 0)
    
    combined = (short_conf * 0.6) + (long_conf * 0.4)
    return combined, short_conf, long_conf


def count_bullish_timeframes(multi_timeframe_data):
    """
    Cuenta cuántos timeframes (daily/weekly/monthly) muestran señal de COMPRA.
    """
    timeframes = multi_timeframe_data.get('timeframes', {})
    bullish_count = 0
    
    for tf_name, tf_data in timeframes.items():
        signal = str(tf_data.get('signal', '')).upper()
        if 'BUY' in signal or 'COMPRA' in signal:
            bullish_count += 1
    
    return bullish_count


def evaluate_fundamental_strength(long_analysis):
    """
    Califica la fortaleza fundamental (0-100).
    
    Basado en:
    - ROE (Return on Equity)
    - Deuda/Equity
    - PEG Ratio
    - Márgenes
    """
    fundamental = long_analysis.get('fundamental', {})
    peg = fundamental.get('peg', 2.0)
    score = 50  # baseline
    
    # PEG Ratio (mejor < 1.5)
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
    
    # Verdict largo plazo
    verdict = strategy.get('verdict', 'HOLD').upper()
    if 'FUERTE COMPRA' in verdict or 'STRONG BUY' in verdict:
        score += 10
    elif 'VENTA' in verdict or 'SELL' in verdict:
        score -= 20
    
    return min(100, max(0, score))


def evaluate_insider_strength(advanced_data):
    """
    Califica actividad de insiders (0-100).
    """
    insider = advanced_data.get('insider_trading', {})
    sentiment = str(insider.get('sentiment', 'NEUTRAL')).upper()
    net_buying = insider.get('net_buying', 0)
    
    if 'BULLISH' in sentiment and net_buying > 0:
        return 80
    elif 'BULLISH' in sentiment:
        return 60
    elif 'NEUTRAL' in sentiment:
        return 50
    else:
        return 20


def get_accumulation_rating(ticker, short_analysis, long_analysis):
    """
    Calcula "Accumulation Rating" (0-100) que indica cuán valiosa es la acción
    para acumular INDEPENDIENTEMENTE del precio.
    
    Criterios:
    1. Largo Plazo Confianza (40%)
    2. Fortaleza Fundamental (30%)
    3. Multi-timeframe Confluencia (20%)
    4. Insider Activity (10%)
    """
    
    metrics = {}
    
    # 1. Largo plazo confianza (40%)
    long_conf = long_analysis.get('strategy', {}).get('confidence', 0)
    metric_1 = min(100, long_conf)  # Cap at 100
    metrics['long_term_confidence'] = metric_1
    
    # 2. Fortaleza fundamental (30%)
    metric_2 = evaluate_fundamental_strength(long_analysis)
    metrics['fundamental_strength'] = metric_2
    
    # 3. Multi-timeframe (20%)
    mtf_data = long_analysis.get('advanced', {}).get('multi_timeframe', {})
    bullish_tf = count_bullish_timeframes(mtf_data)
    metric_3 = (bullish_tf / 3.0) * 100  # 3 timeframes total
    metrics['timeframe_alignment'] = metric_3
    
    # 4. Insider strength (10%)
    advanced = long_analysis.get('advanced', {})
    metric_4 = evaluate_insider_strength(advanced)
    metrics['insider_strength'] = metric_4
    
    # Accumulation Rating (ponderado)
    accum_rating = (
        (metric_1 * 0.40) +
        (metric_2 * 0.30) +
        (metric_3 * 0.20) +
        (metric_4 * 0.10)
    )
    
    return accum_rating, metrics


def format_verdict_color(verdict):
    """Colorea el verdict según tipo."""
    if 'FUERTE COMPRA' in verdict:
        return f"{Fore.LIGHTGREEN_EX}{verdict}{Style.RESET_ALL}"
    elif 'COMPRA' in verdict:
        return f"{Fore.GREEN}{verdict}{Style.RESET_ALL}"
    elif 'VENTA' in verdict:
        return f"{Fore.RED}{verdict}{Style.RESET_ALL}"
    else:
        return f"{Fore.YELLOW}{verdict}{Style.RESET_ALL}"


def scan_accumulation_opportunities(tickers):
    """
    Escanea lista de tickers y devuelve oportunidades de acumulación ordenadas
    por "Accumulation Rating" (valor intrínseco + oportunidad).
    """
    
    print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🎯 ACCUMULATION SCANNER - Identificando Acciones Verdaderamente Valiosas{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
    
    results = []
    
    for ticker in tickers:
        print(f"{Fore.YELLOW}⏳ Analizando {ticker}...{Style.RESET_ALL}", end=" ", flush=True)
        
        try:
            # Análisis CORTO plazo (oportunidad operativa)
            agent_short = FinancialAgent(ticker, is_short_term=True, skip_external_data=True)
            short_analysis = agent_short.run_analysis()
            
            # Análisis LARGO plazo (valor fundamental)
            agent_long = FinancialAgent(ticker, is_short_term=False, skip_external_data=True)
            long_analysis = agent_long.run_analysis()
            
            # Calcular métricas
            combined_conf, short_conf, long_conf = calculate_combined_confidence(short_analysis, long_analysis)
            accum_rating, metrics = get_accumulation_rating(ticker, short_analysis, long_analysis)
            
            short_verdict = short_analysis.get('strategy', {}).get('verdict', 'N/A')
            long_verdict = long_analysis.get('strategy', {}).get('verdict', 'N/A')
            price = short_analysis.get('current_price', 0)
            
            # Clasificar acción de acumulación
            if long_verdict.upper().count('COMPRA') > 0 or 'BUY' in long_verdict.upper():
                # Acciones que merecen acumulación
                accion = "✅ ACUMULAR"
                estilo = Fore.LIGHTGREEN_EX
                
                # Sub-clasificar según corto plazo
                if short_verdict.upper().count('COMPRA') > 0 or 'BUY' in short_verdict.upper():
                    accion += " AGRESIVA"
                    priority = 1
                elif 'HOLD' in short_verdict.upper():
                    accion += " DCA"
                    priority = 2
                else:
                    accion += " (esperar rebote)"
                    priority = 3
            elif long_verdict.upper().count('VENTA') > 0 or 'SELL' in long_verdict.upper():
                accion = "❌ NO ACUMULAR"
                estilo = Fore.RED
                priority = 5
            else:
                accion = "🔄 MONITOREAR"
                estilo = Fore.YELLOW
                priority = 4
            
            results.append({
                'ticker': ticker,
                'price': price,
                'accum_rating': accum_rating,
                'combined_confidence': combined_conf,
                'short_confidence': short_conf,
                'long_confidence': long_conf,
                'short_verdict': short_verdict,
                'long_verdict': long_verdict,
                'action': accion,
                'priority': priority,
                'metrics': metrics,
                'analysis': (short_analysis, long_analysis)
            })
            
            print(f"{Fore.GREEN}✓{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error: {str(e)[:50]}{Style.RESET_ALL}")
    
    # Ordenar por Accumulation Rating (descendente)
    results.sort(key=lambda x: x['accum_rating'], reverse=True)
    
    return results


def print_detailed_report(results):
    """Imprime reporte detallado de acumulación."""
    
    print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 RESULTADOS - Ordenado por Accumulation Rating{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
    
    # Tabla principal
    print(f"{'Ticker':<8} {'Precio':<10} {'AccumRating':<12} {'Conf.Comb':<12} {'Action':<25} {'Short/Long Verdict':<35}")
    print(f"{'-' * 100}")
    
    for r in results:
        ticker = r['ticker']
        price = f"${r['price']:.2f}"
        rating = f"{r['accum_rating']:.0f}%"
        conf = f"{r['combined_confidence']:.0f}%"
        action = r['action']
        verdict = f"{r['short_verdict'][:10]} / {r['long_verdict'][:10]}"
        
        print(f"{ticker:<8} {price:<10} {rating:<12} {conf:<12} {action:<25} {verdict:<35}")
    
    print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📈 ANÁLISIS DETALLADO{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
    
    # Reporte por acción
    for r in results:
        ticker = r['ticker']
        rating = r['accum_rating']
        metrics = r['metrics']
        
        print(f"\n{Fore.LIGHTGREEN_EX}▸ {ticker}{Style.RESET_ALL}")
        print(f"  Precio: ${r['price']:.2f}")
        print(f"  Accumulation Rating: {rating:.0f}% | Combined Confidence: {r['combined_confidence']:.0f}%")
        print(f"  Acción: {r['action']}")
        print(f"  └─ Corto Plazo ({r['short_confidence']:.0f}%): {r['short_verdict']}")
        print(f"  └─ Largo Plazo ({r['long_confidence']:.0f}%): {r['long_verdict']}")
        
        print(f"\n  📊 Desglose Métricas:")
        print(f"     • Confianza Largo Plazo: {metrics['long_term_confidence']:.0f}%")
        print(f"     • Fortaleza Fundamental: {metrics['fundamental_strength']:.0f}%")
        print(f"     • Alineación Timeframes: {metrics['timeframe_alignment']:.0f}%")
        print(f"     • Fuerza Insiders: {metrics['insider_strength']:.0f}%")
        
        # Matriz de decisión
        print(f"\n  🎯 Matriz de Decisión:")
        short_buy = 'COMPRA' in r['short_verdict'].upper() or 'BUY' in r['short_verdict'].upper()
        long_buy = 'COMPRA' in r['long_verdict'].upper() or 'BUY' in r['long_verdict'].upper()
        
        if short_buy and long_buy:
            print(f"     ✅ CORTO: BUY + LARGO: BUY → {Fore.LIGHTGREEN_EX}ACUMULAR AGRESIVAMENTE{Style.RESET_ALL}")
        elif long_buy:
            print(f"     ⚠️  CORTO: {r['short_verdict'][:10]} + LARGO: BUY → {Fore.YELLOW}ACUMULAR DCA (escalonado){Style.RESET_ALL}")
        elif short_buy:
            print(f"     ⚠️  CORTO: BUY + LARGO: {r['long_verdict'][:10]} → {Fore.YELLOW}ESPERAR confirmación fundamental{Style.RESET_ALL}")
        else:
            print(f"     ❌ CORTO: {r['short_verdict'][:10]} + LARGO: {r['long_verdict'][:10]} → {Fore.RED}NO ACUMULAR{Style.RESET_ALL}")


def generate_accumulation_strategy(results):
    """
    Genera estrategia de acumulación personalizada basada en resultados.
    """
    
    print(f"\n\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🚀 ESTRATEGIA DE ACUMULACIÓN RECOMENDADA{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
    
    # Categorizar por tipo de acción
    aggressive = [r for r in results if '✅ ACUMULAR AGRESIVA' in r['action']]
    dca = [r for r in results if 'DCA' in r['action']]
    monitor = [r for r in results if '🔄 MONITOREAR' in r['action']]
    avoid = [r for r in results if '❌ NO ACUMULAR' in r['action']]
    
    print(f"{Fore.LIGHTGREEN_EX}🟢 ACUMULAR AGRESIVAMENTE (MÁXIMA OPORTUNIDAD){Style.RESET_ALL}")
    print(f"   Condición: Corto COMPRA + Largo COMPRA")
    print(f"   Tamaño recomendado: 75-100% de posición planeada")
    print(f"   Estrategia: Entrada grande ahora, pequeñas agregaciones después")
    if aggressive:
        for r in aggressive:
            print(f"   • {r['ticker']}: Rating {r['accum_rating']:.0f}% (${r['price']:.2f})")
    else:
        print(f"   (Ninguna acción cumple criterios ahora)")
    
    print(f"\n{Fore.YELLOW}🟡 ACUMULAR DCA - DOLLAR COST AVERAGING{Style.RESET_ALL}")
    print(f"   Condición: Largo COMPRA pero Corto HOLD/VENTA")
    print(f"   Tamaño recomendado: 25-50% mensual (distribuido)")
    print(f"   Estrategia: Entrada pequeña mensual, promediar precio")
    if dca:
        for r in dca:
            print(f"   • {r['ticker']}: Rating {r['accum_rating']:.0f}% (${r['price']:.2f})")
    else:
        print(f"   (Ninguna acción cumple criterios ahora)")
    
    print(f"\n{Fore.CYAN}🔵 MONITOREAR{Style.RESET_ALL}")
    print(f"   Condición: Métricas neutrales o indecisas")
    print(f"   Acción: No comprar aún, seguir de cerca")
    if monitor:
        for r in monitor:
            print(f"   • {r['ticker']}: Rating {r['accum_rating']:.0f}% (${r['price']:.2f})")
    else:
        print(f"   (Ninguna acción en esta categoría)")
    
    print(f"\n{Fore.RED}🔴 EVITAR{Style.RESET_ALL}")
    print(f"   Condición: Largo VENTA o métricas muy débiles")
    print(f"   Acción: NO comprar, esperar rotación estructura")
    if avoid:
        for r in avoid:
            print(f"   • {r['ticker']}: Rating {r['accum_rating']:.0f}% (${r['price']:.2f})")
    else:
        print(f"   (Ninguna acción flagueada)")
    
    print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    # Tickers a escanear (diversificado)
    tickers_by_sector = {
        'Tech Giants': ['MSFT', 'NVDA', 'META'],
        'Growth': ['TSLA', 'ARM'],
        'Defensive': ['WMT', 'ORCL'],
        'Financials': ['JPM'],
        'Semiconductors': ['BABA', 'SOFI'],
    }
    
    all_tickers = []
    for sector, tickers in tickers_by_sector.items():
        all_tickers.extend(tickers)
    
    # Ejecutar scanner
    results = scan_accumulation_opportunities(all_tickers)
    
    # Imprimir reportes
    print_detailed_report(results)
    generate_accumulation_strategy(results)
    
    # Exportar JSON
    export_data = []
    for r in results:
        export_data.append({
            'ticker': r['ticker'],
            'price': r['price'],
            'accumulation_rating': r['accum_rating'],
            'combined_confidence': r['combined_confidence'],
            'short_confidence': r['short_confidence'],
            'long_confidence': r['long_confidence'],
            'short_verdict': r['short_verdict'],
            'long_verdict': r['long_verdict'],
            'action': r['action'],
            'metrics': r['metrics']
        })
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"accumulation_scan_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"\n✅ Reporte exportado: {output_file}\n")
