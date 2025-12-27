#!/usr/bin/env python3
"""
Auto-updater para alert tracker

Script que actualiza automáticamente el performance de alertas pendientes.
Debe ejecutarse diariamente (por ejemplo, via cron o launchd).
"""

import sys
import os
from datetime import datetime

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from alerts.tracker import update_alert_performance, get_pending_alerts, calculate_performance_metrics


def main():
    """Actualiza alertas pendientes y regenera métricas."""
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting alert tracker update...")
    
    # Obtener alertas pendientes
    pending_before = len(get_pending_alerts())
    
    if pending_before == 0:
        print("No pending alerts to update.")
        return 0
    
    print(f"Found {pending_before} pending alerts")
    
    try:
        # Actualizar performance
        updated = update_alert_performance()
        print(f"Updated {updated} alerts")
        
        # Recalcular métricas
        metrics = calculate_performance_metrics()
        
        pending_after = len(get_pending_alerts())
        completed = pending_before - pending_after
        
        print(f"Completed: {completed} alerts")
        print(f"Remaining: {pending_after} alerts")
        
        # Mostrar win rate si hay datos
        if metrics['performance_7d']['evaluated'] > 0:
            wr = metrics['performance_7d']['win_rate']
            print(f"Current 7d Win Rate: {wr}%")
        
        print("Update completed successfully")
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
