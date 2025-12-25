"""
Market Hours Detection

Detecta si el mercado está abierto basado en horario NYSE (ET timezone).
"""

from datetime import datetime, time
import pytz
from typing import Tuple


def get_eastern_time() -> datetime:
    """
    Obtiene la hora actual en Eastern Time (ET).
    
    Returns:
        datetime en timezone America/New_York
    """
    et_tz = pytz.timezone('America/New_York')
    return datetime.now(et_tz)


def is_market_day() -> bool:
    """
    Verifica si hoy es un día de mercado (Lunes-Viernes).
    
    Returns:
        True si es día hábil
    """
    et_now = get_eastern_time()
    return et_now.strftime('%A') in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']


def is_market_hours() -> bool:
    """
    Verifica si estamos dentro del horario de mercado (9:30 AM - 4:00 PM ET).
    
    Returns:
        True si el mercado está abierto
    """
    if not is_market_day():
        return False
    
    et_now = get_eastern_time()
    current_time = et_now.time()
    
    market_open = time(9, 30)   # 9:30 AM ET
    market_close = time(16, 0)  # 4:00 PM ET
    
    return market_open <= current_time <= market_close


def is_market_open() -> bool:
    """
    Alias de is_market_hours() para mejor legibilidad.
    
    Returns:
        True si el mercado está abierto
    """
    return is_market_hours()


def time_until_market_opens() -> Tuple[int, int]:
    """
    Calcula cuánto tiempo falta para que abra el mercado.
    
    Returns:
        Tupla (horas, minutos) hasta la próxima apertura
    """
    et_now = get_eastern_time()
    
    # Si ya estamos en horario de mercado
    if is_market_open():
        return (0, 0)
    
    # Calcular próxima apertura
    market_open = time(9, 30)
    
    # Si es después de las 4 PM, calcular para mañana
    if et_now.time() > time(16, 0):
        # Avanzar al siguiente día
        next_open = et_now.replace(hour=9, minute=30, second=0, microsecond=0)
        from datetime import timedelta
        next_open += timedelta(days=1)
        
        # Si mañana es fin de semana, avanzar a lunes
        while next_open.strftime('%A') not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            next_open += timedelta(days=1)
    else:
        # Apertura hoy
        next_open = et_now.replace(hour=9, minute=30, second=0, microsecond=0)
    
    delta = next_open - et_now
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    
    return (hours, minutes)


def get_market_status() -> str:
    """
    Retorna el estado actual del mercado como string legible.
    
    Returns:
        String descriptivo del estado del mercado
    """
    if is_market_open():
        return "🟢 Mercado ABIERTO"
    
    if not is_market_day():
        et_now = get_eastern_time()
        return f"🔴 Mercado CERRADO (Fin de semana - {et_now.strftime('%A')})"
    
    hours, minutes = time_until_market_opens()
    return f"🟡 Mercado CERRADO (Abre en {hours}h {minutes}m)"


def should_run_scan(force: bool = False) -> bool:
    """
    Determina si se debe ejecutar un escaneo ahora.
    
    Args:
        force: Si True, ignora el horario de mercado
        
    Returns:
        True si se debe ejecutar el escaneo
    """
    if force:
        return True
    
    # Solo escanear durante horario de mercado
    return is_market_open()
