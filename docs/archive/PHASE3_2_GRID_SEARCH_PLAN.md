# Phase 3.2: Grid Search Optimization Plan

## Objetivo
Encontrar los parámetros óptimos mediante búsqueda sistemática sobre diferentes configuraciones.

## Estado de Ajustes Actuales (Phase 3.1b)

### Ajustes Aplicados ✅
1. **Insider Selling Threshold**:
   - Moderate: $1M → $5M
   - Heavy: $5M → $10M
   - Impacto: Neutral (confianza mantenida)

2. **MTF_DISAGREE Penalty**:
   - Penalty: -15% → -10%
   - Boost: +15% → +10%
   - Impacto: Neutral (confianza mantenida)

### Validación
- Test de 5 tickers: confianza promedio cambió -0.1%
- Warnings siguen detectándose pero con menor penalización
- Sistema más balanceado

---

## Parámetros a Optimizar (Phase 3.2)

### 1. Confluence Scoring Weights
**Actual** (15 puntos máx):
```python
mtf_confirmation = {
    'STRONG': 5 pts,
    'MODERATE': 3 pts
}
technical_alignment = 5 pts max
regime_confirmation = 5 pts max
```

**Opciones para grid search**:
```python
mtf_weights = [3, 5, 7]  # STRONG confirmation
technical_weights = [3, 5, 7]  # Technical alignment
regime_weights = [3, 5, 7]  # Regime confirmation
```

### 2. Confidence Adjustment Ranges
**Actual**:
```python
mtf_penalty = 0.90  # -10%
mtf_boost = 1.10    # +10%
insider_penalty = [0.90, 0.95]  # -10% to -5%
insider_boost = [1.03, 1.05, 1.10]  # +3% to +10%
```

**Opciones**:
```python
mtf_penalty_range = [0.85, 0.90, 0.95]  # -15%, -10%, -5%
insider_penalty_range = [0.85, 0.90, 0.95]  # -15%, -10%, -5%
insider_boost_range = [1.05, 1.10, 1.15]  # +5%, +10%, +15%
```

### 3. Verdict Thresholds
**Actual**:
```python
BUY_THRESHOLD = 25%  # confidence >= 25%
NEUTRAL_THRESHOLD = 25%  # confidence < 25%
```

**Opciones**:
```python
buy_thresholds = [20, 25, 30, 35]  # %
```

### 4. Insider Trading Thresholds
**Actual** (ajustado):
```python
moderate_selling = -$5M
heavy_selling = -$10M
moderate_buying = +$1M
strong_buying = +$1M (with 2+ execs)
```

**Opciones**:
```python
moderate_selling = [-3e6, -5e6, -7e6]  # -$3M, -$5M, -$7M
heavy_selling = [-8e6, -10e6, -15e6]  # -$8M, -$10M, -$15M
moderate_buying = [5e5, 1e6, 2e6]  # $500K, $1M, $2M
```

### 5. Reddit Sentiment Weights
**Actual**:
```python
bearish_penalty = 0.85  # -15% if BEARISH + high engagement
```

**Opciones**:
```python
reddit_penalty = [0.85, 0.90, 0.95]  # -15%, -10%, -5%
engagement_threshold = [50, 75, 100]  # min engagement to trigger
```

---

## Grid Search Strategy

### Approach A: Full Grid Search (Exhaustive)
**Pros**: Encuentra óptimo global  
**Cons**: Muy lento (1000s combinaciones)  

**Combinaciones**:
```
mtf_weights (3) × technical_weights (3) × regime_weights (3) 
× mtf_penalty (3) × buy_threshold (4) 
= 324 combinaciones
```

**Tiempo estimado**: ~6 horas (324 combos × 10 min/combo × 62 tickers)

### Approach B: Random Search (Recomendado)
**Pros**: Más rápido, buenos resultados  
**Cons**: No garantiza óptimo global  

**Estrategia**:
- 50 combinaciones aleatorias
- Enfocarse en parámetros más impactantes
- Validar top 10 resultados

**Tiempo estimado**: ~1 hora

### Approach C: Bayesian Optimization
**Pros**: Muy eficiente, convergencia rápida  
**Cons**: Requiere más setup  

**Estrategia**:
- Usar `scikit-optimize` o `optuna`
- 30-50 iteraciones
- Modelo aprende de resultados previos

**Tiempo estimado**: ~45 minutos

---

## Métricas de Evaluación

### 1. Primary Metrics
```python
# Objetivo principal: Maximizar precision en COMPRA
precision_compra = true_positives / (true_positives + false_positives)

# Objetivo secundario: Mantener coverage
coverage = (compra_signals / total_tickers)

# Balanced score
score = precision_compra * 0.7 + coverage * 0.3
```

### 2. Secondary Metrics
- **Win Rate**: % de señales COMPRA que suben
- **Avg Return**: Retorno promedio de señales COMPRA
- **Max Drawdown**: Pérdida máxima
- **False Positive Rate**: COMPRA que bajan
- **False Negative Rate**: NEUTRAL que suben mucho

### 3. Validation Strategy
- **Training set**: Primeros 40 tickers del watchlist
- **Validation set**: Siguientes 12 tickers
- **Test set**: Últimos 10 tickers

---

## Implementation Plan

### Step 1: Setup Grid Search Framework
```python
# grid_search_optimizer.py

from itertools import product
import pandas as pd
import agent

def evaluate_config(config, tickers):
    """Evaluate single configuration"""
    results = []
    
    for ticker in tickers:
        # Temporarily modify agent parameters
        trading_agent = agent.FinancialAgent(ticker, is_short_term=False)
        # Apply config...
        analysis = trading_agent.run_analysis()
        results.append(analysis)
    
    # Calculate metrics
    precision = calculate_precision(results)
    coverage = calculate_coverage(results)
    score = precision * 0.7 + coverage * 0.3
    
    return {
        'config': config,
        'precision': precision,
        'coverage': coverage,
        'score': score,
        'results': results
    }

def grid_search(param_grid, tickers):
    """Run grid search"""
    all_results = []
    
    for config in generate_configs(param_grid):
        result = evaluate_config(config, tickers)
        all_results.append(result)
        print(f"Config {len(all_results)}: score={result['score']:.3f}")
    
    # Sort by score
    all_results.sort(key=lambda x: x['score'], reverse=True)
    return all_results
```

### Step 2: Define Parameter Grid
```python
param_grid = {
    'mtf_strong_weight': [3, 5, 7],
    'mtf_penalty': [0.85, 0.90, 0.95],
    'insider_threshold_moderate': [-3e6, -5e6, -7e6],
    'insider_threshold_heavy': [-8e6, -10e6, -15e6],
    'buy_threshold': [20, 25, 30, 35],
}
```

### Step 3: Run Optimization
```bash
# Random search (recommended)
python grid_search_optimizer.py --method random --n-samples 50

# Full grid search
python grid_search_optimizer.py --method grid

# Bayesian optimization
python grid_search_optimizer.py --method bayesian --n-iter 50
```

### Step 4: Validate Top Configurations
```python
# test_top_configs.py
# Test top 5 configs on validation set
# Compare with baseline
# Select best config
```

### Step 5: Apply Best Configuration
```python
# Update agent.py and insider_trading.py with optimal parameters
# Re-run full backtesting OLD vs NEW
# Document improvements
```

---

## Expected Outcomes

### Success Criteria
- **Precision improvement**: +5-10% vs current
- **Maintained coverage**: 25-35% COMPRA signals
- **Better balance**: Fewer false positives without missing opportunities

### Risk Mitigation
- **Overfitting**: Use separate validation set
- **Computational cost**: Start with random search
- **Interpretability**: Document why optimal params work

---

## Timeline

### Day 1: Setup & Initial Search
- Create grid_search_optimizer.py
- Define parameter grid
- Run random search (50 configs)
- Analyze top 10 results

### Day 2: Refinement & Validation
- Test top 5 configs on validation set
- Compare with baseline
- Fine-tune best config
- Document findings

### Day 3: Application & Testing
- Apply best config to agent.py
- Re-run full backtesting
- Generate comparison report
- Update documentation

---

## Next Steps

1. ✅ **Phase 3.1b Complete**: Threshold adjustments applied
2. 🔄 **Phase 3.2 Start**: Create grid search framework
3. ⏳ **Phase 3.3 Pending**: Category-specific thresholds

**Current Status**: Ready to begin Phase 3.2 implementation
