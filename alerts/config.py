"""
Configuration Manager for Alert System

Gestiona la configuración de alertas desde alert_config.json
"""

import json
import os
from typing import Dict, Any

CONFIG_FILE = "config/alert_config.json"
DEFAULT_CONFIG = {
    "enabled": True,
    "interval_minutes": 30,
    "market_hours_only": True,
    "analysis_mode": "short_term",  # short_term o long_term
    
    "alert_types": {
        "strong_buy": True,
        "buy": True,
        "sell": True,
        "rm_triggered": True
    },
    
    "min_confidence": {
        "strong_buy": 70,  # Permisivo al inicio para testing
        "buy": 60
    },
    
    "cooldown_hours": 4,
    "max_alerts_per_hour": 5,
    "sound_enabled": False,  # Sin sonido por defecto
    
    "market_hours": {
        "timezone": "America/New_York",
        "open": "09:30",
        "close": "16:00",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    },
    
    "sources": {
        "watchlist": True,
        "portfolio": True
    }
}


def load_config() -> Dict[str, Any]:
    """
    Carga configuración desde archivo o crea una por defecto.
    
    Returns:
        Dict con configuración de alertas
    """
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # Merge con defaults para agregar nuevas keys
        merged = DEFAULT_CONFIG.copy()
        merged.update(config)
        return merged
    
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️  Error leyendo config: {e}. Usando defaults.")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """
    Guarda configuración en archivo JSON.
    
    Args:
        config: Dict con configuración a guardar
    """
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


def get_setting(key: str, default: Any = None) -> Any:
    """
    Obtiene un valor específico de la configuración.
    
    Args:
        key: Clave de configuración (soporta dot notation: "market_hours.open")
        default: Valor por defecto si no existe
        
    Returns:
        Valor de la configuración
    """
    config = load_config()
    
    # Soportar dot notation (e.g., "market_hours.open")
    keys = key.split('.')
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


def update_setting(key: str, value: Any) -> None:
    """
    Actualiza un valor específico de la configuración.
    
    Args:
        key: Clave de configuración (soporta dot notation)
        value: Nuevo valor
    """
    config = load_config()
    
    # Soportar dot notation
    keys = key.split('.')
    target = config
    
    for k in keys[:-1]:
        if k not in target:
            target[k] = {}
        target = target[k]
    
    target[keys[-1]] = value
    save_config(config)


def is_enabled() -> bool:
    """Verifica si el sistema de alertas está habilitado."""
    return get_setting('enabled', True)


def get_interval_minutes() -> int:
    """Retorna el intervalo de escaneo en minutos."""
    return get_setting('interval_minutes', 30)


def get_min_confidence(alert_type: str) -> int:
    """
    Retorna la confianza mínima requerida para un tipo de alerta.
    
    Args:
        alert_type: 'strong_buy' o 'buy'
        
    Returns:
        Confianza mínima (0-100)
    """
    return get_setting(f'min_confidence.{alert_type}', 70)


def is_sound_enabled() -> bool:
    """Verifica si el sonido está habilitado."""
    return get_setting('sound_enabled', False)


def get_cooldown_hours() -> int:
    """Retorna las horas de cooldown entre alertas del mismo ticker."""
    return get_setting('cooldown_hours', 4)


def get_max_alerts_per_hour() -> int:
    """Retorna el máximo de alertas permitidas por hora."""
    return get_setting('max_alerts_per_hour', 5)
