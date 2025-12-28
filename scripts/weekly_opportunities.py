#!/usr/bin/env python3
"""
Weekly Opportunities Scanner
Analiza acciones clave para identificar las mejores oportunidades de la semana
usando el sistema de zonas de confianza.
"""

import sys
import os

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

# Direct import from agent module
from spectral_galileo.core.agent import FinancialAgent
from colorama import Fore, Style
import json
from datetime import datetime

def analyze_opportunities():
    """Analiza oportunidades de inversión para la próxima semana."""
    
    print(f"\n{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔍 ANÁLISIS SEMANAL DE OPORTUNIDADES{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}\n")
    
    # Tickers por sector (diversificado)
    tickers_by_sector = {
        'Tech Giants': ['AAPL', 'MSFT', 'GOOGL', 'META'],
        'AI/Semiconductors': ['NVDA', 'AMD', 'AVGO'],
        'Growth': ['AMZN', 'TSLA', 'NFLX'],
        'Financials': ['JPM', 'BAC', 'V', 'MA'],
        'Defensive': ['WMT', 'KO', 'PG', 'JNJ'],
    }
    
    results = []
    
    print(f"{Fore.YELLOW}Analizando acciones clave...{Style.RESET_ALL}\n")
    
    for sector, tickers in tickers_by_sector.items():
        print(f"\n{Fore.CYAN}▸ {sector}:{Style.RESET_ALL}")
        
        for ticker in tickers:
            try:
                # Análisis rápido sin APIs externas
                trading_agent = FinancialAgent(
                    ticker, 
                    is_short_term=False, 
                    skip_external_data=True
                )
                result = trading_agent.run_analysis()
                
                if result and 'strategy' in result:
                    strategy = result['strategy']
                    confidence = strategy.get('confidence', 0)
                    verdict = strategy.get('verdict', 'N/A')
                    
                    # Determinar zona
                    if confidence >= 75:
                        zone = 'VERDE'
                        zone_emoji = '🟢'
                        priority = 4
                        position_size = '100%'
                    elif confidence >= 55:
                        zone = 'AMARILLA'
                        zone_emoji = '🟡'
                        priority = 3
                        position_size = '50-75%'
                    elif confidence >= 30:
                        zone = 'GRIS'
                        zone_emoji = '⚠️'
                        priority = 2
                        position_size = '25-40%'
                    else:
                        zone = 'ROJA'
                        zone_emoji = '🔴'
                        priority = 1
                        position_size = '0%'
                    
                    # Solo incluir señales de COMPRA
                    if 'COMPRA' in verdict:
                        results.append({
                            'ticker': ticker,
                            'sector': sector,
                            'confidence': confidence,
                            'verdict': verdict,
                            'zone': zone,
                            'zone_emoji': zone_emoji,
                            'priority': priority,
                            'position_size': position_size,
                            'price': result.get('current_price', 0),
                            'stop_loss': strategy.get('stop_loss', 0),
                        })
                        
                        # Print inmediato
                        verdict_short = verdict.replace('🚀', '').replace('🟢', '').strip()[:25]
                        print(f"  {zone_emoji} {ticker:6s} - {confidence:5.1f}% - {verdict_short}")
                    else:
                        print(f"  ⚪ {ticker:6s} - {confidence:5.1f}% - {verdict[:20]}")
                        
            except Exception as e:
                print(f"  ❌ {ticker:6s} - Error en análisis")
    
    # Generar reporte final
    print(f"\n{Fore.MAGENTA}{'═' * 70}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}🎯 RECOMENDACIONES PARA LA PRÓXIMA SEMANA{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'═' * 70}{Style.RESET_ALL}\n")
    
    if not results:
        print(f"{Fore.YELLOW}⚠️  No hay señales de COMPRA fuertes en este momento.{Style.RESET_ALL}")
        print(f"{Fore.WHITE}   Sugerencia: Mantener efectivo y esperar mejores oportunidades.{Style.RESET_ALL}\n")
        return
    
    # Ordenar por prioridad y confianza
    results.sort(key=lambda x: (x['priority'], x['confidence']), reverse=True)
    
    # Recomendaciones por zona
    print(f"{Fore.WHITE}📊 CLASIFICACIÓN POR ZONA DE CONFIANZA:\n{Style.RESET_ALL}")
    
    # Zona Verde
    green = [r for r in results if r['zone'] == 'VERDE']
    if green:
        print(f"{Fore.GREEN}{'─' * 70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🟢 ZONA VERDE - Alta Confianza (75-100%){Style.RESET_ALL}")
        print(f"{Fore.GREEN}   Acción: Compra posición COMPLETA (100% del tamaño planeado){Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'─' * 70}{Style.RESET_ALL}")
        for i, r in enumerate(green, 1):
            print(f"\n{Fore.WHITE}{i}. {r['ticker']:6s} - {r['sector']}{Style.RESET_ALL}")
            print(f"   Confianza: {Fore.GREEN}{r['confidence']:.1f}%{Style.RESET_ALL}")
            print(f"   Veredicto: {r['verdict']}")
            print(f"   Precio: ${r['price']:.2f} | Stop Loss: ${r['stop_loss']:.2f}")
        print()
    
    # Zona Amarilla
    yellow = [r for r in results if r['zone'] == 'AMARILLA']
    if yellow:
        print(f"{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🟡 ZONA AMARILLA - Confianza Moderada (55-75%){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Acción: Compra posición PARCIAL (50-75% del tamaño){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}")
        for i, r in enumerate(yellow, 1):
            print(f"\n{Fore.WHITE}{i}. {r['ticker']:6s} - {r['sector']}{Style.RESET_ALL}")
            print(f"   Confianza: {Fore.YELLOW}{r['confidence']:.1f}%{Style.RESET_ALL}")
            print(f"   Veredicto: {r['verdict']}")
            print(f"   Precio: ${r['price']:.2f} | Stop Loss: ${r['stop_loss']:.2f}")
        print()
    
    # Zona Gris
    gray = [r for r in results if r['zone'] == 'GRIS']
    if gray:
        print(f"{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  ZONA GRIS - Señales Mixtas (30-55%){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Acción: Solo posición PEQUEÑA (25-40% MÁXIMO){Style.RESET_ALL}")
        print(f"{Fore.RED}   ⚠️  PRECAUCIÓN: Stop loss MÁS ESTRICTO (-5% a -8%){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}")
        for i, r in enumerate(gray, 1):
            print(f"\n{Fore.WHITE}{i}. {r['ticker']:6s} - {r['sector']}{Style.RESET_ALL}")
            print(f"   Confianza: {Fore.YELLOW}{r['confidence']:.1f}%{Style.RESET_ALL}")
            print(f"   Veredicto: {r['verdict']}")
            print(f"   Precio: ${r['price']:.2f} | Stop Loss: ${r['stop_loss']:.2f}")
            print(f"   {Fore.RED}⚠️  Usar stop loss estricto y tamaño reducido{Style.RESET_ALL}")
        print()
    
    # Top 5 general
    print(f"{Fore.MAGENTA}{'═' * 70}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}🏆 TOP 5 ACCIONES RECOMENDADAS{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'═' * 70}{Style.RESET_ALL}\n")
    
    for i, r in enumerate(results[:5], 1):
        print(f"{i}. {r['zone_emoji']} {Fore.WHITE}{Style.BRIGHT}{r['ticker']:6s}{Style.RESET_ALL} " +
              f"({r['sector']}) - {Fore.CYAN}Confianza: {r['confidence']:.1f}%{Style.RESET_ALL}")
        print(f"   Tamaño sugerido: {r['position_size']}")
        print(f"   Precio: ${r['price']:.2f} | Stop: ${r['stop_loss']:.2f}")
        print()
    
    # Diversificación sugerida
    print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}💡 ESTRATEGIA DE DIVERSIFICACIÓN:{Style.RESET_ALL}\n")
    
    # Contar por sector
    sectors = {}
    for r in results[:5]:
        sectors[r['sector']] = sectors.get(r['sector'], 0) + 1
    
    print(f"{Fore.WHITE}Top 5 cubre {len(sectors)} sectores:{Style.RESET_ALL}")
    for sector, count in sectors.items():
        print(f"  • {sector}: {count} acción(es)")
    
    print(f"\n{Fore.GREEN}✅ Recomendación: Distribuye tu capital entre los Top 3-5{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   según tu perfil de riesgo y las zonas de confianza.{Style.RESET_ALL}\n")
    
    print(f"{Fore.MAGENTA}{'═' * 70}{Style.RESET_ALL}\n")
    
    # Save results
    output_file = f"data/weekly_opportunities_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'date': datetime.now().isoformat(),
            'results': results
        }, f, indent=2)
    
    print(f"{Fore.GREEN}✅ Resultados guardados en: {output_file}{Style.RESET_ALL}\n")

if __name__ == '__main__':
    analyze_opportunities()
