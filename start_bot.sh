#!/bin/bash
#
# Spectral Galileo - Telegram Bot Startup Script
# Este script inicia el bot de Telegram en background
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🤖 Iniciando Spectral Galileo Telegram Bot..."

# Verificar que existe el archivo .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: Archivo .env no encontrado${NC}"
    echo "Crea el archivo .env basándote en .env.example"
    exit 1
fi

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python3 no está instalado${NC}"
    exit 1
fi

# Verificar que las dependencias están instaladas
if ! python3 -c "import telegram" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Instalando dependencias...${NC}"
    pip install python-telegram-bot python-dotenv
fi

# Crear directorio de logs si no existe
mkdir -p logs

# Verificar si ya está corriendo
if [ -f "telegram_bot.pid" ]; then
    OLD_PID=$(cat telegram_bot.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  El bot ya está corriendo (PID: $OLD_PID)${NC}"
        echo "Usa ./stop_bot.sh para detenerlo primero"
        exit 1
    else
        # PID file existe pero proceso no
        rm telegram_bot.pid
    fi
fi

# Iniciar bot en background
echo "🚀 Iniciando bot en background..."
nohup python3 telegram_bot.py > logs/bot_output.log 2>&1 &
BOT_PID=$!

# Guardar PID
echo $BOT_PID > telegram_bot.pid

# Esperar un momento para verificar que inició correctamente
sleep 2

if ps -p $BOT_PID > /dev/null; then
    echo -e "${GREEN}✅ Bot iniciado correctamente${NC}"
    echo "PID: $BOT_PID"
    echo "Log: logs/bot_output.log"
    echo ""
    echo "Comandos útiles:"
    echo "  • Ver logs en tiempo real: tail -f logs/telegram_bot.log"
    echo "  • Detener el bot: ./stop_bot.sh"
    echo "  • Estado del bot: ./status_bot.sh"
else
    echo -e "${RED}❌ Error: El bot no pudo iniciarse${NC}"
    echo "Revisa logs/bot_output.log para más detalles"
    rm telegram_bot.pid
    exit 1
fi
