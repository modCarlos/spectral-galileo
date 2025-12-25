#!/bin/bash

# Script de desinstalación del daemon de alertas

set -e

PLIST_NAME="com.spectral-galileo.alerts.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

TRACKER_PLIST_NAME="com.spectral-galileo.tracker-updater.plist"
TRACKER_PLIST_DEST="$HOME/Library/LaunchAgents/$TRACKER_PLIST_NAME"

echo "======================================"
echo "Desinstalando Spectral Galileo Alert Daemon"
echo "======================================"
echo ""

# 1. Descargar el servicio
if launchctl list | grep -q "com.spectral-galileo.alerts"; then
    launchctl unload "$PLIST_DEST"
    echo "✅ Servicio descargado de launchd"
else
    echo "⚠️  El servicio no estaba cargado"
fi

# 2. Eliminar plist
if [ -f "$PLIST_DEST" ]; then
    rm "$PLIST_DEST"
    echo "✅ Archivo plist eliminado"
else
    echo "⚠️  El archivo plist no existe"
fi

# 3. Detener daemon si está corriendo
REPO_DIR="/Users/carlosfuentes/GitHub/spectral-galileo"
PID_FILE="$REPO_DIR/data/alerts.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        kill "$PID" 2>/dev/null || true
        echo "✅ Daemon detenido (PID: $PID)"
    fi
    rm "$PID_FILE"
fi

# 4. Desinstalar tracker updater
if launchctl list | grep -q "com.spectral-galileo.tracker-updater"; then
    launchctl unload "$TRACKER_PLIST_DEST"
    echo "✅ Tracker updater descargado"
fi

if [ -f "$TRACKER_PLIST_DEST" ]; then
    rm "$TRACKER_PLIST_DEST"
    echo "✅ Tracker plist eliminado"
fi

echo ""
echo "======================================"
echo "✅ Desinstalación completada"
echo "======================================"
echo ""
echo "El daemon ha sido eliminado del sistema."
echo "Para reinstalar: bash install_daemon.sh"
echo ""
