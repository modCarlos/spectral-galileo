# 🎯 Respuesta: Cuándo Acumular Acciones según el Algoritmo

## Tu Pregunta Original
> *"¿En qué momento debo empezar a acumular acciones según el algoritmo? ¿Es posible hacer una cruza de los algoritmos de corto y largo plazo para saber cuales acciones son verdaderamente valiosas que incluso no importe tanto a que precio comprar si no acumular?"*

---

## La Respuesta (TL;DR)

### ✅ EMPIEZA A ACUMULAR CUANDO:

```
┌─ LARGO PLAZO = COMPRA (confianza ≥ 35%)
│  └─ ROE > benchmark sector
│  └─ Deuda controlada (Deuda/Equity razonable)
│  └─ PEG < 2.0 (crecimiento justificado)
└─ INDEPENDIENTEMENTE del corto plazo

└─ ACELERA acumulación si ADEMÁS: Corto Plazo = COMPRA
```

### 💡 El Concepto Clave

**NO importa tanto el precio si tienes VALOR fundamental.**

```
Escenario A: MSFT a $416 (máximos)
├─ Fundamentales: ROE 35%, PEG 1.2, crecimiento 15%
├─ Largo Plazo: COMPRA (42%)
└─ DECISIÓN: Compra a este precio es mejor que hace 3 meses
            (el valor CRECIÓ, por eso el precio subió)

Escenario B: TSLA a $150 (caída 50%)
├─ Fundamentales: ROE bajando, márgenes presionados
├─ Largo Plazo: VENTA (22%)
└─ DECISIÓN: NO compres en esta caída
            (está barato porque el valor BAJÓ, no por oportunidad)
```

---

## La Arquitectura: Corto + Largo Plazo

### El Algoritmo Ya Lo Tiene Integrado

```python
# En src/spectral_galileo/core/agent.py

class FinancialAgent:
    def __init__(self, ticker, is_short_term=False):
        self.is_short_term = is_short_term
        
    def run_analysis(self):
        # Si is_short_term=True:  Análisis diario/técnico (operativo)
        # Si is_short_term=False: Análisis fundamental (estratégico)
        
        # El analysis devuelve:
        # - verdict: COMPRA/VENTA
        # - confidence: 0-100%
        # - advanced.multi_timeframe: daily/weekly/monthly signals
        # - advanced.insider_trading: net_buying/selling
```

### Cómo Combinarlos

```python
# NUEVO: Análisis Combinado (cruza de estrategias)

short_analysis = FinancialAgent(ticker, is_short_term=True).run_analysis()
long_analysis = FinancialAgent(ticker, is_short_term=False).run_analysis()

# Confianza Combinada = 60% corto + 40% largo
# (porque el timing importa, pero el valor importa MÁS)
combined_confidence = (
    short_analysis['strategy']['confidence'] * 0.6 +
    long_analysis['strategy']['confidence'] * 0.4
)

# Matriz de decisión
if long_analysis['verdict'] == 'COMPRA':
    if short_analysis['verdict'] == 'COMPRA':
        action = "✅ ACUMULAR AGRESIVAMENTE (75-100%)"
    elif short_analysis['verdict'] == 'HOLD':
        action = "🟡 ACUMULAR DCA (25-50% mensual escalonado)"
    else:  # VENTA
        action = "⚠️ ESPERAR rebote técnico, luego acumular"
else:
    if short_analysis['verdict'] == 'COMPRA':
        action = "❌ NO COMPRAR (rebote fake, problemas estructurales)"
    else:
        action = "🔴 EVITAR (todos los indicadores negativos)"
```

---

## Los 5 Componentes que Definen "Verdadero Valor"

### 1️⃣ Largo Plazo Confianza (40% del peso)
```
¿Tiene valor fundamental duradero?

Indicadores clave:
├─ ROE: ¿Retorna bien a accionistas?
│  └─ Benchmark tech: 20% | Benchmark general: 15%
├─ PEG Ratio: ¿Está caro por su crecimiento?
│  └─ PEG < 1.0: Barato | PEG 1.0-1.5: Justo | PEG > 2.0: Caro
├─ Deuda/Equity: ¿Está endeudada?
│  └─ Tech toleran 60-80% | Finanzas toleran 450%+
└─ Free Cash Flow: ¿Genera flujo real?

Ejemplo real:
• MSFT: ROE 35% > Tech 20% ✓ | PEG 1.2 < 1.5 ✓ | FCF positivo ✓
  → LONG PLAZO COMPRA (CONFIANZA 42%)
  
• TSLA: ROE bajando ✗ | Márgenes presionados ✗ | Deuda elevada ✗
  → LONG PLAZO VENTA (CONFIANZA 22%)
```

### 2️⃣ Fortaleza Fundamental (30% del peso)
```
Calificación de 0-100 basada en:
├─ Pros/Cons del análisis
├─ Comparativa con benchmark sector
├─ Trend de métricas (mejorando vs deteriorando)
└─ Riesgo de dilución o restructuración

Escala:
• 75%+: Fundamentales EXCELENTES
• 50-75%: Fundamentales SÓLIDOS
• 25-50%: Fundamentales DÉBILES
• <25%: Fundamentales CRÍTICOS
```

### 3️⃣ Multi-Timeframe Confluencia (20% del peso)
```
¿Alinean daily/weekly/monthly?

3/3 timeframes BUY: MÁXIMA CONVICCIÓN
├─ Daily BUY:   Momentum presente
├─ Weekly BUY:  Tendencia intermedia confirmada
└─ Monthly BUY: Tendencia larga sin reversión

Ejemplo:
• MSFT: Daily BUY + Weekly BUY + Monthly BUY = 3/3 ✓
  → Puedes acumular AGRESIVAMENTE

• WMT: Daily SELL + Weekly BUY + Monthly BUY = 2/3 ✓
  → Es corrección en tendencia alcista
  → Acumula escalonado en la caída
```

### 4️⃣ Insider Activity (10% del peso)
```
¿Directivos están comprando o vendiendo?

BULLISH (net_buying > 0):
├─ Directivos creen en el futuro
├─ Insider buying > selling
└─ Señal positiva de convicción

BEARISH (net_selling > 0):
├─ Directivos están sacando dinero
├─ Insider selling > buying
└─ Bandera roja (aunque puede ser diversificación)

Ejemplo:
• MSFT: Insiders net_buying +$2.3M → Confianza ↑
• TSLA: Insiders net_selling -$15M → Confianza ↓
```

### 5️⃣ Corto Plazo Confianza (para TIMING, no decisión)
```
¿CUÁNDO entrar exactamente?

COMPRA (22%+):  Entra ahora (pequeña dosis)
HOLD (15-25%):  Entra escalonado (DCA mensual)
VENTA (<15%):   Espera a estabilización
FUERTE COMPRA (30%+): Entra GRANDE ahora

Pero si LARGO PLAZO es VENTA:
→ NO entres sin importar qué diga corto plazo
→ Es rebote técnico en acción que sigue cayendo
```

---

## Implementación: 3 Niveles

### NIVEL 1: Uso Manual (Tu Decisión Diaria)
```bash
# Ejecutar el script demo
python3 scripts/accumulation_strategy_demo.py

# Verás 5 ejemplos reales de cómo combinar corto+largo plazo
```

**Matriz de decisión rápida:**
| Corto | Largo | Acción | Posición |
|-------|-------|--------|----------|
| COMPRA | COMPRA | ✅ Acumula AGRESIVA | 75-100% |
| HOLD | COMPRA | 🟡 Acumula DCA | 25-50%/mes |
| VENTA | COMPRA | ⚠️ Espera rebote | 0% (por ahora) |
| COMPRA | VENTA | ❌ No compres | 0% (rebote fake) |
| VENTA | VENTA | 🔴 Evita | 0% |

---

### NIVEL 2: Análisis Semanal
```bash
# Script que escanea watchlist (cuando lo termines)
python3 scripts/accumulation_scanner.py

# Genera: accumulation_scan_YYYYMMDD_HHMMSS.json
# Muestra acciones ordenadas por "Accumulation Rating" (0-100)
# Rating alto = verdaderamente valiosa (precio importa menos)
```

### NIVEL 3: Automación en el Daemon

**Próxima mejora (Opción D):** 
El daemon alertas podría ejecutar AMBOS análisis antes de enviar alertas:

```python
# alerts/daemon.py (próxima versión)

def should_send_accumulation_alert(ticker):
    short = FinancialAgent(ticker, is_short_term=True).run_analysis()
    long = FinancialAgent(ticker, is_short_term=False).run_analysis()
    
    # Solo alerta si LARGO PLAZO es positivo
    # (no queremos alertar sobre rebotes fake)
    
    if long['verdict'] in ['COMPRA', 'FUERTE COMPRA']:
        confidence_combined = ...
        # Envía alerta con recomendación de tamaño de posición
        # "MSFT: ACUMULAR AGRESIVA (75%) - Confianza 68%"
```

---

## Caso de Uso Real: Aplica Esto Ahora

### Con Tu Watchlist Actual (10 tickers)

**Observación del análisis de 08-01-2026:**
```
Todos 10 tickers = NEUTRAL (45.9% confianza promedio)

¿Por qué? Porque estamos en MERCADO LATERAL:
├─ SPY ADX: 11.94 (no hay tendencia)
├─ Fear & Greed: 75.98 (extreme greed, mercado caro)
└─ Ningún ticker muestra COMPRA clara
```

**Estrategia ahora:**
```
✅ LARGO PLAZO COMPRA + CORTO PLAZO NEUTRAL
└─ DCA MENSUAL: Compra 25% mes en cada ticker con Largo COMPRA
   └─ Promedias precio bajo
   └─ Cuando market eventualmente genere señal corto plazo
      → Ya tienes posición acumulada

Espera CONFLUENCIA (2+ timeframes BUY):
└─ Entonces acelera acumulación
```

**Ejemplo:** Si WMT baja 8% (ya sucedió):
- Corto Plazo: VENTA (bajó mucho)
- Largo Plazo: COMPRA (fundamentales OK, dividend stock)
- Acción: Acumula en esta caída (es oportunidad, no trampa)

---

## Resumen Ejecutivo

### Tu Pregunta Reformulada
> "¿Cómo sé si una acción es tan buena que aunque esté cara, seguirá siendo buena inversión?"

### La Respuesta
```
1. Ejecuta análisis LARGO plazo (is_short_term=False)
2. Verifica que COMPRA y confianza > 35%
3. Valida fundamentales (ROE, PEG, Deuda, FCF)
4. ENTONCES empieza a acumular:
   └─ Escalonado si corto plazo es HOLD
   └─ Agresivo si corto plazo es COMPRA
   └─ No toques si largo plazo es VENTA

5. El precio importa MENOS porque tienes CONVICCIÓN en el valor
```

### Acciones "Verdaderamente Valiosas"
Son aquellas donde:
- ✅ Largo Plazo = COMPRA (fundamentales sólidos)
- ✅ Multi-Timeframe ≥ 2/3 en BUY (confluencia)
- ✅ Insider activity = BULLISH (directivos creen)
- ✅ ROE > benchmark + PEG < 2.0 (valoración justa)

**Si cumples 4/5:** ACUMULAR sin importar si está en máximos o depresión - el precio es secundario.

---

## Archivos Relacionados
- [ACCUMULATION_STRATEGY.md](ACCUMULATION_STRATEGY.md) - Guía completa
- [scripts/accumulation_strategy_demo.py](../scripts/accumulation_strategy_demo.py) - Ejecuta para ver ejemplos
- [scripts/accumulation_scanner.py](../scripts/accumulation_scanner.py) - Scanner de oportunidades (en desarrollo)
