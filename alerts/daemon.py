"""
Alert Daemon - Main Loop

Daemon principal que escanea watchlist y portafolio en segundo plano.
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime
from typing import List, Dict, Any

# Agregar directorio raíz al path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from src.spectral_galileo.core.agent import FinancialAgent
from src.spectral_galileo.core.watchlist_manager import get_watchlist_tickers
from src.spectral_galileo.core.portfolio_manager import load_portfolio
from alerts.config import (
    load_config, get_interval_minutes, get_min_confidence,
    is_sound_enabled, get_cooldown_hours, get_max_alerts_per_hour
)
from alerts.market_hours import is_market_open, get_market_status, should_run_scan
from alerts.notifier import send_alert, send_rm_alert, send_status_notification
from alerts.state import (
    should_send_alert, record_alert, can_send_more_alerts,
    increment_alert_count, update_scan_stats, save_daemon_pid,
    remove_daemon_pid, set_daemon_running, get_daemon_pid, is_daemon_running
)
from alerts.tracker import record_alert_for_tracking


# Configurar logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_DIR}/alerts.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AlertDaemon:
    """Daemon principal del sistema de alertas."""
    
    def __init__(self, dry_run: bool = False):
        """
        Inicializa el daemon.
        
        Args:
            dry_run: Si True, no envía notificaciones reales
        """
        self.dry_run = dry_run
        self.running = False
        self.config = load_config()
        
        # Registrar handlers de señales
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Maneja señales de terminación."""
        logger.info(f"📡 Señal {signum} recibida. Deteniendo daemon...")
        self.stop()
    
    def start(self):
        """Inicia el daemon en segundo plano."""
        if is_daemon_running():
            logger.warning("⚠️  Daemon ya está corriendo!")
            return False
        
        logger.info("🚀 Iniciando Alert Daemon...")
        
        # Guardar PID
        save_daemon_pid(os.getpid())
        set_daemon_running(True)
        self.running = True
        
        # Enviar notificación de inicio
        if not self.dry_run:
            send_status_notification("✅ Sistema de alertas iniciado\n"
                                    f"Intervalo: {get_interval_minutes()} minutos")
        
        logger.info(f"✅ Daemon iniciado (PID: {os.getpid()})")
        logger.info(f"📊 Configuración:")
        logger.info(f"   - Intervalo: {get_interval_minutes()} minutos")
        logger.info(f"   - Modo: {self.config['analysis_mode']}")
        logger.info(f"   - Confianza mínima: FUERTE COMPRA {get_min_confidence('strong_buy')}%, "
                   f"COMPRA {get_min_confidence('buy')}%")
        logger.info(f"   - Cooldown: {get_cooldown_hours()} horas")
        logger.info(f"   - Dry run: {self.dry_run}")
        
        # Loop principal
        self._run_loop()
        
        return True
    
    def stop(self):
        """Detiene el daemon."""
        logger.info("🛑 Deteniendo daemon...")
        self.running = False
        set_daemon_running(False)
        remove_daemon_pid()
        
        if not self.dry_run:
            send_status_notification("🛑 Sistema de alertas detenido")
        
        logger.info("✅ Daemon detenido correctamente")
    
    def _run_loop(self):
        """Loop principal del daemon."""
        interval_seconds = get_interval_minutes() * 60
        
        while self.running:
            try:
                # Verificar si debemos escanear
                if should_run_scan():
                    logger.info(f"📡 {get_market_status()} - Iniciando escaneo...")
                    self._scan_and_alert()
                else:
                    logger.info(f"⏸️  {get_market_status()} - Esperando...")
                
                # Esperar hasta próximo escaneo
                logger.info(f"⏰ Próximo escaneo en {get_interval_minutes()} minutos")
                time.sleep(interval_seconds)
            
            except Exception as e:
                logger.error(f"❌ Error en loop principal: {e}", exc_info=True)
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def _scan_and_alert(self):
        """Escanea watchlist y portafolio, envía alertas si es necesario."""
        alerts_sent = 0
        tickers_scanned = []
        
        # 1. Escanear Watchlist
        if self.config['sources']['watchlist']:
            watchlist = get_watchlist_tickers()
            logger.info(f"📋 Watchlist: {len(watchlist)} tickers")
            
            for ticker in watchlist:
                if not self.running:
                    break
                
                try:
                    alert_sent = self._analyze_and_alert(ticker)
                    if alert_sent:
                        alerts_sent += 1
                    tickers_scanned.append(ticker)
                
                except Exception as e:
                    logger.error(f"❌ Error analizando {ticker}: {e}")
        
        # 2. Escanear Portafolio (para alertas de RM)
        if self.config['sources']['portfolio']:
            portfolio = load_portfolio()
            logger.info(f"💼 Portafolio: {len(portfolio)} posiciones")
            
            for stock in portfolio:
                if not self.running:
                    break
                
                try:
                    rm_alert_sent = self._check_rm_and_alert(stock)
                    if rm_alert_sent:
                        alerts_sent += 1
                
                except Exception as e:
                    logger.error(f"❌ Error verificando RM de {stock['ticker']}: {e}")
        
        # Actualizar estadísticas
        update_scan_stats(
            watchlist_count=len(get_watchlist_tickers()),
            portfolio_count=len(load_portfolio())
        )
        
        logger.info(f"✅ Escaneo completado: {len(tickers_scanned)} tickers, {alerts_sent} alertas enviadas")
    
    def _analyze_and_alert(self, ticker: str) -> bool:
        """
        Analiza un ticker y envía alerta si cumple condiciones.
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            True si se envió una alerta
        """
        # Verificar rate limiting
        if not can_send_more_alerts(get_max_alerts_per_hour()):
            logger.warning(f"⚠️  Límite de alertas alcanzado ({get_max_alerts_per_hour()}/hora)")
            return False
        
        # Verificar cooldown
        if not should_send_alert(ticker, get_cooldown_hours()):
            logger.debug(f"⏸️  {ticker}: En cooldown")
            return False
        
        # Analizar ticker (Production: use all external data sources)
        is_short_term = self.config['analysis_mode'] == 'short_term'
        agent = FinancialAgent(ticker, is_short_term=is_short_term, skip_external_data=False)
        results = agent.analyze()
        
        verdict = results.get('verdict', 'NEUTRAL')
        confidence = int(results.get('confidence', 0))
        price = results.get('price', 0)
        
        logger.info(f"📊 {ticker}: {verdict} (Confianza: {confidence}%)")
        
        # Determinar si se debe alertar
        should_alert = False
        alert_type = None
        
        if verdict == "FUERTE COMPRA":
            min_conf = get_min_confidence('strong_buy')
            if confidence >= min_conf:
                should_alert = True
                alert_type = "STRONG_BUY"
        
        elif verdict == "COMPRA":
            min_conf = get_min_confidence('buy')
            
            # OPCIÓN C: Requerir confirmación multi-timeframe (2/3 timeframes en COMPRA)
            # Acceder a análisis multi-timeframe
            multi_tf = results.get('advanced', {}).get('multi_timeframe', {})
            timeframes = multi_tf.get('timeframes', {})
            
            # Contar cuántos timeframes tienen señal de COMPRA
            buy_timeframes = 0
            for tf_name, tf_data in timeframes.items():
                tf_signal = tf_data.get('signal', '').upper()
                if 'BUY' in tf_signal or 'COMPRA' in tf_signal:
                    buy_timeframes += 1
            
            # Requiere: confianza >= umbral Y al menos 2/3 timeframes en COMPRA
            if confidence >= min_conf and buy_timeframes >= 2:
                should_alert = True
                alert_type = "BUY"
                logger.debug(f"✓ {ticker} COMPRA confirmada: {buy_timeframes}/3 timeframes en BUY")
            else:
                logger.debug(f"✗ {ticker} COMPRA rechazada: conf={confidence}% (min={min_conf}%), "
                           f"timeframes={buy_timeframes}/3 (requiere 2)")

        
        elif verdict in ["VENTA", "FUERTE VENTA"] and self.config['alert_types']['sell']:
            should_alert = True
            alert_type = "SELL"
        
        if should_alert:
            # Extraer detalles técnicos
            details = {
                'rsi': results.get('rsi'),
                'macd_status': results.get('macd_status')
            }
            
            logger.info(f"🚨 ALERTA: {ticker} - {verdict} ({confidence}%)")
            
            if not self.dry_run:
                success = send_alert(
                    ticker=ticker,
                    verdict=verdict,
                    confidence=confidence,
                    price=price,
                    details=details,
                    sound=is_sound_enabled()
                )
                
                if success:
                    record_alert(ticker, alert_type, confidence)
                    increment_alert_count()
                    
                    # 🆕 Registrar en tracker para seguimiento de performance
                    record_alert_for_tracking(
                        ticker=ticker,
                        verdict=verdict,
                        confidence=confidence,
                        price=price,
                        details=details
                    )
                    
                    return True
            else:
                logger.info(f"   [DRY RUN] No se envió notificación")
                return True
        
        return False
    
    def _check_rm_and_alert(self, stock: Dict[str, Any]) -> bool:
        """
        Verifica Stop Loss y Take Profit, envía alerta si se alcanzó.
        
        Args:
            stock: Dict con datos de la posición
            
        Returns:
            True si se envió una alerta
        """
        if not self.config['alert_types']['rm_triggered']:
            return False
        
        ticker = stock['symbol']
        entry_price = stock.get('price', 0)
        stop_loss = stock.get('stop_loss')
        take_profit = stock.get('take_profit')
        
        if not entry_price or (not stop_loss and not take_profit):
            return False
        
        # Obtener precio actual (Production: use all external data)
        try:
            agent = FinancialAgent(ticker, is_short_term=True, skip_external_data=False)
            current_price = agent.get_current_price()
        except:
            return False
        
        # Verificar Stop Loss
        if stop_loss and current_price <= stop_loss:
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            logger.warning(f"🛑 STOP LOSS: {ticker} @ ${current_price:.2f} (P&L: {pnl_pct:+.2f}%)")
            
            if not self.dry_run:
                success = send_rm_alert(
                    ticker=ticker,
                    rm_type="STOP_LOSS",
                    price=current_price,
                    target_price=stop_loss,
                    pnl_pct=pnl_pct,
                    sound=is_sound_enabled()
                )
                
                if success:
                    record_alert(ticker, "STOP_LOSS", 100)
                    increment_alert_count()
                    return True
            else:
                logger.info(f"   [DRY RUN] No se envió notificación de SL")
                return True
        
        # Verificar Take Profit
        if take_profit and current_price >= take_profit:
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            logger.info(f"🎯 TAKE PROFIT: {ticker} @ ${current_price:.2f} (P&L: {pnl_pct:+.2f}%)")
            
            if not self.dry_run:
                success = send_rm_alert(
                    ticker=ticker,
                    rm_type="TAKE_PROFIT",
                    price=current_price,
                    target_price=take_profit,
                    pnl_pct=pnl_pct,
                    sound=is_sound_enabled()
                )
                
                if success:
                    record_alert(ticker, "TAKE_PROFIT", 100)
                    increment_alert_count()
                    return True
            else:
                logger.info(f"   [DRY RUN] No se envió notificación de TP")
                return True
        
        return False


def run_daemon(dry_run: bool = False):
    """
    Ejecuta el daemon.
    
    Args:
        dry_run: Si True, modo de prueba sin notificaciones
    """
    daemon = AlertDaemon(dry_run=dry_run)
    daemon.start()


if __name__ == '__main__':
    # Permitir ejecutar directamente
    import argparse
    
    parser = argparse.ArgumentParser(description='Alert System Daemon')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no notifications)')
    
    args = parser.parse_args()
    
    run_daemon(dry_run=args.dry_run)
