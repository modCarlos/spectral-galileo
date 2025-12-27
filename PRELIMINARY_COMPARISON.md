# 🔄 Comparación Preliminar: OLD vs NEW

## Observaciones Tempranas (Primeros 12 tickers)

### Diferencias de Confianza

| Ticker | OLD (main) | NEW (feature) | Delta | Verdict Change |
|--------|------------|---------------|-------|----------------|
| **MSFT** | 30% COMPRA | 24% COMPRA | -6% | - |
| **ARM** | 10% NEUTRAL | 9% NEUTRAL | -1% | - |
| **ORCL** | 11% NEUTRAL | 9% NEUTRAL | -2% | - |
| **META** | 11% NEUTRAL | 9% NEUTRAL | -2% | - |
| **BABA** | 36% COMPRA | 33% COMPRA | -3% | - |
| **WMT** | 43% COMPRA | 35% COMPRA | -8% | - |
| **SOFI** | 25% NEUTRAL | 21% NEUTRAL | -4% | - |
| **NVDA** | 33% COMPRA | 27% COMPRA | -6% | - |
| **NKE** | 13% NEUTRAL | 12% NEUTRAL | -1% | - |
| **TSLA** | 22% NEUTRAL | 18% NEUTRAL | -4% | - |
| **AMD** | 27% COMPRA | 22% NEUTRAL | -5% | ✅ CAMBIÓ |
| **NU** | ? | 20% NEUTRAL | ? | - |

### Hallazgos Clave

1. **Confianza Consistentemente Más Baja en NEW**
   - Todas las confianzas bajaron
   - Delta promedio: -4.2%
   - Rango: -1% a -8%

2. **Cambio de Veredicto Detectado**
   - **AMD**: COMPRA (27%) → NEUTRAL (22%)
   - Razón probable: Warnings de MTF_DISAGREE o INSIDER_SELLING

3. **Warnings Solo en NEW**
   - OLD: 0 warnings en todos
   - NEW: 93% tienen warnings
   - Sistema de warnings es completamente nuevo

4. **Casos Notables**

   **NVDA: -6% confianza**
   - OLD: 33% COMPRA (sin warnings)
   - NEW: 27% COMPRA (con MTF_DISAGREE, INSIDER_SELLING)
   - Insider selling: Jensen Huang -$557M
   - ✅ NEW detecta riesgo que OLD ignora

   **WMT: -8% confianza**
   - OLD: 43% COMPRA (sin warnings)
   - NEW: 35% COMPRA (con MTF_DISAGREE, INSIDER_SELLING)
   - Sigue siendo COMPRA pero más cauteloso
   - ✅ Sistema más conservador

   **AMD: Cambió de COMPRA a NEUTRAL**
   - OLD: 27% COMPRA
   - NEW: 22% NEUTRAL
   - ✅ Sistema evita señal débil

### Tendencias Identificadas

#### ✅ Lo que Funciona Bien:
1. **Más conservador pero no extremo**: Confianza baja 4-8% (razonable)
2. **Mantiene señales fuertes**: WMT sigue COMPRA a 35%
3. **Filtra señales débiles**: AMD 27% no es suficiente confianza
4. **Detecta riesgos**: NVDA penalizado por insider selling

#### ⚠️ Posibles Problemas:
1. **Todos pierden confianza**: Incluso señales fuertes
2. **Warnings ausentes en OLD**: Comparación no equitativa
3. **Thresholds muy estrictos**: AMD 27% → 22% parece pequeño cambio pero cambia veredicto

### Predicciones para Resultados Completos

**Esperado**:
- OLD tendrá más COMPRA (40-50% vs 28%)
- OLD tendrá mayor confianza promedio (25-30% vs 20%)
- OLD no tendrá warnings (0% vs 93%)
- NEW será más selectivo (menos false positives)

**Métricas Clave a Validar**:
1. ¿Cuántos cambios de veredicto? (esperado: 10-15)
2. ¿Delta promedio de confianza? (esperado: -5% a -10%)
3. ¿Warnings son útiles o ruido? (validar con datos reales)

---

**Status**: ⏳ Esperando resultados completos (~10 minutos)
