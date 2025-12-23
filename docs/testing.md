# Guía de Testing

Esta guía explica cómo ejecutar y contribuir tests para el proyecto.

## Estructura de Tests

```
tests/
├── __init__.py
├── test_portfolio_manager.py  (11 tests)
├── test_indicators.py         (8 tests)
└── test_macro_analysis.py     (6 tests)
```

**Total: 24 tests** con 100% de éxito ✅

## Ejecutar Tests

### Todos los tests
```bash
python -m pytest tests/ -v
```

### Test específico
```bash
python -m pytest tests/test_portfolio_manager.py -v
```

### Con cobertura
```bash
python -m pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

### Solo tests que fallaron
```bash
python -m pytest tests/ --lf
```

## Módulos Testeados

### 1. Portfolio Manager (11 tests)

**Cobertura**:
- ✅ Load/Save portfolio
- ✅ Add stock (con precio custom)
- ✅ Validaciones (precio negativo, inválido)
- ✅ Remove last/all entries
- ✅ Clear portfolio
- ✅ Get unique tickers
- ✅ Get holdings por ticker

**Ejemplo de Test**:
```python
def test_add_stock_with_price(self):
    msg = portfolio_manager.add_stock("AAPL", "150.00")
    self.assertIn("AAPL", msg)
    self.assertIn("150.00", msg)
    
    portfolio = portfolio_manager.load_portfolio()
    self.assertEqual(len(portfolio), 1)
    self.assertEqual(portfolio[0]['buy_price'], 150.00)
```

### 2. Indicators (8 tests)

**Cobertura**:
- ✅ SMA calculation
- ✅ RSI bounds (0-100)
- ✅ MACD components
- ✅ Bollinger Bands (upper > lower)
- ✅ ATR positivity
- ✅ Stochastic bounds
- ✅ OBV calculation
- ✅ add_all_indicators()

**Ejemplo de Test**:
```python
def test_calculate_rsi(self):
    rsi = indicators.calculate_rsi(self.df, window=14)
    
    # RSI debe estar entre 0 y 100
    valid_rsi = rsi.dropna()
    self.assertTrue((valid_rsi >= 0).all())
    self.assertTrue((valid_rsi <= 100).all())
```

### 3. Macro Analysis (6 tests)

**Cobertura**:
- ✅ Fear & Greed Index extremes
- ✅ FGI range validation (0-100)
- ✅ Macro context con datos válidos
- ✅ Manejo de datos vacíos
- ✅ TNX trend detection
- ✅ FGI labels correctos

**Ejemplo de Test**:
```python
def test_calculate_fear_greed_index_extremes(self):
    # Miedo extremo: alto VIX, bajo RSI
    fear_index = macro_analysis.calculate_fear_greed_index(
        vix_price=40, 
        gspc_rsi=20
    )
    self.assertLess(fear_index, 30)
    
    # Codicia extrema: bajo VIX, alto RSI
    greed_index = macro_analysis.calculate_fear_greed_index(
        vix_price=10, 
        gspc_rsi=80
    )
    self.assertGreater(greed_index, 70)
```

## Configuración de Tests

### Fixtures y Setup

Cada test suite usa `setUp()` para inicializar datos de prueba:

```python
def setUp(self):
    """Setup test environment before each test"""
    self.test_file = "test_portfolio.json"
    portfolio_manager.PORTFOLIO_FILE = self.test_file
    
def tearDown(self):
    """Cleanup after each test"""
    if os.path.exists(self.test_file):
        os.remove(self.test_file)
```

### Datos Sintéticos

Para `test_indicators.py`, se generan datos OHLCV realistas:

```python
def setUp(self):
    dates = pd.date_range('2024-01-01', periods=100)
    np.random.seed(42)  # Reproducibilidad
    
    self.df = pd.DataFrame({
        'Open': 100 + np.random.randn(100).cumsum(),
        'High': 102 + np.random.randn(100).cumsum(),
        # ...
    })
    
    # Asegurar relaciones OHLC válidas
    self.df['High'] = self.df[['Open', 'Close']].max(axis=1) + abs(...)
    self.df['Low'] = self.df[['Open', 'Close']].min(axis=1) - abs(...)
```

## Agregar Nuevos Tests

### Template para Nuevo Test

```python
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import your_module

class TestYourModule(unittest.TestCase):
    
    def setUp(self):
        """Preparar ambiente antes de cada test"""
        pass
    
    def tearDown(self):
        """Limpiar después de cada test"""
        pass
    
    def test_something(self):
        """Test description"""
        result = your_module.function()
        self.assertEqual(result, expected)
    
    def test_edge_case(self):
        """Test edge case"""
        with self.assertRaises(ValueError):
            your_module.function(invalid_input)

if __name__ == '__main__':
    unittest.main()
```

### Convenciones de Naming

- Archivo: `test_<module_name>.py`
- Clase: `Test<ModuleName>`
- Método: `test_<what_it_tests>`
- Docstring: Descripción clara de lo que verifica

## Tests Pendientes

### agent.py (No Testeado)

**Razón**: Requiere integración compleja con yfinance.

**Solución Propuesta**:
1. Mockar `market_data` responses
2. Verificar scoring logic con datos conocidos
3. Validar que el reporte se genera correctamente

**Ejemplo (futuro)**:
```python
from unittest.mock import patch

class TestFinancialAgent(unittest.TestCase):
    
    @patch('market_data.get_ticker_data')
    @patch('market_data.get_historical_data')
    def test_run_analysis(self, mock_hist, mock_ticker):
        # Setup mocks
        mock_hist.return_value = self.sample_df
        
        agent = FinancialAgent("AAPL")
        result = agent.run_analysis()
        
        self.assertIn('strategy', result)
        self.assertIn('verdict', result['strategy'])
```

## CI/CD Integration (Futuro)

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Debugging Tests

### Ver output completo
```bash
python -m pytest tests/ -v -s
```

### Detener en primer fallo
```bash
python -m pytest tests/ -x
```

### Debugger (pdb)
```bash
python -m pytest tests/ --pdb
```

### Ver solo summary
```bash
python -m pytest tests/ -q
```

## Best Practices

1. **Tests independentes**: Cada test debe poder ejecutarse solo
2. **Cleanup**: Usar `tearDown()` para limpiar archivos/estado
3. **Datos sintéticos**: No depender de APIs externas
4. **Descriptivos**: Nombres claros y docstrings
5. **Rápidos**: < 1s por test idealmente
6. **Determinísticos**: Mismo input → mismo output (usar `random.seed()`)

## Métricas de Calidad

- **Cobertura objetivo**: >80%
- **Tiempo ejecución total**: <5s
- **Tasa de éxito**: 100%
- **Flakiness**: 0 tests intermitentes

---

**Última actualización**: Diciembre 2025
**Tests totales**: 24
**Cobertura actual**: ~75% (estimado, sin agent.py)
