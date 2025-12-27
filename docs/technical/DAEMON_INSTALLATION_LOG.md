# Sistema de Alertas - Daemon Automático

## 📋 Estado de Instalación

**Fecha de instalación:** 25 de diciembre de 2025  
**Versión:** 1.0.0  
**Estado:** ✅ ACTIVO

---

## ⚙️ Configuración del Daemon

### Servicio launchd
- **Nombre:** `com.spectral-galileo.alerts`
- **Ubicación:** `~/Library/LaunchAgents/com.spectral-galileo.alerts.plist`
- **PID actual:** 73397

### Horario de Ejecución
- **Días:** Lunes a Viernes (días laborables)
- **Inicio diario:** 9:00 AM automáticamente
- **Intervalo de escaneo:** Cada 30 minutos
- **Horario activo:** 9:30 AM - 4:00 PM ET (horario de mercado NYSE)

### Comportamiento
- ✅ Se inicia automáticamente al arrancar el sistema
- ✅ Se reinicia automáticamente si falla inesperadamente
- ✅ Solo ejecuta durante horario de mercado (NYSE)
- ✅ Respeta fines de semana y días festivos

---

## 📊 Configuración Actual

```json
{
  "enabled": true,
  "interval_minutes": 30,
  "market_hours_only": true,
  "analysis_mode": "short_term",
  "min_confidence": {
    "strong_buy": 70,
    "buy": 60
  },
  "cooldown_hours": 4,
  "max_alerts_per_hour": 5,
  "sound_enabled": false,
  "sources": {
    "watchlist": true,
    "portfolio": true
  }
}
```

### Fuentes de Datos
- **Watchlist:** 39 tickers monitoreados
- **Portfolio:** 22 posiciones (monitoreo TP/SL)

### Umbrales de Alerta
- **FUERTE COMPRA:** ≥70% confianza
- **COMPRA:** ≥60% confianza
- **VENTA:** Cualquier confianza (para TP/SL)

### Anti-Spam
- **Cooldown:** 4 horas entre alertas del mismo ticker
- **Rate limiting:** Máximo 5 alertas por hora
- **Sonido:** Desactivado

---

## 🎯 Comandos Útiles

### Verificar Estado
```bash
# Ver estado completo del sistema
python main.py --alerts status

# Ver logs en tiempo real
tail -f logs/alerts.log

# Ver estadísticas de launchd
launchctl list | grep spectral
```

### Control Manual
```bash
# Detener daemon
python main.py --alerts stop

# Iniciar daemon manualmente (si está detenido)
python main.py --alerts start

# Enviar notificación de prueba
python main.py --alerts test

# Ver configuración
python main.py --alerts config
```

### Gestión del Servicio
```bash
# Reiniciar servicio launchd
launchctl unload ~/Library/LaunchAgents/com.spectral-galileo.alerts.plist
launchctl load ~/Library/LaunchAgents/com.spectral-galileo.alerts.plist

# Desinstalar servicio automático
bash uninstall_daemon.sh

# Reinstalar servicio
bash install_daemon.sh
```

---

## 📁 Archivos del Sistema

### Logs
- **Principal:** `logs/alerts.log` - Log del daemon con timestamp
- **Stdout:** `logs/alerts_stdout.log` - Salida estándar de launchd
- **Stderr:** `logs/alerts_stderr.log` - Errores de launchd

### Estado
- **State:** `data/alerts_state.json` - Estado del daemon (PID, contadores)
- **History:** `data/alerts_history.json` - Historial de alertas enviadas
- **PID:** `data/alerts.pid` - Process ID del daemon activo

### Configuración
- **Config:** `config/alert_config.json` - Configuración del sistema
- **Plist:** `com.spectral-galileo.alerts.plist` - Configuración launchd

---

## 📈 Estadísticas Actuales

**Al momento de instalación:**
```
🟢 Daemon: CORRIENDO (PID: 73397)
📊 Mercado: CERRADO (Abre en 6h 11m)

Escaneos realizados: 1
Alertas enviadas: 0
Alertas esta hora: 0/5
Tickers monitoreados: 39
Posiciones en portfolio: 22
Último escaneo: 2025-12-25 01:07:37
```

---

## 🔔 Tipos de Notificaciones

### 1. Alertas de Trading
**Cuándo:** Ticker cumple umbral de confianza (FUERTE COMPRA/COMPRA)

**Ejemplo:**
```
🚀 FUERTE COMPRA - AAPL

Precio: $185.20
Confianza: 75%

RSI: 28.5 (Oversold)
MACD: Bullish Crossover
Tendencia: Alcista
```

### 2. Alertas de Risk Management
**Cuándo:** Posición alcanza Take Profit (TP) o Stop Loss (SL)

**Ejemplo:**
```
🎯 TAKE PROFIT - NVDA

Precio actual: $525.00
Precio entrada: $480.00
Ganancia: +9.4%

Recomendación: Vender parcial/total
```

### 3. Alertas de Prueba
**Cuándo:** Se ejecuta `python main.py --alerts test`

**Ejemplo:**
```
🧪 Test de Notificación

Sistema de alertas operativo
Timestamp: 2025-12-25 01:18:45
```

---

## 🎯 Plan de Seguimiento

### Semana 1-2: Observación Pasiva
**Objetivo:** Familiarizarse con el volumen y tipo de alertas

**Tareas:**
- [ ] Revisar alertas diarias (no actuar, solo observar)
- [ ] Anotar cada alerta en spreadsheet (ticker, veredicto, confianza, precio)
- [ ] Identificar patrones iniciales
- [ ] Evaluar si el volumen de alertas es adecuado (target: 3-5/semana)

**Checklist diario:**
```bash
# Mañana (9:30 AM)
python main.py --alerts status

# Tarde (4:30 PM)
tail -20 logs/alerts.log

# Fin de semana
python main.py --alerts status  # Ver resumen semanal
```

### Semana 3-4: Paper Trading Manual
**Objetivo:** Evaluar efectividad de señales

**Tareas:**
- [ ] Paper trade cada señal (anotar como si fueras a ejecutar)
- [ ] Trackear performance 7 días después
- [ ] Calcular win rate preliminar
- [ ] Identificar sectores más efectivos

**Template de tracking:**
```
Date       | Ticker | Verdict        | Conf | Entry  | 7d Price | Result | Return
2025-01-02 | AAPL   | FUERTE COMPRA  | 75%  | 185.20 | 192.50   | ✅ WIN | +3.9%
2025-01-03 | TSLA   | COMPRA         | 62%  | 245.00 | 238.00   | ❌ LOSS| -2.9%
```

### Mes 1: Evaluación
**Objetivo:** Decidir ajustes o continuar

**Métricas clave:**
- **Win rate:** ¿>50%?
- **Avg return per signal:** ¿>2%?
- **False positive rate:** ¿<40%?
- **Señales por semana:** ¿3-5? (ni mucho ni poco)

**Decisiones:**
- Si win rate >60%: Considerar aumentar tamaño de watchlist
- Si win rate 40-60%: Continuar monitoreando
- Si win rate <40%: Revisar configuración (¿ajustar thresholds?)

---

## 🐛 Troubleshooting

### Daemon no inicia
```bash
# Verificar que el servicio está cargado
launchctl list | grep spectral

# Si no aparece, recargar
launchctl load ~/Library/LaunchAgents/com.spectral-galileo.alerts.plist

# Verificar errores en logs
cat logs/alerts_stderr.log
```

### No recibo notificaciones
```bash
# 1. Verificar que el daemon está corriendo
python main.py --alerts status

# 2. Enviar notificación de prueba
python main.py --alerts test

# 3. Verificar permisos de notificaciones en macOS
# System Settings > Notifications > Python/Terminal
```

### Demasiadas alertas
```bash
# Ajustar thresholds de confianza (editar config)
python main.py --alerts config

# Aumentar confianza mínima en config/alert_config.json:
# "strong_buy": 75,  # Era 70
# "buy": 65,         # Era 60
```

### Muy pocas alertas
```bash
# Reducir thresholds de confianza
# "strong_buy": 65,  # Era 70
# "buy": 55,         # Era 60

# O agregar más tickers a watchlist
python main.py --watchlist add TICKER
```

---

## 🔄 Actualización de Configuración

### Cambiar intervalo de escaneo
Editar `config/alert_config.json`:
```json
{
  "interval_minutes": 60  // Cambiar de 30 a 60 minutos
}
```

Luego reiniciar daemon:
```bash
python main.py --alerts stop
python main.py --alerts start
```

### Activar sonido en notificaciones
```json
{
  "sound_enabled": true  // Cambiar a true
}
```

### Ajustar cooldown
```json
{
  "cooldown_hours": 6  // Cambiar de 4 a 6 horas
}
```

---

## 📊 Logs y Monitoreo

### Ver últimas 50 líneas del log
```bash
tail -50 logs/alerts.log
```

### Buscar alertas específicas
```bash
# Buscar alertas de AAPL
grep "AAPL" logs/alerts.log

# Buscar alertas FUERTE COMPRA
grep "FUERTE COMPRA" logs/alerts.log

# Contar alertas del día
grep "$(date +%Y-%m-%d)" logs/alerts.log | wc -l
```

### Limpiar logs antiguos (opcional)
```bash
# Hacer backup
cp logs/alerts.log logs/alerts_backup_$(date +%Y%m%d).log

# Limpiar
echo "" > logs/alerts.log
```

---

## 🎉 Instalación Completada

**Estado:** ✅ Sistema operativo y monitoreando

**Próximos pasos:**
1. Dejar correr durante 2-4 semanas
2. Trackear señales manualmente (paper trading)
3. Evaluar efectividad con datos reales
4. Ajustar configuración si es necesario

**Contacto en caso de issues:**
- Logs: `tail -f logs/alerts.log`
- Estado: `python main.py --alerts status`
- Documentación: `docs/NEXT_STEPS_RECOMMENDATIONS.md`

---

**Fecha:** 25 de diciembre de 2025  
**Instalado por:** Automated setup script  
**Versión del sistema:** 1.0.0  
**Estado:** Producción
