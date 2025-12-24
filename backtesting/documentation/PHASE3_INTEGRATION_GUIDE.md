# 🔧 PHASE 3: Guía de Integración Rápida

**Objetivo:** Conectar Risk Management + Parameter Optimization al backtest existente.

---

## 1️⃣ OPCIÓN A: Risk Management Integration

### Paso 1: Agregar Atributos de Tracking de Posiciones

En `agent_backtester.py`, en el método `__init__`, agregar:

```python
def __init__(self, ...):
    # ... existing code ...
    self.open_positions = {}  # NEW: Track open trades
    self.position_stops = {}   # NEW: Store SL/TP per position
```

### Paso 2: Modificar la Ejecución de Trades

En el método de ejecución (probablemente `run()` o `execute_trades()`), modificar:

**ANTES (Phase 2):**
```python
if signal == 1:  # Buy signal
    shares = (cash * allocation) / current_price
    self.portfolio.buy(ticker, shares, current_price)
```

**DESPUÉS (Phase 3):**
```python
if signal == 1:  # Buy signal
    # Calculate volatility
    volatility = self._calculate_volatility(ticker)
    atr = self._calculate_atr(ticker)
    
    # Dynamic position sizing with risk management
    position_size = self._calculate_position_size(
        entry_price=current_price,
        volatility=volatility,
        atr=atr,
        max_risk_pct=0.02,  # 2% risk per trade
        account_size=self.portfolio.initial_cash
    )
    
    # Calculate stop loss and take profit
    stop_loss = self._get_stop_loss_price(
        entry_price=current_price,
        atr=atr,
        volatility=volatility,
        ticker=ticker
    )
    
    take_profit = self._get_take_profit_price(
        entry_price=current_price,
        ticker=ticker,
        volatility=volatility
    )
    
    # Execute trade with risk management
    self.portfolio.buy(ticker, position_size, current_price)
    
    # Track position with SL/TP
    self.open_positions[ticker] = {
        'entry_price': current_price,
        'shares': position_size,
        'entry_date': date,
    }
    self.position_stops[ticker] = {
        'stop_loss': stop_loss,
        'take_profit': take_profit,
    }
```

### Paso 3: Agregar Chequeo Diario de SL/TP

En el mismo loop diario, DESPUÉS de actualizar precios:

```python
# Check existing positions for SL/TP hits
for ticker in list(self.open_positions.keys()):
    current_price = self.market_data.get_price(ticker, date)
    
    if ticker in self.position_stops:
        stop_loss = self.position_stops[ticker]['stop_loss']
        take_profit = self.position_stops[ticker]['take_profit']
        
        # Check stop loss first (priority)
        should_exit_sl, reason_sl = self._check_stop_loss(
            ticker, current_price, stop_loss
        )
        if should_exit_sl:
            self.portfolio.sell(ticker, current_price)
            del self.open_positions[ticker]
            del self.position_stops[ticker]
            print(f"[SL] {ticker} {reason_sl}")
            continue
        
        # Check take profit
        should_exit_tp, reason_tp = self._check_take_profit(
            ticker, current_price, take_profit
        )
        if should_exit_tp:
            self.portfolio.sell(ticker, current_price)
            del self.open_positions[ticker]
            del self.position_stops[ticker]
            print(f"[TP] {ticker} {reason_tp}")
```

### Paso 4: Calcular Métricas de Risk Management

Al final de `run()`:

```python
# Calculate risk-adjusted metrics
max_dd, dd_date = self._calculate_max_drawdown()
calmar = self._calculate_calmar_ratio(
    returns_annual=self.portfolio.total_return
)

print(f"Max Drawdown: {max_dd:.2f}%")
print(f"Calmar Ratio: {calmar:.2f}")
```

---

## 2️⃣ OPCIÓN D: Parameter Optimization Integration

### Paso 1: Preparar parameter_optimizer.py

Asegurarse que `parameter_optimizer.py` importe `agent_backtester.py`:

```python
from agent_backtester import AgentBacktester

class ParameterOptimizer:
    def __init__(self, strategy_name="phase3_optimization", results_dir="backtest_results"):
        self.strategy_name = strategy_name
        self.results_dir = results_dir
        # NEW: Import backtester
        self.backtester = AgentBacktester()
```

### Paso 2: Reemplazar Placeholder _evaluate_parameters()

**ANTES (Placeholder):**
```python
def _evaluate_parameters(self, params, ticker):
    """Placeholder - returns synthetic metrics"""
    return {
        'return': np.random.uniform(0.01, 0.05),
        'sharpe': np.random.uniform(0.8, 1.5),
        'max_dd': np.random.uniform(5, 12)
    }
```

**DESPUÉS (Real Backtest):**
```python
def _evaluate_parameters(self, params, ticker):
    """Run actual backtest with given parameters"""
    buy_thresh = params['buy_threshold']
    sell_thresh = params['sell_threshold']
    
    # Create backtester with optimized parameters
    bt = AgentBacktester(
        buy_threshold=buy_thresh,
        sell_threshold=sell_thresh
    )
    
    # Run backtest
    results = bt.run(
        tickers=[ticker],
        start_date='2024-06-26',
        end_date='2025-12-23'
    )
    
    # Extract metrics
    return {
        'return': results['total_return'],
        'sharpe': results['sharpe_ratio'],
        'max_dd': results['max_drawdown'],
        'trades': results['total_trades']
    }
```

### Paso 3: Ejecutar Grid Search

```python
optimizer = ParameterOptimizer(strategy_name="phase3_search")

# Grid search by category
category_params = {
    'ultra_conservative': ['META', 'AMZN'],
    'conservative': ['MSFT', 'NVDA'],
    'aggressive': ['PLTR', 'BABA', 'TSLA'],
    'normal': ['AAPL']
}

best_params = optimizer.grid_search_by_category(category_params)

# Results look like:
# {
#     'ultra_conservative': {'buy_threshold': 28, 'sell_threshold': 72, 'return': 3.2},
#     'conservative': {'buy_threshold': 38, 'sell_threshold': 62, 'return': 2.9},
#     'aggressive': {'buy_threshold': 45, 'sell_threshold': 55, 'return': 3.8},
#     'normal': {'buy_threshold': 40, 'sell_threshold': 60, 'return': 3.1}
# }

# Save results
optimizer.save_optimization_results(best_params, 'phase3_grid_search.json')
```

### Paso 4: Validar con Walk-Forward Test

```python
# Validate that optimized parameters are robust
wf_results = optimizer.walk_forward_test(
    start_date='2024-06-26',
    end_date='2025-12-23',
    optimization_window=60,
    step_size=10,
    ticker='AAPL'
)

# Check robustness
in_sample_returns = [r['in_sample_return'] for r in wf_results]
out_sample_returns = [r['out_sample_return'] for r in wf_results]

print(f"In-Sample Avg Return: {np.mean(in_sample_returns):.2%}")
print(f"Out-Sample Avg Return: {np.mean(out_sample_returns):.2%}")
print(f"Robustness: {np.mean(out_sample_returns) / np.mean(in_sample_returns):.2%}")
```

---

## 3️⃣ WORKFLOW COMPLETO: A + D Juntos

### Script de Integración Completa

```python
#!/usr/bin/env python3
"""
PHASE 3: Full Integration of Risk Management + Parameter Optimization
"""

from agent_backtester import AgentBacktester
from parameter_optimizer import ParameterOptimizer
import json

def phase3_integration():
    """Complete Phase 3 workflow"""
    
    print("=" * 60)
    print("PHASE 3: Risk Management + Parameter Optimization")
    print("=" * 60)
    
    # STEP 1: Define categories
    categories = {
        'ultra_conservative': ['META', 'AMZN'],
        'conservative': ['MSFT', 'NVDA'],
        'aggressive': ['PLTR', 'BABA', 'TSLA'],
        'normal': ['AAPL']
    }
    all_tickers = [t for tickers in categories.values() for t in tickers]
    
    # STEP 2: Run baseline (Phase 2 parameters for comparison)
    print("\n[1/4] Running baseline (Phase 2 parameters)...")
    baseline_bt = AgentBacktester()
    baseline_results = baseline_bt.run(
        tickers=all_tickers,
        start_date='2024-06-26',
        end_date='2025-12-23'
    )
    print(f"  Baseline Return: {baseline_results['total_return']:.2%}")
    print(f"  Baseline Sharpe: {baseline_results['sharpe_ratio']:.2f}")
    print(f"  Baseline Max DD: {baseline_results['max_drawdown']:.2%}")
    
    # STEP 3: Optimize parameters
    print("\n[2/4] Optimizing parameters via grid search...")
    optimizer = ParameterOptimizer(strategy_name="phase3_optimization")
    optimized_params = optimizer.grid_search_by_category(categories)
    
    # Save optimization results
    with open('phase3_optimized_params.json', 'w') as f:
        json.dump(optimized_params, f, indent=2)
    print(f"  Optimized parameters saved to phase3_optimized_params.json")
    
    # STEP 4: Run with optimized parameters
    print("\n[3/4] Running backtest with optimized parameters...")
    optimized_bt = AgentBacktester()
    
    # Apply optimized thresholds to backtester
    for category, params in optimized_params.items():
        # Set category-specific thresholds
        optimized_bt.set_category_thresholds(
            category,
            buy=params['buy_threshold'],
            sell=params['sell_threshold']
        )
    
    optimized_results = optimized_bt.run(
        tickers=all_tickers,
        start_date='2024-06-26',
        end_date='2025-12-23'
    )
    print(f"  Optimized Return: {optimized_results['total_return']:.2%}")
    print(f"  Optimized Sharpe: {optimized_results['sharpe_ratio']:.2f}")
    print(f"  Optimized Max DD: {optimized_results['max_drawdown']:.2%}")
    
    # STEP 5: Validate with walk-forward
    print("\n[4/4] Running walk-forward validation...")
    wf_results = optimizer.walk_forward_test(
        start_date='2024-06-26',
        end_date='2025-12-23',
        optimization_window=60,
        step_size=10,
        ticker='AAPL'  # Representative ticker
    )
    
    # Calculate robustness metrics
    in_sample = [r['in_sample_return'] for r in wf_results]
    out_sample = [r['out_sample_return'] for r in wf_results]
    robustness = sum(1 for oos, is_return in zip(out_sample, in_sample) 
                    if oos >= is_return * 0.8) / len(out_sample)
    
    print(f"  In-Sample Avg: {np.mean(in_sample):.2%}")
    print(f"  Out-of-Sample Avg: {np.mean(out_sample):.2%}")
    print(f"  Robustness Score: {robustness:.1%}")
    
    # RESULTS COMPARISON
    print("\n" + "=" * 60)
    print("RESULTS COMPARISON")
    print("=" * 60)
    
    print(f"\n{'Metric':<20} {'Phase 2':<15} {'Phase 3':<15} {'Improvement':<15}")
    print("-" * 60)
    
    metrics = [
        ('Total Return', 'total_return'),
        ('Sharpe Ratio', 'sharpe_ratio'),
        ('Max Drawdown', 'max_drawdown'),
    ]
    
    for metric_name, metric_key in metrics:
        baseline = baseline_results[metric_key]
        optimized = optimized_results[metric_key]
        
        if 'drawdown' in metric_key:
            improvement = (baseline - optimized) / abs(baseline) * 100
            print(f"{metric_name:<20} {baseline:>13.2%} {optimized:>13.2%} {improvement:>13.1f}%")
        else:
            improvement = (optimized - baseline) / abs(baseline) * 100
            print(f"{metric_name:<20} {baseline:>13.2%} {optimized:>13.2%} {improvement:>13.1f}%")
    
    print("\n" + "=" * 60)
    print("✅ PHASE 3 INTEGRATION COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    phase3_integration()
```

---

## 4️⃣ Pasos de Integración (Orden Recomendado)

### ✅ Paso 1: Validar Código (15 min)
```bash
python -m py_compile agent_backtester.py
python -m py_compile parameter_optimizer.py
```

### ✅ Paso 2: Test Risk Management en 1 Ticker (30 min)
```python
bt = AgentBacktester()
results = bt.run(tickers=['AAPL'], start_date='2024-06-26', end_date='2025-12-23')
# Should show SL/TP hits in logs
```

### ✅ Paso 3: Grid Search en 1 Categoría (1-2 horas)
```python
optimizer = ParameterOptimizer()
results = optimizer.grid_search_thresholds(
    buy_range=(35, 45, 2),
    sell_range=(55, 65, 2),
    ticker='AAPL'
)
```

### ✅ Paso 4: Walk-Forward en Categoría (2-3 horas)
```python
wf = optimizer.walk_forward_test(
    start_date='2024-06-26',
    end_date='2025-12-23',
    optimization_window=60,
    step_size=10,
    ticker='AAPL'
)
```

### ✅ Paso 5: Full Optimization Todas Categorías (4-6 horas)
```python
results = optimizer.grid_search_by_category({
    'ultra_conservative': ['META', 'AMZN'],
    'conservative': ['MSFT', 'NVDA'],
    'aggressive': ['PLTR', 'BABA', 'TSLA'],
    'normal': ['AAPL']
})
```

### ✅ Paso 6: Validar en 8 Tickers (1-2 horas)
```python
# Run full 8-ticker backtest with optimized parameters
```

---

## 5️⃣ Checklist de Integración

### Risk Management (A)
- [ ] Agregar atributos `open_positions` y `position_stops` a `__init__`
- [ ] Modificar compra: usar `_calculate_position_size()` y `_get_stop_loss_price()`
- [ ] Agregar loop de chequeo de SL/TP
- [ ] Calcular `_calculate_max_drawdown()` y `_calculate_calmar_ratio()` al final
- [ ] Test en AAPL: verificar que SL/TP se cumplen
- [ ] Test en todos 8 tickers: comparar vs Phase 2

### Parameter Optimization (D)
- [ ] Reemplazar `_evaluate_parameters()` placeholder con real backtest
- [ ] Implementar `grid_search_thresholds()` con real metrics
- [ ] Implementar `walk_forward_test()` con real data split
- [ ] Test en AAPL grid search
- [ ] Test walk-forward en AAPL
- [ ] Run grid search en todas categorías
- [ ] Validar robustness de parámetros

---

## 6️⃣ Archivos a Modificar/Crear

| Archivo | Acción | Complejidad |
|---------|--------|------------|
| `agent_backtester.py` | Modificar método `run()` | Media |
| `parameter_optimizer.py` | Reemplazar placeholder | Media |
| `phase3_integration.py` | Crear new (opcional) | Baja |
| `PHASE3_RESULTS.md` | Crear new | Baja |

---

## 7️⃣ Métricas a Reportar

Después de integración, reportar:

```markdown
## Phase 3 Integration Results

### Risk Management Impact (A)
- Max Drawdown Reduction: XX%
- Position Sizing Average: XX shares
- SL Hit Rate: XX%
- TP Hit Rate: XX%

### Parameter Optimization Impact (D)
- Grid Search Best Parameters: XX (buy) / YY (sell)
- Improvement vs Baseline: +XX%
- Walk-Forward Robustness: XX%

### Combined Impact (A + D)
- Total Return: XX% (vs 2.86% Phase 2)
- Sharpe Ratio: XX (vs 1.23 Phase 2)
- Max Drawdown: XX% (vs 8-9% Phase 2)
```

---

## ✅ Summary

Esta guía te permite:

1. **Integrar Risk Management** en 1-2 horas
2. **Integrar Parameter Optimization** en 2-3 horas
3. **Validar todo** en 4-6 horas
4. **Documentar resultados** en Phase 3 report

¿Listo para comenzar la integración? 🚀
