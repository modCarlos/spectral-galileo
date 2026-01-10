#!/usr/bin/env python3
"""
Demo script: Muestra ejemplo de las 3 tablas del sistema de acumulación
sin ejecutar análisis completos (usa datos mock)
"""

from tabulate import tabulate
from colorama import Fore, Style

def demo_watchlist_output():
    """Muestra exactamente cómo se verá la salida del -ws command"""
    
    print(f"\n{Fore.MAGENTA}Iniciando Análisis de tu Watchlist...{Style.RESET_ALL}\n")
    
    # TABLA 1
    print(f"{Fore.CYAN}{'═' * 120}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 ANÁLISIS DE CORTO PLAZO (Timing Operativo){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 120}{Style.RESET_ALL}\n")
    
    short_table = [
        ["MSFT", "$425.30", f"{Fore.GREEN}FUERTE COMPRA{Style.RESET_ALL}", "87%", "📈 Alcista"],
        ["ARM", "$142.50", f"{Fore.GREEN}COMPRA{Style.RESET_ALL}", "65%", "📈 Alcista"],
        ["META", "$510.20", f"{Fore.WHITE}HOLD{Style.RESET_ALL}", "52%", "↔️ Neutral"],
        ["ORCL", "$138.20", f"{Fore.WHITE}HOLD{Style.RESET_ALL}", "48%", "↔️ Neutral"],
        ["BABA", "$89.10", f"{Fore.RED}VENTA{Style.RESET_ALL}", "35%", "📉 Bajista"],
    ]
    
    print(tabulate(short_table, 
                   headers=["Ticker", "Precio", "Veredicto", "Confianza", "Tendencia"],
                   tablefmt="fancy_grid"))
    
    # TABLA 2
    print(f"\n{Fore.CYAN}{'═' * 120}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}💰 ANÁLISIS DE LARGO PLAZO (Valor Fundamental){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 120}{Style.RESET_ALL}\n")
    
    long_table = [
        ["MSFT", f"{Fore.GREEN}COMPRA{Style.RESET_ALL}", "82%", "1.8", "✓"],
        ["ARM", f"{Fore.WHITE}HOLD{Style.RESET_ALL}", "58%", "2.5", "✗"],
        ["META", f"{Fore.GREEN}COMPRA{Style.RESET_ALL}", "78%", "1.4", "✓"],
        ["ORCL", f"{Fore.GREEN}COMPRA{Style.RESET_ALL}", "75%", "1.2", "✓"],
        ["BABA", f"{Fore.RED}VENTA{Style.RESET_ALL}", "28%", "4.2", "✗"],
    ]
    
    print(tabulate(long_table,
                   headers=["Ticker", "Veredicto", "Confianza", "PEG", "Valuation OK"],
                   tablefmt="fancy_grid"))
    
    # TABLA 3
    print(f"\n{Fore.CYAN}{'═' * 120}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTGREEN_EX}🎯 RECOMENDACIÓN DE ACUMULACIÓN{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 120}{Style.RESET_ALL}\n")
    
    accum_table = [
        ["MSFT", "85%", "84%", "87% / 82%", "ACUMULAR AGRESIVA", "100%"],
        ["META", "78%", "76%", "75% / 78%", "ACUMULAR AGRESIVA", "100%"],
        ["ORCL", "72%", "68%", "48% / 75%", "DCA", "50%"],
        ["ARM", "62%", "64%", "65% / 58%", "DCA", "50%"],
        ["BABA", "35%", "38%", "35% / 28%", "NO COMPRAR", "0%"],
    ]
    
    print(tabulate(accum_table,
                   headers=["Ticker", "AccumRating", "CombConf", "Short/Long", "Acción", "Tamaño"],
                   tablefmt="fancy_grid"))
    
    # RESUMEN
    print(f"\n{Fore.CYAN}{'═' * 120}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}RESUMEN:{Style.RESET_ALL}")
    print(f"  Total analizado: 5 acciones")
    print(f"  {Fore.LIGHTGREEN_EX}✅ ACUMULAR AGRESIVA: 2{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}🟡 ACUMULAR DCA: 2{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}⚠️  ESPERAR rebote: 0{Style.RESET_ALL}")
    print(f"  {Fore.RED}❌ NO COMPRAR: 1{Style.RESET_ALL}")
    print(f"  {Fore.RED}🔴 EVITAR: 0{Style.RESET_ALL}")
    print(f"  ❌ Errores: 0")
    print(f"{Fore.CYAN}{'═' * 120}{Style.RESET_ALL}\n")

def demo_individual_ticker():
    """Muestra ejemplo de análisis individual (python main.py MSFT)"""
    
    print(f"\n{Fore.CYAN}{'═' * 80}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTGREEN_EX}🎯 ANÁLISIS DE ACUMULACIÓN (Corto + Largo Plazo) - MSFT{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 80}{Style.RESET_ALL}\n")
    
    # Tabla 1
    print(f"{Fore.YELLOW}Comparativa Corto vs Largo Plazo:{Style.RESET_ALL}\n")
    
    comp_table = [
        ["Métrica", "Corto Plazo", "Largo Plazo"],
        ["Veredicto", "FUERTE COMPRA", "COMPRA"],
        ["Confianza", "87%", "82%"],
        ["Timeframe", "1-3 meses", "3-5 años"],
        ["Enfoque", "Momentum/Timing", "Fundamentales/Valor"],
    ]
    
    print(tabulate(comp_table[1:], headers=comp_table[0], tablefmt="fancy_grid"))
    
    # Tabla 2
    print(f"\n{Fore.LIGHTGREEN_EX}Métricas de Acumulación:{Style.RESET_ALL}\n")
    
    metrics_table = [
        ["Métrica", "Valor"],
        ["Accumulation Rating", "85%"],
        ["Confianza Combinada", "84%"],
        ["Long Term Confidence", "82%"],
        ["Fundamental Strength", "88%"],
        ["Timeframe Alignment", "75%"],
        ["Insider Strength", "65%"],
    ]
    
    print(tabulate(metrics_table[1:], headers=metrics_table[0], tablefmt="fancy_grid"))
    
    # Tabla 3
    print(f"\n{Fore.LIGHTGREEN_EX}Recomendación de Acumulación:{Style.RESET_ALL}")
    print(f"\n  {Fore.GREEN}✅ ACUMULAR AGRESIVA{Style.RESET_ALL}")
    print(f"  Tamaño de Posición: 100%")
    print(f"  Razonamiento: Valor fundamental excelente (PEG=1.8) + Momentum")
    print(f"              positivo en corto plazo. Consenso COMPRA en ambos")
    print(f"              análisis. Esta es la mejor oportunidad de entrada.")
    
    print(f"\n{Fore.CYAN}{'═' * 80}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    print(f"\n{Fore.MAGENTA}╔════════════════════════════════════════════════════════════════════╗")
    print(f"║    DEMO: SISTEMA DE ANÁLISIS DE ACUMULACIÓN                      ║")
    print(f"║    (Opción D: Combinando Corto Plazo + Largo Plazo)              ║")
    print(f"╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}EJEMPLO 1: python main.py -ws   (Escanear watchlist){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    
    demo_watchlist_output()
    
    print(f"\n{Fore.YELLOW}═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}EJEMPLO 2: python main.py MSFT   (Análisis individual){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    
    demo_individual_ticker()
    
    print(f"\n{Fore.LIGHTGREEN_EX}Para ver la guía completa: cat ACCUMULATION_COLUMNS_GUIDE.md{Style.RESET_ALL}")
    print(f"{Fore.LIGHTGREEN_EX}Para ejecutar de verdad:   python main.py -ws{Style.RESET_ALL}\n")
