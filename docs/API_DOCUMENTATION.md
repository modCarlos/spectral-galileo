# Spectral Galileo - API Documentation

**Versión:** 1.0.0  
**Última actualización:** Diciembre 2025  
**Autor:** modCarlos  

## Tabla de Contenidos

1. [Arquitectura General](#arquitectura-general)
2. [FinancialAgent API](#financialagent-api)
3. [Módulos de Datos](#módulos-de-datos)
4. [Generación de Reportes](#generación-de-reportes)
5. [Gestión de Portafolio](#gestión-de-portafolio)
6. [Configuración](#configuración)
7. [Manejo de Errores](#manejo-de-errores)
8. [Ejemplos de Uso](#ejemplos-de-uso)

---

## Arquitectura General

### Dependencias de Módulos

```
┌──────────────────────────────────────────────────┐
│          main.py / CLI Application              │
└──────────────────┬───────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ↓                      ↓
   ┌────────────┐      ┌──────────────────┐
   │  Agent.py  │      │ReportGenerator   │
   │(Scoring)   │      │(HTML Output)     │
   └────────────┘      └──────────────────┘
        │                      │
    ┌───┴──────────────────────┼──────────────────┐
    ↓       ↓          ↓       ↓   ↓              ↓
┌─────────────────────────────────────────────────────┐
│  Data Modules                                       │
│  ├─ market_data.py    (yFinance wrapper)           │
│  ├─ indicators.py     (Análisis técnico)           │
│  ├─ macro_analysis.py (VIX, TNX, Fear&Greed)       │
│  ├─ sentiment_analysis.py (NLP de noticias)        │
│  └─ portfolio_manager.py (Gestión JSON)            │
└─────────────────────────────────────────────────────┘
        │
        ↓
┌──────────────────────────┐
│  External APIs           │
│  ├─ yFinance            │
│  ├─ NewsAPI             │
│  ├─ Federal Reserve API │
│  └─ VIX/Fear&Greed Feeds│
└──────────────────────────┘
```

---

## FinancialAgent API

### Clase: `FinancialAgent`

Orquestador central que coordina análisis técnico, fundamental, macroeconómico y cualitativo.

#### Constructor

```python
from agent import FinancialAgent

agent = FinancialAgent(
    ticker_symbol: str,              # Símbolo bursátil (ej: "AAPL")
    is_short_term: bool = False      # True para CP, False para LP
)
```

**Parámetros:**
- `ticker_symbol` (str): Símbolo bursátil válido (ej: "MSFT", "GOOGL")
- `is_short_term` (bool): 
  - `False` (default): Análisis Largo Plazo (3-5 años) - Motor v4.2
  - `True`: Análisis Corto Plazo (3-6 meses) - Motor v2.4

**Atributos de instancia:**
```python
agent.ticker_symbol      # str: Símbolo
agent.is_short_term      # bool: Horizonte temporal
agent.ticker             # yfinance.Ticker: Objeto de datos
agent.data               # pd.DataFrame: Datos históricos OHLCV
agent.info               # dict: Datos fundamentales
agent.news               # list: Noticias recientes
agent.macro_data         # dict: Contexto macroeconómico
agent.analysis_results   # dict: Resultados del análisis
```

#### Método: `run_analysis()`

```python
result = agent.run_analysis(pre_data: dict = None) -> dict
```

**Parámetros:**
- `pre_data` (dict, opcional): Datos precolectados por DataManager
  - Estructura esperada:
    ```python
    {
        'history': pd.DataFrame,        # OHLCV
        'fundamentals': dict,           # Datos fundamentales
        'news': list,                   # Noticias
        'macro_data': dict              # Contexto macro
    }
    ```

**Returns: Dict con estructura completa**

```python
{
    # Metadatos
    'ticker': str,                           # "AAPL"
    'timestamp': str,                        # ISO 8601
    'price': float,                          # Precio actual
    
    # ========== ANÁLISIS TÉCNICO ==========
    'technical': {
        'rsi': float,                        # RSI(14) 0-100
        'rsi_signal': str,                   # 'overbought'|'oversold'|'neutral'
        'macd': {
            'value': float,
            'signal': float,
            'histogram': float,
            'trend': str                     # 'bullish'|'bearish'|'neutral'
        },
        'adx': float,                        # ADX(14) 0-100
        'sma_20': float,
        'sma_50': float,
        'sma_200': float,
        'price_position': str,               # 'above'|'below'|'near_200'
        'bollinger_bands': {
            'upper': float,
            'middle': float,
            'lower': float
        },
        'volume_profile': {
            'current': float,
            'avg_50': float,
            'ratio': float                   # actual / promedio
        }
    },
    
    # ========== ANÁLISIS FUNDAMENTAL ==========
    'fundamental': {
        'valuation': {
            'trailing_pe': float,
            'forward_pe': float,
            'peg_ratio': float or None,
            'price_to_book': float,
            'price_to_fcf': float
        },
        'quality': {
            'roe': float,                    # Return on Equity
            'roa': float,
            'debt_to_equity': float,
            'current_ratio': float,
            'fcf_yield': float
        },
        'growth': {
            'revenue_growth': float,
            'earnings_growth': float,
            'fcf_growth': float
        },
        'sector': str,                       # "Technology"
        'industry': str,                     # "Consumer Electronics"
        'benchmarks': {                      # vs sector
            'pe_delta': float,               # %
            'roe_delta': float,
            'de_delta': float
        }
    },
    
    # ========== CONTEXTO MACROECONÓMICO ==========
    'macro': {
        'vix': float,                        # Volatilidad S&P 500
        'vix_interpretation': str,           # 'low'|'moderate'|'high'|'extreme'
        'tnx': float,                        # Yield Bono 10Y
        'fed_rate_interpretation': str,      # 'accommodative'|'neutral'|'restrictive'
        'fear_greed': float,                 # 0-100 (0=fear, 100=greed)
        'credit_spread': float,              # bps (High Yield OAS)
        'sp500_rsi': float,                  # Momentum mercado
        'sector_rotation': str               # 'to_defensives'|'neutral'|'to_cyclicals'
    },
    
    # ========== ANÁLISIS CUALITATIVO ==========
    'qualitative': {
        'business_moat': {
            'score': float,                  # 0-10
            'factors': [str],                # ['brand', 'network_effect', 'patents']
            'interpretation': str
        },
        'management': {
            'insider_ownership': float,      # %
            'insider_trading': str,          # 'buying'|'selling'|'neutral'
            'ceo_tenure_years': float,
            'team_stability': str
        },
        'news_sentiment': {
            'sentiment_score': float,        # -1 to 1
            'critical_news': bool,
            'regulatory_risk': bool,
            'keywords': [str]
        }
    },
    
    # ========== ESTRATEGIA & VEREDICTO ==========
    'strategy': {
        'horizon': str,                      # 'Largo Plazo (3-5 años)' | 'Corto Plazo (3-6 meses)'
        'verdict': str,                      # 'FUERTE COMPRA 🚀'|'COMPRA 🟢'|'NEUTRAL ⚪'|'VENTA 🔴'|'FUERTE VENTA 💀'
        'confidence': float,                 # -100 to 100 (%)
        'monte_carlo_success_rate': float or None,  # 0-100 (%) [LP only]
        'score_breakdown': {
            'technical_score': float,
            'fundamental_score': float,
            'macro_score': float,
            'qualitative_score': float,
            'total_score': float,
            'max_possible_score': float
        },
        'entry_points': {
            'primary': float,                # Precio ideal entrada
            'secondary': float,              # Alternativa
            'stop_loss': float
        },
        'timing_analysis': str,              # Explicación técnica
        'narrative': str                     # Resumen ejecutivo
    },
    
    # Alertas
    'warnings': [str]                        # Riesgos detectados
}
```

**Ejemplo de Uso:**

```python
from agent import FinancialAgent

# Análisis Largo Plazo
agent_lp = FinancialAgent('AAPL', is_short_term=False)
result_lp = agent_lp.run_analysis()

print(f"Veredicto: {result_lp['strategy']['verdict']}")
print(f"Confianza: {result_lp['strategy']['confidence']:.1f}%")
print(f"Narrativa: {result_lp['strategy']['narrative']}")

# Análisis Corto Plazo
agent_cp = FinancialAgent('AAPL', is_short_term=True)
result_cp = agent_cp.run_analysis()

print(f"Veredicto (CP): {result_cp['strategy']['verdict']}")
```

---

## Módulos de Datos

### `market_data.py`

#### Función: `get_ticker_data()`

```python
from market_data import get_ticker_data

ticker = get_ticker_data(symbol: str, timeout: int = 10) -> yfinance.Ticker
```

**Returns:** Objeto yFinance con datos disponibles

**Raises:**
- `NameError`: Símbolo inválido
- `TimeoutError`: Timeout en descarga
- `ConnectionError`: Sin conexión a internet

**Ejemplo:**
```python
ticker = get_ticker_data('MSFT')
price = ticker.info['currentPrice']
pe = ticker.info['trailingPE']
```

---

#### Función: `get_historical_data()`

```python
from market_data import get_historical_data

df = get_historical_data(
    ticker_obj: yfinance.Ticker,
    period: str = '5y'  # '1y', '2y', '5y', 'max'
) -> pd.DataFrame
```

**Returns:** DataFrame OHLCV (Open, High, Low, Close, Volume)

```
           Open    High     Low   Close     Volume
Date                                              
2020-01-02  150.5  150.8  150.2  150.6  1000000
2020-01-03  150.8  151.5  150.5  151.2  950000
...
```

---

#### Función: `get_earnings_surprise()`

```python
from market_data import get_earnings_surprise

surprise_pct = get_earnings_surprise(symbol: str) -> float
```

**Returns:** Promedio de sorpresas de earnings últimos 4 trimestres (en %)

**Ejemplo:**
```python
surprise = get_earnings_surprise('AAPL')
# surprise = 5.2 (5.2% positive average)
```

---

#### Función: `get_spy_correlation()`

```python
from market_data import get_spy_correlation

correlation = get_spy_correlation(symbol: str) -> float
```

**Returns:** Correlación 1 año con SPY (0-1)

---

### `indicators.py`

#### Función: `calculate_rsi()`

```python
from indicators import calculate_rsi

rsi = calculate_rsi(
    prices: pd.Series,
    period: int = 14
) -> pd.Series
```

**Returns:** Serie con RSI para cada fecha

**Ejemplo:**
```python
rsi = calculate_rsi(df['Close'], period=14)
print(rsi.iloc[-1])  # RSI actual
```

---

#### Función: `calculate_macd()`

```python
from indicators import calculate_macd

macd_dict = calculate_macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> dict
```

**Returns:**
```python
{
    'macd': pd.Series,          # Línea MACD
    'signal': pd.Series,        # Línea señal
    'histogram': pd.Series      # Histograma
}
```

---

#### Función: `calculate_adx()`

```python
from indicators import calculate_adx

adx = calculate_adx(
    df: pd.DataFrame  # Debe tener Open, High, Low, Close, Volume
) -> pd.Series
```

**Returns:** Serie con ADX(14) para cada fecha

---

#### Función: `detect_rsi_divergence()`

```python
from indicators import detect_rsi_divergence

has_divergence = detect_rsi_divergence(df: pd.DataFrame) -> bool
```

**Returns:** True si hay divergencia bajista (precio sube, RSI baja)

---

#### Función: `add_all_indicators()`

```python
from indicators import add_all_indicators

df_with_indicators = add_all_indicators(df: pd.DataFrame) -> pd.DataFrame
```

**Columnas añadidas:**
- `RSI`, `MACD`, `MACD_Signal`, `MACD_Histogram`
- `SMA_20`, `SMA_50`, `SMA_200`
- `BB_Upper`, `BB_Lower`, `BB_Middle`
- `ADX`, `ATR`, `OBV`, `MFI`
- `Stoch_K`, `Stoch_D`
- `SMA_Slope` (pendiente de SMA20)

---

### `macro_analysis.py`

#### Función: `analyze_macro_context()`

```python
from macro_analysis import analyze_macro_context

macro = analyze_macro_context(macro_data: dict = None, timeout: int = 10) -> dict
```

**Returns:**
```python
{
    'vix': float,                    # 10.5 to 80+
    'tnx': float,                    # % (10Y Yield)
    'fear_greed_index': float,       # 0-100
    'yield_spread': float,           # % (10Y - 2Y)
    'tnx_trend': str,                # 'Subiendo'|'Bajando'|'Lateral'
    'timestamp': str                 # ISO 8601
}
```

**Interpretaciones automáticas:**
- **VIX < 15**: Calma (Bullish)
- **VIX 15-20**: Normal
- **VIX 20-30**: Volatilidad moderada
- **VIX > 30**: Pánico (Bearish)

---

#### Función: `get_fed_rate()`

```python
from macro_analysis import get_fed_rate

rate = get_fed_rate() -> float
```

**Returns:** Tasa Fed Funds actual (%)

---

### `sentiment_analysis.py`

#### Función: `advanced_sentiment_analysis()`

```python
from sentiment_analysis import advanced_sentiment_analysis

sentiment = advanced_sentiment_analysis(
    news_list: list,           # Lista de strings de noticias
    min_articles: int = 5
) -> dict
```

**Returns:**
```python
{
    'score': float,             # -1 (very negative) to 1 (very positive)
    'label': str,               # 'Negativo'|'Neutral'|'Positivo'
    'volume': int,              # Número de artículos analizados
    'bullish_count': int,
    'neutral_count': int,
    'bearish_count': int
}
```

**Ejemplo:**
```python
news = ['AAPL beats earnings', 'New regulatory issue', 'Strong growth']
sentiment = advanced_sentiment_analysis(news)
print(f"Sentimiento: {sentiment['score']:.2f}")  # 0.45 (Positivo)
```

---

#### Función: `detect_regulatory_factors()`

```python
from sentiment_analysis import detect_regulatory_factors

reg = detect_regulatory_factors(news_list: list) -> dict
```

**Returns:**
```python
{
    'has_regulatory_risk': bool,     # True si hay riesgos detectados
    'risk_type': str,                # 'antitrust'|'tax'|'compliance'|'environmental'
    'sentiment_adjustment': float,   # -1 to 0 (penalización)
    'keywords': [str]                # Palabras clave detectadas
}
```

---

## Generación de Reportes

### Clase: `ReportGenerator`

#### Constructor

```python
from report_generator import ReportGenerator

generator = ReportGenerator(analysis_result: dict)
```

**Parámetros:**
- `analysis_result` (dict): Resultado completo de `agent.run_analysis()`

#### Método: `generate_html_report()`

```python
html_path = generator.generate_html_report(
    output_dir: str = './reports',
    include_charts: bool = True,
    include_recommendations: bool = True
) -> str
```

**Returns:** Path al archivo HTML generado

**Ejemplo:**
```python
from agent import FinancialAgent
from report_generator import ReportGenerator

agent = FinancialAgent('AAPL')
result = agent.run_analysis()

generator = ReportGenerator(result)
report_path = generator.generate_html_report(output_dir='./my_reports')

print(f"Reporte generado: {report_path}")
# Abre en navegador: open {report_path}
```

---

#### Método: `export_to_csv()`

```python
csv_path = generator.export_to_csv(
    results: list,                  # Lista de dicts de análisis
    output_dir: str = './reports',
    filename: str = 'analysis.csv'
) -> str
```

**Returns:** Path al CSV

**Columnas generadas:**
```
ticker, verdict, confidence, price, sector, rsi, macd, vix, tnx, fear_greed, entry_primary, stop_loss
```

---

#### Método: `export_to_json()`

```python
json_path = generator.export_to_json(
    result: dict or list,
    output_dir: str = './reports',
    filename: str = 'analysis.json'
) -> str
```

**Returns:** Path al JSON

---

## Gestión de Portafolio

### Clase: `PortfolioManager`

#### Constructor

```python
from portfolio_manager import PortfolioManager

pm = PortfolioManager(portfolio_file: str = './portfolio.json')
```

#### Método: `add_holding()`

```python
pm.add_holding(
    ticker: str,
    quantity: int,
    purchase_price: float,
    purchase_date: str = None      # ISO 8601, default: hoy
) -> dict
```

**Returns:** Dict con holding añadido

**Ejemplo:**
```python
pm.add_holding('AAPL', quantity=100, purchase_price=150.50)
pm.add_holding('MSFT', quantity=50, purchase_price=280.00)
```

---

#### Método: `get_portfolio_analysis()`

```python
portfolio = pm.get_portfolio_analysis(
    agent_func,                     # Función que ejecuta analysis
    horizon: str = 'long_position'  # 'short_term' or 'long_position'
) -> dict
```

**Returns:**
```python
{
    'total_holdings': int,
    'total_value': float,
    'portfolio_p_l': float,
    'portfolio_p_l_pct': float,
    'holdings': [
        {
            'ticker': 'AAPL',
            'quantity': 100,
            'purchase_price': 150.50,
            'current_price': 180.75,
            'current_value': 18075.00,
            'gain_loss': 3025.00,
            'gain_loss_pct': 20.1,
            'analysis': {
                # Full analysis result
                'strategy': {...},
                'technical': {...},
                ...
            }
        },
        ...
    ],
    'portfolio_verdict': {
        'bullish_holdings': 3,
        'neutral_holdings': 1,
        'bearish_holdings': 0,
        'weighted_confidence': 45.2  # Promedio ponderado
    }
}
```

---

#### Método: `remove_holding()`

```python
pm.remove_holding(ticker: str) -> bool
```

---

#### Método: `save()`

```python
pm.save() -> None
```

Persiste portafolio a `portfolio.json`

---

## Configuración

### Archivo: `agent.py` - Constantes

```python
# Benchmarks por Sector
INDUSTRY_BENCHMARKS = {
    "Technology": {
        "debtToEquity": 60,
        "roe": 0.20,
        "pe": 30,
        "peg": 1.2
    },
    "Healthcare": {
        "debtToEquity": 80,
        "roe": 0.15,
        "pe": 20,
        "peg": 1.0
    },
    "Utilities": {
        "debtToEquity": 150,
        "roe": 0.09,
        "pe": 18,
        "peg": 0.8
    },
    # ... más sectores
}

# Umbrales de Scoring LP (v4.2)
# Veredictos basados en confianza normalizada
VERDICT_THRESHOLDS_LP = {
    'strong_buy': 45,       # FUERTE COMPRA >= 45%
    'buy': 25,              # COMPRA >= 25%
    'neutral': 5,           # NEUTRAL >= 5%
    'sell': -10,            # VENTA >= -10%
    'strong_sell': -100     # FUERTE VENTA < -10%
}

# Umbrales CP (v2.4)
# Más sensibles al VIX e inflación
VERDICT_THRESHOLDS_CP = {
    'base': 15,             # Umbral base
    'strong': 35,           # Umbral fuerte
    'vix_sensitivity': 0.4,
    'tnx_sensitivity': 1.0
}
```

---

## Manejo de Errores

### Excepciones Personalizadas

```python
from agent import FinancialAgent

try:
    agent = FinancialAgent('INVALID_TICKER')
    result = agent.run_analysis()
except NameError as e:
    print(f"Ticker inválido: {e}")
except ConnectionError as e:
    print(f"Sin conexión a internet: {e}")
except TimeoutError as e:
    print(f"Timeout descargando datos: {e}")
```

### Estrategia de Fallback

```python
# Ejemplo: Si PEG no disponible, usa Forward P/E
if peg is None:
    peg_estimate = forward_pe / earnings_growth
    warnings.append("PEG estimado desde Forward P/E")
    
# Ejemplo: Si datos macro no disponibles, usa defaults
if macro_error:
    macro = {
        'vix': 20.0,          # VIX histórico promedio
        'tnx': 4.0,           # TNX promedio
        'fear_greed_index': 50
    }
    warnings.append("Contexto macro usa valores históricos")
```

---

## Ejemplos de Uso

### Ejemplo 1: Análisis Simple

```python
from agent import FinancialAgent
from report_generator import ReportGenerator

# Análisis LP
agent = FinancialAgent('AAPL', is_short_term=False)
result = agent.run_analysis()

# Generar reporte
generator = ReportGenerator(result)
report_path = generator.generate_html_report()

print(f"Veredicto: {result['strategy']['verdict']}")
print(f"Confianza: {result['strategy']['confidence']:.1f}%")
print(f"Reporte: {report_path}")
```

---

### Ejemplo 2: Análisis Batch

```python
from agent import FinancialAgent
from report_generator import ReportGenerator

tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META']
results = []

for ticker in tickers:
    agent = FinancialAgent(ticker, is_short_term=True)
    result = agent.run_analysis()
    results.append(result)

# Exportar a CSV
generator = ReportGenerator(results[0])
csv_path = generator.export_to_csv(results)

# Filtrar por verdict
strong_buys = [r for r in results if 'FUERTE COMPRA' in r['strategy']['verdict']]
print(f"Strong Buys: {[r['ticker'] for r in strong_buys]}")
```

---

### Ejemplo 3: Gestión de Portafolio

```python
from agent import FinancialAgent
from portfolio_manager import PortfolioManager

pm = PortfolioManager()

# Agregar holdings
pm.add_holding('AAPL', quantity=100, purchase_price=150.50)
pm.add_holding('MSFT', quantity=50, purchase_price=280.00)
pm.add_holding('GOOGL', quantity=25, purchase_price=2800.00)

# Analizar portafolio
def run_agent_analysis(ticker):
    agent = FinancialAgent(ticker, is_short_term=False)
    return agent.run_analysis()

portfolio = pm.get_portfolio_analysis(run_agent_analysis)

# Mostrar resultados
print(f"Total Value: ${portfolio['total_value']:,.2f}")
print(f"P&L: ${portfolio['portfolio_p_l']:,.2f} ({portfolio['portfolio_p_l_pct']:.1f}%)")
print(f"Bullish Holdings: {portfolio['portfolio_verdict']['bullish_holdings']}")

# Guardar
pm.save()
```

---

### Ejemplo 4: Comparación LP vs CP

```python
from agent import FinancialAgent

ticker = 'AAPL'

# Largo Plazo
agent_lp = FinancialAgent(ticker, is_short_term=False)
result_lp = agent_lp.run_analysis()

# Corto Plazo
agent_cp = FinancialAgent(ticker, is_short_term=True)
result_cp = agent_cp.run_analysis()

# Comparar
print("=" * 50)
print(f"Análisis de {ticker}")
print("=" * 50)
print(f"\nLARGO PLAZO (3-5 años):")
print(f"  Veredicto: {result_lp['strategy']['verdict']}")
print(f"  Confianza: {result_lp['strategy']['confidence']:.1f}%")
print(f"  Narrativa: {result_lp['strategy']['narrative']}")

print(f"\nCORTO PLAZO (3-6 meses):")
print(f"  Veredicto: {result_cp['strategy']['verdict']}")
print(f"  Confianza: {result_cp['strategy']['confidence']:.1f}%")
print(f"  Narrativa: {result_cp['strategy']['narrative']}")

# Análisis de divergencias
if 'COMPRA' in result_lp['strategy']['verdict'] and 'VENTA' in result_cp['strategy']['verdict']:
    print("\n⚠️ DIVERGENCIA: LP Bullish pero CP Bearish")
    print("   Posible acumulación antes de corrección corto plazo")
```

---

### Ejemplo 5: Análisis de Sector

```python
from agent import FinancialAgent

tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'TSLA']

results = []
for ticker in tech_stocks:
    agent = FinancialAgent(ticker, is_short_term=False)
    result = agent.run_analysis()
    results.append(result)

# Estadísticas de sector
bullish = len([r for r in results if 'COMPRA' in r['strategy']['verdict']])
bearish = len([r for r in results if 'VENTA' in r['strategy']['verdict']])
avg_confidence = sum(r['strategy']['confidence'] for r in results) / len(results)

print(f"Tech Sector Analysis (n={len(results)})")
print(f"  Bullish: {bullish}")
print(f"  Bearish: {bearish}")
print(f"  Avg Confidence: {avg_confidence:.1f}%")

# Top picks
top_picks = sorted(results, key=lambda x: x['strategy']['confidence'], reverse=True)[:3]
print(f"\nTop 3 Picks:")
for r in top_picks:
    print(f"  {r['ticker']}: {r['strategy']['verdict']} ({r['strategy']['confidence']:.1f}%)")
```

---

## Debugging

### Activar Modo Verbose

```python
import logging
logging.basicConfig(level=logging.DEBUG)

agent = FinancialAgent('AAPL')
result = agent.run_analysis()
# Mostrará logs detallados de cada paso
```

### Inspeccionar Score Breakdown

```python
result = agent.run_analysis()

breakdown = result['strategy']['score_breakdown']
print(f"Technical Score: {breakdown['technical_score']:.2f}")
print(f"Fundamental Score: {breakdown['fundamental_score']:.2f}")
print(f"Macro Score: {breakdown['macro_score']:.2f}")
print(f"Qualitative Score: {breakdown['qualitative_score']:.2f}")
print(f"Total: {breakdown['total_score']:.2f} / {breakdown['max_possible_score']:.2f}")
print(f"Confidence: {breakdown['total_score'] / breakdown['max_possible_score'] * 100:.1f}%")
```

---

## Roadmap

### v1.0.0 (Actual)
- ✅ Scoring dual (LP v4.2 / CP v2.4)
- ✅ Análisis técnico multiframe
- ✅ Benchmarking sectorial
- ✅ NLP cualitativo
- ✅ Monte Carlo veredictos (LP)
- ✅ HTML reporting
- ✅ Tests completos

### v1.1.0 (Planeado)
- 🔲 Streamlit UI interactiva
- 🔲 Backtesting framework
- 🔲 Paper trading
- 🔲 Alertas automáticas
- 🔲 Caché persistente de datos macro
- 🔲 Soporte para criptomonedas

---

**Última actualización:** Diciembre 22, 2025  
**Contacto:** modCarlos (GitHub)
