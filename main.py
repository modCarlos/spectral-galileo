import argparse
import sys
import portfolio_manager
import watchlist_manager
import market_data
from agent import FinancialAgent
from data_manager import DataManager
import concurrent.futures
from colorama import init, Fore, Style
from tabulate import tabulate
from tqdm import tqdm
import warnings
import signal
from contextlib import contextmanager

# Suprimir FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)

init(autoreset=True)

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def run_portfolio_scanner(is_short_term=False, generate_html=False):
    """
    Escanea el portafolio completo y muestra un resumen optimizado.
    """
    print(f"\n{Fore.MAGENTA}Iniciando Análisis de Portafolio Personal...{Style.RESET_ALL}")
    
    portfolio = portfolio_manager.load_portfolio()
    if not portfolio:
        print("Tu portafolio está vacío. Usa --add [TICKER] para agregar acciones.")
        return

    unique_tickers = sorted(list(set(item['symbol'] for item in portfolio)))
    
    dm = DataManager()
    macro_data = dm.get_macro_data()
    
    def analyze_ticker(t):
        try:
            data = dm.get_ticker_data(t)
            data['macro_data'] = macro_data
            agent = FinancialAgent(t, is_short_term=is_short_term)
            return t, agent.run_analysis(pre_data=data)
        except Exception as e:
            # print(f"Error analizando {t}: {e}") # Debug
            return t, None

    print(f"Analizando {len(unique_tickers)} acciones únicas en paralelo...")
    analysis_cache = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(tqdm(executor.map(analyze_ticker, unique_tickers), total=len(unique_tickers), desc="Holdings"))
        for t, res in results:
            if res and "error" not in res:
                analysis_cache[t] = res

    results_list = []
    for item in portfolio:
        t = item['symbol']
        buy_price = item['buy_price']
        
        if t not in analysis_cache:
            continue
            
        res = analysis_cache[t]
        curr_price = res['current_price']
        verdict = res['strategy']['verdict']
        
        pnl_pct = ((curr_price - buy_price) / buy_price) * 100
        pnl_str = f"{pnl_pct:+.2f}%"
        pnl_col = Fore.GREEN if pnl_pct > 0 else Fore.RED
        
        advice = "Mantener"
        if "COMPRA" in verdict:
            advice = f"{Fore.GREEN}Promediar Baja{Style.RESET_ALL}" if pnl_pct < 0 else f"{Fore.CYAN}Aumentar{Style.RESET_ALL}"
        elif "VENTA" in verdict:
            advice = f"{Fore.GREEN}Tomar Ganancia{Style.RESET_ALL}" if pnl_pct > 0 else f"{Fore.RED}Vender / SL{Style.RESET_ALL}"
            
        results_list.append([t, f"${buy_price:.2f}", f"${curr_price:.2f}", f"{pnl_col}{pnl_str}{Style.RESET_ALL}", verdict, advice])

    headers = ["Ticker", "Compra", "Actual", "P&L", "Veredicto", "Consejo"]
    print("\n" + "="*80)
    print(f"ESTADO DEL PORTAFOLIO")
    print("="*80 + "\n")
    print(tabulate(results_list, headers=headers, tablefmt="fancy_grid") + "\n")
    
    # Generar HTMLs si se solicitó
    if generate_html:
        try:
            portfolio_tickers = sorted(list(set(item['symbol'] for item in portfolio_manager.load_portfolio())))
            if portfolio_tickers:
                print(f"\n{Fore.CYAN}Generando reportes HTML para {len(portfolio_tickers)} acciones...{Style.RESET_ALL}")
                html_count = 0
                for ticker in portfolio_tickers:
                    try:
                        agent = FinancialAgent(ticker, is_short_term=is_short_term)
                        # Usar datos ya analizados si están disponibles
                        if ticker in analysis_cache:
                            agent.last_results = analysis_cache[ticker]
                        report_path = agent.generate_html_report(output_dir='./reports')
                        if report_path:
                            html_count += 1
                    except Exception:
                        pass
                if html_count > 0:
                    print(f"{Fore.GREEN}✅ {html_count} reportes HTML generados en ./reports/{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Error generando HTMLs: {str(e)}{Style.RESET_ALL}\n")

def run_watchlist_scanner(is_short_term=False, generate_html=False):
    """
    Escanea las acciones en la watchlist.
    """
    tickers = watchlist_manager.get_watchlist_tickers()
    if not tickers:
        print(f"\n{Fore.YELLOW}Tu watchlist está vacía. Usa --watch [TICKER] para agregar acciones.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.MAGENTA}Iniciando Análisis de tu Watchlist...{Style.RESET_ALL}")
    
    dm = DataManager()
    macro_data = dm.get_macro_data()
    
    def analyze_ticker(t):
        try:
            data = dm.get_ticker_data(t)
            data['macro_data'] = macro_data
            agent = FinancialAgent(t, is_short_term=is_short_term)
            return agent.run_analysis(pre_data=data)
        except Exception:
            return None

    print(f"Analizando {len(tickers)} acciones favoritas en paralelo...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(tqdm(executor.map(analyze_ticker, tickers), total=len(tickers), desc="Watchlist"))

    table_data = []
    for res in results:
        if not res or "error" in res: continue
        
        symbol = res['symbol']
        verdict = res['strategy']['verdict']
        v_color = Fore.GREEN if "COMPRA" in verdict else Fore.RED if "VENTA" in verdict else Fore.WHITE
        
        table_data.append([symbol, f"${res['current_price']:.2f}", f"{v_color}{verdict}{Style.RESET_ALL}", f"{res['strategy']['confidence']:.0f}%"])
            
    if table_data:
        print("\n" + tabulate(table_data, headers=["Ticker", "Precio", "Veredicto", "Confianza"], tablefmt="fancy_grid") + "\n")
    else:
        print(f"\n{Fore.YELLOW}No se pudieron obtener resultados para tu watchlist.{Style.RESET_ALL}")
    
    # Generar HTMLs si se solicitó
    if generate_html and table_data:
        try:
            print(f"{Fore.CYAN}Generando reportes HTML para {len(tickers)} acciones...{Style.RESET_ALL}")
            html_count = 0
            for ticker in tickers:
                try:
                    agent = FinancialAgent(ticker, is_short_term=is_short_term)
                    report_path = agent.generate_html_report(output_dir='./reports')
                    if report_path:
                        html_count += 1
                except Exception:
                    pass
            if html_count > 0:
                print(f"{Fore.GREEN}✅ {html_count} reportes HTML generados en ./reports/{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Error generando HTMLs: {str(e)}{Style.RESET_ALL}\n")



def run_scanner(is_short_term=False, generate_html=False):
    """
    Escanea las top 25 empresas del S&P 500 en paralelo.
    """
    tickers = market_data.get_sp500_top25()
    print(f"\n{Fore.CYAN}Escaneando Top 25 empresas del S&P 500 en paralelo...{Style.RESET_ALL}")
    
    dm = DataManager()
    macro_data = dm.get_macro_data()
    
    def analyze_ticker(t):
        try:
            data = dm.get_ticker_data(t)
            data['macro_data'] = macro_data
            agent = FinancialAgent(t, is_short_term=is_short_term)
            return agent.run_analysis(pre_data=data)
        except Exception as e:
            # print(f"Error analizando {t}: {e}") # Debug
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = list(tqdm(executor.map(analyze_ticker, tickers), total=len(tickers), desc="Escaneando"))

    table_data = []
    for res in results:
        if not res or "error" in res: continue
        
        symbol = res['symbol']
        verdict = res['strategy']['verdict']
        v_color = Fore.GREEN if "COMPRA" in verdict else Fore.RED if "VENTA" in verdict else Fore.WHITE
        
        if "COMPRA" in verdict or "VENTA" in verdict:
            table_data.append([symbol, f"${res['current_price']:.2f}", f"{v_color}{verdict}{Style.RESET_ALL}", f"{res['strategy']['confidence']:.0f}%"])
            
    if table_data:
        print("\n" + tabulate(table_data, headers=["Ticker", "Precio", "Veredicto", "Confianza"], tablefmt="fancy_grid"))
    else:
        print(f"\n{Fore.YELLOW}No se encontraron oportunidades claras.{Style.RESET_ALL}")
    
    # Generar HTMLs si se solicitó
    if generate_html and tickers:
        try:
            print(f"\n{Fore.CYAN}Generando reportes HTML para {len(tickers)} acciones...{Style.RESET_ALL}")
            html_count = 0
            for ticker in tickers:
                try:
                    agent = FinancialAgent(ticker, is_short_term=is_short_term)
                    report_path = agent.generate_html_report(output_dir='./reports')
                    if report_path:
                        html_count += 1
                except Exception:
                    pass
            if html_count > 0:
                print(f"{Fore.GREEN}✅ {html_count} reportes HTML generados en ./reports/{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Error generando HTMLs: {str(e)}{Style.RESET_ALL}\n")

def main():
    parser = argparse.ArgumentParser(
        description='🤖 Agente de Análisis Financiero Inteligente - Análisis técnico, fundamental, macro y cualitativo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EJEMPLOS DE USO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ANÁLISIS:
  python main.py AAPL                    Análisis Estructural (Horizonte: 3-5 años)
  python main.py --short-term AAPL       Análisis Táctico (Horizonte: 3-6 meses) + ADX/Trend Gate
  python main.py --scan                  Escanear Top 25 (Largo Plazo)
  python main.py --scan --short-term     Escanear con enfoque táctico (Corto Plazo)

💼 PORTAFOLIO:
  python main.py --scan-portfolio        Ver estado de tu portafolio (Consolidación)
  python main.py --add AAPL              Agregar AAPL al precio de mercado actual
  python main.py --add AAPL 150.50       Agregar AAPL a $150.50 personalizado
  python main.py --remove AAPL           Eliminar última entrada de AAPL
  python main.py --remove-all AAPL       Eliminar todas las entradas de AAPL
  python main.py --remove-all            Vaciar portafolio (con confirmación)

📈 BACKTESTING:
  python main.py --backtest NVDA         Simular estrategia en período reciente
  python main.py --backtest NVDA 2024-01-01 2024-12-31     Backtest período custom

🤖 ANÁLISIS CON IA:
  python main.py --ai AAPL               Análisis profundo generativo (Requiere GEMINI_API_KEY)

👀 WATCHLIST:
  python main.py --watch AAPL            Agregar acción a favoritos
  python main.py --unwatch AAPL          Eliminar de favoritos
  python main.py --watchlist             Analizar acciones en seguimiento
  python main.py --scan --watchlist      Escanear favoritos (Atajo)
SISTEMA DE EXCELENCIA 2.0:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Técnico:     RSI, MACD, ADX, Slope, MFI, Stoch (Momentum Integrado 0-1)
📈 Fundamental: P/E, PEG Refinado, ROE, FCF, Recomendaciones Filtradas
🌍 Macro:       VIX Dinámico, FGI Sensible a Tendencia, TNX Suavizado
📰 Sentimiento: Fuente Híbrida (Yahoo + Google RSS, ~30-40 noticias)
🎯 Narrativa:   Timing Adverso, Desafío Estructural, Consolidación

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
    )
    
    parser.add_argument('ticker', type=str, nargs='?', help='Símbolo de la acción a analizar (ej. AAPL)')
    
    # Escáner de Mercado
    parser.add_argument('--scan', '--reviewSP500', action='store_true', 
                        help='Escanear las Top 25 empresas del S&P 500')
    
    # Watchlist
    parser.add_argument('--watchlist', '--favs', action='store_true',
                        help='Escanear acciones en mi watchlist')
    parser.add_argument('--watch', type=str, metavar='TICKER',
                        help='Agregar acción a la watchlist')
    parser.add_argument('--unwatch', type=str, metavar='TICKER',
                        help='Eliminar acción de la watchlist')
    
    # Gestión de Portafolio
    parser.add_argument('--add', type=str, nargs='+', metavar='TICKER [PRICE]',
                        help='Agregar una acción al portafolio (ej. --add AAPL o --add AAPL 150.50)')
    parser.add_argument('--scan-portfolio', '--my-stocks', action='store_true',
                        help='Analizar mi portafolio guardado')
    parser.add_argument('--remove', type=str, metavar='TICKER',
                        help='Eliminar última entrada de una acción del portafolio')
    parser.add_argument('--remove-all', type=str, nargs='?', const='ALL', metavar='TICKER',
                        help='Eliminar todas las entradas de una acción (sin TICKER = vaciar portafolio)')
    
    # Backtesting
    parser.add_argument('--backtest', type=str, nargs='+', metavar='TICKER [START] [END]',
                        help='Backtesting simple (ej. --backtest NVDA 2025-01-01 2025-12-21)')
    
    # Report generation
    parser.add_argument('--html', action='store_true',
                        help='Generar reporte HTML del análisis (se guardará en ./reports/)')
    
    parser.add_argument('--short-term', action='store_true',
                        help='Análisis optimizado para el corto plazo (3-6 meses)')
    
    # Análisis con IA
    parser.add_argument('--ai', type=str, metavar='TICKER',
                        help='Análisis potenciado por IA con Gemini (requiere GEMINI_API_KEY)')
    
    args = parser.parse_args()
    
    # Procesar comandos
    if args.add:
        ticker = args.add[0]
        price = args.add[1] if len(args.add) > 1 else None
        msg = portfolio_manager.add_stock(ticker, price)
        print(f"\n{Fore.GREEN}{msg}{Style.RESET_ALL}\n")
        
    elif args.backtest:
        import backtest
        ticker = args.backtest[0]
        start = args.backtest[1] if len(args.backtest) > 1 else "2025-01-01"
        end = args.backtest[2] if len(args.backtest) > 2 else "2025-12-21"
        backtest.simple_backtest(ticker, start_date=start, end_date=end)
    
    elif args.ai:
        try:
            from llm_agent import LLMFinancialAgent
            agent = LLMFinancialAgent(args.ai)
            agent.run_llm_analysis()
        except ImportError as e:
            print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}\n")
        except ValueError as e:
            print(f"\n{Fore.YELLOW}{str(e)}{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"\n{Fore.RED}Error inesperado: {str(e)}{Style.RESET_ALL}\n")
        
    elif args.remove:
        msg = portfolio_manager.remove_last_stock(args.remove)
        print(f"\n{Fore.YELLOW}{msg}{Style.RESET_ALL}\n")
        
    elif args.remove_all is not None:
        if args.remove_all == 'ALL':
            # Vaciar portafolio completo - DOBLE CONFIRMACIÓN
            portfolio = portfolio_manager.load_portfolio()
            if not portfolio:
                print(f"\n{Fore.YELLOW}El portafolio ya está vacío.{Style.RESET_ALL}\n")
            else:
                print(f"\n{Fore.RED}⚠️  ADVERTENCIA: Estás a punto de ELIMINAR TODO el portafolio.{Style.RESET_ALL}")
                print(f"Tienes {len(portfolio)} entrada(s) guardada(s).")
                confirm1 = input("¿Estás seguro? (escribe 'SI' para confirmar): ")
                if confirm1.strip().upper() == 'SI':
                    confirm2 = input(f"{Fore.RED}Confirmación final. Escribe 'ELIMINAR TODO' para proceder: {Style.RESET_ALL}")
                    if confirm2.strip().upper() == 'ELIMINAR TODO':
                        msg = portfolio_manager.clear_portfolio()
                        print(f"\n{Fore.GREEN}{msg}{Style.RESET_ALL}\n")
                    else:
                        print(f"\n{Fore.CYAN}Operación cancelada.{Style.RESET_ALL}\n")
                else:
                    print(f"\n{Fore.CYAN}Operación cancelada.{Style.RESET_ALL}\n")
        else:
            # Eliminar todas las entradas de un ticker específico
            msg = portfolio_manager.remove_all_stock(args.remove_all)
            print(f"\n{Fore.YELLOW}{msg}{Style.RESET_ALL}\n")
            
    elif args.scan_portfolio:
        run_portfolio_scanner(is_short_term=args.short_term, generate_html=args.html)
        
    elif args.watchlist or (args.scan and not any([args.add, args.remove, args.remove_all])):
        # Si se usa --watchlist O si se usa --scan pero el usuario tiene intención de ver favoritos (lógica flexible)
        # Priorizamos el comando explícito
        if args.watchlist:
            run_watchlist_scanner(is_short_term=args.short_term, generate_html=args.html)
        elif args.scan:
            run_scanner(is_short_term=args.short_term, generate_html=args.html)
            
    elif args.watch:
        msg = watchlist_manager.add_to_watchlist(args.watch)
        print(f"\n{Fore.GREEN}{msg}{Style.RESET_ALL}\n")

    elif args.unwatch:
        msg = watchlist_manager.remove_from_watchlist(args.unwatch)
        print(f"\n{Fore.YELLOW}{msg}{Style.RESET_ALL}\n")
        
    elif args.ticker:
        print(f"\nIniciando análisis para {Fore.CYAN}{args.ticker}{Style.RESET_ALL}...")
        print("Recopilando datos fundamentales, técnicos y noticias...\n")
        
        dm = DataManager()
        try:
            # Obtener datos y macro en paralelo a través del DataManager
            data = dm.get_ticker_data(args.ticker)
            data['macro_data'] = dm.get_macro_data()
            
            agent = FinancialAgent(args.ticker, is_short_term=args.short_term)
            results = agent.run_analysis(pre_data=data)
            
            if "error" in results:
                print(f"\n{Fore.RED}Error al analizar {args.ticker}: {results['error']}{Style.RESET_ALL}\n")
            else:
                print(agent.get_report_string())
                
                # Generar HTML si se solicitó
                if args.html:
                    try:
                        report_path = agent.generate_html_report(output_dir='./reports')
                        if report_path:
                            print(f"\n{Fore.GREEN}✅ Reporte HTML generado:{Style.RESET_ALL}")
                            print(f"   📄 {report_path}\n")
                        else:
                            print(f"\n{Fore.YELLOW}⚠️ No se pudo generar el reporte HTML{Style.RESET_ALL}\n")
                    except Exception as e:
                        print(f"\n{Fore.YELLOW}⚠️ Error generando HTML: {str(e)}{Style.RESET_ALL}\n")
                
                print(f"{Fore.GREEN}Análisis Completado.{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}Error inesperado: {str(e)}{Style.RESET_ALL}\n")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
