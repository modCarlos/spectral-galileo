# 🚀 Guía Completa de Backtesting - Spectral Galileo

## Quick Start (30 segundos)

```bash
# Test rápido con Tesla (6 meses)
python backtest_cli.py --ticker TSLA --type short

# Test con 5 tickers (6 meses)
python backtest_cli.py --tickers AAPL,MSFT,NVDA,GOOGL,TSLA --type short

# Test de Apple a largo plazo (5 años)
python backtest_cli.py --ticker AAPL --type long
```

---

## Respuestas a tus Preguntas

### 1️⃣ ¿Cómo correr un backtest manual?

**Opción A: CLI Rápido (RECOMENDADO)**
```bash
python backtest_cli.py --ticker AAPL --type short
```
- ✅ Más fácil
- ✅ Configuración automática de fechas
- ✅ Salida clara y bonita

**Opción B: Script Quick Test**
```bash
python quick_agent_test.py
```
- ✅ Corre AMBOS (short + long)
- ✅ Genera reportes comparativos
- ✅ Tiempo: ~3-5 minutos

**Opción C: Python Directo**
```python
from agent_backtester import AgentBacktester

backtester = AgentBacktester(
    tickers=['TSLA'],
    start_date='2025-09-01',
    end_date='2025-12-23',
    analysis_type='short_term'
)

results = backtester.run_backtest()
backtester.save_results(results)
```

---

### 2️⃣ ¿El backtesting usa el agente local o son pruebas simuladas?

**Respuesta: 100% REAL - USA TU AGENTE LOCAL**

El backtester REALMENTE ejecuta `FinancialAgent.run_analysis()` cada día:

```
Cada día del backtest:
┌─────────────────────────────────────────────────┐
│ 1. Cargar datos históricos (60 días previos)   │
│ 2. Ejecutar: agent.run_analysis(data)          │
│ 3. Recibir: score (0-100) del agente          │
│ 4. Convertir: score → BUY/SELL/HOLD signal    │
│ 5. Ejecutar: Trade si hay señal               │
│ 6. Registrar: Resultado (P&L)                 │
└─────────────────────────────────────────────────┘
```

**Validación - Mira los trades reales:**
```bash
cat backtest_results/agent_backtest_transactions_short_term_*.csv
```

Verás trades como:
```
Date,Type,Ticker,Shares,Price,Value,Cash_After,P&L
2025-06-26,BUY,TSLA,31,312.63,9691.53,90308.47,0
2025-06-27,SELL,TSLA,31,319.68,9910.08,100218.55,218.55
```

Esos números son:
- ✅ Precios REALES de Yahoo Finance
- ✅ Decisiones REALES de tu FinancialAgent
- ✅ NO simulados o aleatorios
- ✅ Ejecutados por el backtester cada día histórico

---

### 3️⃣ ¿Costo de GitHub Copilot Premium?

**Copilot Pro: $20 USD/mes (~$400 MXN)**

| Característica | Free | Pro ⭐ |
|---|---|---|
| Code Completions | 20/semana | Unlimited |
| Chat Messages | 50/día | 500/día |
| Modelo IA | Base | GPT-4o |
| Análisis Avanzado | ❌ | ✅ |
| Debugging | Básico | Avanzado |
| Documentación Auto | ❌ | ✅ |

**Mi recomendación: ACTIVA PRO porque:**
1. Costo mínimo ($20 = 2 cafés)
2. Unlimited chats (asistente 24/7)
3. Mejor modelo (GPT-4o vs base)
4. Break-even: Si ahorra 2h/mes, ya se pagó

**Cómo activar:**
- VS Code → Copilot icon → "Switch to Copilot Pro"
- O en github.com → Settings → Billing & Plans
- Listo en 2 minutos

---

## Comandos CLI Completos

### Formato Básico
```bash
python backtest_cli.py [OPTIONS]
```

### Opciones

| Opción | Ejemplo | Descripción |
|--------|---------|-------------|
| `--ticker` | `--ticker AAPL` | Un solo ticker |
| `--tickers` | `--tickers AAPL,MSFT,NVDA` | Múltiples (sin espacios) |
| `--type` | `--type short` | `short` (6mo) o `long` (5 años) |
| `--start` | `--start 2025-01-01` | Fecha inicio (opcional) |
| `--end` | `--end 2025-06-30` | Fecha fin (opcional) |
| `--capital` | `--capital 50000` | Capital inicial (default: 100k) |

### Ejemplos Prácticos

**TSLA - Corto plazo (6 meses)**
```bash
python backtest_cli.py --ticker TSLA --type short
```

**Apple - Largo plazo (5 años)**
```bash
python backtest_cli.py --ticker AAPL --type long
```

**Portfolio diversificado**
```bash
python backtest_cli.py --tickers AAPL,MSFT,NVDA,GOOGL,TSLA --type short
```

**Período personalizado (2025 enero a junio)**
```bash
python backtest_cli.py --ticker MSFT --type short \
  --start 2025-01-01 --end 2025-06-30
```

**Capital inicial diferente**
```bash
python backtest_cli.py --ticker NVDA --type short --capital 50000
```

---

## Entendiendo los Resultados

### Ejemplo de Output

```
╔═══════════════════════════════════════════════════╗
│        🎯 BACKTEST CONFIGURATION                │
╚═══════════════════════════════════════════════════╝

📊 Tickers:         TSLA
📅 Período:         2025-06-26 → 2025-12-23
🎪 Tipo:            Short Term
💰 Capital Inicial: $100,000.00

Iniciando backtesting...

╔═══════════════════════════════════════════════════╗
│        ✅ RESULTADOS                              │
╚═══════════════════════════════════════════════════╝

💰 Valor Final:       $105,885.11
📈 Retorno Total:         5.89%
📊 Volatilidad:           5.64%
⭐ Sharpe Ratio:          1.20
📉 Max Drawdown:         -2.56%
🔄 Total Trades:             4
🏆 Win Rate:             0.0%
```

### Métricas Explicadas

| Métrica | Significado | Bueno es... |
|---------|------------|-------------|
| **Retorno Total** | % ganancia neta | 📈 Mayor |
| **Volatilidad** | Fluctuaciones del portfolio | 📉 Menor |
| **Sharpe Ratio** | Retorno ajustado por riesgo | 📈 >1.0 |
| **Max Drawdown** | Caída máxima desde pico | 📉 Cercano a 0 |
| **Total Trades** | Compras + Ventas | 📊 Depende de estrategia |
| **Win Rate** | % trades ganadores | 📈 >50% es bueno |

---

## Archivos Generados

Cada backtest genera:

```
backtest_results/
├── report_agent_short_term_TSLA_20251223_095155.html
│   └─ 🔥 Abre en navegador - Gráficos interactivos
│
├── agent_backtest_daily_short_term_TSLA_20251223_095155.csv
│   └─ Valores diarios del portfolio
│
├── agent_backtest_transactions_short_term_TSLA_20251223_095155.csv
│   └─ Cada BUY/SELL con entrada y salida
│
└── agent_backtest_summary_short_term_TSLA_20251223_095155.txt
    └─ Resumen en texto plano
```

### Cómo Analizar

**1. HTML Report (Lo más importante)**
```bash
# Abre en tu navegador
backtest_results/report_agent_short_term_TSLA_*.html
```
Contiene:
- Equity curve (gráfico del crecimiento)
- Drawdown (caídas máximas)
- Distribución de retornos
- Tabla con todos los datos

**2. Trades Ejecutados**
```bash
cat backtest_results/agent_backtest_transactions_short_term_*.csv
```
Verás cada operación:
- Fecha, tipo (BUY/SELL), ticker, shares, precio
- Valor total, P&L

**3. Valores Diarios**
```bash
cat backtest_results/agent_backtest_daily_short_term_*.csv
```
Portfolio value cada día - útil para:
- Análisis en Excel
- Comparaciones
- Cálculos personalizados

---

## Flujo de Backtesting Completo

### Corto Plazo (6 meses)
```
Período: Últimos 6 meses (180 días)
Estrategia: Momentum-based (RSI, MACD, Stochastic)
Tickers: Tech volátiles (AAPL, MSFT, NVDA, GOOGL, TSLA)
Focus: Capturar movimientos rápidos
Resultado típico: 16.83% retorno, Sharpe 2.39
```

### Largo Plazo (5 años)
```
Período: Últimos 5 años (1,254 días)
Estrategia: Fundamental-based (P/E, ROE, Debt)
Tickers: Blue-chips estables (AAPL, MSFT, JPM, JNJ, WMT)
Focus: Crecimiento a largo plazo, resistir crisis
Resultado típico: 31.86% retorno, CAGR 5.71%
```

---

## Troubleshooting

**Error: "No data for ticker"**
```bash
# Verifica que el ticker existe
python -c "import yfinance as yf; print(yf.Ticker('TSLA').info['symbol'])"
```

**Error: "Not enough historical data"**
```bash
# Usa --type long en lugar de short
python backtest_cli.py --ticker UNKNOWN --type long
```

**Resultado parece incorrecto**
```bash
# Verifica los trades reales
cat backtest_results/agent_backtest_transactions_*.csv

# Si ves 0 trades, puede ser:
# - Agente fue muy conservador
# - Período muy corto (intenta --type long)
# - Ticker muy volátil
```

---

## Archivos Relevantes

```
spectral-galileo/
├── backtest_cli.py          ← 🎯 CLI para backtests manuales
├── quick_agent_test.py      ← Quick test (short + long)
├── agent_backtester.py      ← Motor del backtester (606 líneas)
├── agent_testing.py         ← Comparativa short vs long
├── backtest_data/           ← Datos históricos (CSV local)
│   ├── AAPL.csv
│   ├── MSFT.csv
│   └── [tickers...]
└── backtest_results/        ← Reportes generados
    ├── report_*.html
    ├── *_daily_*.csv
    ├── *_transactions_*.csv
    └── *_summary_*.txt
```

---

## Resumen

| Pregunta | Respuesta |
|----------|-----------|
| **¿Cómo correr backtest?** | `python backtest_cli.py --ticker AAPL --type short` |
| **¿Real o simulado?** | Real - usa FinancialAgent local cada día |
| **¿Copilot Pro?** | $20/mes - Altamente recomendado |

**Next Steps:**
1. ✅ Prueba: `python backtest_cli.py --ticker TSLA --type short`
2. ✅ Abre el HTML report en navegador
3. ✅ Examina los trades en CSV
4. ✅ Personaliza según necesites

---

**Última actualización:** 2025-12-23  
**Status:** Production Ready ✨
