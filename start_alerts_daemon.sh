#!/bin/bash
# Script para iniciar el daemon de alertas en modo real

set -e

cd /Users/carlosfuentes/GitHub/spectral-galileo

echo "🚀 Iniciando daemon de alertas..."
echo ""

# Activar venv
source venv/bin/activate

# Ejecutar daemon en background
nohup python3 alerts/daemon.py > logs/daemon_startup.log 2>&1 &

DAEMON_PID=$!
echo "✅ Daemon iniciado (PID: $DAEMON_PID)"
sleep 2

# Verificar que está corriendo
if kill -0 $DAEMON_PID 2>/dev/null; then
    echo "✅ Daemon confirmado corriendo"
    echo ""
    echo "📝 Monitoreando alertas.log:"
    tail -5 logs/alerts.log
else
    echo "❌ Error: Daemon no se inició"
    cat logs/daemon_startup.log
fi
