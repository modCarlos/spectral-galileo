# Plan de Mejoras del Agente (Sin ML Complejo)

**Fecha**: 26 de Diciembre, 2025  
**Rama**: `feature/advanced-improvements`  
**Objetivo**: Mejorar precisión y confianza del agente usando técnicas probadas

---

## Fase 1: Quick Wins (1-2 días) ⚡

### 1.1 Multi-Timeframe Confirmation
**Problema**: Solo analizamos timeframe diario (1d)  
**Solución**: Confirmar señales con weekly y monthly

**Implementación**:
- Crear función `analyze_multiple_timeframes(ticker)`
- Calcular indicadores en 1d, 1wk, 1mo
- Solo dar señal fuerte si 2+ timeframes coinciden
- Agregar campo `timeframe_confluence` al reporte

**Impacto esperado**: -30% false positives

---

### 1.2 Market Regime Detection
**Problema**: Misma estrategia en bull, bear y sideways markets  
**Solución**: Detectar régimen y ajustar thresholds

**Implementación**:
- Función `detect_market_regime(spy_data)`:
  - Bull: SPY > SMA200 y subiendo
  - Bear: SPY < SMA200 y bajando
  - Sideways: ADX < 20
- Ajustar `buy_threshold` dinámicamente:
  - Bull: 40 (agresivo)
  - Sideways: 50 (neutral)
  - Bear: 65 (ultra conservador)

**Impacto esperado**: +20% en bear markets, -15% drawdown

---

### 1.3 Confluence Scoring Mejorado
**Problema**: Indicadores se evalúan independientemente  
**Solución**: Puntuar alineación de múltiples señales

**Implementación**:
- Sistema de puntos por coincidencias:
  - RSI oversold + MACD bullish = +3 pts
  - Price > SMA50 > SMA200 = +2 pts (Golden Cross)
  - Volume > 1.5x avg = +2 pts
  - ADX > 25 = +1 pt
- Solo operar con confluence >= 5 pts
- Agregar `confluence_score` al reporte

**Impacto esperado**: +25% win rate

---

## Fase 2: Datos Externos (3-5 días) 📊

### 2.1 Reddit/WallStreetBets Sentiment ✅
**STATUS**: COMPLETADO  
**API**: requests + Reddit JSON API (sin autenticación)  
**Datos**:
- Menciones del ticker (últimas 24h)
- Sentiment score (bullish/bearish)
- Upvotes/engagement
- Top posts de r/wallstreetbets, r/stocks, r/investing

**Integración**:
```python
reddit_sentiment = get_reddit_sentiment(ticker)
# Scoring (5 pts max):
# - BULLISH + 20+ menciones = +5 pts
# - BULLISH + 10+ menciones = +4 pts
# - BEARISH + 20+ menciones = -5 pts (warning)
# Ajustes de confianza automáticos
```

**Implementado**:
- `reddit_sentiment.py`: Módulo completo con análisis de sentiment
- Integrado en `agent.py` dentro del confluence scoring
- 5 puntos adicionales al confluence scoring (total ahora: 15 pts)
- Warnings para sentiment bearish fuerte
- Reporte muestra menciones, sentiment, engagement, top posts

**Resultados de prueba**:
- TSLA: 2 menciones, NEUTRAL, 100/100 engagement
- NVDA: 2 menciones, NEUTRAL, 38/100 engagement
- Sistema funcionando correctamente

---

### 2.2 Earnings Calendar + Surprises ✅
**STATUS**: COMPLETADO  
**Fuente**: Yahoo Finance / yfinance  
**Datos**:
- Próximo earnings date
- Historical earnings surprises
- Consensus estimates

**Integración**:
```python
if days_to_earnings < 7:
    confidence *= 0.8  # Reducir antes de earnings (volatilidad)

if last_earnings_surprise > 10%:
    pros.append("Strong earnings momentum")
```

**Implementado**: earnings_calendar.py, integrado en agent.py con pre-earnings warnings y earnings momentum boost

---

### 2.3 Insider Trading Activity ✅
**STATUS**: COMPLETADO  
**Fuente**: SEC EDGAR (gratis)  
**Datos**:
- Form 4 filings (últimos 90 días)
- Net insider buying/selling
- Executive vs Director trades

**Integración**:
```python
insider_activity = get_insider_trades(ticker)
if insider_activity['net_buying'] > 0:
    confidence += 5
    pros.append(f"Insider buying: ${insider_activity['total_value']/1e6:.1f}M")
```

**Implementado**: insider_trading.py, integrado en agent.py con confidence adjustments (+10% to -10%) based on insider sentiment

---

## Fase 3: Optimización (1 semana) 🔧

### 3.1 Backtest Comparativo
**Objetivo**: Validar mejoras con datos históricos

**Métricas a medir**:
- Win Rate (antes vs después)
- Sharpe Ratio
- Max Drawdown
- False Positives / False Negatives
- Performance by regime (bull/bear/sideways)

**Archivos**:
- `backtesting/compare_versions.py`
- Comparar: Baseline vs Fase1 vs Fase2

---

### 3.2 Grid Search de Pesos
**Objetivo**: Encontrar pesos óptimos para indicadores

**Parámetros a optimizar**:
```python
weights = {
    'rsi': [0.15, 0.20, 0.25, 0.30],
    'macd': [0.20, 0.25, 0.30, 0.35],
    'adx': [0.15, 0.20, 0.25],
    'volume': [0.10, 0.15, 0.20],
    'bollinger': [0.05, 0.10, 0.15]
}
```

**Método**:
- Grid search con backtesting
- Optimizar por Sharpe Ratio
- Validar con out-of-sample data

---

### 3.3 Thresholds por Categoría
**Problema**: Mismos thresholds para todas las acciones  
**Solución**: Ajustar por volatilidad y sector

**Implementación**:
```python
thresholds = {
    'mega_cap_tech': {'buy': 35, 'sell': 65},  # AAPL, MSFT
    'high_vol_growth': {'buy': 43, 'sell': 57},  # TSLA, PLTR
    'stable_value': {'buy': 45, 'sell': 55},  # KO, PG
    'small_cap': {'buy': 50, 'sell': 50}  # High risk
}
```

---

## Cronograma

| Fase | Tarea | Días | Status |
|------|-------|------|--------|
| 1.1 | Multi-timeframe | 0.5 | ✅ |
| 1.2 | Regime detection | 0.5 | ✅ |
| 1.3 | Confluence scoring | 1 | ✅ |
| 2.1 | Reddit sentiment | 1 | ✅ |
| 2.2 | Earnings data | 1 | ✅ |
| 2.3 | Insider trading | 2 | ✅ |
| 3.1 | Backtesting | 2 | 🔲 |
| 3.2 | Grid search | 2 | 🔲 |
| 3.3 | Thresholds | 1 | 🔲 |

**Total estimado**: 11 días de trabajo  
**Completado hasta ahora**: 5 días (Fase 1 + Fase 2 completa)

---

## Estado Actual

**✅ FASE 1 COMPLETADA** (Quick Wins):
- 1.1: Multi-timeframe analysis
- 1.2: Market regime detection
- 1.3: Confluence scoring

**✅ FASE 2 COMPLETADA** (External Data):
- 2.1: Reddit sentiment (r/wallstreetbets, r/stocks, etc.)
- 2.2: Earnings calendar & surprises
- 2.3: Insider trading activity

**⏸️ FASE 3 PENDIENTE** (Optimization):
- 3.1: Backtesting comparison
- 3.2: Grid search optimization
- 3.3: Thresholds per category

**Próximo paso**: Backtesting para validar mejoras

---

## KPIs de Éxito

**Baseline (actual)**:
- Win Rate: ~53%
- Sharpe: 0.88
- Max Drawdown: -15%

**Target (post-mejoras)**:
- Win Rate: >65%
- Sharpe: >1.2
- Max Drawdown: <10%
- False Positives: -40%

---

## Notas

- Todas las mejoras son gratuitas (no requieren APIs pagadas)
- Enfoque en datos de calidad sobre complejidad algorítmica
- Cada fase se valida antes de pasar a la siguiente
- Si Fase 1-3 no mejoran, considerar data premium (dark pool, options flow)
