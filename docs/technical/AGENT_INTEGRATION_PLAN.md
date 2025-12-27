# Plan de Implementación: Integración de Mejoras del Backtesting al Agent.py

**Autor:** Spectral Galileo  
**Fecha:** December 24, 2025  
**Versión:** 1.0

---

## 📊 Resumen Ejecutivo

### Situación Actual

**Agent.py (Producción):**
- Sistema de scoring basado en documentación (scoring_formula.md y scoring_formula_short_term.md)
- Pesos: Tech variable, Fund 2.3-4.5pts, Macro 3-4pts, Qual 2-4.5pts
- Thresholds dinámicos basados en VIX y TNX
- Sin validación empírica de rendimiento

**Agent_backtester.py (Backtesting):**
- Sistema optimizado mediante 6,656 backtests
- Mejoras validadas: +114% retorno, +71% Sharpe
- Thresholds categorizados y optimizados (35/65 a 43/57)
- RSI correctamente interpretado para momentum

### Gap Crítico Identificado

**❌ Agent.py NO implementa las mejoras validadas del backtesting**

---

## 🔍 Análisis Detallado de Diferencias

### 1. Scoring de Short-Term

#### Agent.py (Actual):
```python
# Momentum compuesto (0-5 puntos)
mom_score = 0
if macd > macd_signal: mom_score += 1.0
if rsi > 50 and slope > 0: mom_score += 1.0
if price > sma_50 > sma_200: mom_score += 2.0
if vol_rel > 1.5 or mfi > 70: mom_score += 1.0

# Normalización centrada en 2.5
momentum_net_cp = (mom_score - 2.5) / 2.5
score += momentum_net_cp * 4.0

# Problema: Interpretación compleja y no validada
```

#### Agent_backtester.py (Optimizado - Phase 2):
```python
# RSI: Interpretación directa de momentum (CRÍTICO)
rsi = tech.get('rsi', 50)
if rsi < 30:
    rsi_score = 80  # Oversold = strong BUY
elif rsi < 40:
    rsi_score = 70
elif rsi < 60:
    rsi_score = 50  # Neutral
elif rsi < 70:
    rsi_score = 30
else:
    rsi_score = 20  # Overbought = strong SELL

# MACD directo
macd_score = 75 if macd == 'Bullish' else 25 if macd == 'Bearish' else 50

# Stochastic
stoch_k = tech.get('stoch_k', 50)
if stoch_k < 20:
    stoch_score = 75  # Oversold
elif stoch_k < 50:
    stoch_score = 55
elif stoch_k < 80:
    stoch_score = 45
else:
    stoch_score = 25  # Overbought

# Combinar con pesos optimizados
tech_score = (rsi_score * 0.50 + macd_score * 0.35 + stoch_score * 0.15)
score_components.append(('technical', tech_score, 0.85))

# Resultado: +74% mejora validada
```

**Diferencia Clave:**
- ❌ Agent.py: RSI > 50 es positivo (confuso)
- ✅ Backtester: RSI < 30 es BUY (correcto momentum)
- **Impacto:** Esta corrección sola generó +74% mejora en Phase 2

---

### 2. Dynamic Thresholds

#### Agent.py (Actual):
```python
# Thresholds basados en VIX y TNX (no validados)
vix_val = macro_res.get('vix', 20)
tnx_val = macro_res.get('tnx', 0)

umbral_base = 15 + (vix_val - 15) * 0.4 + inf_adj
umbral_fuerte = 35 + (vix_val - 15) * 0.6 + inf_adj

if confidence >= umbral_fuerte: verdict = "FUERTE COMPRA 🚀"
elif confidence >= umbral_base: verdict = "COMPRA 🟢"

# Problema: Umbrales dinámicos pero sin categorización por stock
```

#### Agent_backtester.py (Optimizado - Phase 2 & 3):
```python
def _categorize_stock(self, volatility: float, ticker: str = None) -> str:
    """Categorize stock by volatility and characteristics"""
    vol_pct = volatility * 100
    
    # Mega-cap tech
    mega_cap_tech = ['MSFT', 'META', 'NVDA']
    
    if ticker and ticker.upper() in ['META', 'AMZN'] and vol_pct < 35:
        return 'mega_cap_tech_ultra_conservative'
    
    if ticker and ticker.upper() in mega_cap_tech and vol_pct < 35:
        return 'mega_cap_tech'
    
    if vol_pct > 40:
        return 'high_volatility'
    
    return 'normal'

def _dynamic_thresholds_short_term(self, volatility: float, ticker: str = None) -> tuple:
    """Phase 2 optimized thresholds by stock category"""
    category = self._categorize_stock(volatility, ticker)
    
    if category == 'mega_cap_tech_ultra_conservative':
        return 35.0, 65.0  # META, AMZN - prevent whipsaws
    elif category == 'mega_cap_tech':
        return 38.0, 62.0  # MSFT, NVDA
    elif category == 'high_volatility':
        return 43.0, 57.0  # PLTR, BABA
    else:
        return 42.0, 58.0  # Normal

# Validación: 256 grid search backtests
# Resultado: -28% false signals on mega-caps
```

**Diferencia Clave:**
- ❌ Agent.py: Un umbral para todos los stocks
- ✅ Backtester: 4 categorías con umbrales específicos
- **Impacto:** -28% señales falsas en mega-caps, +12% oportunidades en alta volatilidad

---

### 3. Technical Weight Distribution

#### Agent.py (Actual):
```python
# Short-term weights no están claramente definidos
# Usa momentum_pts_cp = 4.0 pero sobre score normalizado complejo
# No hay separación clara entre technical/volatility/fundamental
```

#### Agent_backtester.py (Optimizado):
```python
# SHORT-TERM: Pesos optimizados Phase 2
Technical:     85%  (momentum focus)
Volatility:    15%  (risk adjustment)
Fundamental:   0%   (not relevant for 3-6 months)

# LONG-TERM: Balanced approach
Technical:     50%
Fundamental:   35%
Sentiment:     15%
```

**Diferencia Clave:**
- ❌ Agent.py: Pesos mezclados y complejos
- ✅ Backtester: 85% technical para ST (validado)
- **Impacto:** +51% Sharpe improvement

---

### 4. Risk Management

#### Agent.py (Actual):
```python
# Solo cálculo de stop loss básico
stop_loss = price - (2 * atr)
sell_short = price + (1.5 * atr)

# No hay:
# - Position sizing dinámico
# - Take profit sistemático
# - Daily SL/TP validation
```

#### Agent_backtester.py (Optimizado - Phase 3):
```python
# ATR-based dynamic position sizing
def _calculate_position_size(self, ticker: str, entry_price: float, account_value: float) -> int:
    atr = self._calculate_atr(ticker, periods=14)
    stop_loss_multiplier = 1.5
    
    risk_amount = account_value * self.max_risk_per_trade  # 2% default
    risk_per_share = atr * stop_loss_multiplier
    
    shares = int(risk_amount / risk_per_share)
    
    # Cap at 20% of account
    max_position_value = account_value * 0.20
    max_shares = int(max_position_value / entry_price)
    
    return min(shares, max_shares)

# Stop Loss & Take Profit
stop_loss = entry_price - (atr * 1.5)
take_profit = entry_price + (atr * 3.0)

# Daily validation
for ticker in self.open_positions:
    if current_price <= stop_loss:
        # Execute SL
    elif current_price >= take_profit:
        # Execute TP

# Validación: 52,847 events, 75.8% TP rate, 3.1:1 TP:SL
```

**Diferencia Clave:**
- ❌ Agent.py: Solo niveles sugeridos, sin ejecución
- ✅ Backtester: Sistema completo de RM con 75.8% profitable exits
- **Impacto:** -23% max drawdown, +15% Sharpe

---

## 🎯 Plan de Implementación (4 Fases)

### **FASE 1: Corrección Crítica de RSI (Prioridad ALTA)** 🔴

**Objetivo:** Implementar interpretación correcta de RSI para momentum

**Archivo:** `agent.py`  
**Líneas a modificar:** ~140-180 (sección de análisis técnico ST)

**Cambios:**

```python
# ANTES (agent.py actual):
if rsi > 50 and slope > 0: mom_score += 1.0

# DESPUÉS (implementar lógica backtester):
def _calculate_rsi_momentum_score(self, rsi: float) -> float:
    """
    Phase 2 validated: Direct momentum interpretation
    """
    if rsi < 30:
        return 80  # Oversold = strong BUY opportunity
    elif rsi < 40:
        return 70  # Weak oversold = BUY
    elif rsi < 60:
        return 50  # Neutral
    elif rsi < 70:
        return 30  # Weak overbought = SELL
    else:
        return 20  # Overbought = strong SELL

# En run_analysis(), línea ~140:
rsi = latest['RSI']
rsi_momentum_score = self._calculate_rsi_momentum_score(rsi)

# Usar rsi_momentum_score en lugar de la lógica antigua
```

**Validación:**
- Ejecutar backtest comparativo con agent.py modificado
- Esperar mejora de al menos +50% vs versión actual
- Target: Aproximar 2.86% return de Phase 2

**Esfuerzo:** 2 horas  
**Impacto Esperado:** +50-70% return improvement

---

### **FASE 2: Thresholds Dinámicos por Categoría (Prioridad ALTA)** 🔴

**Objetivo:** Implementar categorización de stocks y thresholds optimizados

**Archivo:** `agent.py`  
**Nuevas funciones a agregar:** ~900-950 (antes de `if __name__`)

**Cambios:**

```python
# Agregar estas funciones al final de la clase FinancialAgent:

def _calculate_volatility(self, periods: int = 20) -> float:
    """Calculate annualized volatility"""
    if len(self.data) < periods:
        return 0.02
    
    close = self.data['Close'].tail(periods).values
    returns = np.diff(close) / close[:-1]
    daily_volatility = np.std(returns)
    annual_volatility = daily_volatility * np.sqrt(252)
    
    return float(annual_volatility)

def _categorize_stock(self, volatility: float, ticker: str = None) -> str:
    """
    Phase 2 optimized: Categorize stock by volatility and characteristics
    
    Returns: 'mega_cap_tech_ultra_conservative', 'mega_cap_tech', 
             'high_volatility', 'normal'
    """
    vol_pct = volatility * 100
    
    mega_cap_tech = ['MSFT', 'META', 'NVDA']
    
    if ticker and ticker.upper() in ['META', 'AMZN'] and vol_pct < 35:
        return 'mega_cap_tech_ultra_conservative'
    
    if ticker and ticker.upper() in mega_cap_tech and vol_pct < 35:
        return 'mega_cap_tech'
    
    if vol_pct > 40:
        return 'high_volatility'
    
    return 'normal'

def _dynamic_thresholds_short_term(self, volatility: float, ticker: str = None) -> tuple:
    """
    Phase 2/3 validated thresholds by stock category
    
    Grid Search results (256 backtests):
    - Ultra-conservative: 35/65 (META, AMZN)
    - Conservative: 38/62 (MSFT, NVDA)
    - Normal: 42/58
    - Aggressive: 43/57 (PLTR, BABA)
    """
    category = self._categorize_stock(volatility, ticker)
    
    if category == 'mega_cap_tech_ultra_conservative':
        return 35.0, 65.0
    elif category == 'mega_cap_tech':
        return 38.0, 62.0
    elif category == 'high_volatility':
        return 43.0, 57.0
    else:
        return 42.0, 58.0

# Modificar la sección de veredicto (línea ~490-520):
if self.is_short_term:
    # Calcular volatilidad
    volatility = self._calculate_volatility()
    
    # Obtener thresholds optimizados
    buy_threshold, sell_threshold = self._dynamic_thresholds_short_term(
        volatility, 
        self.ticker_symbol
    )
    
    # Aplicar thresholds
    if confidence < buy_threshold:
        verdict = "COMPRA 🟢"
    elif confidence > sell_threshold:
        verdict = "VENTA 🔴"
    else:
        verdict = "NEUTRAL ⚪"
    
    # Fuerte compra/venta con margen adicional
    if confidence < (buy_threshold - 10):
        verdict = "FUERTE COMPRA 🚀"
    elif confidence > (sell_threshold + 10):
        verdict = "FUERTE VENTA 💀"
```

**Validación:**
- Probar con META, MSFT, PLTR individualmente
- Verificar que thresholds se aplican correctamente
- Comparar señales con agent_backtester.py

**Esfuerzo:** 3 horas  
**Impacto Esperado:** -25% false signals, +4pp win rate

---

### **FASE 3: Simplificación de Scoring Short-Term (Prioridad MEDIA)** 🟡

**Objetivo:** Alinear pesos con backtesting optimizado (85% Tech, 15% Vol, 0% Fund)

**Archivo:** `agent.py`  
**Líneas a modificar:** ~100-300 (toda la sección de scoring)

**Cambios:**

```python
# Refactorizar scoring para short-term:

if self.is_short_term:
    # TECHNICAL SCORING (85% weight = 8.5 pts de 10 total)
    tech_score = 0
    tech_max = 8.5
    
    # 1. RSI (50% de technical = 4.25 pts)
    rsi_score = self._calculate_rsi_momentum_score(rsi)
    tech_score += (rsi_score / 100) * 4.25
    
    # 2. MACD (35% de technical = 3.0 pts)
    macd_score = 75 if macd > macd_signal else 25 if macd < macd_signal else 50
    tech_score += (macd_score / 100) * 3.0
    
    # 3. Stochastic (15% de technical = 1.25 pts)
    stoch_score = 75 if stoch_k < 20 else 55 if stoch_k < 50 else 45 if stoch_k < 80 else 25
    tech_score += (stoch_score / 100) * 1.25
    
    # VOLATILITY RISK (15% weight = 1.5 pts)
    vol_score = 0
    vol_max = 1.5
    volatility = self._calculate_volatility()
    
    if volatility > 0.08:
        vol_score = 0.6  # 40% of max - very volatile
    elif volatility > 0.05:
        vol_score = 0.9  # 60% of max
    else:
        vol_score = 1.5  # 100% - normal
    
    # FUNDAMENTAL = 0 para short-term (Phase 2 finding)
    # No agregar fundamental scoring
    
    # Total score
    score = tech_score + vol_score
    potential_max = tech_max + vol_max
    
    # Confidence
    confidence = (score / potential_max) * 100
```

**Validación:**
- Backtest comparativo 6 meses
- Comparar Sharpe ratio vs versión actual
- Target: Sharpe > 1.20

**Esfuerzo:** 6 horas  
**Impacto Esperado:** +30% Sharpe improvement

---

### **FASE 4: Integración de Risk Management (Prioridad BAJA)** 🟢

**Objetivo:** Agregar position sizing y RM recommendations

**Archivo:** `agent.py`  
**Nueva sección:** Después de `strategy` en results

**Cambios:**

```python
# Agregar funciones de RM:

def _calculate_atr(self, periods: int = 14) -> float:
    """Calculate Average True Range"""
    if len(self.data) < periods + 1:
        return self.data['Close'].iloc[-1] * 0.02
    
    high = self.data['High'].tail(periods + 1)
    low = self.data['Low'].tail(periods + 1)
    close = self.data['Close'].tail(periods + 1)
    
    tr1 = high.iloc[1:].values - low.iloc[1:].values
    tr2 = np.abs(high.iloc[1:].values - close.iloc[:-1].values)
    tr3 = np.abs(low.iloc[1:].values - close.iloc[:-1].values)
    
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    atr = np.mean(tr)
    
    return float(atr)

def _calculate_position_size(self, entry_price: float, account_value: float, 
                            max_risk_pct: float = 0.02) -> dict:
    """
    Phase 3 validated: ATR-based position sizing
    
    Args:
        entry_price: Expected entry price
        account_value: Total account value
        max_risk_pct: Max risk per trade (default 2%)
    
    Returns:
        dict with shares, position_value, risk_amount
    """
    atr = self._calculate_atr(periods=14)
    stop_loss_multiplier = 1.5
    
    risk_amount = account_value * max_risk_pct
    risk_per_share = atr * stop_loss_multiplier
    
    if risk_per_share <= 0:
        shares = 0
    else:
        shares = int(risk_amount / risk_per_share)
    
    # Cap at 20% of account
    max_position_value = account_value * 0.20
    max_shares = int(max_position_value / entry_price)
    
    shares = min(shares, max_shares)
    position_value = shares * entry_price
    
    return {
        'shares': shares,
        'position_value': position_value,
        'risk_amount': risk_amount,
        'stop_loss': entry_price - (atr * stop_loss_multiplier),
        'take_profit': entry_price + (atr * 3.0),
        'risk_per_share': risk_per_share
    }

# En run_analysis(), agregar a results:
atr = self._calculate_atr()

# Position sizing recommendations
rm_recommendation = self._calculate_position_size(
    entry_price=price,
    account_value=100000  # Default, user adjustable
)

self.analysis_results['risk_management'] = {
    'atr': atr,
    'position_sizing': rm_recommendation,
    'max_risk_per_trade': 0.02,  # 2%
    'max_position_size': 0.20,   # 20%
    'stop_loss_multiplier': 1.5,
    'take_profit_multiplier': 3.0
}
```

**Validación:**
- Verificar que RM recommendations son realistas
- Comparar con Phase 3 resultados (3.1:1 TP:SL)

**Esfuerzo:** 4 horas  
**Impacto Esperado:** Mejor gestión de riesgo, -20% drawdown

---

## 📅 Timeline de Implementación

### Sprint 1 (2 días): Correcciones Críticas
- **Día 1:** Fase 1 - RSI correction (2h) + testing (4h)
- **Día 2:** Fase 2 - Dynamic thresholds (3h) + testing (3h)

### Sprint 2 (3 días): Optimización
- **Día 3-4:** Fase 3 - Scoring simplification (6h) + testing (6h)
- **Día 5:** Fase 4 - Risk Management (4h) + testing (2h)

### Sprint 3 (2 días): Validación Final
- **Día 6:** Backtest completo 1 año con nuevo agent.py
- **Día 7:** Paper trading 30 días + ajustes finales

**Total: 7 días hábiles**

---

## 📊 Métricas de Éxito

### Pre-Implementación (Agent.py actual)
```
Return: ~0.5-1.0% (estimado, no validado)
Sharpe: ~0.3-0.5 (estimado)
Win Rate: ~50% (estimado)
Max Drawdown: Unknown
```

### Post-Fase 1 (RSI fix)
```
Target Return: 2.0-2.5%
Target Sharpe: 0.9-1.1
Target Win Rate: 54-56%
```

### Post-Fase 2 (Dynamic thresholds)
```
Target Return: 2.5-3.0%
Target Sharpe: 1.1-1.3
Target Win Rate: 56-58%
False Signals: -25%
```

### Post-Fase 3 (Scoring optimization)
```
Target Return: 2.8-3.2%
Target Sharpe: 1.25-1.35
Target Win Rate: 56-60%
```

### Post-Fase 4 (Risk Management)
```
Target Return: 3.0-3.5%
Target Sharpe: 1.35-1.50
Target Win Rate: 58-62%
Target Max Drawdown: 6.5-7.5%
```

**Meta Final:** Igualar o superar Phase 3 backtesting results (3.5% return, 1.47 Sharpe, 60% win rate)

---

## 🚨 Riesgos y Mitigaciones

### Riesgo 1: Breaking Changes
**Problema:** Las modificaciones pueden romper funcionalidad existente  
**Mitigación:**
- Crear branch `feature/backtest-integration`
- Tests unitarios para cada fase
- Rollback plan documentado

### Riesgo 2: Overfitting
**Problema:** Parámetros optimizados en backtesting pueden no funcionar en producción  
**Mitigación:**
- Walk-forward validation ya completada (6,400 backtests)
- Paper trading 30 días antes de capital real
- Monitoreo continuo de métricas

### Riesgo 3: Diferencias de Datos
**Problema:** Agent.py usa datos live, backtester usa históricos  
**Mitigación:**
- Validar que yfinance data es consistente
- Comparar señales en tiempo real vs backtest
- Ajustar si hay discrepancias >5%

---

## 🎯 Próximos Pasos Inmediatos

### Acción 1: Backup y Branch
```bash
cd /Users/carlosfuentes/GitHub/spectral-galileo
git checkout -b feature/backtest-integration
cp agent.py agent.py.backup
```

### Acción 2: Implementar Fase 1
- Modificar `agent.py` líneas 140-180
- Agregar función `_calculate_rsi_momentum_score()`
- Ejecutar tests comparativos

### Acción 3: Validación Inmediata
```bash
# Backtest con agent.py modificado
cd backtesting/scripts
python agent_backtester.py --tickers AAPL MSFT META PLTR \
  --start 2024-06-26 --end 2024-12-23 \
  --capital 100000 --short-term
```

### Acción 4: Documentar Cambios
- Crear `AGENT_IMPROVEMENTS_LOG.md`
- Documentar cada cambio con before/after
- Registrar resultados de cada fase

---

## 📚 Referencias

1. **Phase 2 Results:** `backtesting/documentation/PHASE2_RESULTS_SUMMARY.md`
2. **Phase 3 Results:** `backtesting/documentation/PHASE3_RESULTS.md`
3. **Formula Comparison:** `docs/backtesting_vs_scoring_formulas.md`
4. **Agent Backtester:** `backtesting/scripts/agent_backtester.py` (líneas 280-545)
5. **Parameter Optimizer:** `backtesting/scripts/parameter_optimizer.py`

---

## ✅ Checklist de Implementación

### Pre-requisitos
- [ ] Backup de agent.py creado
- [ ] Branch feature/backtest-integration creado
- [ ] Tests unitarios preparados
- [ ] Métricas baseline documentadas

### Fase 1: RSI Correction
- [ ] Función `_calculate_rsi_momentum_score()` agregada
- [ ] Lógica de scoring actualizada
- [ ] Tests passing
- [ ] Backtest comparativo ejecutado
- [ ] Mejora >50% confirmada

### Fase 2: Dynamic Thresholds
- [ ] Función `_categorize_stock()` agregada
- [ ] Función `_dynamic_thresholds_short_term()` agregada
- [ ] Función `_calculate_volatility()` agregada
- [ ] Lógica de veredicto actualizada
- [ ] Tests por ticker (META, MSFT, PLTR)
- [ ] Reducción señales falsas >20% confirmada

### Fase 3: Scoring Simplification
- [ ] Refactor de scoring short-term completo
- [ ] Pesos 85/15/0 implementados
- [ ] Tests de integración passing
- [ ] Sharpe ratio >1.20 confirmado

### Fase 4: Risk Management
- [ ] Función `_calculate_atr()` agregada
- [ ] Función `_calculate_position_size()` agregada
- [ ] Results incluyendo 'risk_management'
- [ ] Reporte actualizado con RM recommendations

### Validación Final
- [ ] Backtest 1 año completo ejecutado
- [ ] Métricas vs Phase 3 comparadas
- [ ] Paper trading 30 días iniciado
- [ ] Documentación actualizada
- [ ] Pull request creado

---

**Status:** LISTO PARA IMPLEMENTACIÓN  
**Próximo Review:** Después de Fase 1 (2 días)  
**Owner:** Developer Team  
**Stakeholders:** Trading Team, Risk Management
