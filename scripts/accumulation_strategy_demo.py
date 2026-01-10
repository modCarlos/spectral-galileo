#!/usr/bin/env python3
"""
🎯 Accumulation Strategy Demo - Demuestra cómo combinan corto y largo plazo
para identificar acciones "verdaderamente valiosas"
"""

from colorama import Fore, Style
from datetime import datetime

def demo_accumulation_strategy():
    """
    Demonstración visual de cómo funciona la estrategia de acumulación.
    Muestra ejemplos reales con los tickers del watchlist.
    """
    
    print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🎯 ESTRATEGIA DE ACUMULACIÓN - DEMOSTRACIÓN CONCEPTUAL{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
    
    # Ejemplos con los tickers del watchlist
    examples = [
        {
            'name': '📈 CASO 1: MSFT - Excelente Acumulación',
            'ticker': 'MSFT',
            'price': 416.25,
            'short_verdict': 'COMPRA',
            'short_confidence': 28,
            'short_reasoning': 'RSI 35 (oversold), MACD bullish, precio cerca SMA50',
            'long_verdict': 'COMPRA',
            'long_confidence': 42,
            'long_reasoning': 'ROE 35% > benchmark Tech 20%, PEG 1.2 < 1.5, deuda controlada',
            'insider': 'BULLISH (net_buying: +$2.3M)',
            'timeframes': {'daily': 'BUY', 'weekly': 'BUY', 'monthly': 'BUY'},
        },
        {
            'name': '🤖 CASO 2: NVDA - Semiconductor Volátil',
            'ticker': 'NVDA',
            'price': 128.50,
            'short_verdict': 'HOLD',
            'short_confidence': 22,
            'short_reasoning': 'RSI 45 (neutral), Bollinger Bands medio, sin momentum claro',
            'long_verdict': 'FUERTE COMPRA',
            'long_confidence': 51,
            'long_reasoning': 'ROE 50% >> Tech benchmark, PEG 0.9, dominancia AI indispensable',
            'insider': 'NEUTRAL',
            'timeframes': {'daily': 'HOLD', 'weekly': 'BUY', 'monthly': 'BUY'},
        },
        {
            'name': '❌ CASO 3: TSLA - Problemas Estructurales',
            'ticker': 'TSLA',
            'price': 242.80,
            'short_verdict': 'VENTA',
            'short_confidence': 18,
            'short_reasoning': 'RSI 28 (muy oversold), pero volumen bajo en rebotes, ADX 9 (sin tendencia)',
            'long_verdict': 'VENTA',
            'long_confidence': 22,
            'long_reasoning': 'ROE bajando, competencia china, márgenes presionados, PEG 1.8 elevado',
            'insider': 'BEARISH (net_selling: -$15M)',
            'timeframes': {'daily': 'SELL', 'weekly': 'SELL', 'monthly': 'HOLD'},
        },
        {
            'name': '⚠️  CASO 4: WMT - Defensa en Corrección',
            'ticker': 'WMT',
            'price': 89.30,
            'short_verdict': 'VENTA',
            'short_confidence': 25,
            'short_reasoning': 'Bajó 8% en 2 semanas, RSI 32, cierre debajo SMA50',
            'long_verdict': 'COMPRA',
            'long_confidence': 38,
            'long_reasoning': 'Dividend-paying, ROE 15%, deuda bajar reciente, e-commerce crece',
            'insider': 'BULLISH (net_buying: +$840K)',
            'timeframes': {'daily': 'SELL', 'weekly': 'BUY', 'monthly': 'BUY'},
        },
        {
            'name': '🔄 CASO 5: META - Recuperación Temprana',
            'ticker': 'META',
            'price': 498.50,
            'short_verdict': 'HOLD',
            'short_confidence': 30,
            'short_reasoning': 'Rebote fuerte últimos 5 días pero sin MACD cruce, Reels monetización en progreso',
            'long_verdict': 'COMPRA',
            'long_confidence': 35,
            'long_reasoning': 'Earnings beat expectativas, capex para IA bajo control, DAU growth 3% YoY',
            'insider': 'NEUTRAL (Mark Zuckerberg sin movimiento)',
            'timeframes': {'daily': 'HOLD', 'weekly': 'BUY', 'monthly': 'BUY'},
        },
    ]
    
    # Mostrar cada ejemplo
    for example in examples:
        print(f"{Fore.LIGHTCYAN_EX}{example['name']}{Style.RESET_ALL}\n")
        
        # Panel información
        print(f"  Ticker: {Fore.LIGHTGREEN_EX}{example['ticker']}{Style.RESET_ALL} | Precio: ${example['price']}")
        print(f"  Insiders: {example['insider']}\n")
        
        # Análisis Corto Plazo
        print(f"  {Fore.YELLOW}📊 CORTO PLAZO (Momentum Operativo):{Style.RESET_ALL}")
        print(f"     Verdict: {Fore.YELLOW}{example['short_verdict']}{Style.RESET_ALL} ({example['short_confidence']}%)")
        print(f"     Reasoning: {example['short_reasoning']}\n")
        
        # Análisis Largo Plazo
        print(f"  {Fore.LIGHTGREEN_EX}💰 LARGO PLAZO (Valor Fundamental):{Style.RESET_ALL}")
        print(f"     Verdict: {Fore.LIGHTGREEN_EX}{example['long_verdict']}{Style.RESET_ALL} ({example['long_confidence']}%)")
        print(f"     Reasoning: {example['long_reasoning']}\n")
        
        # Multi-timeframe
        tf_summary = []
        for tf, signal in example['timeframes'].items():
            color = Fore.LIGHTGREEN_EX if 'BUY' in signal else Fore.YELLOW if 'HOLD' in signal else Fore.RED
            tf_summary.append(f"{tf}: {color}{signal}{Style.RESET_ALL}")
        print(f"  🎯 Multi-Timeframe: {' | '.join(tf_summary)}\n")
        
        # DECISIÓN DE ACUMULACIÓN
        short_buy = 'COMPRA' in example['short_verdict'] or 'BUY' in example['short_verdict']
        long_buy = 'COMPRA' in example['long_verdict'] or 'FUERTE COMPRA' in example['long_verdict']
        short_sell = 'VENTA' in example['short_verdict'] or 'SELL' in example['short_verdict']
        long_sell = 'VENTA' in example['long_verdict'] or 'SELL' in example['long_verdict']
        
        print(f"  {Fore.LIGHTCYAN_EX}{'─' * 90}{Style.RESET_ALL}")
        print(f"  {Fore.LIGHTCYAN_EX}🎯 DECISIÓN DE ACUMULACIÓN:{Style.RESET_ALL}\n")
        
        if short_buy and long_buy:
            combined = (example['short_confidence'] * 0.6) + (example['long_confidence'] * 0.4)
            print(f"  ✅ {Fore.LIGHTGREEN_EX}ACUMULAR AGRESIVAMENTE{Style.RESET_ALL}")
            print(f"     Confianza Combinada: {combined:.0f}%")
            print(f"     └─ Tamaño recomendado: 75-100% de posición planeada")
            print(f"     └─ Estrategia: Entrada GRANDE ahora, agregar en dips")
            print(f"     └─ Por qué: Tanto momentum como fundamentales son sólidos")
            
        elif long_buy and not short_buy:
            combined = (example['short_confidence'] * 0.6) + (example['long_confidence'] * 0.4)
            print(f"  🟡 {Fore.YELLOW}ACUMULAR ESCALONADO (DCA){Style.RESET_ALL}")
            print(f"     Confianza Combinada: {combined:.0f}%")
            print(f"     └─ Tamaño recomendado: 25-50% mensual distribuido")
            print(f"     └─ Estrategia: Entrada pequeña mensual, promediar precio")
            print(f"     └─ Por qué: Fundamentales sólidos pero timing corto plazo incierto")
            
        elif short_buy and not long_buy:
            print(f"  ⚠️  {Fore.YELLOW}ESPERAR CONFIRMACIÓN{Style.RESET_ALL}")
            print(f"     └─ NO acumular aún, esperar claridad fundamental")
            print(f"     └─ Riesgo: Rebote técnico en acción con problemas reales")
            
        else:
            print(f"  ❌ {Fore.RED}NO ACUMULAR{Style.RESET_ALL}")
            print(f"     └─ Tanto momentum como fundamentales son débiles")
            print(f"     └─ Esperar a mejora estructural")
        
        print(f"\n{Fore.LIGHTCYAN_EX}{'═' * 90}{Style.RESET_ALL}\n")
    
    # Resumen de matriz
    print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📋 MATRIZ DE DECISIÓN - Resumen de 5 Casos{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
    
    print(f"{'Ticker':<8} {'Precio':<10} {'Corto':<15} {'Largo':<15} {'Decisión':<35} {'Confianza':<10}")
    print(f"{'-' * 100}")
    
    for example in examples:
        short_buy = 'COMPRA' in example['short_verdict']
        long_buy = 'COMPRA' in example['long_verdict'] or 'FUERTE COMPRA' in example['long_verdict']
        
        if short_buy and long_buy:
            decision = "✅ ACUMULAR AGRESIVA"
        elif long_buy and not short_buy:
            decision = "🟡 ACUMULAR DCA"
        elif short_buy and not long_buy:
            decision = "⚠️ ESPERAR CONFIRMACIÓN"
        else:
            decision = "❌ NO ACUMULAR"
        
        combined = (example['short_confidence'] * 0.6) + (example['long_confidence'] * 0.4)
        
        print(f"{example['ticker']:<8} ${example['price']:<9.2f} {example['short_verdict']:<15} "
              f"{example['long_verdict']:<15} {decision:<35} {combined:.0f}%")
    
    print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")


def show_accumulation_principles():
    """Muestra los principios clave de la acumulación inteligente."""
    
    print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}💡 PRINCIPIOS DE ACUMULACIÓN INTELIGENTE{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
    
    principles = [
        {
            'title': '1. PRECIO vs. VALOR',
            'content': [
                '❌ Comprar porque está barato → Falsa economía (puede caer más)',
                '✅ Comprar porque es barato Y tiene valor → Verdadera oportunidad',
                '',
                'MSFT a $350 (máximos) es MEJOR compra que TSLA a $150 (caída)',
                'si MSFT sigue creciendo y TSLA sigue cayendo'
            ]
        },
        {
            'title': '2. MULTI-HORIZONTE',
            'content': [
                'Corto Plazo (1-3 meses): ¿Cuándo entrar? → Timing operativo',
                'Largo Plazo (1-5 años): ¿Debo entrar? → Decisión estratégica',
                '',
                'Si solo miras corto plazo → Pierdes oportunidades de valor',
                'Si solo miras largo plazo → Entras en peor momento posible',
                'Combina ambos → Mejor entrada + mayor confianza'
            ]
        },
        {
            'title': '3. CONFLUENCIA DE SEÑALES',
            'content': [
                '2-3 timeframes en BUY = Mayor probabilidad de éxito',
                'Daily + Weekly + Monthly todos dicen BUY = MÁXIMA CONVICCIÓN',
                '',
                'Ej: WMT baja (daily SELL) pero weekly+monthly ↑',
                '→ Es corrección en tendencia alcista = ACUMULAR barato'
            ]
        },
        {
            'title': '4. TAMAÑO ESCALONADO',
            'content': [
                '✅ 25% ahora + 25% en -3% + 25% en -7% + 25% en estable',
                '❌ 100% ahora en precio que puede bajar más',
                '',
                'Promedio de entrada más bajo',
                'Menos arrepentimiento si baja más'
            ]
        },
        {
            'title': '5. FUNDAMENTALES NO DECEPCIONEN',
            'content': [
                'Antes de acumular, verifica que ROE, deuda, crecimiento sean sólidos',
                'Si fundamentales se deterioran → NO acumular sin importar rebote técnico',
                '',
                'Ej: TSLA caída + márgenes presionados + competencia china',
                '→ NO acumular, esperar rotación estructural'
            ]
        }
    ]
    
    for principle in principles:
        print(f"{Fore.LIGHTGREEN_EX}{principle['title']}{Style.RESET_ALL}\n")
        for line in principle['content']:
            if line.strip():
                print(f"   {line}")
            else:
                print()
        print()


if __name__ == "__main__":
    # Mostrar estrategia
    demo_accumulation_strategy()
    
    # Mostrar principios
    show_accumulation_principles()
    
    print(f"\n{Fore.LIGHTGREEN_EX}✅ CONCLUSIÓN:{Style.RESET_ALL}\n"
          f"La acumulación inteligente requiere AMBOS análisis:\n"
          f"• Corto Plazo: ¿Cuándo entrar? (timing)\n"
          f"• Largo Plazo: ¿Debo entrar? (valor)\n\n"
          f"Combina ambos y encontrarás acciones \"verdaderamente valiosas\"")
    print(f"donde el precio de entrada importa MENOS.\n")
