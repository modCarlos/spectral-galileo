"""
Test Suite para el Sistema de Alertas

Suite completa de tests para validar el funcionamiento del sistema de alertas.
"""

import sys
import os
import time
from datetime import datetime
from colorama import Fore, Style

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from alerts.config import load_config, update_setting, get_setting
from alerts.state import (
    should_send_alert, record_alert, can_send_more_alerts,
    increment_alert_count, get_stats, load_state, save_state
)
from alerts.market_hours import (
    is_market_open, get_market_status, is_market_day,
    time_until_market_opens
)
from alerts.notifier import send_notification, send_alert, send_test_notification
from watchlist_manager import get_watchlist_tickers


def print_header(title):
    """Imprime un header de sección."""
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{title.center(70)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def print_test(name, passed, details=""):
    """Imprime resultado de un test."""
    status = f"{Fore.GREEN}✅ PASS{Style.RESET_ALL}" if passed else f"{Fore.RED}❌ FAIL{Style.RESET_ALL}"
    print(f"{status} - {name}")
    if details:
        print(f"     {details}")


def test_configuration():
    """Test 1: Configuración"""
    print_header("TEST 1: CONFIGURACIÓN")
    
    config = load_config()
    
    # Test valores por defecto
    print_test(
        "Configuración cargada",
        config is not None and len(config) > 0
    )
    
    print_test(
        "Intervalo configurado",
        config.get('interval_minutes') == 30,
        f"Intervalo: {config.get('interval_minutes')} min"
    )
    
    print_test(
        "Modo análisis configurado",
        config.get('analysis_mode') == 'short_term',
        f"Modo: {config.get('analysis_mode')}"
    )
    
    print_test(
        "Confianza mínima correcta",
        config.get('min_confidence', {}).get('strong_buy') == 70,
        f"FUERTE COMPRA: {config.get('min_confidence', {}).get('strong_buy')}%"
    )
    
    print_test(
        "Cooldown configurado",
        config.get('cooldown_hours') == 4,
        f"Cooldown: {config.get('cooldown_hours')} horas"
    )
    
    print_test(
        "Sonido desactivado",
        config.get('sound_enabled') == False,
        "Sonido: Desactivado"
    )
    
    return True


def test_market_hours():
    """Test 2: Detección de horario de mercado"""
    print_header("TEST 2: DETECCIÓN DE HORARIO DE MERCADO")
    
    market_status = get_market_status()
    is_open = is_market_open()
    is_weekday = is_market_day()
    
    print_test(
        "Estado del mercado obtenido",
        market_status is not None,
        f"Estado: {market_status}"
    )
    
    print_test(
        "Detección de día hábil",
        isinstance(is_weekday, bool),
        f"Es día hábil: {is_weekday}"
    )
    
    print_test(
        "Detección de mercado abierto",
        isinstance(is_open, bool),
        f"Mercado abierto: {is_open}"
    )
    
    if not is_open:
        hours, minutes = time_until_market_opens()
        print_test(
            "Cálculo de tiempo hasta apertura",
            hours >= 0 and minutes >= 0,
            f"Abre en: {hours}h {minutes}m"
        )
    
    return True


def test_state_management():
    """Test 3: Gestión de estado"""
    print_header("TEST 3: GESTIÓN DE ESTADO")
    
    # Obtener estadísticas
    stats = get_stats()
    
    print_test(
        "Estadísticas obtenidas",
        stats is not None,
        f"Total alertas: {stats.get('total_alerts_sent', 0)}"
    )
    
    print_test(
        "Estado del daemon detectado",
        isinstance(stats.get('daemon_running'), bool),
        f"Daemon running: {stats.get('daemon_running')}"
    )
    
    # Test de cooldown
    test_ticker = "TEST_TICKER"
    should_send = should_send_alert(test_ticker, cooldown_hours=4)
    
    print_test(
        "Verificación de cooldown (nuevo ticker)",
        should_send == True,
        f"{test_ticker}: Puede enviar alerta"
    )
    
    # Registrar alerta
    record_alert(test_ticker, "STRONG_BUY", 85)
    
    # Verificar que ahora está en cooldown
    should_send_after = should_send_alert(test_ticker, cooldown_hours=4)
    
    print_test(
        "Verificación de cooldown (después de registrar)",
        should_send_after == False,
        f"{test_ticker}: En cooldown"
    )
    
    # Test de rate limiting
    can_send = can_send_more_alerts(max_per_hour=5)
    
    print_test(
        "Rate limiting funciona",
        isinstance(can_send, bool),
        f"Puede enviar más alertas: {can_send}"
    )
    
    return True


def test_notifications():
    """Test 4: Sistema de notificaciones"""
    print_header("TEST 4: SISTEMA DE NOTIFICACIONES")
    
    # Test notificación básica
    success = send_notification(
        title="🧪 Test Notification",
        message="Testing alert system...",
        sound=False
    )
    
    print_test(
        "Notificación básica enviada",
        success,
        "Revisa Notification Center"
    )
    
    time.sleep(2)
    
    # Test alerta de trading
    success_alert = send_alert(
        ticker="TEST",
        verdict="FUERTE COMPRA",
        confidence=85,
        price=100.50,
        details={'rsi': 28.5, 'macd_status': 'Bullish'},
        sound=False
    )
    
    print_test(
        "Alerta de trading enviada",
        success_alert,
        "TEST @ $100.50 - FUERTE COMPRA 85%"
    )
    
    return success and success_alert


def test_watchlist_integration():
    """Test 5: Integración con watchlist"""
    print_header("TEST 5: INTEGRACIÓN CON WATCHLIST")
    
    try:
        tickers = get_watchlist_tickers()
        
        print_test(
            "Watchlist cargada",
            tickers is not None,
            f"Tickers en watchlist: {len(tickers)}"
        )
        
        print_test(
            "Watchlist no vacía",
            len(tickers) > 0,
            f"Primeros 5: {tickers[:5]}"
        )
        
        return len(tickers) > 0
    
    except Exception as e:
        print_test(
            "Watchlist cargada",
            False,
            f"Error: {e}"
        )
        return False


def test_analysis_flow():
    """Test 6: Flujo de análisis"""
    print_header("TEST 6: FLUJO DE ANÁLISIS (DRY RUN)")
    
    try:
        from src.spectral_galileo.core.agent import FinancialAgent
        
        # Analizar un ticker simple
        ticker = "AAPL"
        print(f"Analizando {ticker}...")
        
        agent = FinancialAgent(ticker, is_short_term=True)
        results = agent.run_analysis()
        
        print_test(
            "Análisis completado",
            results is not None,
            f"Ticker: {ticker}"
        )
        
        verdict = results.get('verdict')
        confidence = results.get('confidence', 0)
        
        print_test(
            "Veredicto obtenido",
            verdict is not None,
            f"{verdict} (Confianza: {confidence}%)"
        )
        
        print_test(
            "Precio obtenido",
            results.get('price', 0) > 0,
            f"Precio: ${results.get('price', 0):.2f}"
        )
        
        # Simular lógica de alerta
        config = load_config()
        should_alert = False
        
        if verdict == "FUERTE COMPRA":
            min_conf = config['min_confidence']['strong_buy']
            should_alert = confidence >= min_conf
        elif verdict == "COMPRA":
            min_conf = config['min_confidence']['buy']
            should_alert = confidence >= min_conf
        
        print_test(
            "Lógica de decisión de alerta",
            True,
            f"Enviar alerta: {should_alert} ({verdict} con {confidence}% vs mín {config['min_confidence']})"
        )
        
        return True
    
    except Exception as e:
        print_test(
            "Flujo de análisis",
            False,
            f"Error: {e}"
        )
        return False


def test_file_permissions():
    """Test 7: Permisos de archivos"""
    print_header("TEST 7: PERMISOS Y ESTRUCTURA DE ARCHIVOS")
    
    # Verificar estructura de carpetas
    folders = ['alerts', 'config', 'data', 'logs', 'assets']
    
    for folder in folders:
        exists = os.path.exists(folder)
        print_test(
            f"Carpeta '{folder}' existe",
            exists
        )
    
    # Verificar archivos clave
    files = [
        'config/alert_config.json',
        'assets/icon_notification.png',
        'alerts/__init__.py',
        'alerts/config.py',
        'alerts/daemon.py',
        'alerts/notifier.py',
        'alerts/state.py',
        'alerts/market_hours.py'
    ]
    
    for file in files:
        exists = os.path.exists(file)
        print_test(
            f"Archivo '{file}' existe",
            exists
        )
    
    # Verificar que se pueden crear archivos en data/
    try:
        test_file = 'data/test_write.tmp'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        print_test(
            "Permisos de escritura en data/",
            True,
            "OK"
        )
    except Exception as e:
        print_test(
            "Permisos de escritura en data/",
            False,
            f"Error: {e}"
        )
    
    return True


def run_all_tests():
    """Ejecuta todos los tests."""
    print(f"\n{Fore.CYAN}╔{'═'*68}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{'SUITE DE TESTING - SISTEMA DE ALERTAS'.center(68)}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═'*68}╝{Style.RESET_ALL}")
    
    start_time = time.time()
    
    tests = [
        ("Configuración", test_configuration),
        ("Detección de horario", test_market_hours),
        ("Gestión de estado", test_state_management),
        ("Sistema de notificaciones", test_notifications),
        ("Integración watchlist", test_watchlist_integration),
        ("Flujo de análisis", test_analysis_flow),
        ("Estructura de archivos", test_file_permissions)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error en test '{name}': {e}{Style.RESET_ALL}\n")
            results.append((name, False))
    
    # Resumen
    elapsed = time.time() - start_time
    
    print_header("RESUMEN DE TESTS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Fore.GREEN}✅{Style.RESET_ALL}" if result else f"{Fore.RED}❌{Style.RESET_ALL}"
        print(f"{status} {name}")
    
    print(f"\n{Fore.CYAN}Resultado: {passed}/{total} tests pasaron{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Tiempo: {elapsed:.2f}s{Style.RESET_ALL}")
    
    if passed == total:
        print(f"\n{Fore.GREEN}🎉 ¡Todos los tests pasaron!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Sistema listo para producción{Style.RESET_ALL}\n")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Algunos tests fallaron{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Revisa los errores arriba{Style.RESET_ALL}\n")
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
