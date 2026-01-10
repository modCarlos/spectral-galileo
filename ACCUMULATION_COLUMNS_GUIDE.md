# 📊 Guía de Columnas del Sistema de Análisis de Acumulación

## 🎯 Visión General

El sistema Spectral Galileo ahora implementa **Opción D: Análisis de Acumulación**, que combina:
- **Corto Plazo (60%)**: Timing operativo, momentum de 1-3 meses
- **Largo Plazo (40%)**: Valor fundamental, tesis de 3-5 años

Esto responde a tu pregunta: **"¿En qué momento debo empezar a acumular acciones?"**

---

## 📋 COMANDO 1: Watchlist Scanner (`python main.py -ws`)

Escanea las 37 acciones de tu watchlist combinando ambos análisis de plazo.

### 📊 TABLA 1: Análisis de Corto Plazo (Timing Operativo)

```
Ticker | Precio   | Veredicto    | Confianza | Tendencia
─────────────────────────────────────────────────────────
MSFT   | $425.30  | FUERTE COMPRA| 87%       | 📈 Alcista
ARM    | $142.50  | COMPRA       | 65%       | 📈 Alcista
ORCL   | $138.20  | HOLD         | 55%       | ↔️ Neutral
```

**Columnas:**
| Columna | Significado | Qué Significa |
|---------|-------------|---|
| **Ticker** | Símbolo de la acción | MSFT, ARM, etc. |
| **Precio** | Precio actual de mercado | Se actualiza en tiempo real |
| **Veredicto** | Recomendación de corto plazo | 🟢 FUERTE COMPRA / 🟡 COMPRA / ⚪ HOLD / 🔴 VENTA |
| **Confianza** | Nivel de certeza del algoritmo | 50-100%: Qué tan seguro estoy de esta recomendación |
| **Tendencia** | Dirección técnica actual | 📈 Alcista, ↔️ Neutral, 📉 Bajista |

**Interpretación de Veredictos Corto Plazo:**
- **FUERTE COMPRA (87-100%)**: Señales técnicas muy bullish, momentum positivo claro
- **COMPRA (70-86%)**: Señales técnicas bullish moderadas, vale la pena seguir
- **HOLD (45-69%)**: Neutral, sin urgencia de entrar o salir
- **VENTA (20-44%)**: Señales técnicas bearish, momentum negativo
- **FUERTE VENTA (<20%)**: Señales técnicas muy bearish, evitar

---

### 💰 TABLA 2: Análisis de Largo Plazo (Valor Fundamental)

```
Ticker | Veredicto    | Confianza | PEG  | Valuation OK
────────────────────────────────────────────────────
MSFT   | COMPRA       | 82%       | 1.8  | ✓
ARM    | HOLD         | 58%       | 2.5  | ✗
ORCL   | COMPRA       | 75%       | 1.2  | ✓
```

**Columnas:**
| Columna | Significado | Qué Significa |
|---------|-------------|---|
| **Ticker** | Símbolo de la acción | MSFT, ARM, etc. |
| **Veredicto** | Recomendación de largo plazo | 🟢 COMPRA / ⚪ HOLD / 🔴 VENTA |
| **Confianza** | Nivel de certeza fundamentales | % de confianza en análisis de fundamentales |
| **PEG** | Relación Precio/Crecimiento | **< 1.0**: Muy barato ✅ \| **1.0-2.0**: Justo 🟡 \| **> 2.0**: Caro ❌ |
| **Valuation OK** | ¿Está barato?** | ✓ Sí (PEG < 2.0) / ✗ No (PEG ≥ 2.0) |

**Interpretación de PEG Ratio:**
```
PEG < 1.0   = 🟢 Excelente valor (crece rápido, está barato)
PEG 1.0-1.5 = 🟡 Buen valor (justo precio)
PEG 1.5-2.0 = 🟡 Valor aceptable (algo caro pero justificado)
PEG > 2.0   = 🔴 Sobrevalorado (muy caro relativo a crecimiento)
```

---

### 🎯 TABLA 3: Recomendación de Acumulación (✨ LA MAS IMPORTANTE ✨)

```
Ticker | AccumRating | CombConf | Short/Long | Acción           | Tamaño
─────────────────────────────────────────────────────────────────────────
MSFT   | 85%         | 84%      | 87% / 82%  | ACUMULAR AGRESIVA| 100%
ARM    | 62%         | 64%      | 65% / 58%  | DCA              | 50%
ORCL   | 56%         | 61%      | 55% / 75%  | MANTENER/ESPERAR | 25%
BABA   | 35%         | 38%      | 42% / 28%  | NO COMPRAR       | 0%
```

**Columnas:**
| Columna | Significado | Cálculo | Interpretación |
|---------|-------------|---------|---|
| **Ticker** | Símbolo | - | MSFT, ARM, etc. |
| **AccumRating** | Calidad para acumular | 40% Largo Conf + 30% Fundamentales + 20% Multi-timeframe + 10% Insider | **80-100%**: Excelente para acumular \| **60-79%**: Bueno \| **40-59%**: Neutral \| **<40%**: Evitar |
| **CombConf** | Confianza Combinada | 60% × Corto + 40% × Largo | Consenso ponderado entre timing e valor |
| **Short/Long** | Verdicts individuales | Corto% / Largo% | Ejemplo: 87% (corto bullish) / 82% (largo bullish) |
| **Acción** | Qué hacer | Matriz de decisión | Ver tabla de acciones abajo |
| **Tamaño** | Posición sugerida | % de capital | 0%, 25%, 50%, 100% |

**Matriz de Decisiones de Acumulación:**
```
Corto Plazo | Largo Plazo | Acción                  | Tamaño | Prioridad | Razonamiento
────────────┼─────────────┼─────────────────────────┼────────┼───────────┼──────────────
COMPRA      | COMPRA      | ACUMULAR AGRESIVA       | 100%   | ⭐⭐⭐⭐⭐ | Mejor: Valor + Momentum
COMPRA      | HOLD        | DCA (ACUMULAR GRADUAL)  | 50%    | ⭐⭐⭐⭐  | Valor ok, timing débil
HOLD        | COMPRA      | DCA (ACUMULAR GRADUAL)  | 50%    | ⭐⭐⭐⭐  | Valor excelente, esperar rebote
HOLD        | HOLD        | MANTENER/ESPERAR       | 25%    | ⭐⭐      | Sin urgencia
COMPRA      | VENTA       | ESPERAR (rebote largo)  | 25%    | ⭐⭐⭐    | Timing bueno pero valor dudoso
VENTA       | COMPRA      | ESPERAR (corrección)    | 0%     | ⭐        | Valor bueno, timing malo
VENTA       | VENTA       | NO COMPRAR/EVITAR       | 0%     | ⭐        | Peor: Sin valor + sin momentum
```

---

## 📋 COMANDO 2: Análisis Individual de Ticker (`python main.py MSFT`)

Análisis profundo de una sola acción con comparativa corto vs largo plazo.

### 📊 TABLA 1: Análisis Comparativo

```
Métrica      | Corto Plazo     | Largo Plazo
─────────────┼─────────────────┼──────────────
Veredicto    | FUERTE COMPRA   | COMPRA
Confianza    | 87%             | 82%
Timeframe    | 1-3 meses       | 3-5 años
Enfoque      | Momentum/Timing | Fundamentales/Valor
```

**Interpretación:**
- Compara las señales de corto vs largo plazo
- Busca **consenso**: Si ambos dicen COMPRA → muy bullish
- Si dicen lo opuesto → oportunidad de acumular en correcciones

---

### 🎯 TABLA 2: Métricas de Acumulación

```
Métrica                    | Valor
───────────────────────────┼──────
Accumulation Rating        | 85%
Confianza Combinada        | 84%
Long Term Confidence (40%) | 82%
Fundamental Strength (30%) | 88%
Timeframe Alignment (20%)  | 75%
Insider Strength (10%)     | 65%
```

**Explicación de cada métrica:**

| Métrica | Peso | Rango | Significado |
|---------|------|-------|---|
| **Long Term Confidence** | 40% | 0-100% | Confianza en el análisis fundamental (PEG, ratios, crecimiento, etc.) |
| **Fundamental Strength** | 30% | 0-100% | Qué tan buenos son los números: ROE, deuda, márgenes, crecimiento |
| **Timeframe Alignment** | 20% | 0-100% | ¿Está la acción en tendencia alcista en TODOS los timeframes? |
| **Insider Strength** | 10% | 0-100% | ¿Los insiders están comprando la acción? Señal bullish fuerte |

**Fórmula:**
```
AccumRating = (40% × LongTermConf) + (30% × FundamentalStr) + (20% × TimeframeAlign) + (10% × InsiderStr)
```

---

### 💡 TABLA 3: Recomendación de Acumulación

```
ACUMULAR AGRESIVA
Tamaño de Posición: 100%
Razonamiento: Valor excelente (PEG=1.2) + Momentum positivo
             en corto plazo. Consenso bullish claro.
```

**Acciones Posibles:**

| Acción | Significado | Cuándo | Capital |
|--------|-------------|--------|---------|
| **ACUMULAR AGRESIVA** | Compra máxima prioritaria | Cuando ambos análisis dan COMPRA | 100% |
| **DCA** | Compra gradual (Dollar Cost Averaging) | Valor ok, timing dudoso O timing ok, valor dudoso | 50% |
| **MANTENER/ESPERAR** | No hacer nada ahora | Neutral, sin señal clara | 0-25% |
| **ESPERAR** | Esperar a mejor precio | Valor bueno pero momentum negativo | 0-25% |
| **NO COMPRAR** | Evitar completamente | Sin valor + Sin momentum | 0% |

---

## 🧮 Ejemplos Prácticos

### Ejemplo 1: MSFT - Acción clara
```
Corto Plazo:  87% FUERTE COMPRA (momentum excelente)
Largo Plazo:  82% COMPRA (PEG=1.8, valor excelente)

AccumRating:  85%
CombConf:     84% (60% × 87% + 40% × 82%)

DECISIÓN: 🟢 ACUMULAR AGRESIVA (100%)
RAZONEM: "Ambos análisis dan COMPRA. Valor + Momentum = Oportunidad excelente"
```

### Ejemplo 2: ORCL - Conflicto
```
Corto Plazo:  55% HOLD (momentum neutral/débil)
Largo Plazo:  75% COMPRA (PEG=1.2, valor excelente)

AccumRating:  62%
CombConf:     61% (60% × 55% + 40% × 75%)

DECISIÓN: 🟡 DCA - ACUMULAR GRADUAL (50%)
RAZONEM: "Valor fundamental excelente pero timing no es óptimo.
         Estrategia: Entrar gradualmente en rebotes bajistas"
```

### Ejemplo 3: ARM - Timing débil
```
Corto Plazo:  65% COMPRA (momentum ok)
Largo Plazo:  58% HOLD (PEG=2.5, algo caro)

AccumRating:  58%
CombConf:     63% (60% × 65% + 40% × 58%)

DECISIÓN: 🟡 DCA - ACUMULAR GRADUAL (50%)
RAZONEM: "Timing es ok pero fundamentales no dan certeza.
         Esperar más datos antes de posición grande"
```

### Ejemplo 4: BABA - Evitar
```
Corto Plazo:  42% VENTA (momentum negativo)
Largo Plazo:  28% VENTA (PEG=4.2, sobrevalorado, riesgos regulatorios)

AccumRating:  35%
CombConf:     38% (60% × 42% + 40% × 28%)

DECISIÓN: 🔴 NO COMPRAR / EVITAR (0%)
RAZONEM: "Ambos análisis dan VENTA. Esperar a reversión clara"
```

---

## 🎓 Guía de Uso Recomendada

### Para Inversión a Largo Plazo (3-5 años)
1. **Prioridad:** Mirar primero la **Tabla 2 (Largo Plazo)** y la **Columna Valuation OK**
2. **Filtro:** Seleccionar acciones con **PEG < 2.0** ✓
3. **Acción:** Si AccumRating ≥ 70%, usar DCA o ACUMULAR AGRESIVA

### Para Trading de Corto Plazo (1-3 meses)
1. **Prioridad:** Mirar primero la **Tabla 1 (Corto Plazo)** y **Confianza > 75%**
2. **Filtro:** Seleccionar veredictos COMPRA o FUERTE COMPRA
3. **Acción:** Considerar STOP LOSS cercano al precio actual

### Para Acumulación Híbrida (RECOMENDADO)
1. **Paso 1:** Filtrar por AccumRating ≥ 65% (Tabla 3)
2. **Paso 2:** Verificar que CombConf ≥ 60% (consenso entre plazos)
3. **Paso 3:** Usar DCA si Short/Long divergen, AGRESIVA si convergen
4. **Paso 4:** Reaналizar cada semana para ajustar posiciones

---

## 📌 Resumen Rápido

### Las 4 Decisiones Clave

```
┌─────────────────────────────────────────────────────────┐
│   ACUMULAR AGRESIVA (100%)                              │
│   └─> Mejor timing ever: Valor + Momentum              │
│   └─> Entra con máxima posición                         │
├─────────────────────────────────────────────────────────┤
│   DCA - ACUMULAR GRADUAL (50%)                          │
│   └─> Valor ok pero timing dudoso (O inverso)          │
│   └─> Entra gradualmente, aprovecha rebotes            │
├─────────────────────────────────────────────────────────┤
│   MANTENER / ESPERAR (25%)                              │
│   └─> Neutral: Sin urgencia                             │
│   └─> Espera a que se defina la tendencia              │
├─────────────────────────────────────────────────────────┤
│   NO COMPRAR / EVITAR (0%)                              │
│   └─> Peor caso: Sin valor + Sin momentum              │
│   └─> Busca otra oportunidad                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Cómo Ejecutar

```bash
# Escanear TODA tu watchlist con análisis de acumulación
python main.py -ws

# Analizar un ticker individual con comparativa
python main.py MSFT

# Con reporte HTML
python main.py -ws --html
python main.py MSFT --html
```

---

**¿Preguntas sobre las columnas? Ej:**
- "¿Qué significa si AccumRating es 65%?" → Lee la sección "Ejemplo 3"
- "¿Cuándo compro?" → Lee "Matriz de Decisiones" en la Tabla 3
- "¿Cuál es la diferencia entre Corto y Largo?" → Lee "Visión General"
