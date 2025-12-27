# Fórmula de Scoring: Corto Plazo (3-6 Meses) v2.4 ⭐ (Flexibilidad)

El motor v2.3 sofisticación el análisis táctico mediante personalización sectorial, métricas de flujo de caja libre (FCF), historial de sorpresas en beneficios y filtros de correlación de mercado.

## ⚖️ Distribución de Pesos v2.3

| Categoría | Puntos Máx | Enfoque Principal |
|-----------|------------|-------------------|
| 📈 **Técnico (Multiframe)** | **6.0 pts** | Momentum Daily + **Tendencia Weekly (ADX)** |
| 🌍 **Macro & Sectorial** | **4.0 pts** | Spreads, VIX e **Impacto Sectorial TNX** |
| 📉 **Fundamentales (Cash)** | **2.3 pts** | PEG + **FCF Yield + Earnings Surprises** |
| 🧠 **Cualitativo** | **2.0 pts** | Sentiment Cuantitativo (>0.6) |

---

## 🏗️ Análisis Técnico Multiframe
Para garantizar que el momentum táctico tenga respaldo estructural:
1. **RSI & Divergencias**: Calculados en gráfico **Daily** (marcos de 14 y 20 días).
2. **ADX Weekly**: La fuerza de tendencia se valida en gráfico **Semanal**. Solo se otorgan bonos de tendencia si la estructura mayor es sólida (ADX-W > 25).

---

## 🏛️ Ajuste Dinámico por Sector (GICS)
El sistema reconoce que no todos los sectores reaccionan igual a las tasas:
- **Sectores Sensibles (Tech/Cyclical)**: Si el bono a 10 años (**TNX**) supera el **4.0%**, la exigencia de confianza sube un **+3%** total.
- **Sectores Defensivos (Utilities/Staples)**: Ignoran la penalización inflacionaria de TNX, permitiendo veredictos positivos incluso en entornos de tasas altas.

---

## 📊 Earnings Surprises & FCF Yield (Simetría)
Refuerzo fundamental para el corto plazo (3-6 meses) con balance de riesgo:
1. **Earnings Surprise** (±0.3 pts):
   - **Bono**: Si el promedio de sorpresas (4Q) es **> 5%**.
   - **Penalización**: Si el promedio de sorpresas (4Q) es **< -5%**.
2. **FCF Yield** (±0.2 pts):
   - **Bono**: Si `FCF / Market Cap` es **> 5%**.
   - **Penalización**: Si `FCF / Market Cap` es **< 2%** o negativo.
3. **Valuación Inteligente (v2.4)**:
   - **PEG Fallback**: Uso de **Forward P/E vs Industria** si el PEG no está disponible.
   - **Bono de Valor**: Si el P/E es < 80% del benchmark sectorial.

---

## 🔗 Filtro de Correlación de Mercado (SPY)
Identifica si el movimiento es propio del activo o un arrastre del índice:
- **Condición**: Correlación de 60 días con **SPY > 0.8**.
- **Impacto**: Multiplicador de **x0.9** al macro score (señal diluida).
- **Advertencia**: Notificación de "Alta correlación de mercado".

---

## 📚 Ejemplos de Referencia (Benchmarks Diversificados)
Para una calibración equilibrada fuera del sector tecnológico:
- **NVDA (Tech)**: Momentum extremo y sorpresas masivas.
- **XOM (Energy)**: Valoración por FCF y baja correlación con tech.
- **PG (Staples)**: Comportamiento defensivo (inmune a TNX > 4.0%).
- **JPM (Financials)**: Sensibilidad a la curva de tipos y correlación SPY.

---

## 📈 Normalización Dinámica del Max Score

A diferencia del análisis tradicional, el "Máximo Puntaje Posible" no es estático. Se ajusta en tiempo real según las restricciones del entorno:

1.  **Ajuste por Gate**: Si la puerta de tendencia está cerrada (Bajo SMA 200), el máximo puntaje técnico posible se reduce proporcionalmente.
2.  **Ajuste por Entorno**: El `multiplier` de ADX/Slope también reduce el máximo teórico.

**Beneficio**: Esto permite que una señal fuerte en un mercado difícil (ej. una compra clara en plena caída) mantenga un nivel de **Confianza %** realista y no se diluya por factores que el activo no puede controlar.

---

## 📚 Ejemplos de Referencia (Benchmarks)

Para facilitar la interpretación de los reportes, el agente ahora incluye un **Resumen Táctico** unificado en todos los modos:

- **TSLA**: Detectó tendencia sólida (ADX 44) -> **COMPRA🟢**
- **NVDA**: Detectó mercado lateral (ADX 10) -> **COMPRA🟢** (con advertencia de debilidad de tendencia).
- **ORCL**: Estructura bajista + lateral -> **NEUTRAL⚪** (con opinión de paciencia estratégica).

---

## 🛠️ Unificación Visual
A partir de la versión 2.0, el bloque de **Resumen Táctico** y **Guía de Benchmarks** aparece tanto en el modo de largo plazo como en el de corto plazo, garantizando que el usuario siempre tenga contexto sobre la fuerza del mercado actual.
