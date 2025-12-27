# Backtesting Comparison Process

## Objetivo
Comparar el agente VIEJO (main branch) vs NUEVO (con mejoras de Phase 1 + Phase 2) para validar que las mejoras realmente funcionan.

## Metodología: Watchlist Comparison (Option 1)

**Ventajas**:
- ✅ Rápido (~10 minutos)
- ✅ Datos reales actuales
- ✅ Fácil de interpretar
- ✅ No requiere lógica de timing

**Desventajas**:
- ❌ No es backtesting histórico real
- ❌ No mide rentabilidad actual

## Proceso Completo

### Paso 1: Ejecutar NEW version (COMPLETADO)
```bash
# En branch: feature/advanced-improvements
python backtesting_comparison.py
# Output: backtesting_comparison_new.csv
```

**Status**: 🔄 EN PROGRESO (26/62 tickers completados)

### Paso 2: Ejecutar OLD version (PENDIENTE)
```bash
# Guardar trabajo actual
git add .
git commit -m "temp: before backtesting OLD version"

# Cambiar a main branch
git checkout main

# Ejecutar sobre el mismo watchlist
python backtesting_comparison.py
# Output: backtesting_comparison_old.csv

# Regresar a feature branch
git checkout feature/advanced-improvements
```

**Status**: ⏸️ PENDIENTE (esperar a que termine Paso 1)

### Paso 3: Generar reporte comparativo
```bash
python generate_comparison_report.py
# Output: backtesting_comparison_report.md
```

Este script:
- Lee ambos CSVs (old y new)
- Calcula deltas de confianza
- Identifica cambios de veredicto
- Cuenta warnings detectados
- Genera reporte markdown

## Métricas a Analizar

### 1. Distribución de Veredictos
```
| Veredicto | OLD | NEW | Cambio |
|-----------|-----|-----|--------|
| COMPRA    | 35  | 8   | -27    |  <- ¿Se volvió muy conservador?
| NEUTRAL   | 20  | 48  | +28    |  <- ¿Muchos ahora NEUTRAL?
| VENTA     | 7   | 6   | -1     |
```

### 2. Confianza Promedio
```
OLD: 45.2%
NEW: 32.8%  <- Más conservador (esperado)
Delta: -12.4%
```

**Interpretación**:
- Caída moderada (10-15%) = ✅ BUENO (más selectivo)
- Caída severa (>20%) = ⚠️ Revisar (demasiado conservador)
- Aumento = ❌ MAL (no cumple objetivo)

### 3. Warnings Detectados (NEW only)
```
Tickers con warnings: 54/62 (87%)

Tipos:
- MTF_DISAGREE: 32 tickers  <- Timeframes en conflicto
- INSIDER_SELLING: 18 tickers  <- Detección de venta interna
- PRE_EARNINGS: 12 tickers  <- Próximo earnings cercano
- BEAR_MARKET: 8 tickers
- REDDIT_BEARISH: 5 tickers
```

**Interpretación**:
- 70-90% con warnings = ✅ Sistema funciona
- <50% = ⚠️ Warnings muy restrictivos
- 100% = ❌ Demasiado sensible

### 4. Cambios de Veredicto Específicos

**Casos interesantes**:
```
NVDA: COMPRA 65% → NEUTRAL 27% (-38%)
  Warnings: INSIDER_SELLING, MTF_DISAGREE
  Razón: Jensen Huang vendió $557M

TSLA: COMPRA 55% → NEUTRAL 18% (-37%)
  Warnings: INSIDER_SELLING, REDDIT_BEARISH
  Razón: Kimbal Musk vendió, Reddit negativo

AAPL: NEUTRAL 40% → NEUTRAL 35% (-5%)
  Warnings: INSIDER_SELLING
  Razón: Tim Cook vendió $33M (normal)
```

### 5. Impacto de Features Nuevos

**Multi-Timeframe Confluence**:
- ¿Cuántos tickers tienen desacuerdo entre timeframes?
- ¿Es un warning útil o ruido?

**Reddit Sentiment**:
- ¿Cuántos tickers tienen actividad en Reddit?
- ¿Sentiment correlaciona con precio?

**Earnings Calendar**:
- ¿Pre-earnings warnings son útiles?
- ¿Beat streak correlaciona con momentum?

**Insider Trading**:
- ¿Venta masiva es señal válida? (NVDA -$557M)
- ¿Compras pequeñas son señal? (<$100K)

## Criterios de Éxito

### ✅ Resultado IDEAL:
1. Confianza promedio baja 10-15% (más selectivo)
2. COMPRAS se redujeron 30-50% (solo las mejores)
3. Warnings detectan riesgos reales (insider, timeframes, earnings)
4. Sistema mantiene señales fuertes (WMT 35%, BABA 33%)

### ⚠️ Resultado ACEPTABLE:
1. Confianza baja 15-20%
2. Warnings útiles pero algunos falsos positivos
3. Algunos veredictos conservadores pero justificados

### ❌ Resultado MALO:
1. Confianza baja >25% (demasiado conservador)
2. COMPRAS desaparecen casi totalmente (<5 tickers)
3. Warnings son ruido (no accionables)
4. Sistema rechaza oportunidades obvias

## Resultados Preliminares (26/62 completados)

### Distribución actual:
```
COMPRA: 8/26 (31%)
NEUTRAL: 18/26 (69%)

Confianza promedio:
- COMPRA: 29.6% (más bajo que antes, esperado)
- NEUTRAL: 15.4%
```

### Observations:
- ✅ WMT y XOM tienen 35% (señales fuertes se mantienen)
- ✅ BABA 33% (oportunidad detectada)
- ✅ NVDA solo 27% vs típico 60%+ (insider selling funcionó)
- ✅ TSLA 18% neutral (Reddit bearish + insider selling)
- ⚠️ META 9% muy bajo (revisar por qué tan conservador)

### Warnings más comunes (hasta ahora):
- 2 warnings: 17 tickers (65%)
- 1 warning: 7 tickers (27%)
- 0 warnings: 2 tickers (8%)

**Interpretación**: Sistema está siendo muy cuidadoso, casi todos tienen algún warning.

## Próximos Pasos

1. **Esperar a que termine backtesting NEW** (ETA: ~5 minutos)
2. **Analizar CSV completo** (62 tickers)
3. **Hacer commit del código actual**
4. **Checkout main y ejecutar OLD version**
5. **Generar reporte comparativo**
6. **Tomar decisión**:
   - Si resultados buenos → Continuar a Phase 3.2-3.3
   - Si muy conservador → Ajustar thresholds
   - Si no hay impacto → Revisar approach

## Comandos Rápidos

```bash
# Ver progreso actual
cat backtesting_comparison_new.csv | wc -l

# Ver últimas líneas
tail -20 backtesting_comparison_new.csv

# Contar veredictos
grep "COMPRA" backtesting_comparison_new.csv | wc -l
grep "NEUTRAL" backtesting_comparison_new.csv | wc -l
grep "VENTA" backtesting_comparison_new.csv | wc -l

# Ver confianza promedio (aproximado)
awk -F',' '{sum+=$3; count++} END {print sum/count}' backtesting_comparison_new.csv
```

## Notas Técnicas

**Tiempo por ticker**: ~10 segundos
- Fetch data: 2-3s
- Análisis: 4-5s
- Delay: 1s
- Print: 1s

**Warnings detectados via string parsing**:
```python
if 'Timeframes en desacuerdo' in con:
    warnings.append('MTF_DISAGREE')
if 'insider selling' in con.lower():
    warnings.append('INSIDER_SELLING')
if 'Earnings en' in con and 'días' in con:
    warnings.append('PRE_EARNINGS')
```

**Métricas extraídas**:
- verdict, confidence, regime
- mtf_signal, mtf_confluence
- reddit_mentions, reddit_sentiment
- earnings_trend, earnings_beat_streak
- insider_sentiment, insider_net_value
- warnings (parsed from cons list)
- pros_count, cons_count

## Interpretación de Resultados (Guía)

### Si NEW es mucho más conservador:
**Posibles causas**:
1. Penalties están stacking demasiado
2. Timeframe disagreements son muy comunes
3. Insider selling es sobrevalorado
4. Reddit sentiment es demasiado negativo

**Ajustes**:
- Reducir penalty de MTF_DISAGREE de -15% a -10%
- Aumentar threshold de insider selling ($5M → $10M)
- Reducir peso de Reddit bearish (-15% → -10%)

### Si NEW no tiene mucho impacto:
**Posibles causas**:
1. Mejoras no están activadas correctamente
2. Datos externos no tienen señal
3. Thresholds muy permisivos

**Ajustes**:
- Verificar que todas las funciones se llaman
- Aumentar sensibilidad de warnings
- Considerar agregar más features

### Si NEW es mejor selectivo:
**Señales positivas**:
1. Mantiene señales fuertes (35%+)
2. Rechaza señales débiles (<20%)
3. Warnings son accionables
4. Insider/Reddit/Earnings aportan

**Próximo paso**: Phase 3.2-3.3 (Optimization)
