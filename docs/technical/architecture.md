# Arquitectura del Agente Financiero

Este documento describe la arquitectura y el diseño del sistema del agente de análisis financiero.

## Visión General

El agente está diseñado con una arquitectura modular que separa las responsabilidades en componentes especializados. Cada módulo realiza una función específica y se comunica con otros a través de interfaces bien definidas.

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│                    (CLI Interface)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │      FinancialAgent         │
        │   (Orchestration Layer)     │
        └─────────────┬───────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        ▼             ▼             ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│ market_data  │ │indicators│ │ macro_   │ │ sentiment_   │
│     .py      │ │   .py    │ │analysis  │ │  analysis    │
└──────────────┘ └──────────┘ └──────────┘ └──────────────┘
        │
        ▼
┌──────────────────────┐
│  portfolio_manager   │
│        .py           │
│ (portfolio.json)     │
└──────────────────────┘
```

## Módulos Principales

### 1. `main.py` - CLI Interface
**Responsabilidad**: Punto de entrada de la aplicación.

- Parsing de argumentos (argparse)
- Delegación a funciones específicas (análisis, scanner, portfolio)
- Formateo de salida coloreada (colorama)

**Comandos Soportados**:
- Análisis individual
- Market scanner
- Gestión de portafolio (add/remove/scan)

### 2. `agent.py` - Orchestration Layer
**Responsabilidad**: Motor central del análisis.

**Flujo de Ejecución**:
```python
def run_analysis():
    1. Fetch data (market_data.py)
    2. Calculate indicators (indicators.py)
    3. Analyze macro context (macro_analysis.py)
    4. Analyze sentiment (sentiment_analysis.py)
    5. Calculate score (internal logic)
    6. Generate verdict
    7. Return structured results
```

**Sistema de Scoring**:
- 12 factores evaluados
- Score máximo: 13.5 puntos
- Normalización a porcentaje de confianza
- Conversión a veredicto categorical

### 3. `market_data.py` - Data Layer
**Responsabilidad**: Interfaz con yfinance API.

**Funciones**:
- `get_ticker_data()`: Inicializa ticker object
- `get_historical_data()`: OHLCV data
- `get_fundamental_info()`: 30+ métricas financieras
- `get_news()`: Noticias recientes
- `get_macro_data()`: VIX, TNX, S&P 500
- `get_sp500_top25()`: Lista estática de tickers

**Manejo de Errores**:
- Redirección de stderr para silenciar warnings
- Try/except para conexiones fallidas
- Retorno de None en caso de error

### 4. `indicators.py` - Technical Analysis
**Responsabilidad**: Cálculo de indicadores técnicos.

**Indicadores Implementados**:
- SMA (50, 200)
- RSI (14)
- MACD (12, 26, 9)
- Bollinger Bands (20, 2σ)
- ATR (14)
- Stochastic Oscillator (14)
- OBV (On-Balance Volume)

**Patrón de Diseño**:
```python
def add_all_indicators(df):
    """Función conveniente que agrega todos los indicadores al DataFrame"""
    df['SMA_50'] = calculate_sma(df, 50)
    df['RSI'] = calculate_rsi(df, 14)
    # ...
    return df
```

### 5. `macro_analysis.py` - Macro Context
**Responsabilidad**: Evaluar contexto macroeconómico.

**Algoritmos Clave**:

**Fear & Greed Index (Sintético)**:
```python
def calculate_fear_greed_index(vix_price, gspc_rsi):
    # Normalizar VIX (invertido: bajo VIX = greed)
    vix_normalized = (50 - vix_price) / 50 * 50
    
    # RSI del S&P 500 (alto RSI = greed)
    rsi_normalized = gspc_rsi * 0.5
    
    # Promedio ponderado
    fgi = (vix_normalized + rsi_normalized)
    return max(0, min(100, fgi))
```

**TNX Trend Detection**:
```python
def detect_trend(series, window=20):
    sma = series.rolling(window).mean()
    current = series.iloc[-1]
    
    if current > sma.iloc[-1] * 1.01:
        return "Subiendo"
    elif current < sma.iloc[-1] * 0.99:
        return "Bajando"
    else:
        return "Lateral"
```

### 6. `sentiment_analysis.py` - NLP
**Responsabilidad**: Análisis de sentimiento de noticias.

**Proceso**:
1. Extracción de títulos de noticias (yfinance)
2. Análisis de polaridad con TextBlob
3. Agregación de scores
4. Clasificación (Positivo/Neutral/Negativo)

**Limitaciones Conocidas**:
- Solo analiza títulos (no contenido completo)
- TextBlob es básico (no fine-tuned para finanzas)
- Idioma: funciona mejor en inglés

### 7. `portfolio_manager.py` - Persistence Layer
**Responsabilidad**: Gestión del portafolio local.

**Estructura de Datos** (portfolio.json):
```json
[
  {
    "symbol": "AAPL",
    "buy_price": 150.50,
    "date": "2025-12-21 18:25:37"
  }
]
```

**Operaciones CRUD**:
- `load_portfolio()`: Read
- `add_stock()`: Create
- `remove_last_stock()`: Delete (específico)
- `remove_all_stock()`: Delete (batch)
- `clear_portfolio()`: Delete (all)

## Patrones de Diseño Utilizados

### 1. Strategy Pattern
El agente usa diferentes estrategias de análisis dependiendo del símbolo:
- Stocks con dividendos vs growth stocks
- Largo plazo vs corto plazo (basado en tendencia SMA200)

### 2. Facade Pattern
`FinancialAgent` actúa como una fachada simplificada que oculta la complejidad de múltiples módulos.

### 3. Factory Pattern (implícito)
`get_ticker_data()` actúa como factory para crear objetos yfinance Ticker.

## Flujo de Datos

### Análisis Individual

```
User Input (AAPL)
    ↓
main.py --ticker AAPL
    ↓
FinancialAgent(AAPL)
    ↓
┌─────────────────────────────────┐
│ Data Collection (Parallel)      │
│  - Historical OHLCV             │
│  - Fundamentals                 │
│  - News                         │
│  - Macro data                   │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Analysis Phase                  │
│  - Add indicators to df         │
│  - Calculate macro FGI          │
│  - Sentiment scoring            │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Scoring Engine                  │
│  - Technical: 4.5 pts           │
│  - Fundamental: 4.0 pts         │
│  - Macro: 1.5 pts               │
│  - Qualitative: 3.5 pts         │
│  Total: score / 13.5            │
└─────────────────────────────────┘
    ↓
Verdict + Report Generation
    ↓
Console Output (formatted)
```

### Market Scanner

```
User: --scan
    ↓
Load SP500 top 25 tickers
    ↓
For each ticker (parallel processing possible):
    - Run FinancialAgent.run_analysis()
    - Extract: price, verdict, confidence, R/R
    - Handle timeouts (10s limit)
    ↓
Sort by verdict strength
    ↓
Display tabulated results
```

## Consideraciones de Performance

### Optimizaciones Actuales
1. **Timeout Protection**: 10s límite por análisis para evitar cuelgues
2. **Error Handling**: Continuar scanner aunque fallos individuales
3. **Stderr Redirection**: Silenciar warnings de yfinance (mejora UX)

### Futuras Mejoras
1. **Parallel Processing**: Analizar múltiples tickers concurrentemente (asyncio)
2. **Caching**: Guardar datos macro (VIX, TNX) para no recargar cada vez
3. **Rate Limiting**: Respetar límites de yfinance API

## Testing Strategy

### Unit Tests
- Cada módulo tiene su test suite
- Uso de mock data para evitar dependencia de yfinance
- Coverage: ~85%

### Integration Tests
- `agent.py` actualmente sin tests de integración
- Future: mock yfinance responses y verificar flujo completo

## Extensibilidad

### Agregar Nuevo Indicador Técnico

1. Implementar en `indicators.py`:
```python
def calculate_new_indicator(df, param=10):
    # Lógica
    return series

def add_all_indicators(df):
    # ...
    df['NEW_IND'] = calculate_new_indicator(df)
    return df
```

2. Integrar en `agent.py`:
```python
if data['NEW_IND'].iloc[-1] > threshold:
    score += 0.5
    pros.append("NEW_IND bullish")
```

### Agregar Nueva Fuente de Datos

Crear nuevo módulo siguiendo el patrón de `market_data.py`:
```python
# custom_data_source.py
def fetch_alternative_data(ticker):
    # Implementación
    return data
```

Integrar en `agent.py`:
```python
custom_data = custom_data_source.fetch_alternative_data(self.symbol)
# Usar en scoring
```

## Seguridad y Privacidad

- **No se almacenan credenciales**: yfinance es público
- **Datos locales**: portfolio.json se guarda en directorio local (no cloud)
- **Sin tracking**: No se envían analytics a servidores externos

## Limitaciones Conocidas

1. **Datos de yfinance**:
   - Puede estar atrasado 15-20 minutos
   - Ocasionalmente errores de conexión
   - Métricas fundamentales a veces `None`

2. **Análisis**:
   - No considera eventos corporativos (splits, dividendos especiales)
   - Sentimiento NLP es básico
   - No backtesting automático

3. **Escalabilidad**:
   - Scanner limitado a 25 tickers
   - Sin paralelización (secuencial)
   - Sin base de datos (JSON)

## Mejoras Futuras

Ver [ideas.md](ideas.md) para roadmap completo.
