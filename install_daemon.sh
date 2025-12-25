#!/bin/bash

# Script de instalación del daemon de alertas como servicio de macOS (launchd)

set -e

REPO_DIR="/Users/carlosfuentes/GitHub/spectral-galileo"
PLIST_NAME="com.spectral-galileo.alerts.plist"
PLIST_SOURCE="$REPO_DIR/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "======================================"
echo "Instalando Spectral Galileo Alert Daemon"
echo "======================================"
echo ""

# 1. Verificar que el archivo plist existe
if [ ! -f "$PLIST_SOURCE" ]; then
    echo "❌ Error: No se encuentra $PLIST_SOURCE"
    exit 1
fi

echo "✅ Archivo plist encontrado"

# 2. Crear directorio LaunchAgents si no existe
mkdir -p "$HOME/Library/LaunchAgents"
echo "✅ Directorio LaunchAgents verificado"

# 3. Copiar plist
cp "$PLIST_SOURCE" "$PLIST_DEST"
echo "✅ Archivo plist copiado a LaunchAgents"

# 4. Descargar el servicio si ya existe (por si acaso)
launchctl unload "$PLIST_DEST" 2>/dev/null || true
echo "✅ Servicio anterior descargado (si existía)"

# 5. Cargar el servicio
launchctl load "$PLIST_DEST"
echo "✅ Servicio cargado en launchd"

# 6. Verificar estado
sleep 2
if launchctl list | grep -q "com.spectral-galileo.alerts"; then
    echo ""
    echo "======================================"
    echo "🎉 ¡Instalación exitosa!"
    echo "======================================"
    echo ""
    echo "El daemon se iniciará automáticamente:"
    echo "  • Lunes-Viernes a las 9:00 AM"
    echo "  • Se reinicia automáticamente si falla"
    echo "  • Solo ejecuta durante horario de mercado"
    echo ""
    echo "Comandos útiles:"
    echo "  • Ver logs: tail -f $REPO_DIR/logs/alerts.log"
    echo "  • Estado: python $REPO_DIR/main.py --alerts status"
    echo "  • Reiniciar: launchctl unload $PLIST_DEST && launchctl load $PLIST_DEST"
    echo "  • Desinstalar: bash $REPO_DIR/uninstall_daemon.sh"
    echo ""
else
    echo ""
    echo "⚠️  El servicio se instaló pero no se detecta en launchd"
    echo "Verifica con: launchctl list | grep spectral"
fi
