"""
macOS Notification Manager

Envía notificaciones al Notification Center de macOS usando pync.
"""

import pync
import os
from typing import Optional, Dict, Any
from datetime import datetime

# Ruta al ícono personalizado
ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon_notification.png")


def send_notification(
    title: str,
    message: str,
    subtitle: Optional[str] = None,
    sound: bool = False,
    group: str = "spectral-galileo"
) -> bool:
    """
    Envía una notificación al Notification Center de macOS.
    
    Args:
        title: Título de la notificación
        message: Mensaje principal
        subtitle: Subtítulo opcional
        sound: Si True, reproduce sonido
        group: ID de grupo para agrupar notificaciones
        
    Returns:
        True si se envió correctamente
    """
    try:
        # Construir la notificación
        kwargs = {
            "title": title,
            "message": message,
            "group": group
        }
        
        if subtitle:
            kwargs["subtitle"] = subtitle
        
        if sound:
            kwargs["sound"] = "default"
        
        # Agregar ícono personalizado si existe
        if os.path.exists(ICON_PATH):
            kwargs["appIcon"] = ICON_PATH
        
        # Enviar notificación
        pync.notify(**kwargs)
        return True
    
    except Exception as e:
        print(f"❌ Error enviando notificación: {e}")
        return False


def send_alert(
    ticker: str,
    verdict: str,
    confidence: int,
    price: float,
    details: Dict[str, Any],
    sound: bool = False
) -> bool:
    """
    Envía una alerta de trading formateada.
    
    Args:
        ticker: Símbolo del ticker (e.g., "NVDA")
        verdict: Veredicto (e.g., "FUERTE COMPRA")
        confidence: Porcentaje de confianza (0-100)
        price: Precio actual
        details: Dict con detalles adicionales (RSI, MACD, etc)
        sound: Si True, reproduce sonido
        
    Returns:
        True si se envió correctamente
    """
    # Determinar emoji según veredicto
    emoji_map = {
        "FUERTE COMPRA": "🚀",
        "COMPRA": "🟢",
        "NEUTRAL": "⚪",
        "VENTA": "🟡",
        "FUERTE VENTA": "🔴"
    }
    emoji = emoji_map.get(verdict, "📊")
    
    # Título
    title = f"{emoji} {verdict} Detectada!"
    
    # Mensaje principal
    message_lines = [
        f"{ticker} @ ${price:.2f}",
        f"Confianza: {confidence}%"
    ]
    
    # Agregar detalles relevantes
    if "rsi" in details:
        message_lines.append(f"RSI: {details['rsi']:.1f}")
    
    if "macd_status" in details:
        message_lines.append(f"MACD: {details['macd_status']}")
    
    message = "\n".join(message_lines)
    
    # Subtítulo con timestamp
    subtitle = datetime.now().strftime("%H:%M:%S")
    
    return send_notification(
        title=title,
        message=message,
        subtitle=subtitle,
        sound=sound
    )


def send_rm_alert(
    ticker: str,
    rm_type: str,
    price: float,
    target_price: float,
    pnl_pct: float,
    sound: bool = False
) -> bool:
    """
    Envía una alerta de Risk Management (TP/SL alcanzado).
    
    Args:
        ticker: Símbolo del ticker
        rm_type: "STOP_LOSS" o "TAKE_PROFIT"
        price: Precio actual
        target_price: Precio objetivo (SL o TP)
        pnl_pct: Porcentaje de P&L
        sound: Si True, reproduce sonido
        
    Returns:
        True si se envió correctamente
    """
    if rm_type == "STOP_LOSS":
        emoji = "🛑"
        title = f"{emoji} Stop Loss Alcanzado"
        color_code = "🔴"
    else:  # TAKE_PROFIT
        emoji = "🎯"
        title = f"{emoji} Take Profit Alcanzado"
        color_code = "🟢"
    
    message = (
        f"{ticker} @ ${price:.2f}\n"
        f"Objetivo: ${target_price:.2f}\n"
        f"{color_code} P&L: {pnl_pct:+.2f}%"
    )
    
    subtitle = datetime.now().strftime("%H:%M:%S")
    
    return send_notification(
        title=title,
        message=message,
        subtitle=subtitle,
        sound=sound
    )


def send_status_notification(message: str, sound: bool = False) -> bool:
    """
    Envía una notificación de estado del sistema.
    
    Args:
        message: Mensaje a mostrar
        sound: Si True, reproduce sonido
        
    Returns:
        True si se envió correctamente
    """
    return send_notification(
        title="📡 Alert System",
        message=message,
        sound=sound
    )


def send_test_notification() -> bool:
    """
    Envía una notificación de prueba.
    
    Returns:
        True si se envió correctamente
    """
    return send_notification(
        title="✅ Test Notification",
        message="El sistema de alertas está funcionando correctamente.\n\n"
                "Recibirás notificaciones cuando se detecten oportunidades de trading.",
        subtitle=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        sound=False
    )
