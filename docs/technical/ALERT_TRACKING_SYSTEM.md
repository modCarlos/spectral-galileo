# Sistema de Tracking Automático de Alertas

## 📊 Descripción

Sistema que registra automáticamente cada alerta generada y trackea su performance en el tiempo (1 día, 7 días, 30 días), calculando métricas como win rate, avg return, mejor/peor trade, etc.

---

## ✨ Características

### Registro Automático
- ✅ Cada alerta (FUERTE COMPRA, COMPRA, VENTA) se registra automáticamente
- ✅ Guarda: ticker, veredicto, confianza, precio, fecha, detalles técnicos
- ✅ Sin intervención manual necesaria

### Actualización Automática
- ✅ Se ejecuta diariamente a las 6:00 PM (después del cierre de mercado)
- ✅ Descarga precios históricos vía yfinance
- ✅ Calcula returns a 1d, 7d, 30d
- ✅ Determina WIN/LOSS automáticamente

### Métricas Calculadas
- Win Rate (%)
- Average Return (%)
- Average Win/Loss (%)
- Mejor y peor trade
- Performance por veredicto (FUERTE COMPRA vs COMPRA)
- Performance por ticker
- Performance por nivel de confianza (90-100%, 80-89%, etc.)

---

## 🚀 Instalación

El sistema se instala automáticamente con el daemon:

```bash
bash install_daemon.sh
```

Esto instala:
1. **Alert Daemon** - Escanea watchlist cada 30 min
2. **Tracker Updater** - Actualiza performance diariamente a las 6 PM

---

## 📋 Comandos CLI

### Ver Reporte de Performance
```bash
python main.py --alerts report
```

**Output:**
```
📊 REPORTE DE PERFORMANCE DE ALERTAS
============================================================

📈 RESUMEN GENERAL
   Total alertas: 25
   Pendientes de evaluación: 5

📅 PERFORMANCE 7 DÍAS
   Evaluadas: 20
   Wins: 13 | Losses: 7
   Win Rate: 65.0%
   Avg Return: +3.2%
   Avg Win: +5.8%
   Avg Loss: -2.1%
   Mejor: NVDA (+12.5%)
   Peor: TSLA (-5.2%)

📅 PERFORMANCE 30 DÍAS
   Evaluadas: 10
   Wins: 7 | Losses: 3
   Win Rate: 70.0%
   Avg Return: +8.5%

📋 POR VEREDICTO (7d)
   FUERTE COMPRA: 12 alertas | Win Rate: 75.0%
   COMPRA: 8 alertas | Win Rate: 50.0%

📈 TOP TICKERS (7d)
   NVDA: +8.5% | WR: 80% (5 alertas)
   AAPL: +4.2% | WR: 66% (3 alertas)
   MSFT: +2.1% | WR: 60% (5 alertas)

🎯 POR NIVEL DE CONFIANZA (7d)
   90-100%: 3 alertas | Win Rate: 100%
   80-89%: 5 alertas | Win Rate: 80%
   70-79%: 8 alertas | Win Rate: 62%
   60-69%: 4 alertas | Win Rate: 50%
```

### Actualizar Performance Manualmente
```bash
python main.py --alerts update
```

Descarga precios actualizados y recalcula métricas.

**Uso:** Solo si quieres actualizar fuera del horario automático (6 PM).

---

## 📁 Archivos Generados

### `data/alerts_tracker.json`
Historial completo de todas las alertas:

```json
{
  "alerts": [
    {
      "id": 1,
      "ticker": "AAPL",
      "verdict": "FUERTE COMPRA",
      "confidence": 75,
      "entry_price": 185.20,
      "entry_date": "2025-01-02T10:30:00",
      "details": {"rsi": 28.5, "macd_status": "Bullish"},
      
      "price_1d": 187.50,
      "price_7d": 192.30,
      "price_30d": 195.80,
      
      "return_1d": 1.24,
      "return_7d": 3.83,
      "return_30d": 5.72,
      
      "result_7d": "WIN",
      "result_30d": "WIN",
      
      "status": "COMPLETE",
      "last_updated": "2025-02-01T18:00:00"
    }
  ],
  "stats": {
    "total_tracked": 25,
    "pending_evaluation": 5,
    "evaluated_7d": 20,
    "evaluated_30d": 10
  }
}
```

### `data/alerts_performance.json`
Métricas agregadas (regenerado automáticamente):

```json
{
  "generated_at": "2025-01-15T18:00:00",
  "total_alerts": 25,
  "pending_evaluation": 5,
  
  "performance_7d": {
    "evaluated": 20,
    "wins": 13,
    "losses": 7,
    "win_rate": 65.0,
    "avg_return": 3.2,
    "avg_win": 5.8,
    "avg_loss": -2.1,
    "best_trade": {"ticker": "NVDA", "return": 12.5},
    "worst_trade": {"ticker": "TSLA", "return": -5.2}
  },
  
  "by_verdict": {
    "FUERTE COMPRA": {"count": 12, "win_rate": 75.0},
    "COMPRA": {"count": 8, "win_rate": 50.0}
  },
  
  "by_ticker": {
    "NVDA": {"count": 5, "win_rate": 80, "avg_return": 8.5},
    "AAPL": {"count": 3, "win_rate": 66, "avg_return": 4.2}
  },
  
  "by_confidence": {
    "90-100%": {"count": 3, "win_rate": 100},
    "80-89%": {"count": 5, "win_rate": 80},
    "70-79%": {"count": 8, "win_rate": 62}
  }
}
```

---

## 🔄 Flujo Automático

### Día 1 (Lunes 9:30 AM)
1. Daemon escanea watchlist
2. Detecta oportunidad: AAPL - FUERTE COMPRA (75%)
3. Envía notificación macOS
4. **Registra en tracker** con precio $185.20

### Día 1 (6:00 PM)
1. Tracker updater se ejecuta automáticamente
2. Descarga precio de cierre: $187.50
3. Calcula return 1d: +1.24%

### Día 7 (Lunes 6:00 PM)
1. Tracker updater ejecuta
2. Descarga precio: $192.30
3. Calcula return 7d: +3.83%
4. Determina resultado: **WIN** (return > 0 para COMPRA)

### Día 30 (Jueves 6:00 PM)
1. Tracker updater ejecuta
2. Descarga precio: $195.80
3. Calcula return 30d: +5.72%
4. Determina resultado: **WIN**
5. Marca alerta como **COMPLETE**

---

## 🎯 Interpretación de Métricas

### Win Rate
- **>60%** = Excelente (mejor que promedio de mercado)
- **50-60%** = Bueno (rentable con gestión de riesgo)
- **40-50%** = Aceptable (necesita gestión de riesgo estricta)
- **<40%** = Revisar estrategia

### Average Return
- **>5%** (7d) = Muy bueno
- **2-5%** (7d) = Bueno
- **0-2%** (7d) = Neutro
- **<0%** (7d) = Revisar

### Por Veredicto
- **FUERTE COMPRA** debe tener win rate >65%
- **COMPRA** debe tener win rate >55%
- Si no: ajustar thresholds de confianza

### Por Confianza
- **90-100%**: Win rate esperado >75%
- **80-89%**: Win rate esperado >65%
- **70-79%**: Win rate esperado >55%
- **60-69%**: Win rate esperado >50%

Si no se cumple: aumentar threshold mínimo en config.

---

## 🔧 Troubleshooting

### No se registran alertas
```bash
# Verificar que el daemon está corriendo
python main.py --alerts status

# Verificar logs
tail -f logs/alerts.log
```

### Actualizaciones no funcionan
```bash
# Verificar que el tracker updater está instalado
launchctl list | grep tracker-updater

# Ver logs
cat logs/tracker_updater.log

# Ejecutar manualmente para ver errores
python update_tracker.py
```

### Error descargando precios
**Causa:** yfinance puede fallar ocasionalmente

**Solución:** La actualización automática reintentará al día siguiente

### Alertas marcadas como LOSS incorrectamente
**Causa:** Solo considera return simple, no considera contexto

**Nota:** El sistema es para tracking, no para evaluación definitiva. Usa tu criterio.

---

## 📊 Ejemplo de Uso Real

### Semana 1-2: Acumulación de datos
```bash
# Cada día (opcional)
python main.py --alerts report

# Deberías ver:
# Total alertas: 5-10 (dependiendo de mercado)
# Pendientes: La mayoría
```

### Semana 3: Primeros resultados 7d
```bash
python main.py --alerts report

# Ahora verás:
# Performance 7d:
#   Evaluadas: 5-8
#   Win Rate: XX%
#   Avg Return: XX%
```

### Mes 1: Evaluación completa
```bash
python main.py --alerts report

# Datos suficientes para análisis:
# - Win rate 7d y 30d
# - Performance por ticker
# - Performance por confianza
# - Identificar qué funciona mejor
```

---

## 🎯 Decisiones basadas en data

### Si Win Rate 7d <40%
```bash
# Opción 1: Aumentar threshold de confianza
# Editar config/alert_config.json:
{
  "min_confidence": {
    "strong_buy": 75,  // Era 70
    "buy": 65          // Era 60
  }
}
```

### Si "COMPRA" tiene bajo win rate
```bash
# Opción 2: Solo alertas FUERTE COMPRA
{
  "min_confidence": {
    "strong_buy": 70,
    "buy": 100  // Deshabilitar COMPRA
  }
}
```

### Si un ticker específico siempre pierde
```bash
# Remover de watchlist
python main.py --watchlist remove TICKER
```

### Si un rango de confianza funciona mejor
```bash
# Ejemplo: 80-89% tiene 90% win rate
# → Ajustar threshold a 80
{
  "min_confidence": {
    "strong_buy": 80
  }
}
```

---

## 🔄 Mantenimiento

### Limpiar alertas antiguas (opcional)
```python
# Script manual (crear si es necesario)
from alerts.tracker import load_tracker_data, save_tracker_data
from datetime import datetime, timedelta

data = load_tracker_data()

# Mantener solo últimos 3 meses
cutoff = datetime.now() - timedelta(days=90)
data['alerts'] = [
    a for a in data['alerts']
    if datetime.fromisoformat(a['entry_date']) >= cutoff
]

save_tracker_data(data)
```

### Backup de datos
```bash
# Hacer backup periódico
cp data/alerts_tracker.json data/alerts_tracker_backup_$(date +%Y%m%d).json
```

---

## 📌 Notas Importantes

1. **Los datos son históricos** - Performance pasada no garantiza resultados futuros
2. **El sistema es para aprendizaje** - Usa los insights para mejorar, no como verdad absoluta
3. **Paper trading primero** - No uses estos datos para decisiones reales sin validación
4. **Contexto importa** - Un "LOSS" en crash de mercado no invalida el sistema

---

## 🎉 Ventajas del Sistema

✅ **Totalmente automático** - No tienes que anotar nada manualmente
✅ **Data objetiva** - Sin sesgos de memoria selectiva
✅ **Métricas accionables** - Puedes ajustar thresholds basado en data real
✅ **Histórico completo** - Todos los trades registrados
✅ **Fácil de interpretar** - Reportes claros y visuales

---

**Última actualización:** 25 de diciembre de 2025  
**Versión:** 1.0.0
