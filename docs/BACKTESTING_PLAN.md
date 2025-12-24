# 📊 Plan de Backtesting - Spectral Galileo

## 1. ¿Qué es Backtesting?

### Definición
**Backtesting** es el proceso de evaluar la efectividad de una estrategia de trading usando datos históricos. Es como hacer una "prueba en el tiempo" de tu estrategia sin arriesgar dinero real.

### ¿Por qué es importante?
- ✅ Validar si tu estrategia realmente funciona
- ✅ Identificar fortalezas y debilidades antes de invertir
- ✅ Optimizar parámetros (confianza, umbrales, etc.)
- ✅ Calcular métricas clave: Sharpe ratio, Win rate, Max drawdown
- ✅ Entender riesgo/recompensa de manera objetiva

### Ejemplo simple
```
Si tu estrategia dice "COMPRA" el 2024-01-15:
- ¿A qué precio entraste? (historical)
- ¿Cuándo dijiste "VENTA"? (future)
- ¿Ganaste o perdiste dinero?
- ¿Cuál fue tu P&L?

Backtesting = Repetir esto para 250+ días y ver resultados agregados
```

---

## 2. Plan de Backtesting Detallado

### Fase 1: Recolección de Datos (Local Storage)

#### 2.1 Descarga de Datos Históricos
```
✅ POSIBLE: yfinance permite descargar datos de los últimos 20+ años
  - 1 año = 250 días trading
  - Tamaño por ticker: ~12 KB (muy comprimido)
  - Múltiples tickers: Negligible (MB total)

Opciones de almacenamiento:
  1. CSV local (simple, portable)
  2. SQLite database (consultas rápidas)
  3. Parquet (comprimido, optimizado para análisis)
```

#### 2.2 Actualización Diaria de Datos
```
✅ POSIBLE: Script que se ejecuta diariamente
  - Descargar close de mercado
  - Append a base de datos local
  - Mantener histórico completo
  - Sin limite de tiempo
```

### Fase 2: Arquitectura del Backtester

```
┌─────────────────────────────────────────┐
│   Backtester Principal                  │
│  (orchestrator de todo el flujo)       │
└─────────────────────────────────────────┘
           │
      ┌────┴────┐
      ▼         ▼
  ┌────────┐  ┌──────────────┐
  │  Data │  │ Strategy     │
  │Manager│  │ Executor     │
  └────────┘  │(agent.run_) │
      │       └──────────────┘
      │             │
      ▼             ▼
  ┌──────────────────────────┐
  │  Portfolio Manager        │
  │  - Track positions       │
  │  - Calculate P&L         │
  │  - Manage cash           │
  └──────────────────────────┘
      │
      ▼
  ┌──────────────────────────┐
  │  Metrics Calculator      │
  │  - Sharpe Ratio          │
  │  - Win Rate              │
  │  - Max Drawdown          │
  │  - Profit Factor         │
  └──────────────────────────┘
```

### Fase 3: Estructura de Datos

#### DataManager Local
```python
class BacktestDataManager:
    """Maneja datos locales para backtesting"""
    
    # Almacenar en: ./backtest_data/
    #   ├── AAPL.csv (histórico 1 año+)
    #   ├── MSFT.csv
    #   ├── NVDA.csv
    #   └── [tickers...]
    
    def download_historical(ticker, years=1):
        """Descarga datos de hace N años"""
        # Guarda en CSV local
        # ✅ Se puede hacer una sola vez
    
    def append_daily(ticker):
        """Actualiza con cierre de hoy"""
        # Descarga último día
        # Append a CSV existente
        # ✅ Se ejecuta diariamente (cron)
    
    def get_historical_range(ticker, start_date, end_date):
        """Lee datos de CSV local (fast)"""
        # No requiere conexión a internet
        # Ideal para backtesting rápido
```

#### Portfolio Snapshot
```python
class BacktestPortfolio:
    """Simula portfolio durante backtesting"""
    
    def __init__(self, initial_cash=100_000):
        self.cash = initial_cash
        self.positions = {}  # {ticker: {'shares': N, 'avg_cost': price}}
        self.trades = []     # Histórico de todas las transacciones
        self.daily_values = []  # Para calcular drawdown
    
    def execute_signal(self, ticker, signal, price, date):
        """
        COMPRA/VENTA basada en signal del agent
        
        if signal == "FUERTE COMPRA":
            buy_amount = self.cash * 0.30  # 30% del cash
        elif signal == "COMPRA":
            buy_amount = self.cash * 0.15
        elif signal == "VENTA":
            sell_all_positions(ticker)
        """
    
    def calculate_daily_pnl(self, prices_dict, date):
        """
        Calcula P&L diario basado en mark-to-market
        """
```

---

## 3. Plan de Implementación Técnica

### Sprint 1: Data Infrastructure (1-2 días)

```
Archivos a crear:
├── backtest_data_manager.py
│   ├── download_historical_data(tickers, years)
│   ├── update_daily_data(tickers)
│   ├── get_data_range(ticker, start, end)
│   └── data validation
│
├── backtest_portfolio.py
│   ├── Portfolio class
│   ├── Order execution
│   ├── P&L calculation
│   └── Trade logging
│
└── backtest_data/
    ├── AAPL.csv
    ├── MSFT.csv
    └── [auto-generated]
```

### Sprint 2: Backtester Engine (2-3 días)

```
Archivos a crear:
├── backtester.py
│   ├── Backtester class
│   ├── Loop temporal (day by day)
│   ├── Signal generation (agent.run_analysis)
│   ├── Trade execution
│   ├── Event logging
│   └── Result aggregation
│
└── backtest_metrics.py
    ├── calculate_returns()
    ├── sharpe_ratio()
    ├── max_drawdown()
    ├── win_rate()
    ├── profit_factor()
    └── additional metrics
```

### Sprint 3: Reporting & Analysis (1-2 días)

```
Archivos a crear:
├── backtest_report_generator.py
│   ├── Generate HTML report
│   ├── Equity curve
│   ├── Drawdown chart
│   ├── Monthly returns table
│   └── Trade list
│
└── backtest_visualizer.py
    ├── Plot equity curve
    ├── Plot drawdown
    ├── Plot monthly returns
    ├── Trade markers on price chart
```

---

## 4. Capacidades de yFinance Validadas

### ✅ Confirmado Funcional

| Capacidad | Estado | Detalles |
|-----------|--------|----------|
| Descargar 1 año datos | ✅ Sí | 250 días, 5 columnas (OHLCV) |
| Descargar múltiples años | ✅ Sí | Sin límite aparente |
| Múltiples tickers | ✅ Sí | Descarga paralela sin problema |
| Datos completos (OHLCV) | ✅ Sí | Open, High, Low, Close, Volume |
| Frecuencia diaria | ✅ Sí | Datos a cierre de mercado |
| Actualización incremental | ✅ Sí | Append nuevo día sin redownload |

### 📊 Características Ideales para Backtesting

```
Datos por día:
├── Open    → Precio apertura
├── High    → Máximo del día
├── Low     → Mínimo del día
├── Close   → Precio cierre (usar para análisis)
└── Volume  → Volumen (para validación)

Ventajas para nuestro caso:
- Datos limpios y confiables
- Sincronizados con análisis técnico
- Volume para confirmar movimientos
- Sin gaps de datos (mercado cerrado = sin entrada)
```

---

## 5. Estrategia de Almacenamiento Local

### Opción Recomendada: Hybrid (CSV + SQLite)

#### CSV (datos raw)
```
./backtest_data/
├── raw/
│   ├── AAPL.csv
│   ├── MSFT.csv
│   └── [más tickers]
└── meta/
    ├── last_update.json
    └── symbol_list.json
```

**Formato CSV:**
```csv
Date,Open,High,Low,Close,Volume
2024-12-23,253.62,254.50,253.15,254.12,40858800
2024-12-24,254.34,257.05,254.10,257.04,23234700
```

**Ventajas:**
- ✅ Portable (copy-paste fácil)
- ✅ Legible (abrir en Excel)
- ✅ Sin dependencias (pandas lo lee)
- ✅ Versionable en git

#### SQLite (para backtesting rápido)
```python
# Consulta ultra-rápida durante backtesting
df = pd.read_sql(
    "SELECT * FROM prices WHERE symbol='AAPL' AND date BETWEEN ? AND ?",
    conn,
    params=(start_date, end_date)
)
```

**Ventajas:**
- ✅ Queries rápidas
- ✅ Múltiples índices
- ✅ Comprimido (~80% menos espacio)
- ✅ ACID transactions

---

## 6. Implementación del Update Diario

### Opción 1: Script Manual
```bash
# Ejecutar cuando quieras
python backtest_data_manager.py --update-daily

# O con scheduler (cron)
# 0 18 * * 1-5 cd /path && python backtest_data_manager.py --update-daily
```

### Opción 2: Integración en main.py
```bash
# Cada vez que ejecutas main.py, actualiza datos
python main.py --update-data
python main.py AAPL  # Usa datos frescos
```

### Opción 3: Background Service
```python
# Ejecuta en background cada noche
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(update_daily_data, 'cron', hour=18)  # 6 PM
scheduler.start()
```

---

## 7. Arquitectura Final del Proyecto

```
spectral-galileo/
├── backtest_data/              # 📁 LOCAL DATA STORAGE
│   ├── raw/
│   │   ├── AAPL.csv
│   │   ├── MSFT.csv
│   │   └── [tickers...]
│   ├── backtest.db             # SQLite para queries rápidas
│   └── meta/
│       └── last_update.json
│
├── backtest_data_manager.py    # 🔄 DATA MANAGEMENT
├── backtest_portfolio.py       # 💼 PORTFOLIO SIMULATION
├── backtester.py              # 🎯 MAIN ENGINE
├── backtest_metrics.py        # 📊 METRICS CALCULATION
├── backtest_report.py         # 📄 REPORT GENERATION
├── backtest_visualizer.py     # 📈 CHARTS & GRAPHS
│
├── backtest_results/          # 📁 OUTPUT DIRECTORY
│   ├── backtest_2025_01.html
│   ├── backtest_2025_01.csv
│   └── equity_curve_2025_01.png
│
└── [existing files...]
```

---

## 8. Flujo de Backtesting Paso a Paso

### Ejemplo: Backtest AAPL para Jan 2025

```
1. INICIALIZAR
   - Portfolio inicial: $100,000 cash
   - Dates: 2025-01-01 a 2025-01-31
   - Tickers: [AAPL, MSFT, NVDA] 

2. LOOP DIARIO (for each day in range):
   ├─ 2025-01-01 (day 1)
   │  ├─ Close anterior: $254.12
   │  ├─ Cargar datos históricos (últimos 300 días)
   │  ├─ Ejecutar agent.run_analysis(data)
   │  │  └─ Devuelve: {verdict: "COMPRA", confidence: 65%}
   │  ├─ Ejecutar trade según signal
   │  │  └─ Compra $19,500 de AAPL (19.5% de $100k)
   │  │  └─ Portfolio.cash = $80,500
   │  ├─ Registrar trade
   │  └─ Portfolio.value = $80,500 + mark_to_market(AAPL)
   │
   ├─ 2025-01-02 (day 2)
   │  ├─ Price AAPL: $256.80 (+2.68%)
   │  ├─ Mark to market: positions worth $20,042
   │  ├─ Portfolio.value = $80,500 + $20,042 = $100,542
   │  ├─ Run analysis again...
   │  │  └─ Signal: "NEUTRAL" → No action
   │  └─ Continue tracking
   │
   └─ ... (repeat for all days)

3. CALCULAR METRICS (después de completar backtest)
   ├─ Total return: 8.5%
   ├─ Sharpe ratio: 1.22
   ├─ Max drawdown: -12.3%
   ├─ Win rate: 58%
   ├─ Profit factor: 2.1x
   └─ # Trades: 45

4. GENERAR REPORTES
   ├─ HTML report (visualización interactiva)
   ├─ Equity curve chart
   ├─ Monthly returns heatmap
   ├─ Trade list con entry/exit details
   └─ Comparison vs benchmark (SPY)
```

---

## 9. Casos de Uso Prácticos

### Uso 1: Validar Estrategia
```bash
python backtester.py --symbol AAPL --start 2024-01-01 --end 2025-01-31

Resultado:
✅ Strategy shows 8.5% return (vs SPY +12%)
⚠️ Max drawdown 12.3% is acceptable
✅ Win rate 58% is decent
```

### Uso 2: Optimizar Parámetros
```bash
# Probar diferentes confidence thresholds
python backtester.py --symbol AAPL --param min_confidence 40
python backtester.py --symbol AAPL --param min_confidence 50
python backtester.py --symbol AAPL --param min_confidence 60

→ Encuentra qué threshold da mejores resultados
```

### Uso 3: Multi-Ticker Portfolio
```bash
python backtester.py --symbols "AAPL,MSFT,NVDA" --start 2024-01-01
--end 2025-01-31 --initial_capital 100000

→ Simula portfolio diversificado
```

### Uso 4: Comparar vs Benchmark
```bash
python backtester.py --symbol AAPL --benchmark SPY

→ Muestra: Strategy return vs SPY return
   Sharpe ratio mejora/degrada vs SPY?
```

---

## 10. Cronograma Recomendado

| Fase | Duración | Tareas |
|------|----------|--------|
| **1. Setup** | 1-2 h | Data download, CSV structure |
| **2. Basic Engine** | 4-6 h | Loop temporal, order execution |
| **3. Metrics** | 3-4 h | Cálculos de performance |
| **4. Reporting** | 2-3 h | HTML report, charts |
| **5. Testing** | 2-3 h | Validar resultados, edge cases |
| **6. Documentation** | 1-2 h | Docstrings, README |
| **TOTAL** | **13-20 h** | Backtester completo |

---

## 11. Preguntas Respondidas

### ❓ "¿Qué es exactamente backtesting?"
**Respuesta:** Ejecutar tu estrategia sobre datos históricos para validar que funciona antes de arriesgar dinero real. Es como jugar un videojuego en "modo demo" antes de competir de verdad.

### ❓ "¿Es posible descargar datos de hace un año para backtesting?"
**Respuesta:** ✅ **SÍ, completamente posible**
- yfinance descarga datos de 20+ años sin problema
- 1 año = 250 días = ~12 KB por ticker
- Puedes guardar en CSV o SQLite localmente
- Actualización toma <1 segundo por ticker

### ❓ "¿Es posible descargar datos diariamente y guardarlos localmente?"
**Respuesta:** ✅ **SÍ, muy fácil**
- Script que se ejecuta cada noche (cron)
- Descarga last close, lo append al CSV
- Sin redownload de histórico (append-only)
- Crecimiento: ~4 KB por año por ticker
- A prueba de tiempo (funciona indefinidamente)

---

## 12. Siguiente: Plan de Implementación

¿Quieres que implemente:

1. **Fase 1 (Data):** BacktestDataManager + descarga de históricos
2. **Fase 2 (Engine):** Backtester + Portfolio simulation
3. **Fase 3 (Reporting):** Metrics + HTML report generator

**Mi recomendación:** Empezar con Fase 1 para tener datos locales, luego Fase 2 para que veas backtest funcionando, y finalmente Fase 3 para reportes bonitos.

¿Cuál quieres que comencemos?
