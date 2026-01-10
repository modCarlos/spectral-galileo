#!/usr/bin/env python3
"""
Test script para verificar la implementación de Accumulation Strategy
sin esperar a análisis completos (usa skip_external_data=True)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.spectral_galileo.core.agent import FinancialAgent
from src.spectral_galileo.core.accumulation_helper import (
    calculate_combined_confidence, get_accumulation_rating, 
    get_accumulation_decision, format_accumulation_summary
)
from colorama import Fore, Style
from tabulate import tabulate

def test_accumulation_ticker(ticker):
    """Test accumulation analysis para un ticker"""
    
    print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTGREEN_EX}🎯 PRUEBA: Análisis de Acumulación para {ticker}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
    
    try:
        # Análisis CORTO plazo (sin datos externos para rapidez)
        print(f"{Fore.YELLOW}⏳ Analizando corto plazo...{Style.RESET_ALL}")
        agent_short = FinancialAgent(ticker, is_short_term=True, skip_external_data=True)
        short_analysis = agent_short.run_analysis()
        
        # Análisis LARGO plazo
        print(f"{Fore.YELLOW}⏳ Analizando largo plazo...{Style.RESET_ALL}")
        agent_long = FinancialAgent(ticker, is_short_term=False, skip_external_data=True)
        long_analysis = agent_long.run_analysis()
        
        print(f"{Fore.GREEN}✓ Análisis completado{Style.RESET_ALL}\n")
        
        # Calcular métricas
        combined_conf, short_conf, long_conf = calculate_combined_confidence(short_analysis, long_analysis)
        accum_rating, metrics = get_accumulation_rating(short_analysis, long_analysis)
        
        short_verdict = short_analysis.get('strategy', {}).get('verdict', 'N/A')
        long_verdict = long_analysis.get('strategy', {}).get('verdict', 'N/A')
        price = short_analysis.get('current_price', 0)
        
        decision = get_accumulation_decision(short_verdict, long_verdict, combined_conf)
        
        # === TABLA 1: Comparativa ===
        print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}📊 TABLA 1: Análisis Comparativo Corto vs Largo Plazo{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
        
        comparison_data = [
            [ticker, short_verdict, f"{short_conf:.0f}%", long_verdict, f"{long_conf:.0f}%"],
        ]
        
        print(tabulate(
            comparison_data,
            headers=["Ticker", "Corto Plazo Verdict", "Conf. Corto", "Largo Plazo Verdict", "Conf. Largo"],
            tablefmt="fancy_grid"
        ))
        
        # === TABLA 2: Métricas de Acumulación ===
        print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}🎯 TABLA 2: Métricas de Acumulación{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
        
        metrics_data = [
            ["Accumulation Rating", f"{accum_rating:.0f}%"],
            ["Confianza Combinada", f"{combined_conf:.0f}%"],
            ["Long-term Confidence (40%)", f"{metrics['long_term_confidence']:.0f}%"],
            ["Fundamental Strength (30%)", f"{metrics['fundamental_strength']:.0f}%"],
            ["Timeframe Alignment (20%)", f"{metrics['timeframe_alignment']:.0f}%"],
            ["Insider Strength (10%)", f"{metrics['insider_strength']:.0f}%"],
        ]
        
        print(tabulate(
            metrics_data,
            headers=["Métrica", "Valor"],
            tablefmt="fancy_grid"
        ))
        
        # === TABLA 3: Decisión ===
        print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}💡 TABLA 3: Recomendación de Acumulación{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
        
        decision_data = [
            [ticker, f"${price:.2f}", decision['action'], decision['position_size'], decision['reasoning']],
        ]
        
        print(tabulate(
            decision_data,
            headers=["Ticker", "Precio", "Acción", "Tamaño", "Reasoning"],
            tablefmt="fancy_grid"
        ))
        
        print(f"\n{Fore.CYAN}{'═' * 100}{Style.RESET_ALL}\n")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test con los primeros 3 tickers del watchlist
    tickers = ['MSFT', 'ARM', 'ORCL']
    
    for ticker in tickers:
        test_accumulation_ticker(ticker)
