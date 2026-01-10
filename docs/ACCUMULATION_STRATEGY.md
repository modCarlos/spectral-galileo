# 🎯 Estrategia de Acumulación Multi-Horizonte

## 📊 ¿Cuándo Empezar a Acumular Acciones?

### Marco Conceptual

Tu pregunta es estratégica y correcta: **"¿A qué precio comprar importa menos si la acción es realmente valiosa?"**

Este documento define cuándo activar la acumulación según el algoritmo de Spectral Galileo.

---

## 1. Los Tres Pilares de la Acumulación

### Pilar 1: Señal de Corto Plazo (Operativa) 🟢
**¿CUÁNDO?** Cuando el análisis diario muestra:
- **Verdict:** COMPRA o FUERTE COMPRA
- **Confianza:** ≥ 22% (COMPRA) o ≥ 30% (FUERTE COMPRA) 
- **Multi-timeframe:** Mínimo 2/3 timeframes (daily/weekly/monthly) en BUY

**¿POR QUÉ?** Momentum positivo a corto plazo = oportunidad operativa

**¿CUÁNTO ACUMULAR?**
- **COMPRA (22-35%):** Entrada pequeña (15-25% de posición)
- **FUERTE COMPRA (35%+):** Entrada grande (50-75% de posición)

---

### Pilar 2: Validación de Largo Plazo (Fundamental) 💰
**¿CUÁNDO?** Cuando el análisis LARGO PLAZO (`is_short_term=False`) muestra:
- **Verdict:** COMPRA o FUERTE COMPRA
- **Fundamentales sólidos:**
  - ROE > benchmark del sector
  - Deuda/Equity razonable para la industria
  - PEG < 2.0 (crecimiento justificado)
  - Margen operativo estable o mejorando

**¿POR QUÉ?** Garantiza que la acción tiene valor intrínseco duradero

**Benchmark por sector (INDUSTRY_BENCHMARKS en agent.py):**
```
Tech:           PE=30, ROE=20%, D/E=60
Financial:      PE=12, ROE=12%, D/E=450
Healthcare:     PE=20, ROE=15%, D/E=80
Consumer:       PE=25, ROE=18%, D/E=100
Utilities:      PE=18, ROE=09%, D/E=150
```

---

### Pilar 3: Confluencia de Señales (Multi-Timeframe) 🎯
**¿CUÁNDO?** Cuando MÚLTIPLES timeframes alinean:

```
Daily:   COMPRA     ✓ (Momentum corto-plazo)
Weekly:  COMPRA     ✓ (Tendencia intermedia)
Monthly: COMPRA     ✓ (Tendencia larga)
═══════════════════════════════════════════════
ACUMULAR AGRESIVAMENTE (HIGH CONVICTION)
```

**Niveles de Confluencia:**
- **3/3 timeframes en COMPRA:** Acumular 75-100% (MÁXIMA OPORTUNIDAD)
- **2/3 timeframes en COMPRA:** Acumular 50% (BUENA OPORTUNIDAD)
- **1/3 timeframes en COMPRA:** Acumular 25% (ESPECULATIVA)

---

## 2. La Estrategia Híbrida: Precio vs. Valor

### El Dilema Clásico
```
Escenario A:
└─ Acción está en máximos históricos
   ├─ Fundamentales: Excelentes (ROE 25%, crecimiento 30%)
   ├─ Corto Plazo: FUERTE COMPRA (40%)
   ├─ Largo Plazo: COMPRA (38%)
   └─ DECISIÓN: Acumular de todas formas (precio alto, pero valor real)

Escenario B:
└─ Acción caída 50% desde máximos
   ├─ Fundamentales: Débiles (ROE 8%, caída de ingresos -10%)
   ├─ Corto Plazo: COMPRA (25%, rebote técnico)
   ├─ Largo Plazo: VENTA (20%, problemas estructurales)
   └─ DECISIÓN: NO acumular (precio bajo, pero sin valor real)
```

**CONCLUSIÓN:** El precio bajo solo es atractivo si hay VALOR fundamentaldetrás.

---

## 3. Matriz de Acumulación

Cruza análisis CORTO y LARGO plazo:

```
                    LARGO PLAZO
                    COMPRA      VENTA/HOLD
                    ──────────────────────
CORTO     COMPRA │ ✅ ACUMULAR  │ ⚠️ ESPERAR
PLAZO     VENTA  │ ❌ NO COMPRAR│ ❌ VENDER
          HOLD   │ 🔄 MONITOREAR│ 🔴 EVITAR

DECISIONES:

✅ ACUMULAR (Verde)
└─ Corto COMPRA + Largo COMPRA
   └─ Significado: Oportunidad REAL, tanto técnica como fundamental
   └─ Acción: Acumular 25-75% según confianza
   └─ Seguimiento: Mantener posición, agregar en nuevos niveles

⚠️ ESPERAR (Amarillo)
└─ Corto COMPRA + Largo VENTA
   └─ Significado: Rebote técnico en acción con problemas estructurales
   └─ Acción: NO acumular aún, esperar claridad
   └─ Seguimiento: Monitorear si largo plazo mejora

❌ NO COMPRAR (Rojo)
└─ Corto VENTA + Largo COMPRA
   └─ Significado: Corrección en acción fundamentalmente sólida
   └─ Acción: Esperar a próxima señal de compra corto plazo
   └─ Seguimiento: Ideal para DÓLLAR COST AVERAGING (DCA)

🔴 EVITAR (Crítico)
└─ Corto VENTA + Largo VENTA
   └─ Significado: Problemas en MÚLTIPLES niveles
   └─ Acción: Venderficialmente, NO comprar
   └─ Seguimiento: Esperar a rotación estructural
```

---

## 4. Protocolo de Acumulación Escalonada

### Fase 1: IDENTIFICAR (Corto + Largo Plazo Alineados)
```python
# Ejecutar análisis en AMBOS modos
short_term_analysis = FinancialAgent(ticker, is_short_term=True).run_analysis()
long_term_analysis = FinancialAgent(ticker, is_short_term=False).run_analysis()

# Verificar alineación
if short_term_analysis['strategy']['verdict'] == 'COMPRA' and \
   long_term_analysis['strategy']['verdict'] == 'COMPRA':
    confidence_combined = (
        short_term_analysis['strategy']['confidence'] * 0.6 +  # 60% peso corto
        long_term_analysis['strategy']['confidence'] * 0.4     # 40% peso largo
    )
    print(f"ACUMULAR: Confianza combinada = {confidence_combined:.0f}%")
```

### Fase 2: CALCULAR (Tamaño de Posición)
```
Confianza Combinada    Tamaño Recomendado    Precio Importa
──────────────────────────────────────────────────────────
80%+                   75-100% posición      NO importa
60-80%                 50-75% posición       Importa poco
40-60%                 25-50% posición       Importa medio
20-40%                 0-25% posición        Importa mucho
```

**Ejemplo:** MSFT con confianza combinada 72%
- Tamaño: 60% de posición planeada
- Presupuesto: $10,000 × 60% = $6,000 para acumular

### Fase 3: EJECUTAR (Escalonado)
```
Entrada 1: 25% de posición → Cuando COMPRA (22%+) ✓
Entrada 2: 25% de posición → Cuando precio baja 3-5%
Entrada 3: 25% de posición → Cuando precio baja 7-10%
Entrada 4: 25% de posición → Cuando precio se estabiliza

Ventaja: Precio promedio más bajo que si compras todo de una vez
```

### Fase 4: MONITOREAR (Diario)
```
✓ Si corto plazo se mantiene en COMPRA → Mantener/Agregar
✓ Si largo plazo mejora (VENTA → COMPRA) → Agregar agresivamente
✓ Si corto plazo cae a VENTA → Pausar acumulación, proteger ganancias
✗ Si largo plazo cae a VENTA → SALIR completamente, reevaluar
```

---

## 5. Casos de Uso Reales

### Caso 1: NVIDIA en Nov-Dic 2024
```
Escenario: Caída de 30% por preocupaciones de competencia
├─ Corto plazo: VENTA (-15%)
├─ Largo plazo: FUERTE COMPRA (+50%, "compra el miedo")
├─ Precio: Bajísimo histórico
└─ ACCIÓN: NO acumular en corto plazo (momentum negativo)
           Esperar a rebote técnico + estabilización
```

### Caso 2: MSFT en Tendencia Alcista
```
Escenario: Sube 3 meses consecutivos, nuevos máximos
├─ Corto plazo: FUERTE COMPRA (+45%)
├─ Largo plazo: COMPRA (+40%, continuará sólido)
├─ Precio: Máximos, pero vale más ahora que hace 3 meses
└─ ACCIÓN: ACUMULAR 75% en entrada grande
           Precio alto OK porque el valor aumentó también
```

### Caso 3: Meta en Consolidación
```
Escenario: Lateral 2 meses, earnings próximos
├─ Corto plazo: HOLD/VENTA (25%, indeciso)
├─ Largo plazo: COMPRA (+38%, Reels monetización OK)
├─ Precio: Neutral
└─ ACCIÓN: ESPERAR a corto plazo claro
           No acumular hasta que se resuelva volatilidad
```

---

## 6. Señales de "Acción Verdaderamente Valiosa"

Una acción es **verdaderamente valiosa** cuando:

```
✅ CRITERIOS VERDES (Acumular sin importar precio):

1. Largo Plazo = COMPRA + Confianza > 35%
   └─ Fundamentales sólidos, crecimiento verificado

2. Multi-timeframe: 2+ timeframes en COMPRA
   └─ Confluencia de tendencias

3. Sentimiento Contrario:
   ├─ Precio bajo ≠ Valor bajo
   ├─ Fundamentales NO deteriorados
   └─ Solo hay miedo temporal (reddit_sentiment = BEARISH pero earnings OK)

4. Insider Activity = BULLISH (net_buying > 0)
   └─ Directivos comprando = confianza real

5. Valuation Metrics:
   ├─ PEG < 1.5 (crecimiento BARATO)
   ├─ ROE > sector benchmark
   ├─ Deuda/Equity controlada
   └─ Free Cash Flow positivo

Si cumple 4/5 → ACUMULAR sin importar precio
Si cumple 3/5 → ACUMULAR pero escalonado
Si cumple 2/5 → ESPERAR confirmación
Si cumple <2/5 → NO TOCAR
```

---

## 7. Implementación en el Daemon

El daemon alertas ya implementa Opción C:

```
Actual (Opción C):
├─ Threshold 22% para COMPRA
├─ Requiere 2/3 timeframes en BUY
└─ Genera 2-4 alertas/semana

Mejora Propuesta (Opción D - Acumulación):
├─ Ejecutar ambos análisis (corto + largo)
├─ Calcular "confianza combinada"
├─ Generar alertas de ACUMULACIÓN solo si:
│  ├─ Corto COMPRA + Largo COMPRA (ACUMULAR AGRESIVA)
│  ├─ Corto HOLD + Largo COMPRA (ACUMULAR DCA)
│  └─ Insider activity BULLISH (BUY STRENGTH)
└─ Marcar precio actual como "entry level" para referencia
```

---

## Resumen: Cuándo Acumular

| Situación | Acción | Razón |
|-----------|--------|-------|
| **Ambos modos COMPRA** | Acumular 50-75% | Oportunidad real |
| **Largo COMPRA, Corto HOLD** | DCA mensual | Valor confirmado |
| **Largo COMPRA, Corto VENTA** | Esperar rebote | Valor OK, timing malo |
| **Corto COMPRA, Largo VENTA** | NO comprar | Rebote fake |
| **Ambos VENTA** | Vender/Evitar | Sin valor |

**La respuesta a tu pregunta:**
- ✅ **Empieza a acumular cuando LARGO PLAZO = COMPRA** (independientemente del corto plazo)
- ✅ **Acelera la acumulación cuando AMBOS = COMPRA** (máxima convicción)
- ✅ **El precio IMPORTA MENOS si el valor fundamental es real**
- ✅ **Usa escalonamiento** (DCA) para reducir riesgo de timing
