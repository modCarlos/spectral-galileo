# 🚀 Spectral Galileo - Backtesting System

## Resumen Ejecutivo

Sistema completo de backtesting profesional con análisis avanzado, basado en datos reales de 5 años (2020-2025) para validar estrategias de trading automático.

**Status:** ✅ **FASES 1-3 COMPLETADAS** | **Producción-Ready**

---

## 📊 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│          Spectral Galileo Backtesting System           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  FASE 3: Advanced Metrics & Reports                    │
│  ├─ advanced_metrics.py (564 líneas)                   │
│  │  └─ 20+ métricas financieras profesionales          │
│  ├─ report_generator_v2.py (490 líneas)                │
│  │  └─ HTML interactivos con Chart.js                  │
│  └─ long_term_example.py (292 líneas)                  │
│     └─ Integración completa                            │
│                                                         │
│  FASE 2: Backtester Engine                             │
│  ├─ backtester.py (483 líneas)                         │
│  │  └─ Loop diario con signals & trades                │
│  ├─ backtest_portfolio.py (507 líneas)                 │
│  │  └─ Simulación de portafolio                        │
│  └─ example_backtest.py (282 líneas)                   │
│     └─ Demostraciones y validación                     │
│                                                         │
│  FASE 1: Data Infrastructure                           │
│  └─ backtest_data_manager.py (441 líneas)              │
│     └─ Local CSV storage (2.6 MB, 5 años)              │
│                                                         │
│  DATA LAYER                                            │
│  └─ backtest_data/ (23 tickers, 1254 días cada uno)    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Capacidades Actuales

### Horizonte de Prueba

| Período | Uso | Status |
|---------|-----|--------|
| 1-3 meses | Validación rápida de señales | ✅ Soportado |
| 6-12 meses | Patrones estacionales | ✅ Soportado |
| 2-5 años | Ciclos completos de mercado | ✅ **NUEVO** |

### Métricas Calculadas

**Retornos (4):** Total return, Annualized return, Daily average, Best/worst day

**Riesgo (4):** Volatility, Max drawdown, Avg drawdown, Recovery factor

**Risk-Adjusted (4):** Sharpe ratio, Sortino ratio, Calmar ratio, Recovery factor

**Trading (10):** Win rate, Profit factor, Avg win/loss, Expectancy, Consecutive wins/losses, Total trades, etc.

**Distribución (7):** Skewness, Kurtosis, Mean, Median, Std, Min, Max

### Reportes

- ✅ **HTML Interactivos** con gráficos (Equity curve, Drawdown, Returns)
- ✅ **JSON** con métricas detalladas
- ✅ **CSV** con valores diarios y transacciones
- ✅ **TXT** con resumen ejecutivo

---

## 📁 Estructura de Carpetas

```
spectral-galileo/
├── 📄 advanced_metrics.py              ✅ Cálculo de 20+ métricas
├── 📄 report_generator_v2.py           ✅ Generador HTML
├── 📄 long_term_example.py             ✅ Integración completa
├── 📄 backtester.py                    ✅ Orquestador
├── 📄 backtest_portfolio.py            ✅ Simulador portafolio
├── 📄 backtest_data_manager.py         ✅ Gestor de datos
├── 📄 example_backtest.py              ✅ Ejemplos
│
├── 📁 backtest_data/                   📊 Datos locales
│   ├── AAPL.csv (115 KB, 1254 días)
│   ├── MSFT.csv (114 KB, 1254 días)
│   ├── NVDA.csv (117 KB, 1254 días)
│   ├── ... (23 tickers total = 2.6 MB)
│
├── 📁 backtest_results/                📈 Resultados
│   ├── report_*.html                   (Reportes interactivos)
│   ├── metrics_*.json                  (Métricas detalladas)
│   ├── backtest_daily_*.csv            (Valores diarios)
│   ├── backtest_summary_*.txt          (Resumen ejecutivo)
│   └── backtest_transactions_*.csv     (Transacciones)
│
├── 📄 FASE3_COMPLETION.md              📋 Documentación Fase 3
├── 📄 LONG_TERM_DATA_UPDATE.md         📋 Actualización de datos
├── 📄 README.md                        📋 General
└── 📄 BACKTESTING_SUMMARY.md           📋 Sumarios anteriores
```

---

## 🚀 Cómo Usar

### 1. Ejecutar Backtest Completo (5 años)

```bash
python long_term_example.py --long-term
```

**Output:**
- Métricas calculadas en terminal
- `report_*.html` (gráficos interactivos)
- `metrics_*.json` (20+ indicadores)
- `backtest_daily_*.csv` (1254 días)
- `backtest_transactions_*.csv` (trades)

### 2. Análisis Multi-Período

```bash
python long_term_example.py --multi-period
```

**Output:**
- Comparativa de 5 años vs 2 años vs 1 año
- Tabla resumen
- Métricas por período

### 3. Usar desde Python

```python
from backtester import Backtester
from advanced_metrics import AdvancedMetricsCalculator
from report_generator_v2 import ReportGeneratorV2

# 1. Ejecutar backtest
backtester = Backtester(
    tickers=["AAPL", "MSFT", "NVDA"],
    start_date="2020-12-24",
    end_date="2025-12-22",
    initial_cash=100000
)
results = backtester.run_backtest()

# 2. Calcular métricas
metrics_calc = AdvancedMetricsCalculator(
    daily_values=results['daily_values']['Portfolio Value'].tolist(),
    trades=[...],
)
metrics = metrics_calc.generate_summary()
metrics_calc.print_summary()

# 3. Generar reporte
generator = ReportGeneratorV2()
html_file = generator.generate_html_report(
    backtest_name="Mi Estrategia",
    metrics_summary=metrics,
    daily_values=results['daily_values']['Portfolio Value'].tolist(),
    trades=[...],
)
```

### 4. Ver Reportes HTML

Abre cualquier archivo `report_*.html` en navegador:
- Visualización de equity curve
- Gráfico de drawdown
- Distribución de retornos
- Todas las métricas en tarjetas

---

## 📊 Datos Disponibles

### Período de Cobertura
- **Inicio:** December 24, 2020
- **Fin:** December 22, 2025
- **Duración:** 5 años completos (1254 días de trading)

### Tickers Descargados (23)

**Tecnología (9):**
AAPL, MSFT, NVDA, GOOGL, META, TSLA, NFLX, AMZN, MSTR

**Financiero (3):**
JPM, V, KO

**Salud (3):**
JNJ, MRK, PFE

**Consumidor (4):**
WMT, PG, MCD, DIS

**Defensa (3):**
BA, LMT, RTX

**Cripto (1):**
COIN

### Almacenamiento

```
Total:     2.6 MB
Per ticker: ~113 KB (CSV)
Format:    Pandas DataFrame (OHLCV)
Load time: <100ms per ticker
```

---

## 📈 Interpretación de Métricas

### Sharpe Ratio
- **Definición:** Retorno excesivo por unidad de riesgo
- **Ideal:** > 1 (bueno), > 2 (muy bueno), > 3 (excelente)
- **Cálculo:** (Retorno - Tasa Libre Riesgo) / Volatilidad
- **Uso:** Comparar estrategias ajustadas por riesgo

### Calmar Ratio
- **Definición:** Retorno anualizado / |Máximo Drawdown|
- **Ideal:** > 3 (bueno), > 5 (muy bueno)
- **Uso:** Medir recuperación de pérdidas

### Profit Factor
- **Definición:** Ganancias brutas / Pérdidas brutas
- **Ideal:** > 1.5 (viable), > 2 (bueno), > 3 (excelente)
- **Uso:** Evaluar eficiencia de trades

### Maximum Drawdown
- **Definición:** Mayor pérdida desde peak
- **Típico:** -10% a -30% (aceptable)
- **Uso:** Risk management, dimensionamiento posición

### Win Rate
- **Definición:** % de trades ganadores
- **Ideal:** > 50% (combinado con profit factor)
- **Uso:** Evaluar consistencia

---

## 🔧 Próximos Pasos Opcionales

### Fase 4: Parameter Optimization (2-3 horas)
- Grid search de parámetros (RSI oversold/overbought, MA period)
- Walk-forward analysis
- Out-of-sample testing
- Análisis de robustez

### Fase 5: Agent Integration (2-3 horas)
- Usar `agent.py` para señales basadas en LLM
- Combinar análisis técnico + sentiment
- Testing en vivo
- Risk management avanzado

### Experimentación
- Ajustar umbrales de RSI
- Modificar período de MA
- Añadir filtros (volumen, ATR, ADX)
- Probar diferentes tickers
- Backtests por sector

---

## 📋 Documentación Completa

| Archivo | Contenido |
|---------|----------|
| `FASE3_COMPLETION.md` | Documentación detallada de Fase 3 |
| `LONG_TERM_DATA_UPDATE.md` | Actualización de datos a 5 años |
| `BACKTESTING_SUMMARY.md` | Sumarios de Fases anteriores |
| Código fuente | Docstrings completos en cada clase |

---

## 🧪 Testing Realizado

| Test | Entrada | Output | Status |
|------|---------|--------|--------|
| Advanced Metrics | 252 días | 20+ métricas | ✅ PASS |
| HTML Report | Datos + trades | HTML 34-44 KB | ✅ PASS |
| 5-Year Backtest | AAPL+MSFT+NVDA+GOOGL+META | 1254 días | ✅ PASS |
| Data Loading | 23 tickers | CSV local | ✅ PASS |
| Multi-Period | 5/2/1 años | Comparativa | ✅ PASS |

---

## ✨ Features Destacados

✅ **5 Años de Datos** - Ciclos completos de mercado
✅ **20+ Métricas** - Análisis profesional
✅ **Reportes HTML** - Gráficos interactivos (Chart.js)
✅ **Multi-Período** - Análisis de corto/medio/largo plazo
✅ **Producción-Ready** - ~1,900 líneas de código bien documentado
✅ **Escalable** - Fácil agregar tickers, períodos, métricas
✅ **JSON Export** - Integración con otros sistemas
✅ **CSV Export** - Análisis en Excel/Power BI

---

## 🎯 Estado Actual

**Fase 1:** ✅ COMPLETADA
- Data Infrastructure
- BacktestDataManager
- 23 tickers, 5 años, 2.6 MB

**Fase 2:** ✅ COMPLETADA
- Backtester Engine
- Portfolio Simulator
- Signal Generation

**Fase 3:** ✅ COMPLETADA
- Advanced Metrics (20+ indicadores)
- Report Generator (HTML + JSON)
- Long-Term Analysis (5 años)

**Fase 4:** ⏳ OPCIONAL
- Parameter Optimization
- Grid Search
- Walk-Forward Analysis

**Fase 5:** ⏳ OPCIONAL
- Agent Integration
- LLM Signals
- Live Testing

---

## 📞 Contacto & Soporte

Para reportar bugs, sugerencias o preguntas:
1. Revisa los archivos de documentación
2. Examina los ejemplos en `long_term_example.py`
3. Consulta docstrings en código fuente

---

**Última Actualización:** December 23, 2025  
**Versión:** 3.0 (Fase 3 Completa)  
**Licencia:** MIT

---

*Spectral Galileo - Transformando datos en decisiones*
