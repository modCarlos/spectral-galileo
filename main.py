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
        confidence = res['strategy']['confidence']
        
        pnl_pct = ((curr_price - buy_price) / buy_price) * 100
        pnl_str = f"{pnl_pct:+.2f}%"
        pnl_col = Fore.GREEN if pnl_pct > 0 else Fore.RED
        
        advice = "Mantener"
        if "COMPRA" in verdict:
            advice = f"{Fore.GREEN}Promediar Baja{Style.RESET_ALL}" if pnl_pct < 0 else f"{Fore.CYAN}Aumentar{Style.RESET_ALL}"
        elif "VENTA" in verdict:
            advice = f"{Fore.GREEN}Tomar Ganancia{Style.RESET_ALL}" if pnl_pct > 0 else f"{Fore.RED}Vender / SL{Style.RESET_ALL}"
            
        results_list.append([t, f"${buy_price:.2f}", f"${curr_price:.2f}", f"{pnl_col}{pnl_str}{Style.RESET_ALL}", verdict, f"{confidence:.0f}%", advice])

    headers = ["Ticker", "Compra", "Actual", "P&L", "Veredicto", "Confianza", "Consejo"]
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
        confidence = res['strategy']['confidence']
        v_color = Fore.GREEN if "COMPRA" in verdict else Fore.RED if "VENTA" in verdict else Fore.WHITE
        
        table_data.append([symbol, f"${res['current_price']:.2f}", f"{v_color}{verdict}{Style.RESET_ALL}", f"{confidence:.0f}%"])
    
    # Ordenar por confianza descendente
    table_data.sort(key=lambda x: float(x[3].rstrip('%')), reverse=True)
            
    if table_data:
        full_table = tabulate(table_data, headers=["Ticker", "Precio", "Veredicto", "Confianza"], tablefmt="fancy_grid")
        print("\n" + full_table + "\n")
        
        # Resumen por veredicto
        compra = len([x for x in table_data if "COMPRA" in x[2]])
        venta = len([x for x in table_data if "VENTA" in x[2]])
        neutral = len([x for x in table_data if "NEUTRAL" in x[2] or "MANTENER" in x[2]])
        
        print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
        print(f"{Fore.CYAN}RESUMEN:{Style.RESET_ALL}")
        print(f"  Total analizado: {len(table_data)} acciones")
        print(f"  🟢 COMPRA/FUERTE COMPRA: {compra}")
        print(f"  🔴 VENTA/FUERTE VENTA: {venta}")
        print(f"  ⚪ NEUTRAL/MANTENER: {neutral}")
        print(f"  ❌ Errores de descarga: {len(tickers) - len(table_data)}")
        print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}\n")
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

def handle_alerts_command(command: str, dry_run: bool = False):
    """
    Maneja comandos del sistema de alertas.
    
    Args:
        command: 'start', 'stop', 'status', 'test', 'config'
        dry_run: Modo dry-run para testing
    """
    from alerts.state import is_daemon_running, get_daemon_pid, get_stats
    from alerts.config import load_config
    from alerts.notifier import send_test_notification
    from alerts.market_hours import get_market_status
    import subprocess
    import os
    import signal
    import json
    
    if command == 'start':
        # Iniciar daemon
        if is_daemon_running():
            print(f"{Fore.YELLOW}⚠️  El daemon ya está corriendo (PID: {get_daemon_pid()}){Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}🚀 Iniciando sistema de alertas...{Style.RESET_ALL}")
        
        # Ejecutar daemon en background
        python_exec = sys.executable
        daemon_script = os.path.join(os.path.dirname(__file__), 'alerts', 'daemon.py')
        
        cmd = [python_exec, daemon_script]
        if dry_run:
            cmd.append('--dry-run')
            print(f"{Fore.YELLOW}   [DRY RUN MODE - No enviará notificaciones reales]{Style.RESET_ALL}")
        
        # Iniciar proceso en background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Esperar un momento para verificar que inició
        import time
        time.sleep(2)
        
        if is_daemon_running():
            pid = get_daemon_pid()
            config = load_config()
            print(f"{Fore.GREEN}✅ Daemon iniciado correctamente (PID: {pid}){Style.RESET_ALL}")
            print(f"{Fore.CYAN}📊 Configuración:{Style.RESET_ALL}")
            print(f"   - Intervalo: {config['interval_minutes']} minutos")
            print(f"   - Modo: {config['analysis_mode']}")
            print(f"   - Confianza mínima: {config['min_confidence']}")
            print(f"   - Estado del mercado: {get_market_status()}")
            print(f"\n{Fore.GREEN}💡 Usa 'python main.py --alerts status' para ver el estado{Style.RESET_ALL}")
            print(f"{Fore.GREEN}💡 Usa 'python main.py --alerts stop' para detener{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.RED}❌ Error iniciando daemon. Ver logs/alerts.log{Style.RESET_ALL}")
    
    elif command == 'stop':
        # Detener daemon
        if not is_daemon_running():
            print(f"{Fore.YELLOW}⚠️  El daemon no está corriendo{Style.RESET_ALL}")
            return
        
        pid = get_daemon_pid()
        print(f"{Fore.CYAN}🛑 Deteniendo daemon (PID: {pid})...{Style.RESET_ALL}")
        
        try:
            os.kill(pid, signal.SIGTERM)
            
            # Esperar a que termine
            import time
            for _ in range(5):
                time.sleep(1)
                if not is_daemon_running():
                    break
            
            if not is_daemon_running():
                print(f"{Fore.GREEN}✅ Daemon detenido correctamente{Style.RESET_ALL}\n")
            else:
                print(f"{Fore.YELLOW}⚠️  Daemon no responde, forzando terminación...{Style.RESET_ALL}")
                os.kill(pid, signal.SIGKILL)
                print(f"{Fore.GREEN}✅ Daemon terminado{Style.RESET_ALL}\n")
        
        except ProcessLookupError:
            print(f"{Fore.YELLOW}⚠️  Proceso no encontrado, limpiando estado...{Style.RESET_ALL}")
            from alerts.state import remove_daemon_pid
            remove_daemon_pid()
        except Exception as e:
            print(f"{Fore.RED}❌ Error deteniendo daemon: {e}{Style.RESET_ALL}")
    
    elif command == 'status':
        # Mostrar estado del sistema
        stats = get_stats()
        config = load_config()
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📡 ESTADO DEL SISTEMA DE ALERTAS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # Estado del daemon
        if stats['daemon_running']:
            pid = get_daemon_pid()
            print(f"🟢 Daemon: {Fore.GREEN}CORRIENDO{Style.RESET_ALL} (PID: {pid})")
        else:
            print(f"🔴 Daemon: {Fore.RED}DETENIDO{Style.RESET_ALL}")
        
        print(f"📊 Estado del mercado: {get_market_status()}")
        print()
        
        # Estadísticas
        print(f"{Fore.CYAN}📈 ESTADÍSTICAS:{Style.RESET_ALL}")
        print(f"   Escaneos realizados: {stats['total_scans']}")
        print(f"   Alertas enviadas: {stats['total_alerts_sent']}")
        print(f"   Alertas esta hora: {stats['alerts_this_hour']}/{config['max_alerts_per_hour']}")
        print(f"   Tickers en watchlist: {stats['watchlist_count']}")
        print(f"   Posiciones en portafolio: {stats['portfolio_count']}")
        print(f"   Tickers en historial: {stats['tickers_in_history']}")
        
        if stats['last_scan']:
            from datetime import datetime
            last_scan = datetime.fromisoformat(stats['last_scan'])
            print(f"   Último escaneo: {last_scan.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"   Último escaneo: Nunca")
        print()
        
        # Configuración
        print(f"{Fore.CYAN}⚙️  CONFIGURACIÓN:{Style.RESET_ALL}")
        print(f"   Intervalo: {config['interval_minutes']} minutos")
        print(f"   Modo de análisis: {config['analysis_mode']}")
        print(f"   Confianza mínima:")
        print(f"      - FUERTE COMPRA: {config['min_confidence']['strong_buy']}%")
        print(f"      - COMPRA: {config['min_confidence']['buy']}%")
        print(f"   Cooldown: {config['cooldown_hours']} horas")
        print(f"   Sonido: {'✅ Activado' if config['sound_enabled'] else '❌ Desactivado'}")
        print(f"   Solo horario de mercado: {'✅ Sí' if config['market_hours_only'] else '❌ No'}")
        print()
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    elif command == 'test':
        # Enviar notificación de prueba
        print(f"{Fore.CYAN}📬 Enviando notificación de prueba...{Style.RESET_ALL}")
        success = send_test_notification()
        
        if success:
            print(f"{Fore.GREEN}✅ Notificación enviada correctamente{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 Revisa el Notification Center de macOS{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.RED}❌ Error enviando notificación{Style.RESET_ALL}\n")
    
    elif command == 'config':
        # Mostrar configuración completa
        config = load_config()
        print(f"\n{Fore.CYAN}⚙️  CONFIGURACIÓN COMPLETA{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        print(json.dumps(config, indent=2))
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📝 Edita: config/alert_config.json{Style.RESET_ALL}\n")
    
    elif command == 'report':
        # Mostrar reporte de performance
        from alerts.tracker import calculate_performance_metrics, load_tracker_data, get_pending_alerts
        
        print(f"\n{Fore.CYAN}📊 REPORTE DE PERFORMANCE DE ALERTAS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        try:
            metrics = calculate_performance_metrics()
            
            if 'error' in metrics:
                print(f"{Fore.YELLOW}⚠️  {metrics['error']}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}💡 Las alertas se registrarán automáticamente cuando el daemon esté activo{Style.RESET_ALL}\n")
                return
            
            # Resumen general
            print(f"{Fore.YELLOW}📈 RESUMEN GENERAL{Style.RESET_ALL}")
            print(f"   Total alertas: {metrics['total_alerts']}")
            print(f"   Pendientes de evaluación: {metrics['pending_evaluation']}")
            
            # Performance 7 días
            perf_7d = metrics['performance_7d']
            if perf_7d['evaluated'] > 0:
                print(f"\n{Fore.YELLOW}📅 PERFORMANCE 7 DÍAS{Style.RESET_ALL}")
                print(f"   Evaluadas: {perf_7d['evaluated']}")
                print(f"   Wins: {perf_7d['wins']} | Losses: {perf_7d['losses']}")
                
                # Color para win rate
                wr_color = Fore.GREEN if perf_7d['win_rate'] >= 50 else Fore.RED
                print(f"   Win Rate: {wr_color}{perf_7d['win_rate']}%{Style.RESET_ALL}")
                
                # Color para avg return
                ar_color = Fore.GREEN if perf_7d['avg_return'] > 0 else Fore.RED
                print(f"   Avg Return: {ar_color}{perf_7d['avg_return']:+.2f}%{Style.RESET_ALL}")
                
                if perf_7d['avg_win'] > 0:
                    print(f"   Avg Win: {Fore.GREEN}{perf_7d['avg_win']:+.2f}%{Style.RESET_ALL}")
                if perf_7d['avg_loss'] < 0:
                    print(f"   Avg Loss: {Fore.RED}{perf_7d['avg_loss']:+.2f}%{Style.RESET_ALL}")
                
                if perf_7d['best_trade']:
                    print(f"   Mejor: {perf_7d['best_trade']['ticker']} ({Fore.GREEN}{perf_7d['best_trade']['return']:+.2f}%{Style.RESET_ALL})")
                if perf_7d['worst_trade']:
                    print(f"   Peor: {perf_7d['worst_trade']['ticker']} ({Fore.RED}{perf_7d['worst_trade']['return']:+.2f}%{Style.RESET_ALL})")
            
            # Performance 30 días
            perf_30d = metrics['performance_30d']
            if perf_30d['evaluated'] > 0:
                print(f"\n{Fore.YELLOW}📅 PERFORMANCE 30 DÍAS{Style.RESET_ALL}")
                print(f"   Evaluadas: {perf_30d['evaluated']}")
                print(f"   Wins: {perf_30d['wins']} | Losses: {perf_30d['losses']}")
                
                wr_color = Fore.GREEN if perf_30d['win_rate'] >= 50 else Fore.RED
                print(f"   Win Rate: {wr_color}{perf_30d['win_rate']}%{Style.RESET_ALL}")
                
                ar_color = Fore.GREEN if perf_30d['avg_return'] > 0 else Fore.RED
                print(f"   Avg Return: {ar_color}{perf_30d['avg_return']:+.2f}%{Style.RESET_ALL}")
                
                if perf_30d['best_trade']:
                    print(f"   Mejor: {perf_30d['best_trade']['ticker']} ({Fore.GREEN}{perf_30d['best_trade']['return']:+.2f}%{Style.RESET_ALL})")
                if perf_30d['worst_trade']:
                    print(f"   Peor: {perf_30d['worst_trade']['ticker']} ({Fore.RED}{perf_30d['worst_trade']['return']:+.2f}%{Style.RESET_ALL})")
            
            # Por veredicto
            if metrics['by_verdict']:
                print(f"\n{Fore.YELLOW}📋 POR VEREDICTO (7d){Style.RESET_ALL}")
                for verdict, data in metrics['by_verdict'].items():
                    wr_color = Fore.GREEN if data['win_rate'] >= 50 else Fore.RED
                    print(f"   {verdict}: {data['count']} alertas | Win Rate: {wr_color}{data['win_rate']}%{Style.RESET_ALL}")
            
            # Por ticker (top 5)
            if metrics['by_ticker']:
                print(f"\n{Fore.YELLOW}📈 TOP TICKERS (7d){Style.RESET_ALL}")
                sorted_tickers = sorted(metrics['by_ticker'].items(), key=lambda x: x[1]['avg_return'], reverse=True)
                for ticker, data in sorted_tickers[:5]:
                    ar_color = Fore.GREEN if data['avg_return'] > 0 else Fore.RED
                    wr_color = Fore.GREEN if data['win_rate'] >= 50 else Fore.RED
                    print(f"   {ticker}: {ar_color}{data['avg_return']:+.2f}%{Style.RESET_ALL} | WR: {wr_color}{data['win_rate']}%{Style.RESET_ALL} ({data['count']} alertas)")
            
            # Por confianza
            if any(v['count'] > 0 for v in metrics['by_confidence'].values()):
                print(f"\n{Fore.YELLOW}🎯 POR NIVEL DE CONFIANZA (7d){Style.RESET_ALL}")
                for bucket, data in metrics['by_confidence'].items():
                    if data['count'] > 0:
                        wr_color = Fore.GREEN if data['win_rate'] >= 50 else Fore.RED
                        print(f"   {bucket}: {data['count']} alertas | Win Rate: {wr_color}{data['win_rate']}%{Style.RESET_ALL}")
            
            # Alertas pendientes
            pending = get_pending_alerts()
            if pending:
                print(f"\n{Fore.YELLOW}⏳ ALERTAS PENDIENTES{Style.RESET_ALL}")
                print(f"   {len(pending)} alertas esperando evaluación completa")
                print(f"{Fore.CYAN}   💡 Usa 'python main.py --alerts update' para actualizar{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📝 Archivo: data/alerts_performance.json{Style.RESET_ALL}\n")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}\n")
    
    elif command == 'update':
        # Actualizar performance de alertas pendientes
        from alerts.tracker import update_alert_performance, get_pending_alerts
        
        print(f"\n{Fore.CYAN}🔄 ACTUALIZANDO PERFORMANCE DE ALERTAS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        pending_before = len(get_pending_alerts())
        
        if pending_before == 0:
            print(f"{Fore.YELLOW}⚠️  No hay alertas pendientes de actualización{Style.RESET_ALL}\n")
            return
        
        print(f"{Fore.YELLOW}Alertas pendientes: {pending_before}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Descargando datos de precios...{Style.RESET_ALL}\n")
        
        try:
            updated = update_alert_performance()
            
            pending_after = len(get_pending_alerts())
            completed = pending_before - pending_after
            
            print(f"{Fore.GREEN}✅ Actualización completada{Style.RESET_ALL}")
            print(f"   Alertas actualizadas: {updated}")
            print(f"   Completadas: {completed}")
            print(f"   Pendientes restantes: {pending_after}")
            
            if completed > 0:
                print(f"\n{Fore.CYAN}💡 Usa 'python main.py --alerts report' para ver el reporte actualizado{Style.RESET_ALL}\n")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}\n")

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
  python main.py AAPL -st                Análisis Táctico (Horizonte: 3-6 meses) + ADX/Trend Gate
  python main.py VOO --etf               Análisis de ETF (80% técnico, 20% macro)
  python main.py QQQ --etf -st           Análisis de ETF en corto plazo
  python main.py -s                      Escanear Top 25 (Largo Plazo)
  python main.py -s -st                  Escanear con enfoque táctico (Corto Plazo)

💼 PORTAFOLIO:
  python main.py -p                      Ver estado de tu portafolio
  python main.py -rm                     Verificar Stop Loss y Take Profit
  python main.py -a AAPL                 Agregar AAPL al precio de mercado
  python main.py -a AAPL 150.50          Agregar AAPL a $150.50 personalizado
  python main.py -aa AAPL                Analizar y agregar con RM automático
  python main.py -aa AAPL -st            Agregar con RM para corto plazo
  python main.py -r AAPL                 Eliminar última entrada de AAPL
  python main.py -ra AAPL                Eliminar todas las entradas de AAPL
  python main.py -ra                     Vaciar portafolio (con confirmación)

📈 BACKTESTING:
  python main.py -b NVDA                 Simular estrategia en período reciente
  python main.py -b NVDA 2024-01-01 2024-12-31     Backtest período custom

🤖 ANÁLISIS CON IA:
  python main.py --ai AAPL               Análisis profundo generativo (Requiere GEMINI_API_KEY)

👀 WATCHLIST:
  python main.py -w AAPL                 Agregar acción a watchlist
  python main.py -uw AAPL                Eliminar de watchlist
  python main.py -ws                     Analizar watchlist
  python main.py -ws -st                 Escanear watchlist (Corto Plazo)

🔔 ALERTAS (Sistema Automático):
  python main.py --alerts start          Iniciar monitoreo automático de watchlist
  python main.py --alerts stop           Detener sistema de alertas
  python main.py --alerts status         Ver estado y estadísticas
  python main.py --alerts test           Enviar notificación de prueba
  python main.py --alerts config         Ver configuración completa
  python main.py --alerts report         Ver reporte de performance de alertas
  python main.py --alerts update         Actualizar performance de alertas pendientes
  python main.py --alerts start --dry-run  Modo prueba (sin notificaciones)
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
    parser.add_argument('-s', '--scan', action='store_true', 
                        help='Escanear Top 25 del mercado')
    parser.add_argument('-st', '--short-term', action='store_true',
                        help='Modo corto plazo (3-6 meses). Combina con cualquier comando')
    parser.add_argument('--etf', action='store_true',
                        help='Modo ETF (prioriza análisis técnico, skip fundamentales complejos)')
    
    # Watchlist
    parser.add_argument('-w', '--watch', type=str, metavar='TICKER',
                        help='Agregar ticker a watchlist')
    parser.add_argument('-uw', '--unwatch', type=str, metavar='TICKER',
                        help='Quitar ticker de watchlist')
    parser.add_argument('-ws', '--watchlist', action='store_true',
                        help='Escanear mi watchlist')
    
    # Gestión de Portafolio
    parser.add_argument('-a', '--add', type=str, nargs='+', metavar='TICKER [PRICE]',
                        help='Agregar al portafolio (ej. -a AAPL o -a AAPL 150.50)')
    parser.add_argument('-aa', '--add-auto', type=str, metavar='TICKER',
                        help='Analizar y agregar con RM automático')
    parser.add_argument('-p', '--portfolio', action='store_true',
                        help='Analizar mi portafolio')
    parser.add_argument('-r', '--remove', type=str, metavar='TICKER',
                        help='Quitar última entrada de ticker')
    parser.add_argument('-ra', '--remove-all', type=str, nargs='?', const='ALL', metavar='TICKER',
                        help='Quitar todas las entradas (sin TICKER = vaciar todo)')
    parser.add_argument('-rm', '--check-rm', action='store_true',
                        help='Verificar Stop Loss y Take Profit')
    
    # Otras opciones
    parser.add_argument('-b', '--backtest', type=str, nargs='+', metavar='TICKER [START] [END]',
                        help='Backtesting (ej. -b NVDA 2025-01-01 2025-12-21)')
    parser.add_argument('--html', action='store_true',
                        help='Generar reporte HTML en ./reports/')
    parser.add_argument('--ai', type=str, metavar='TICKER',
                        help='Análisis con IA (requiere GEMINI_API_KEY)')
    
    # Sistema de Alertas
    parser.add_argument('--alerts', type=str, choices=['start', 'stop', 'status', 'test', 'config', 'report', 'update'],
                        help='Control del sistema de alertas')
    parser.add_argument('--dry-run', action='store_true',
                        help='Modo dry-run (para testing de alertas)')
    
    args = parser.parse_args()
    
    # Procesar comando de alertas PRIMERO (antes de otros comandos)
    if args.alerts:
        handle_alerts_command(args.alerts, args.dry_run)
        return
    
    # Procesar comandos
    if args.add:
        ticker = args.add[0]
        price = args.add[1] if len(args.add) > 1 else None
        msg = portfolio_manager.add_stock(ticker, price)
        print(f"\n{Fore.GREEN}{msg}{Style.RESET_ALL}\n")
    
    elif args.add_auto:
        # Phase 4C: Auto-add with RM from analysis
        ticker = args.add_auto.upper()
        print(f"\n{Fore.CYAN}Analizando {ticker} para agregar con RM automático...{Style.RESET_ALL}\n")
        
        try:
            agent = FinancialAgent(ticker, is_short_term=args.short_term)
            results = agent.run_analysis()
            
            # Extract RM metrics
            current_price = results['current_price']
            rm = results.get('risk_management', {})
            
            if not rm:
                print(f"{Fore.YELLOW}⚠️  No se pudieron calcular métricas de RM para {ticker}{Style.RESET_ALL}")
                print(f"Agregando sin RM...")
                msg = portfolio_manager.add_stock(ticker, current_price)
                print(f"\n{Fore.GREEN}{msg}{Style.RESET_ALL}\n")
            else:
                stop_loss = rm.get('stop_loss_price')
                take_profit = rm.get('take_profit_price')
                position_size = rm.get('position_size_shares')
                
                # Show RM metrics
                print(f"{Fore.CYAN}📊 Métricas de Risk Management:{Style.RESET_ALL}")
                print(f"  Precio Actual: ${current_price:.2f}")
                print(f"  Stop Loss: ${stop_loss:.2f} ({((stop_loss/current_price - 1)*100):.2f}%)")
                print(f"  Take Profit: ${take_profit:.2f} (+{((take_profit/current_price - 1)*100):.2f}%)")
                print(f"  Posición Sugerida: {position_size} acciones (${position_size * current_price:,.2f})")
                print(f"  ATR: ${rm.get('atr', 0):.2f}")
                print(f"  Risk/Reward: {rm.get('risk_reward_ratio', 0):.2f}:1\n")
                
                # Add to portfolio with RM
                msg = portfolio_manager.add_stock(
                    ticker=ticker,
                    price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=position_size
                )
                print(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}\n")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error al analizar {ticker}: {str(e)}{Style.RESET_ALL}\n")
            import traceback
            traceback.print_exc()
        
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
    
    elif args.check_rm:
        # Phase 4B: Verificar Stop Loss y Take Profit
        print(f"\n{Fore.CYAN}Verificando Risk Management del Portafolio...{Style.RESET_ALL}\n")
        alerts = portfolio_manager.check_stop_loss_take_profit()
        formatted = portfolio_manager.format_rm_alerts(alerts)
        print(formatted)
        
        # Resumen
        total_sl = len(alerts["stop_loss_hit"])
        total_tp = len(alerts["take_profit_hit"])
        total_no_rm = len(alerts["no_rm"])
        total_active = len(alerts["active"])
        
        print(f"\n{Fore.CYAN}RESUMEN:{Style.RESET_ALL}")
        print(f"  Stop Loss alcanzados: {total_sl}")
        print(f"  Take Profit alcanzados: {total_tp}")
        print(f"  Sin Risk Management: {total_no_rm}")
        print(f"  Posiciones activas: {total_active}")
        print()
            
    elif args.portfolio:
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
            
            agent = FinancialAgent(args.ticker, is_short_term=args.short_term, is_etf=args.etf)
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
                
                # Phase 4C: Show RM metrics and offer to add to portfolio
                rm = results.get('risk_management', {})
                if rm:
                    current_price = results.get('current_price')
                    stop_loss = rm.get('stop_loss_price')
                    take_profit = rm.get('take_profit_price')
                    position_size = rm.get('position_size_shares')
                    atr = rm.get('atr')
                    rr_ratio = rm.get('risk_reward_ratio')
                    
                    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}📊 MÉTRICAS DE RISK MANAGEMENT{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
                    print(f"  Precio Actual: {Fore.WHITE}${current_price:.2f}{Style.RESET_ALL}")
                    print(f"  Stop Loss: {Fore.RED}${stop_loss:.2f}{Style.RESET_ALL} ({Fore.RED}{((stop_loss/current_price - 1)*100):.2f}%{Style.RESET_ALL})")
                    print(f"  Take Profit: {Fore.GREEN}${take_profit:.2f}{Style.RESET_ALL} ({Fore.GREEN}+{((take_profit/current_price - 1)*100):.2f}%{Style.RESET_ALL})")
                    print(f"  Posición Sugerida: {Fore.WHITE}{position_size} acciones{Style.RESET_ALL} (${Fore.WHITE}{position_size * current_price:,.2f}{Style.RESET_ALL})")
                    print(f"  ATR: {Fore.WHITE}${atr:.2f}{Style.RESET_ALL}")
                    print(f"  Risk/Reward: {Fore.WHITE}{rr_ratio:.2f}:1{Style.RESET_ALL}")
                    
                    strategy = "Corto Plazo (3-6 meses)" if args.short_term else "Largo Plazo (3-5 años)"
                    print(f"  Estrategia: {Fore.CYAN}{strategy}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
                    
                    # Ask if user wants to add to portfolio
                    try:
                        response = input(f"{Fore.YELLOW}¿Agregar {args.ticker} al portafolio con estos parámetros de RM? (s/n): {Style.RESET_ALL}").strip().lower()
                        if response in ['s', 'si', 'sí', 'y', 'yes']:
                            msg = portfolio_manager.add_stock(
                                ticker=args.ticker,
                                price=current_price,
                                stop_loss=stop_loss,
                                take_profit=take_profit,
                                position_size=position_size
                            )
                            print(f"\n{Fore.GREEN}✅ {msg}{Style.RESET_ALL}\n")
                        else:
                            print(f"\n{Fore.CYAN}No se agregó al portafolio.{Style.RESET_ALL}\n")
                    except (EOFError, KeyboardInterrupt):
                        print(f"\n{Fore.CYAN}No se agregó al portafolio.{Style.RESET_ALL}\n")
                
                print(f"{Fore.GREEN}Análisis Completado.{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}Error inesperado: {str(e)}{Style.RESET_ALL}\n")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
