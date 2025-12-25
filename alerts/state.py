"""
State Management for Alert System

Gestiona el estado persistente del daemon de alertas.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


STATE_FILE = "data/alerts_state.json"
HISTORY_FILE = "data/alerts_history.json"
PID_FILE = "data/alerts.pid"


def load_state() -> Dict[str, Any]:
    """
    Carga el estado actual del daemon.
    
    Returns:
        Dict con estado del sistema
    """
    if not os.path.exists(STATE_FILE):
        return {
            "last_scan": None,
            "total_scans": 0,
            "total_alerts_sent": 0,
            "alerts_this_hour": 0,
            "hour_start": datetime.now().isoformat(),
            "watchlist_count": 0,
            "portfolio_count": 0,
            "running": False
        }
    
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return load_state()  # Retornar estado por defecto


def save_state(state: Dict[str, Any]) -> None:
    """
    Guarda el estado actual del daemon.
    
    Args:
        state: Dict con estado a guardar
    """
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)


def load_history() -> Dict[str, Dict[str, Any]]:
    """
    Carga el historial de alertas (para anti-spam).
    
    Returns:
        Dict con ticker como key y datos de última alerta
    """
    if not os.path.exists(HISTORY_FILE):
        return {}
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_history(history: Dict[str, Dict[str, Any]]) -> None:
    """
    Guarda el historial de alertas.
    
    Args:
        history: Dict con historial de alertas
    """
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)


def should_send_alert(ticker: str, cooldown_hours: int = 4) -> bool:
    """
    Determina si se debe enviar una alerta para un ticker (anti-spam).
    
    Args:
        ticker: Símbolo del ticker
        cooldown_hours: Horas de cooldown entre alertas
        
    Returns:
        True si se debe enviar la alerta
    """
    history = load_history()
    
    if ticker not in history:
        return True
    
    last_alert = history[ticker]
    last_timestamp = datetime.fromisoformat(last_alert["timestamp"])
    cooldown_delta = timedelta(hours=cooldown_hours)
    
    return datetime.now() - last_timestamp >= cooldown_delta


def record_alert(ticker: str, alert_type: str, confidence: int) -> None:
    """
    Registra una alerta enviada en el historial.
    
    Args:
        ticker: Símbolo del ticker
        alert_type: Tipo de alerta (e.g., "STRONG_BUY")
        confidence: Confianza de la alerta
    """
    history = load_history()
    
    history[ticker] = {
        "timestamp": datetime.now().isoformat(),
        "type": alert_type,
        "confidence": confidence
    }
    
    save_history(history)


def can_send_more_alerts(max_per_hour: int = 5) -> bool:
    """
    Verifica si se pueden enviar más alertas esta hora (rate limiting).
    
    Args:
        max_per_hour: Máximo de alertas por hora
        
    Returns:
        True si se pueden enviar más alertas
    """
    state = load_state()
    
    # Verificar si cambió la hora
    hour_start = datetime.fromisoformat(state.get("hour_start", datetime.now().isoformat()))
    if datetime.now() - hour_start >= timedelta(hours=1):
        # Nueva hora, resetear contador
        state["alerts_this_hour"] = 0
        state["hour_start"] = datetime.now().isoformat()
        save_state(state)
        return True
    
    return state.get("alerts_this_hour", 0) < max_per_hour


def increment_alert_count() -> None:
    """Incrementa el contador de alertas enviadas."""
    state = load_state()
    state["total_alerts_sent"] = state.get("total_alerts_sent", 0) + 1
    state["alerts_this_hour"] = state.get("alerts_this_hour", 0) + 1
    save_state(state)


def update_scan_stats(watchlist_count: int, portfolio_count: int) -> None:
    """
    Actualiza estadísticas del último escaneo.
    
    Args:
        watchlist_count: Número de tickers en watchlist
        portfolio_count: Número de posiciones en portafolio
    """
    state = load_state()
    state["last_scan"] = datetime.now().isoformat()
    state["total_scans"] = state.get("total_scans", 0) + 1
    state["watchlist_count"] = watchlist_count
    state["portfolio_count"] = portfolio_count
    save_state(state)


def get_daemon_pid() -> Optional[int]:
    """
    Obtiene el PID del daemon si está corriendo.
    
    Returns:
        PID del proceso o None
    """
    if not os.path.exists(PID_FILE):
        return None
    
    try:
        with open(PID_FILE, 'r') as f:
            return int(f.read().strip())
    except (ValueError, IOError):
        return None


def save_daemon_pid(pid: int) -> None:
    """
    Guarda el PID del daemon.
    
    Args:
        pid: Process ID
    """
    os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
    
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))


def remove_daemon_pid() -> None:
    """Elimina el archivo PID."""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def is_daemon_running() -> bool:
    """
    Verifica si el daemon está corriendo.
    
    Returns:
        True si el daemon está activo
    """
    pid = get_daemon_pid()
    if not pid:
        return False
    
    # Verificar si el proceso existe
    try:
        os.kill(pid, 0)  # Signal 0 solo verifica existencia
        return True
    except OSError:
        # Proceso no existe, limpiar PID file
        remove_daemon_pid()
        return False


def set_daemon_running(running: bool) -> None:
    """
    Actualiza el estado de ejecución del daemon.
    
    Args:
        running: True si está corriendo
    """
    state = load_state()
    state["running"] = running
    save_state(state)


def get_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas del sistema de alertas.
    
    Returns:
        Dict con estadísticas
    """
    state = load_state()
    history = load_history()
    
    return {
        "daemon_running": is_daemon_running(),
        "last_scan": state.get("last_scan"),
        "total_scans": state.get("total_scans", 0),
        "total_alerts_sent": state.get("total_alerts_sent", 0),
        "alerts_this_hour": state.get("alerts_this_hour", 0),
        "watchlist_count": state.get("watchlist_count", 0),
        "portfolio_count": state.get("portfolio_count", 0),
        "tickers_in_history": len(history)
    }
