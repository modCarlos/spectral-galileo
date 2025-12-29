#!/bin/bash
#
# Spectral Galileo - Stop Telegram Bot
#

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🛑 Deteniendo Spectral Galileo Telegram Bot..."

if [ ! -f "telegram_bot.pid" ]; then
    echo -e "${YELLOW}⚠️  No se encontró PID file. El bot no parece estar corriendo.${NC}"
    exit 1
fi

BOT_PID=$(cat telegram_bot.pid)

if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "Deteniendo proceso $BOT_PID..."
    kill $BOT_PID
    sleep 2
    
    # Verificar si se detuvo
    if ps -p $BOT_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  El proceso no se detuvo. Forzando...${NC}"
        kill -9 $BOT_PID
    fi
    
    echo -e "${GREEN}✅ Bot detenido${NC}"
    rm telegram_bot.pid
else
    echo -e "${YELLOW}⚠️  El proceso $BOT_PID no está corriendo${NC}"
    rm telegram_bot.pid
fi
