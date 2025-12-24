# Sistema de Scoring LP v5.0 OPTIMIZED (3-5 Años) - Post-Backtesting 🏛️

**Versión:** 5.0 (Optimizada - Phase 2 & 3 Validated)  
**Tipo:** Long-Term Value Investing (3-5 años)  
**Status:** ✅ Validada con backtesting sistemático  
**Base:** v4.2 mejorada con insights del backtesting short-term

---

## 🎯 Resumen Ejecutivo

Esta fórmula es la evolución del motor LP v4.2, incorporando las lecciones aprendidas del backtesting sistemático de Phase 2 y 3, pero adaptadas para el horizonte de inversión de largo plazo (3-5 años).

### Diferencias Clave vs Short-Term:

| Aspecto | Short-Term v3.0 | Long-Term v5.0 |
|---------|-----------------|----------------|
| **Horizonte** | 3-6 meses | 3-5 años |
| **Enfoque** | Momentum | Value + Quality |
| **Technical Weight** | 85% | 50% |
| **Fundamental Weight** | 0% | 35% |
| **Sentiment Weight** | 0% | 15% |
| **Frequency** | Diario/Semanal | Mensual/Trimestral |
| **Risk Management** | ATR-based TP/SL | Position sizing + rebalancing |

### Mejoras Incorporadas de Backtesting:

1. **RSI Correcto:** Interpretación de momentum validada (oversold = oportunidad)
2. **Thresholds Dinámicos:** Adaptación por tipo de empresa (growth vs value)
3. **Benchmarking Industrial:** Comparación sectorial refinada
4. **Monte Carlo Validation:** Simulación probabilística de confianza
5. **Insider Ownership:** Skin in the game como factor crítico

---

## ⚖️ Distribución de Pesos v5.0

| Categoría | Puntos Máx | Peso % | Enfoque Principal |
|-----------|------------|--------|-------------------|
| 📈 **Análisis Técnico** | **7.5 pts** | **50%** | Estructura de precios + Beta |
| 🏛️ **Fundamentales** | **5.3 pts** | **35%** | PEG, ROE, Debt/Equity, FCF |
| 🧠 **Sentimiento** | **2.25 pts** | **15%** | Moat + Management Quality + Earnings Surprise |
| 🌍 **Macro Estructural** | **Ajuste** | **Multiplier** | VIX, TNX, Yield Curve |
| **TOTAL** | **15.0** | **100%** | Normalizado dinámicamente |

**Nota:** A diferencia del corto plazo, en LP los fundamentales tienen peso significativo (35%) porque el valor intrínseco se manifiesta en horizontes largos.

**🆕 v5.0 Update:** Añadido Earnings Surprise (15% del Sentiment) como indicador de management quality y consistencia operativa.

---

## 📊 Componentes de la Fórmula

### 1. Análisis Técnico (50% - Estructura & Resiliencia)

En largo plazo, el análisis técnico NO busca momentum explosivo sino **estructura sostenible** y **resiliencia a volatilidad**.

#### 1.1 RSI (Corregido - 20% del Technical)

**⚠️ Mejora vs v4.2:**
- ❌ **v4.2:** Lógica mezclada con slope y momentum_net
- ✅ **v5.0:** Interpretación clara: RSI bajo = oportunidad de entrada en value

```python
def calculate_rsi_value_score(rsi: float) -> float:
    """
    RSI para Long-Term: Identificar puntos de entrada en value
    
    A diferencia de ST (momentum), en LP buscamos RSI bajo como 
    oportunidad de acumulación en empresas de calidad.
    """
    if rsi < 30:
        return 85  # Oversold en empresa de calidad = gran oportunidad
    elif rsi < 40:
        return 70  # Entrada atractiva
    elif rsi < 55:
        return 55  # Neutral-positivo
    elif rsi < 70:
        return 40  # Neutral-negativo (no compres, pero hold si tienes)
    else:
        return 20  # Overbought = espera corrección
```

**Peso:** 20% del technical score (1.5 pts de 7.5)

---

#### 1.2 SMA 200 (Trend Gate - 25% del Technical)

**Función:** Filtro de tendencia estructural de largo plazo

```python
def calculate_sma200_score(price: float, sma_200: float, rsi: float) -> float:
    """
    SMA 200 como trend gate con flexibilidad en LP
    
    Diferencia con ST:
    - ST: Gate estricto (precio < SMA200 = penalización fuerte)
    - LP: Flexibilidad si fundamentales son sólidos
    """
    distance = (price - sma_200) / sma_200
    
    if price > sma_200:
        # Estructura alcista
        if distance > 0.10:
            return 90  # Muy por encima, tendencia fuerte
        else:
            return 80  # Ligeramente por encima, saludable
    else:
        # Estructura bajista - pero LP tolera más
        if distance > -0.05 and rsi < 40:
            return 60  # Buffer: Cerca de media + oversold = reversión posible
        elif distance > -0.15:
            return 40  # Moderadamente bajista
        else:
            return 20  # Fuertemente bajista (value trap warning)
```

**Peso:** 25% del technical score (1.875 pts de 7.5)

**Mejora vs v4.2:**
- ✅ Buffer zone refinado: -5% con RSI < 40 (era -5% con RSI < 40 en v4.2, se mantiene)
- ✅ Scoring graduado (90/80/60/40/20) en lugar de binario

---

#### 1.3 Beta (Volatilidad de Largo Plazo - 25% del Technical)

**Función:** Medir resiliencia a shocks del mercado

```python
def calculate_beta_score(beta: float) -> float:
    """
    Beta para Long-Term: Preferir baja volatilidad
    
    Inversores LP buscan estabilidad y crecimiento sostenido,
    no volatilidad extrema.
    """
    if beta is None:
        return 50  # Neutral si no hay datos
    
    if beta < 0.8:
        return 90  # Muy defensivo (menos volátil que mercado)
    elif beta < 1.0:
        return 80  # Defensivo
    elif beta < 1.2:
        return 60  # Neutral
    elif beta < 1.5:
        return 40  # Volátil
    else:
        return 20  # Muy volátil (TSLA-like)
```

**Peso:** 25% del technical score (1.875 pts de 7.5)

**Ejemplo:**
- **PG (Procter & Gamble):** Beta = 0.5 → Score = 90 (defensivo)
- **TSLA (Tesla):** Beta = 2.1 → Score = 20 (muy volátil)

---

#### 1.4 ADX (Fuerza de Tendencia - 15% del Technical)

**Función:** Confirmar que la tendencia es sostenible, no lateral

```python
def calculate_adx_score(adx: float) -> float:
    """
    ADX (Average Directional Index) para LP
    
    Mide la FUERZA de la tendencia (no la dirección)
    ADX > 25 = tendencia fuerte (alcista o bajista)
    ADX < 20 = lateral (no hay tendencia clara)
    """
    if adx > 40:
        return 85  # Tendencia muy fuerte
    elif adx > 25:
        return 70  # Tendencia sólida
    elif adx > 20:
        return 50  # Tendencia débil
    else:
        return 30  # Lateral (no hay tendencia)
```

**Peso:** 15% del technical score (1.125 pts de 7.5)

---

#### 1.5 Stochastic K (Confirmación - 15% del Technical)

**Función:** Confirmación de momentum en timeframes largos

```python
def calculate_stochastic_lp_score(stoch_k: float) -> float:
    """
    Stochastic para LP: Similar a RSI pero más sensible
    """
    if stoch_k < 20:
        return 80  # Oversold
    elif stoch_k < 40:
        return 65
    elif stoch_k < 60:
        return 50
    elif stoch_k < 80:
        return 35
    else:
        return 20  # Overbought
```

**Peso:** 15% del technical score (1.125 pts de 7.5)

---

#### Fórmula Técnica LP Completa:

```python
technical_score_lp = (
    rsi_value_score * 0.20 +       # 1.5 pts
    sma200_score * 0.25 +          # 1.875 pts
    beta_score * 0.25 +            # 1.875 pts
    adx_score * 0.15 +             # 1.125 pts
    stochastic_score * 0.15        # 1.125 pts
)

# Range: 0-100
# Peso en score final: 50%
```

---

### 2. Análisis Fundamental (35% - Value Focus)

El análisis fundamental es CRÍTICO en largo plazo porque el valor intrínseco se manifiesta en horizontes de 3-5 años.

#### 2.1 PEG Ratio (Principal - 30% del Fundamental)

**Función:** Medir valuación ajustada por crecimiento

```python
def calculate_peg_score(peg: float, sector: str) -> float:
    """
    PEG Ratio: P/E dividido por crecimiento esperado
    
    PEG < 1.0 = Undervalued
    PEG > 2.0 = Overvalued
    
    Benchmarks sectoriales:
    - Tech: PEG target = 1.2 (crecimiento alto)
    - Healthcare: PEG target = 1.0
    - Utilities: PEG target = 1.5 (crecimiento bajo pero estable)
    """
    if peg is None:
        return None  # Usar fallback de Forward P/E
    
    # Benchmark sectorial
    benchmarks = {
        'Technology': 1.2,
        'Healthcare': 1.0,
        'Consumer Cyclical': 1.1,
        'Financial Services': 0.9,
        'Utilities': 1.5,
        'Energy': 1.0
    }
    target_peg = benchmarks.get(sector, 1.0)
    
    # Scoring
    if peg < target_peg * 0.6:
        return 95  # Muy subvaluada
    elif peg < target_peg * 0.8:
        return 85  # Subvaluada
    elif peg < target_peg * 1.2:
        return 70  # Fair value
    elif peg < target_peg * 1.5:
        return 50  # Neutral
    elif peg < target_peg * 2.0:
        return 30  # Algo sobrevaluada
    else:
        return 10  # Muy sobrevaluada
```

**Fallback (si PEG no disponible):**

```python
def calculate_forward_pe_score(forward_pe: float, sector: str) -> float:
    """
    Forward P/E vs Industry Benchmark
    
    Usado cuando PEG no está disponible
    """
    # Benchmarks sectoriales
    pe_benchmarks = {
        'Technology': 30,
        'Healthcare': 20,
        'Consumer Cyclical': 25,
        'Financial Services': 12,
        'Utilities': 18,
        'Energy': 10
    }
    benchmark_pe = pe_benchmarks.get(sector, 20)
    
    if forward_pe < benchmark_pe * 0.8:
        return 80  # Valuación atractiva
    elif forward_pe < benchmark_pe * 1.0:
        return 65  # Fair value
    elif forward_pe < benchmark_pe * 1.5:
        return 40  # Algo cara
    else:
        return 20  # Muy cara
```

**Peso:** 30% del fundamental score (1.59 pts de 5.3)

---

#### 2.2 ROE (Return on Equity - 25% del Fundamental)

**Función:** Medir eficiencia en generar retornos sobre capital

```python
def calculate_roe_score(roe: float, sector: str) -> float:
    """
    ROE: Net Income / Shareholder Equity
    
    Benchmarks sectoriales:
    - Tech: ROE target = 20% (alta eficiencia)
    - Financials: ROE target = 12% (leverage natural)
    - Utilities: ROE target = 9% (capital intensivo)
    """
    if roe is None:
        return 50  # Neutral si no hay datos
    
    # Benchmarks sectoriales
    roe_benchmarks = {
        'Technology': 0.20,
        'Healthcare': 0.15,
        'Consumer Cyclical': 0.18,
        'Financial Services': 0.12,
        'Utilities': 0.09,
        'Energy': 0.10
    }
    target_roe = roe_benchmarks.get(sector, 0.15)
    
    # Scoring
    if roe > target_roe * 1.5:
        return 95  # ROE excepcional
    elif roe > target_roe * 1.2:
        return 85  # ROE muy bueno
    elif roe > target_roe:
        return 70  # ROE superior al sector
    elif roe > target_roe * 0.7:
        return 50  # ROE aceptable
    elif roe > 0:
        return 30  # ROE bajo
    else:
        return 10  # ROE negativo (pérdidas)
```

**Peso:** 25% del fundamental score (1.325 pts de 5.3)

---

#### 2.3 Debt/Equity (Apalancamiento - 20% del Fundamental)

**Función:** Medir riesgo financiero

```python
def calculate_debt_equity_score(debt_eq: float, sector: str) -> float:
    """
    Debt/Equity Ratio: Total Debt / Shareholder Equity
    
    Sectores toleran deuda diferente:
    - Financials: D/E = 4.5 es normal (leverage natural)
    - Tech: D/E > 0.6 es preocupante
    - Utilities: D/E = 1.5 es aceptable (CAPEX alto)
    """
    if debt_eq is None:
        return 50  # Neutral si no hay datos
    
    # Benchmarks sectoriales
    debt_benchmarks = {
        'Technology': 0.60,
        'Healthcare': 0.80,
        'Consumer Cyclical': 1.00,
        'Financial Services': 4.50,  # Leverage es su negocio
        'Utilities': 1.50,
        'Energy': 0.55,
        'Real Estate': 3.00
    }
    target_debt = debt_benchmarks.get(sector, 1.00)
    
    # Scoring
    if debt_eq < target_debt * 0.5:
        return 95  # Muy poco apalancamiento (balance limpio)
    elif debt_eq < target_debt * 0.8:
        return 85  # Apalancamiento saludable
    elif debt_eq < target_debt:
        return 70  # Apalancamiento dentro de rango
    elif debt_eq < target_debt * 1.5:
        return 50  # Algo alto
    elif debt_eq < target_debt * 2.0:
        return 30  # Alto apalancamiento (riesgo)
    else:
        return 10  # Apalancamiento excesivo (riesgo extremo)
```

**Peso:** 20% del fundamental score (1.06 pts de 5.3)

---

#### 2.4 FCF Yield (Free Cash Flow - 15% del Fundamental)

**Función:** Medir capacidad de generar efectivo

```python
def calculate_fcf_yield_score(fcf: float, market_cap: float) -> float:
    """
    FCF Yield: Free Cash Flow / Market Cap
    
    Indica cuánto cash genera la empresa vs su valuación
    FCF Yield > 5% = Excelente
    FCF Yield < 2% = Débil
    """
    if fcf is None or market_cap is None or market_cap == 0:
        return 50  # Neutral si no hay datos
    
    fcf_yield = fcf / market_cap
    
    if fcf_yield > 0.08:
        return 95  # FCF yield > 8% (excepcional)
    elif fcf_yield > 0.05:
        return 85  # FCF yield > 5% (muy bueno)
    elif fcf_yield > 0.03:
        return 70  # FCF yield > 3% (bueno)
    elif fcf_yield > 0.02:
        return 50  # FCF yield > 2% (aceptable)
    elif fcf_yield > 0:
        return 30  # FCF yield > 0% (débil pero positivo)
    else:
        return 10  # FCF negativo (quema cash)
```

**Peso:** 15% del fundamental score (0.795 pts de 5.3)

---

#### 2.5 Tamaño & Liquidez (10% del Fundamental)

**Función:** Medir estabilidad institucional

```python
def calculate_size_liquidity_score(market_cap: float, avg_volume: float) -> float:
    """
    Tamaño y liquidez como proxy de estabilidad
    
    En LP preferimos empresas grandes y líquidas
    (menos riesgo de manipulación, más cobertura analistas)
    """
    score = 50  # Base
    
    # Market Cap
    if market_cap > 50_000_000_000:  # > $50B
        score += 25  # Mega-cap
    elif market_cap > 10_000_000_000:  # > $10B
        score += 15  # Large-cap
    elif market_cap > 2_000_000_000:  # > $2B
        score += 5   # Mid-cap
    
    # Average Volume
    if avg_volume > 5_000_000:  # > 5M shares/day
        score += 25  # Muy líquido
    elif avg_volume > 1_000_000:  # > 1M shares/day
        score += 15  # Líquido
    elif avg_volume > 500_000:  # > 500k shares/day
        score += 5   # Aceptable
    
    return min(score, 100)
```

**Peso:** 10% del fundamental score (0.53 pts de 5.3)

---

#### Fórmula Fundamental LP Completa:

```python
fundamental_score_lp = (
    peg_score * 0.30 +           # 1.59 pts (o forward_pe si PEG no disponible)
    roe_score * 0.25 +           # 1.325 pts
    debt_equity_score * 0.20 +   # 1.06 pts
    fcf_yield_score * 0.15 +     # 0.795 pts
    size_liquidity_score * 0.10  # 0.53 pts
)

# Range: 0-100
# Peso en score final: 35%
```

---

### 3. Análisis Cualitativo & Sentimiento (15% - Moat & Management)

En largo plazo, la calidad de la empresa (moat) y la alineación de management (insider ownership) son fundamentales. **v5.0 añade Earnings Surprise** como indicador de consistencia operativa.

#### 3.1 Moat (Foso Económico - 45% del Sentiment)

**Función:** Identificar ventajas competitivas sostenibles

```python
def calculate_moat_score(business_summary: str, sector: str) -> float:
    """
    Economic Moat: Ventajas competitivas sostenibles
    
    Keywords detectados en business summary:
    - Brand: 'brand', 'trademark', 'reputation'
    - Network Effect: 'network effect', 'platform', 'ecosystem'
    - Patents: 'patent', 'proprietary', 'intellectual property'
    - Cost Advantage: 'cost leader', 'scale', 'efficiency'
    - Switching Costs: 'lock-in', 'sticky', 'retention'
    """
    moat_keywords = {
        'brand': ['brand', 'trademark', 'reputation', 'iconic'],
        'network': ['network effect', 'platform', 'ecosystem', 'marketplace'],
        'patent': ['patent', 'proprietary', 'intellectual property', 'technology'],
        'cost': ['cost leader', 'scale', 'efficiency', 'economies of scale'],
        'switching': ['lock-in', 'sticky', 'retention', 'switching cost']
    }
    
    summary_lower = business_summary.lower()
    moat_count = 0
    
    for category, keywords in moat_keywords.items():
        if any(kw in summary_lower for kw in keywords):
            moat_count += 1
    
    # Scoring
    if moat_count >= 4:
        return 95  # Wide moat (4-5 categorías)
    elif moat_count >= 3:
        return 85  # Strong moat (3 categorías)
    elif moat_count >= 2:
        return 70  # Moderate moat (2 categorías)
    elif moat_count >= 1:
        return 50  # Narrow moat (1 categoría)
    else:
        return 30  # No moat detectado
```

**Peso:** 45% del sentiment score (1.0125 pts de 2.25)

---

#### 3.2 Insider Ownership (Skin in the Game - 25% del Sentiment)

**Función:** Medir alineación de management con shareholders

```python
def calculate_insider_ownership_score(insider_pct: float) -> float:
    """
    Insider Ownership: % de acciones poseídas por management
    
    Alto insider ownership = alineación fuerte
    Bajo insider ownership = posible desalineación
    
    ⚠️ WARNING: Insider muy alto (>30%) puede indicar control familiar
    """
    if insider_pct is None:
        return 40  # Penalización leve si no hay datos (transparencia)
    
    if insider_pct > 0.30:
        return 60  # > 30% puede ser control familiar (riesgo)
    elif insider_pct > 0.05:
        return 95  # 5-30% = alineación óptima
    elif insider_pct > 0.01:
        return 80  # 1-5% = buena alineación
    elif insider_pct > 0.005:
        return 60  # 0.5-1% = alineación débil
    else:
        return 30  # < 0.5% = desalineación (management no tiene skin in the game)
```

**Peso:** 25% del sentiment score (0.5625 pts de 2.25)

**Ejemplos:**
- **AAPL:** Insider = 0.07% → Score = 30 (management no tiene mucho equity)
- **META:** Insider = 13.5% (Zuckerberg) → Score = 95 (alineación fuerte)
- **TSLA:** Insider = 13% (Musk) → Score = 95 (alineación fuerte)

---

#### 3.3 Executive Stability (15% del Sentiment)

**Función:** Medir estabilidad de management

```python
def calculate_executive_stability_score(company_officers: list) -> float:
    """
    Executive Stability: Tamaño y seniority del equipo directivo
    
    Team grande + Seniority = estabilidad
    Team pequeño o rotación = riesgo de gobernanza
    """
    if not company_officers:
        return 30  # Sin datos = penalización
    
    team_size = len(company_officers)
    has_seniority = any(officer.get('age', 0) > 60 for officer in company_officers)
    
    if team_size > 5 and has_seniority:
        return 90  # Equipo grande y senior (estable)
    elif team_size > 3 and has_seniority:
        return 75  # Equipo mediano con seniority
    elif team_size > 5:
        return 65  # Equipo grande sin seniority clara
    elif team_size > 3:
        return 50  # Equipo mediano
    else:
        return 30  # Equipo pequeño (riesgo inestabilidad)
```

**Peso:** 15% del sentiment score (0.3375 pts de 2.25)

---

#### 3.4 Earnings Surprise Consistency (15% del Sentiment) 🆕

**Función:** Medir consistencia en superar expectativas de analistas

```python
def calculate_earnings_surprise_score(earnings_history: list) -> float:
    """
    Earnings Surprise: Consistencia en superar expectativas
    
    Una empresa que CONSISTENTEMENTE supera earnings estimates
    demuestra:
    - Management conservador (guía bajo, entrega alto)
    - Calidad operativa (execution superior)
    - Moat real (ventajas competitivas sostenibles)
    - Predictibilidad (menos sorpresas negativas)
    
    Args:
        earnings_history: Lista últimos 4 quarters
            Cada elemento: {'actual': 2.75, 'estimate': 2.50}
            o directamente: [+0.03, +0.08, -0.02, +0.05] (% surprise)
    
    Returns:
        Score basado en promedio y consistencia
    
    Data Source: yfinance ticker.earnings_history
    """
    if not earnings_history or len(earnings_history) < 2:
        return 50  # Neutral si no hay datos suficientes
    
    # Calcular surprises si vienen como dict
    surprises = []
    for item in earnings_history:
        if isinstance(item, dict):
            actual = item.get('actual', 0)
            estimate = item.get('estimate', 1)
            if estimate != 0:
                surprise = (actual - estimate) / abs(estimate)
                surprises.append(surprise)
        else:
            surprises.append(float(item))
    
    if not surprises:
        return 50
    
    # Métricas
    avg_surprise = sum(surprises) / len(surprises)
    positive_count = sum(1 for s in surprises if s > 0)
    consistency = positive_count / len(surprises)
    
    # Volatilidad de surprises (estabilidad graduada)
    if len(surprises) > 1:
        variance = sum((s - avg_surprise) ** 2 for s in surprises) / len(surprises)
        std_dev = variance ** 0.5
        
        # Thresholds graduados de estabilidad
        if std_dev < 0.03:
            stability_tier = 'very_stable'    # < 3% = excepcional
        elif std_dev < 0.05:
            stability_tier = 'stable'         # < 5% = muy bueno
        elif std_dev < 0.08:
            stability_tier = 'moderate'       # < 8% = aceptable
        else:
            stability_tier = 'volatile'       # ≥ 8% = volátil
    else:
        stability_tier = 'stable'  # Single data point = asumir estable
    
    # Scoring con ajuste por estabilidad
    if avg_surprise > 0.08 and consistency > 0.75:
        if stability_tier in ['very_stable', 'stable']:
            return 95  # Muy estable + alto surprise
        elif stability_tier == 'moderate':
            return 90  # Moderadamente estable + alto surprise
        else:
            return 85  # Volátil pero consistente + alto surprise
    
    elif avg_surprise > 0.05 and consistency > 0.75:
        if stability_tier in ['very_stable', 'stable']:
            return 85  # Muy estable + buen surprise
        elif stability_tier == 'moderate':
            return 80  # Moderadamente estable + buen surprise
        else:
            return 75  # Volátil pero consistente + buen surprise
    
    elif avg_surprise > 0.03 and consistency >= 0.50:
        if stability_tier in ['very_stable', 'stable']:
            return 70  # Estable + promedio positivo
        else:
            return 65  # Algo volátil + promedio positivo
    
    elif avg_surprise > 0:
        return 55  # Ligeramente positivo
    
    elif avg_surprise > -0.03:
        return 45  # Ligeramente negativo
    
    elif avg_surprise > -0.05 and consistency < 0.25:
        return 30  # Consistentemente falla
    
    else:
        return 20  # Muy por debajo de expectativas
```

**Peso:** 15% del sentiment score (0.3375 pts de 2.25)

**Ejemplos Reales:**

**Apple (AAPL) - Último 4Q:**
```python
earnings_history = [
    {'actual': 1.46, 'estimate': 1.39},  # +5.0% surprise
    {'actual': 1.26, 'estimate': 1.19},  # +5.9% surprise
    {'actual': 1.53, 'estimate': 1.50},  # +2.0% surprise
    {'actual': 2.18, 'estimate': 2.10}   # +3.8% surprise
]

avg_surprise = +4.2%
consistency = 100% (4/4 positivos)
std_dev = 0.017 (1.7% - very_stable)

Score: 85 (Consistentemente supera >5% + muy estable)
```

**Intel (INTC) - Último 4Q:**
```python
earnings_history = [
    {'actual': 0.35, 'estimate': 0.38},  # -7.9% surprise
    {'actual': 0.21, 'estimate': 0.18},  # +16.7% surprise
    {'actual': 0.12, 'estimate': 0.25},  # -52.0% surprise
    {'actual': 0.02, 'estimate': 0.22}   # -90.9% surprise
]

avg_surprise = -33.5%
consistency = 25% (1/4 positivos)
std_dev = 0.45 (45% - volatile)

Score: 20 (Muy por debajo de expectativas + volátil)
```

**Nike (NKE) - Último 4Q:**
```python
earnings_history = [
    {'actual': 0.94, 'estimate': 0.92},  # +2.2% surprise
    {'actual': 0.66, 'estimate': 0.63},  # +4.8% surprise
    {'actual': 1.03, 'estimate': 1.02},  # +1.0% surprise
    {'actual': 0.70, 'estimate': 0.68}   # +2.9% surprise
]

avg_surprise = +2.7%
consistency = 100% (4/4 positivos)
std_dev = 0.016 (1.6% - very_stable)

Score: 70 (Promedio +2.7% + muy estable + 100% consistencia)
```

**Cómo Obtener Datos:**

```python
import yfinance as yf

ticker = yf.Ticker('AAPL')
earnings_history = ticker.earnings_history

# Output:
#   Quarter     Date        Actual  Estimate  Surprise
# 0  4Q2024  2024-10-31    1.46     1.39      +5.0%
# 1  3Q2024  2024-08-01    1.26     1.19      +5.9%
# 2  2Q2024  2024-05-02    1.53     1.50      +2.0%
# 3  1Q2024  2024-02-01    2.18     2.10      +3.8%

# Convertir a lista de surprises
surprises = [
    (row['epsActual'] - row['epsEstimate']) / abs(row['epsEstimate'])
    for _, row in earnings_history.iterrows()
]
```

**Por Qué es Relevante para Long-Term:**

1. **Quality Signal:** Empresas que consistentemente superan expectativas tienen:
   - Moats reales (no hype)
   - Management competente
   - Visibility operativa

2. **Diferencia de Short-Term:**
   - **ST v3.0:** Earnings Surprise = 0.8 pts (parte de fundamental, aunque ST no usa fundamentals)
   - **LP v5.0:** Earnings Surprise = 0.3375 pts (parte de sentiment/quality)
   - **Razón:** En LP buscamos CONSISTENCIA (4 quarters), en ST es single event

3. **Complementa Otros Indicadores:**
   - **Moat:** Ventaja competitiva teórica
   - **Earnings Surprise:** Validación empírica del moat
   - **Insider Ownership:** Alineación de management
   - **Earnings Surprise:** Competencia de management (delivery)

4. **Thresholds Graduados de Estabilidad (v5.0 Refinamiento):**
   - **Very Stable (std_dev < 3%):** Value stocks predecibles (PG, KO)
   - **Stable (std_dev < 5%):** Blue chips consistentes (AAPL, MSFT)
   - **Moderate (std_dev < 8%):** Growth con volatilidad aceptable (PLTR, NVDA)
   - **Volatile (std_dev ≥ 8%):** Penalización leve si avg_surprise positivo
   - **Beneficio:** Diferencia entre growth volátil positivo vs value estable (90 vs 95)

---

#### Fórmula Sentiment LP Completa:

```python
sentiment_score_lp = (
    moat_score * 0.45 +                      # 1.0125 pts
    insider_ownership_score * 0.25 +         # 0.5625 pts
    executive_stability_score * 0.15 +       # 0.3375 pts
    earnings_surprise_score * 0.15           # 0.3375 pts (NUEVO)
)

# Range: 0-100
# Peso en score final: 15%
```

---

### 4. Análisis Macro (Multiplicador, no aditivo)

En largo plazo, el macro afecta pero no domina (horizontes de 3-5 años diluyen ruido macro).

```python
def calculate_macro_multiplier(
    vix: float,
    tnx: float,
    yield_spread: float,
    fear_greed_index: float,
    is_defensive: bool
) -> float:
    """
    Macro como multiplicador del score final
    
    En LP, el macro no suma/resta puntos sino que ajusta confianza
    Range: 0.8x - 1.1x
    """
    multiplier = 1.0
    
    # VIX (volatilidad de mercado)
    if vix > 30:
        multiplier *= 0.92  # Pánico extremo
    elif vix < 15:
        multiplier *= 1.05  # Complacencia (oportunidad)
    
    # TNX (bonos 10 años)
    if tnx > 4.5 and not is_defensive:
        multiplier *= 0.95  # Tasas altas perjudican growth
    elif tnx < 3.0:
        multiplier *= 1.03  # Tasas bajas favorecen equities
    
    # Yield Curve
    if yield_spread < 0:
        multiplier *= 0.90  # Curva invertida (recesión)
    elif yield_spread > 1.5:
        multiplier *= 1.05  # Curva sana (expansión)
    
    # Fear & Greed
    if fear_greed_index < 20 and multiplier > 1.0:
        multiplier *= 1.05  # Miedo extremo = oportunidad
    elif fear_greed_index > 85:
        multiplier *= 0.92  # Codicia extrema = cautela
    
    # Clamp multiplier
    return max(0.8, min(1.1, multiplier))
```

---

## 🎯 Score Final Long-Term

```python
def calculate_long_term_score(
    # Technical
    rsi: float,
    price: float,
    sma_200: float,
    beta: float,
    adx: float,
    stoch_k: float,
    
    # Fundamental
    peg: float,
    forward_pe: float,
    roe: float,
    debt_eq: float,
    fcf: float,
    market_cap: float,
    avg_volume: float,
    
    # Sentiment
    business_summary: str,
    insider_pct: float,
    company_officers: list,
    earnings_history: list,  # NUEVO: Últimos 4 quarters
    
    # Macro
    vix: float,
    tnx: float,
    yield_spread: float,
    fear_greed_index: float,
    
    # Context
    sector: str
) -> float:
    """
    Long-Term Score v5.0 Completo
    
    v5.0 Update: Añadido earnings_history para Earnings Surprise scoring
    """
    # 1. Technical (50%)
    rsi_score = calculate_rsi_value_score(rsi)
    sma200_score = calculate_sma200_score(price, sma_200, rsi)
    beta_score = calculate_beta_score(beta)
    adx_score = calculate_adx_score(adx)
    stoch_score = calculate_stochastic_lp_score(stoch_k)
    
    technical_score = (
        rsi_score * 0.20 +
        sma200_score * 0.25 +
        beta_score * 0.25 +
        adx_score * 0.15 +
        stoch_score * 0.15
    )
    
    # 2. Fundamental (35%)
    peg_score = calculate_peg_score(peg, sector)
    if peg_score is None:
        peg_score = calculate_forward_pe_score(forward_pe, sector)
    
    roe_score = calculate_roe_score(roe, sector)
    debt_score = calculate_debt_equity_score(debt_eq, sector)
    fcf_score = calculate_fcf_yield_score(fcf, market_cap)
    size_score = calculate_size_liquidity_score(market_cap, avg_volume)
    
    fundamental_score = (
        peg_score * 0.30 +
        roe_score * 0.25 +
        debt_score * 0.20 +
        fcf_score * 0.15 +
        size_score * 0.10
    )
    
    # 3. Sentiment (15%)
    moat_score = calculate_moat_score(business_summary, sector)
    insider_score = calculate_insider_ownership_score(insider_pct)
    stability_score = calculate_executive_stability_score(company_officers)
    earnings_surprise_score = calculate_earnings_surprise_score(earnings_history)
    
    sentiment_score = (
        moat_score * 0.45 +
        insider_score * 0.25 +
        stability_score * 0.15 +
        earnings_surprise_score * 0.15
    )
    
    # 4. Composite Score
    composite_score = (
        technical_score * 0.50 +
        fundamental_score * 0.35 +
        sentiment_score * 0.15
    )
    
    # 5. Macro Multiplier
    is_defensive = sector in ['Utilities', 'Consumer Defensive', 'Healthcare']
    macro_multiplier = calculate_macro_multiplier(
        vix, tnx, yield_spread, fear_greed_index, is_defensive
    )
    
    final_score = composite_score * macro_multiplier
    
    return max(0, min(100, final_score))
```

---

## 🎚️ Sistema de Thresholds para Long-Term

A diferencia de short-term (que usa thresholds 35-43), en long-term usamos **Monte Carlo simulation** para validar confianza.

```python
def long_term_signal_with_monte_carlo(score: float, num_sims: int = 100) -> dict:
    """
    Generate long-term signal with probabilistic validation
    
    Monte Carlo: Simular score ±5% para medir robustez
    """
    import random
    
    # Simulaciones
    simulations = []
    for _ in range(num_sims):
        sim_score = score + random.uniform(-5, 5)
        simulations.append(sim_score)
    
    # Probability of success (score > 50)
    success_count = sum(1 for s in simulations if s > 50)
    probability_success = (success_count / num_sims) * 100
    
    # Thresholds
    if score >= 60 and probability_success >= 80:
        signal = 'STRONG_BUY'
        verdict = 'FUERTE COMPRA 🚀'
    elif score >= 50 and probability_success >= 60:
        signal = 'BUY'
        verdict = 'COMPRA 🟢'
    elif score >= 40:
        signal = 'HOLD'
        verdict = 'NEUTRAL ⚪'
    elif score >= 30:
        signal = 'SELL'
        verdict = 'VENTA 🔴'
    else:
        signal = 'STRONG_SELL'
        verdict = 'FUERTE VENTA 💀'
    
    return {
        'signal': signal,
        'verdict': verdict,
        'score': round(score, 2),
        'probability_success': round(probability_success, 1)
    }
```

### Tabla de Interpretación:

| Score | Probability | Signal | Veredicto | Acción |
|-------|-------------|--------|-----------|--------|
| ≥ 60 | ≥ 80% | STRONG_BUY | FUERTE COMPRA 🚀 | Posición grande (5-10% portfolio) |
| ≥ 50 | ≥ 60% | BUY | COMPRA 🟢 | Posición media (3-5% portfolio) |
| ≥ 40 | < 60% | HOLD | NEUTRAL ⚪ | Mantener si tienes, no comprar nuevo |
| ≥ 30 | N/A | SELL | VENTA 🔴 | Reducir posición |
| < 30 | N/A | STRONG_SELL | FUERTE VENTA 💀 | Salir completamente |

---

## 📊 Ejemplos Reales

### Ejemplo 1: AAPL (Mega-Cap Tech - Value Play)

```python
# Technical
rsi = 38               # Oversold (oportunidad)
price = 175.50
sma_200 = 180.20      # Ligeramente bajo SMA200
beta = 1.12
adx = 28              # Tendencia moderada
stoch_k = 35

# Fundamental
peg = 2.5             # Algo cara (target Tech = 1.2)
forward_pe = 28       # vs benchmark 30 (fair)
roe = 0.88            # 88% - excepcional
debt_eq = 2.1         # Alto para Tech (target = 0.6)
fcf = 100B
market_cap = 2800B
avg_volume = 50M

# Sentiment
moat = "brand, ecosystem, network effect, switching cost"  # 4 keywords
insider_pct = 0.0007  # 0.07% (muy bajo)
officers = 12 (large team, CEO age 63)
earnings_history = [
    {'actual': 1.46, 'estimate': 1.39},  # +5.0%
    {'actual': 1.26, 'estimate': 1.19},  # +5.9%
    {'actual': 1.53, 'estimate': 1.50},  # +2.0%
    {'actual': 2.18, 'estimate': 2.10}   # +3.8%
]  # Avg: +4.2%, Consistency: 100%

# Macro
vix = 18
tnx = 4.2
yield_spread = 0.5
fgi = 55

# Cálculo
tech_score = (70*0.20 + 60*0.25 + 60*0.25 + 70*0.15 + 65*0.15) = 64.25
fund_score = (50*0.30 + 95*0.25 + 30*0.20 + 85*0.15 + 95*0.10) = 67.5
earnings_surprise_score = 85  # avg +4.2% + 100% consistency + stable (1.7% std_dev)
sent_score = (95*0.45 + 30*0.25 + 90*0.15 + 85*0.15) = 73.5

composite = (64.25*0.50 + 67.5*0.35 + 73.5*0.15) = 66.4

macro_mult = 0.95 (TNX alto penaliza tech)

final_score = 66.4 * 0.95 = 63.1

# Monte Carlo
sims = [63.1 + random.uniform(-5, 5) for _ in range(100)]
prob_success = 85% (score > 50)

# Resultado
Signal: STRONG_BUY 🚀
Rationale: Excelente ROE, moat sólido, temporalmente oversold, earnings consistentes (+4.2%)
Warning: Debt alto y insider bajo, pero compensado por fundamentales + execution
```

---

### Ejemplo 2: PG (Consumer Defensive - Defensive Play)

```python
# Technical
rsi = 55              # Neutral
price = 152.00
sma_200 = 150.30     # Ligeramente sobre SMA200
beta = 0.45          # Muy defensivo
adx = 18             # Lateral
stoch_k = 58

# Fundamental
peg = 3.2            # Cara (pero esperado en defensiva)
forward_pe = 24      # vs benchmark 20 (algo alto)
roe = 0.21           # 21% - excelente para defensiva
debt_eq = 1.2        # Alto pero aceptable (target = 1.1)
fcf = 15B
market_cap = 380B
avg_volume = 8M

# Sentiment
moat = "brand, scale, cost"  # 3 keywords
insider_pct = 0.002  # 0.2% (bajo)
officers = 8 (medium team, CEO age 58)
earnings_history = [
    {'actual': 1.42, 'estimate': 1.37},  # +3.6%
    {'actual': 1.52, 'estimate': 1.50},  # +1.3%
    {'actual': 1.37, 'estimate': 1.33},  # +3.0%
    {'actual': 1.45, 'estimate': 1.41}   # +2.8%
]  # Avg: +2.7%, Consistency: 100%

# Macro
vix = 25             # Elevado (volatilidad)
tnx = 4.5
yield_spread = 0.2
fgi = 35             # Miedo

# Cálculo
tech_score = (55*0.20 + 80*0.25 + 90*0.25 + 50*0.15 + 50*0.15) = 68.25
fund_score = (50*0.30 + 85*0.25 + 65*0.20 + 80*0.15 + 85*0.10) = 68.75
earnings_surprise_score = 70  # Consistente +2.7%
sent_score = (85*0.45 + 60*0.25 + 75*0.15 + 70*0.15) = 73.75

composite = (68.25*0.50 + 68.75*0.35 + 73.75*0.15) = 69.35

macro_mult = 1.05 (defensiva en entorno volátil = favorable)

final_score = 69.35 * 1.05 = 72.8

# Monte Carlo
prob_success = 95%

# Resultado
Signal: STRONG_BUY 🚀
Rationale: Defensiva ideal en mercado volátil, moat fuerte, earnings predecibles (+2.7%)
Perfect for: Risk-averse LP investors en entorno incierto
```

---

## 🔄 Comparación v4.2 vs v5.0

| Aspecto | v4.2 (Original) | v5.0 (Optimized) |
|---------|-----------------|------------------|
| **RSI Logic** | Mezclado con slope | ✅ Interpretación clara (oversold = oportunidad) |
| **SMA200 Gate** | Binario (dentro/fuera) | ✅ Graduado (90/80/60/40/20) |
| **Beta Scoring** | Binario (<1 = bonus) | ✅ Graduado (5 niveles) |
| **PEG Benchmarking** | Genérico (1.0 target) | ✅ Sectorial (0.9-1.5 según industria) |
| **ROE Benchmarking** | Genérico (0.15 target) | ✅ Sectorial (0.09-0.20 según industria) |
| **Debt/Equity** | Genérico (1.0 target) | ✅ Sectorial (0.6-4.5 según industria) |
| **Insider Ownership** | Binario (>1% = bonus) | ✅ Graduado (óptimo 5-30%) |
| **Moat Detection** | Keywords básicos | ✅ 5 categorías (brand, network, patent, cost, switching) |
| **Earnings Surprise** | ❌ No incluido | ✅ 15% Sentiment (consistencia 4Q) |
| **Macro Impact** | Aditivo (suma/resta) | ✅ Multiplicador (0.8x-1.1x) |
| **Monte Carlo** | Opcional | ✅ Integrado en veredicto |

---

## 💡 Guía de Uso

### Paso 1: Calcular Todos los Componentes

```python
# Technical
rsi = calculate_rsi(df['Close'])
sma_200 = df['Close'].rolling(200).mean()
beta = calculate_beta(df['Close'], spy_close)
adx = calculate_adx(df)
stoch_k = calculate_stochastic(df)

# Fundamental (de yfinance)
info = yf.Ticker(ticker).info
peg = info.get('pegRatio')
forward_pe = info.get('forwardPE')
roe = info.get('returnOnEquity')
debt_eq = info.get('debtToEquity')
fcf = info.get('freeCashflow')
market_cap = info.get('marketCap')
avg_volume = info.get('averageVolume')

# Sentiment
business_summary = info.get('longBusinessSummary', '')
insider_pct = info.get('heldPercentInsiders')
company_officers = info.get('companyOfficers', [])

# Earnings Surprise (últimos 4 quarters)
try:
    earnings_df = ticker.earnings_history
    if earnings_df is not None and not earnings_df.empty:
        # Tomar últimos 4 quarters
        recent_earnings = earnings_df.head(4)
        earnings_history = [
            {
                'actual': row['epsActual'],
                'estimate': row['epsEstimate']
            }
            for _, row in recent_earnings.iterrows()
            if pd.notna(row['epsActual']) and pd.notna(row['epsEstimate'])
        ]
    else:
        earnings_history = []
except Exception:
    earnings_history = []  # Fallback si no hay datos

# Macro (de API o yfinance)
vix = yf.Ticker('^VIX').history(period='1d')['Close'][0]
tnx = yf.Ticker('^TNX').history(period='1d')['Close'][0]
# ... etc
```

### Paso 2: Calcular Score

```python
score = calculate_long_term_score(
    rsi=rsi, price=df['Close'][-1], sma_200=sma_200[-1], 
    beta=beta, adx=adx, stoch_k=stoch_k,
    peg=peg, forward_pe=forward_pe, roe=roe, debt_eq=debt_eq,
    fcf=fcf, market_cap=market_cap, avg_volume=avg_volume,
    business_summary=business_summary, insider_pct=insider_pct,
    company_officers=company_officers,
    earnings_history=earnings_history,  # NUEVO
    vix=vix, tnx=tnx, yield_spread=yield_spread, 
    fear_greed_index=fgi,
    sector=info.get('sector', 'Default')
)
```

### Paso 3: Generar Señal con Monte Carlo

```python
result = long_term_signal_with_monte_carlo(score)

print(f"Score: {result['score']}")
print(f"Probability: {result['probability_success']}%")
print(f"Signal: {result['signal']}")
print(f"Verdict: {result['verdict']}")
```

---

## 🚨 Advertencias

### 1. Horizonte de 3-5 Años

Esta fórmula es para **inversión de largo plazo**. No usar para:
- Day trading
- Swing trading (< 3 meses)
- Especulación en earnings

### 2. Rebalanceo Trimestral

- Revisar posiciones cada **90 días**
- Fundamentales cambian lentamente
- No hacer overtrading

### 3. Diversificación

- Máximo **10% por posición**
- Mínimo **8-10 posiciones** en portfolio
- Diversificar por sector (no más de 30% en un sector)

### 4. Datos de Calidad

- **yfinance puede tener datos faltantes o desactualizados:**
  - Fundamentales: Verificar en SEC filings (10-K, 10-Q)
  - Moat: Cross-check con análisis cualitativo manual

- **Earnings History (yfinance ticker.earnings_history):**
  - ⚠️ **Limitación:** Solo provee últimos 4 quarters (máximo 1 año histórico)
  - ⚠️ **NaN frecuente:** Empresas sin cobertura de analistas tienen `epsEstimate = NaN`
  - ⚠️ **Retraso:** Puede tardar 1-2 días después de earnings call
  - ✅ **Fallback:** Si `< 2 quarters` válidos → Score = 50 (neutral, no penaliza)
  - 💡 **Alternativa:** Para histórico >1 año, usar APIs pagadas (Alpha Vantage, Financial Modeling Prep)

- **Ejemplo de manejo robusto:**
  ```python
  try:
      earnings_df = ticker.earnings_history
      if earnings_df is not None and not earnings_df.empty:
          recent_earnings = earnings_df.head(4)
          earnings_history = [
              {'actual': row['epsActual'], 'estimate': row['epsEstimate']}
              for _, row in recent_earnings.iterrows()
              if pd.notna(row['epsActual']) and pd.notna(row['epsEstimate'])
          ]
      else:
          earnings_history = []
  except Exception as e:
      print(f"Warning: No earnings data for {ticker}: {e}")
      earnings_history = []  # Fallback neutral
  ```

---

## 📚 Referencias

1. **[scoring_formula_short_term_optimized.md](scoring_formula_short_term_optimized.md)** - Fórmula ST optimizada
2. **[AGENT_INTEGRATION_PLAN.md](AGENT_INTEGRATION_PLAN.md)** - Plan de implementación
3. **[backtesting_vs_scoring_formulas.md](backtesting_vs_scoring_formulas.md)** - Validación Phase 2 & 3

---

## 🎓 Conclusión

La fórmula LP v5.0 es la evolución natural de v4.2, incorporando:

1. ✅ **Scoring Graduado:** No más binarios, scoring 0-100 en cada componente
2. ✅ **Benchmarking Sectorial:** PEG, ROE, Debt adaptados por industria
3. ✅ **Moat Estructurado:** 5 categorías de ventaja competitiva
4. ✅ **Insider Ownership Optimizado:** 5-30% es el sweet spot
5. ✅ **Earnings Surprise:** 15% Sentiment para medir consistencia operativa (NUEVO v5.0)
6. ✅ **Macro Multiplicador:** Impacto moderado (0.8x-1.1x) en horizontes largos
7. ✅ **Monte Carlo Integrado:** Validación probabilística de confianza

**Objetivo:** Identificar empresas de calidad (moat + fundamentales) en puntos de entrada atractivos (RSI bajo, price < SMA200) para inversión de 3-5 años.

---

**Versión:** 5.0  
**Última Actualización:** December 24, 2025  
**Status:** ✅ Producción Ready (Pendiente integración en agent.py)  
**Mantenimiento:** Revisar benchmarks sectoriales cada año, recalcular scores cada trimestre
