#!/bin/bash
#
# Spectral Galileo - Check Bot Status
#

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "📊 Estado del Bot de Telegram"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "telegram_bot.pid" ]; then
    echo -e "${RED}❌ Bot no está corriendo${NC}"
    echo ""
    echo "Para iniciar: ./start_bot.sh"
    exit 1
fi

BOT_PID=$(cat telegram_bot.pid)

if ps -p $BOT_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Bot está corriendo${NC}"
    echo "PID: $BOT_PID"
    echo ""
    
    # Mostrar información del proceso
    echo "Información del proceso:"
    ps -p $BOT_PID -o pid,etime,rss,cmd
    echo ""
    
    # Mostrar últimas líneas del log
    if [ -f "logs/telegram_bot.log" ]; then
        echo "Últimas 5 líneas del log:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        tail -5 logs/telegram_bot.log
    fi
else
    echo -e "${RED}❌ Bot no está corriendo (PID obsoleto)${NC}"
    rm telegram_bot.pid
    echo ""
    echo "Para iniciar: ./start_bot.sh"
    exit 1
fi
