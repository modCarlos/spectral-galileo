# Sistema de Scoring LP v4.2 (3-5 Años) - Flexibilidad Prudente 🏛️

El motor **v4.1** de Largo Plazo está diseñado para inversores institucionales y de convicción, priorizando la **calidad del negocio (Moat)**, la **salud financiera sectorial** y la **resiliencia estadística** mediante simulaciones Monte Carlo.

---

## ⚖️ Distribución de Pesos LP v4.1

| Categoría | Puntos Máx | Enfoque Principal |
|-----------|------------|-------------------|
| 🏭 **Fundamentales (Bench)** | **4.5 pts** | Comparativa vs Sector (PEG, ROE, Deuda) |
| 🛡️ **Cualitativo (Moat & MGMT)**| **4.5 pts** | **NLP de Márgenes**, Insider Ownership, Tenure |
| 🌊 **Análisis Técnico & Beta** | **3.0 pts** | Resiliencia (Beta < 1.0) y **Trend Gate** |
| 🌍 **Macro Estructural** | **3.0 pts** | Inflación, Spreads de Crédito y VIX |
| **TOTAL** | **~15.0** | *Normalizado dinámicamente según datos* |

---

## 🛡️ Innovaciones Institucionales (v4.1)

### 1. Trend Gate Gradual (Optimizado)
A diferencia del modo táctico, en LP el agente utiliza un **Trend Gate**. 
- **Filtro Estándar**: Si el Precio < SMA200 y ADX > 25, se aplica un multiplicador de **0.7x**.
- **Buffer de Flexibilidad**: Si el precio está a menos del **5%** de la SMA200 y el **RSI < 40** (sobreventa), el multiplicador se relaja a **0.9x**, detectando posibles suelos técnicos.

### 2. Benchmarking Industrial (GICS) & Fallback de Valuación
El agente no juzga a todas las empresas por igual.
- **PEG Fallback**: Si el `pegRatio` no está disponible, el sistema compara el **Forward P/E** contra el benchmark del sector (**Tech: 30, Healthcare: 20**, etc.).
- **Bono**: Si el P/E es un **20% inferior** al benchmark sectorial.
- **Penalización**: Si el P/E supera en **50%** al benchmark.
- **Tecnología**: Exige ROE alto (>20%) pero permite deuda moderada.
- **Energía**: Valora intensamente el **FCF Yield** y la eficiencia de capital.
- **Utilidades**: Tolera mayor deuda pero exige estabilidad en márgenes.

### 3. Narrativa de Gestión (NLP & Simetría)
Escaneo profundo de noticias y reportes buscando la tríada de excelencia, ahora con balance de riesgo:
- **Pricing Power**: Capacidad de subir precios sin perder clientes.
- **Efficiency**: Menciones de expansión de márgenes operativos.
- **Insider Alignment** (±0.5 pts): 
  - **Bono**: Si los directivos poseen **> 1%** de la compañía.
  - **Penalización**: Si la propiedad es **< 0.5%** (Falta de alineación).
- **Executive Tenure** (±0.5 pts):
  - **Bono**: Estabilidad alta (Tenure > 5 años).
  - **Penalización**: Inestabilidad detectada (Tenure < 2 años o alta rotación).

---

## 🎲 Veredicto Probabilístico (Monte Carlo)
El veredicto final no depende de un solo cálculo, sino de **100 simulaciones**.
- **Lógica**: Se varía el score final un ±5% aleatoriamente para simular incertidumbre de mercado.
- **Criterio de Éxito**: Se calcula cuántas veces el score resultante supera el umbral de compra (**25% de confianza**).
- **Exigencia**: Para un veredicto de **FUERTE COMPRA**, no basta con un score alto; se requiere una **probabilidad de éxito > 80%**.

---

## 📚 Ejemplos de Referencia por Sector (Benchmarks)

Para una calibración equilibrada fuera del ecosistema tecnológico:

| Ticker | Sector | Perfil LP | Comportamiento del Modelo |
|-----------|-----------|------------------|----------------------|
| **AAPL** | Tech | Foso masivo + ROE | **Fuerte Compra** (si Monte Carlo > 80%) |
| **XOM** | Energy | FCF alto + Commodity | **Neutral** si Trend Gate detecta bajista (pese a FCF) |
| **PG** | Staples | Defensivo estable | **Compra** (Inmune a volatilidad de tasas TNX) |
| **JPM** | Financials| Beta bajo + Ciclo | **Venta** si hay deterioro en curva de tipos o deuda |

---

## 🎯 Umbrales de Confianza Unificados

Para garantizar coherencia con el motor de corto plazo, los umbrales se han sincronizado:

| Veredicto | Confianza Mínima | Requisito Extra (LP) |
|-----------|------------------|----------------------|
| **FUERTE COMPRA 🚀** | **≥ 45%** | Monte Carlo > 80% |
| **COMPRA 🟢** | **≥ 25%** | Estructura no bajista |
| **NEUTRAL ⚪** | **5% a 25%** | Consonancia fundamental |
| **VENTA 🔴** | **< 5%** | Debilidad estructural |
| **FUERTE VENTA 💀** | **< -10%** | Deterioro Moat/Fundamental |

---

> [!IMPORTANT]
> **Normalización Dinámica**: El sistema calcula el `max_score` teórico en cada ejecución basándose solo en los datos que yFinance pudo obtener. Si falta el FCF o el PEG, el sistema no te penaliza injustamente; simplemente reduce el máximo posible para que la **Confianza (%)** sea siempre honesta.
