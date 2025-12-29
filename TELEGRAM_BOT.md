# 🤖 Spectral Galileo - Telegram Bot

Bot de análisis financiero para Telegram con integración completa con el sistema Spectral Galileo.

## 🚀 Inicio Rápido

### 1. Configuración

El bot ya está configurado con:
- ✅ Token de Telegram Bot
- ✅ Usuarios autorizados: @modCarlos, @fenixfierce
- ✅ Rate limiting: 10 req/min, 50 req/hora
- ✅ Logging completo
- ✅ Manejo de errores

### 2. Iniciar el Bot

```bash
# Iniciar bot en background
./start_bot.sh

# Ver estado del bot
./status_bot.sh

# Detener el bot
./stop_bot.sh

# Ver logs en tiempo real
tail -f logs/telegram_bot.log
```

## 📱 Comandos Disponibles

### Análisis
- `/analizar AAPL` - Análisis básico largo plazo
- `/analizar AAPL -st` - Análisis corto plazo
- `/analizar AAPL -f` - Análisis completo con detalles

### Portafolio
- `/portafolio` - Ver tu portafolio con P&L
- `/agregar AAPL 150.50` - Agregar acción al portafolio
- `/eliminar AAPL` - Eliminar acción del portafolio

### Watchlist
- `/watchlist` - Ver tu watchlist
- `/watch AAPL` - Agregar a watchlist
- `/unwatch AAPL` - Quitar de watchlist

### Alertas
- `/alertas` - Ver estado del sistema de alertas
- `/alertas_status` - Información detallada de alertas

### Utilidades
- `/stats` - Estadísticas de uso personal
- `/help` - Ver ayuda completa
- `/start` - Menú principal con botones

## 🔒 Seguridad

### Rate Limiting
- **Por minuto:** 10 requests
- **Por hora:** 50 requests
- Sistema automático de control

### Autorización
Solo usuarios autorizados pueden usar el bot:
- @modCarlos
- @fenixfierce

Intentos no autorizados son registrados en logs.

### Token Seguro
- ✅ Token almacenado en `.env` (no versionado)
- ✅ `.env` incluido en `.gitignore`
- ⚠️ **NUNCA** commitear el token al repositorio

## 📊 Features Principales

### 1. Análisis Completo
- Análisis técnico con RSI, MACD, ADX
- Análisis fundamental (P/E, ROE, etc.)
- Veredicto automático: COMPRA/VENTA/NEUTRAL
- Análisis de tendencia para NEUTRAL
- Stop Loss y Take Profit calculados

### 2. Gestión de Portafolio
- Ver todas tus posiciones
- Cálculo automático de P&L
- Precio promedio ponderado
- Resumen total de inversión

### 3. Watchlist Inteligente
- Monitoreo de acciones favoritas
- Precios en tiempo real
- Análisis rápido con botones

### 4. Sistema de Alertas
- Integración con sistema de alertas de consola
- Monitoreo 24/7 de watchlist
- Notificaciones automáticas

### 5. Botones Inline
- Análisis completo con un click
- Agregar a portafolio directamente
- Agregar a watchlist
- Navegación rápida

## 📁 Estructura de Archivos

```
spectral-galileo/
├── telegram_bot.py          # Bot principal
├── .env                     # Configuración (NO commitear)
├── .env.example            # Template de configuración
├── start_bot.sh            # Script de inicio
├── stop_bot.sh             # Script para detener
├── status_bot.sh           # Ver estado del bot
├── logs/
│   ├── telegram_bot.log    # Log del bot
│   └── bot_output.log      # Output de consola
└── telegram_bot.pid        # PID del proceso
```

## 🔧 Mantenimiento

### Ver Logs
```bash
# Logs del bot (interacciones)
tail -f logs/telegram_bot.log

# Output de consola (errores críticos)
tail -f logs/bot_output.log

# Últimas 50 líneas
tail -50 logs/telegram_bot.log
```

### Reiniciar Bot
```bash
./stop_bot.sh && ./start_bot.sh
```

### Verificar Estado
```bash
./status_bot.sh
```

## 🐛 Troubleshooting

### El bot no inicia
1. Verificar que existe `.env` con el token
2. Verificar permisos: `chmod +x *.sh`
3. Ver logs: `cat logs/bot_output.log`

### Bot no responde
1. Verificar que está corriendo: `./status_bot.sh`
2. Ver logs en tiempo real: `tail -f logs/telegram_bot.log`
3. Reiniciar: `./stop_bot.sh && ./start_bot.sh`

### Rate limit muy restrictivo
Editar `.env`:
```bash
MAX_REQUESTS_PER_MINUTE=20
MAX_REQUESTS_PER_HOUR=100
```
Luego reiniciar el bot.

### Agregar usuarios autorizados
Editar `.env`:
```bash
AUTHORIZED_USERS=modCarlos,fenixfierce,nuevoUsuario
```
Luego reiniciar el bot.

## 📝 Logs y Monitoreo

### Qué se registra
- ✅ Todos los comandos ejecutados
- ✅ Usuario que ejecutó cada comando
- ✅ Errores y excepciones
- ✅ Intentos de acceso no autorizados
- ✅ Rate limiting activado
- ✅ Análisis completados

### Formato de Logs
```
2025-12-28 18:30:15 - telegram_bot - INFO - Command from authorized user @modCarlos: /analizar AAPL
2025-12-28 18:30:18 - telegram_bot - INFO - Analysis completed for AAPL by @modCarlos
```

## 🚦 Estados del Bot

| Estado | Descripción | Acción |
|--------|-------------|--------|
| ✅ Running | Bot funcionando correctamente | Ninguna |
| ⚠️ Rate Limited | Usuario excedió límite | Esperar 1 minuto |
| 🚫 Unauthorized | Usuario no autorizado | Agregar a `.env` |
| ❌ Stopped | Bot no está corriendo | `./start_bot.sh` |
| 🔄 Restarting | Bot reiniciándose | Esperar 5 segundos |

## 🎯 Próximas Mejoras

- [ ] Notificaciones push cuando hay cambio de veredicto
- [ ] Gráficos de análisis técnico
- [ ] Alertas personalizadas por precio
- [ ] Comparación de múltiples acciones
- [ ] Resumen semanal automático
- [ ] Integración con sistema de backtesting

## 📞 Soporte

Si encuentras algún problema:
1. Revisa los logs
2. Verifica la configuración en `.env`
3. Consulta esta documentación
4. Revisa el código en `telegram_bot.py`

## ⚠️ IMPORTANTE

**NUNCA** subas estos archivos a GitHub:
- `.env` (contiene el token)
- `telegram_bot.pid`
- `logs/` (puede contener información sensible)

Estos están protegidos en `.gitignore`.
