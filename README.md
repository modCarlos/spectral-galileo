# 🤖 Agente de Análisis Financiero

Un agente inteligente en Python para análisis completo de acciones del mercado bursátil. Combina análisis técnico, fundamental, macroeconómico y cualitativo para generar recomendaciones de inversión.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Características

- 📊 **Análisis Técnico Avanzado**: RSI, MACD, ADX, SMA Slope, Bollinger Bands, Estocástico, OBV
- 📈 **Análisis Fundamental**: P/E, PEG, ROE, Deuda/Capital, Dividendos, FCF, Crecimiento
- 🌍 **Contexto Macroeconómico**: VIX (Umbrales Dinámicos), Índice Miedo/Codicia, Tasas TNX
- 🧠 **Sentimiento Híbrido**: Análisis de ~30 noticias combinando yFinance + Google RSS
- 💼 **Gestión de Portafolio**: Tracking con precios personalizados y escaneo automático
- 🎯 **Veredicto Inteligente**: Trend Gate y Filtro de Entorno para horizontes de CP y LP
- 🔍 **Market Scanner**: Escaneo masivo con enfoque táctico o estratégico
- 🧪 **100% Tested**: Suite completa de tests con pytest y cobertura

## 🚀 Inicio Rápido

### Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd spectral-galileo

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Uso Básico

```bash
# Analizar una acción
python main.py AAPL

# Escanear mercado (Top 25 S&P 500)
python main.py -s                # o --scan

# Análisis Corto Plazo (3-6 meses)
python main.py AAPL -st          # o --short-term

# Gestión de portafolio
python main.py -a AAPL 150.50    # o --add
python main.py -p                # o --portfolio

# Backtesting (estrategia técnica)
python main.py -b NVDA           # Último año
python main.py -b AAPL 2024-01-01 2024-12-31   # Período custom

# 🤖 Análisis con IA (requiere GEMINI_API_KEY)
python main.py --ai AAPL         # Análisis profundo con Gemini

# Ver ayuda completa
python main.py -h
```

> **💡 Análisis con IA**: Usa Gemini API para análisis profundo de noticias y recomendaciones contextuales. Ver [docs/llm_analysis.md](docs/llm_analysis.md) para configuración y precios.


### ⚡ Backtesting

El comando `--backtest` ejecuta una simulación histórica usando **solo indicadores técnicos**:

**Reglas de la Estrategia (Agresivas):**
- **Compra**: RSI < 45 Y Precio > SMA200
- **Venta**: RSI > 65 O Pérdida > 10% O Ganancia > 15%

> **⚠️ Diferencia con el Agente Principal**: Las reglas de backtesting son **más agresivas** que las del agente de análisis (que usa 16 factores). Esto permite generar más actividad de trading para evaluar mejor la estrategia técnica.

**Ejemplo de salida:**
```
📊 PERFORMANCE
Capital Inicial:     $10,000.00
Capital Final:       $9,981.29
Ganancia/Pérdida:    -$18.71 (-0.19%)

📈 COMPARACIÓN: Buy & Hold
Valor Buy & Hold:    $9,991.17
❌ Buy & Hold fue mejor por 0.10%

📋 REGLAS DE LA ESTRATEGIA (AGRESIVAS)
Compra:  RSI < 45 Y Precio > SMA200
Venta:   RSI > 65 O Pérdida > 10% O Ganancia > 15%

📊 ESTADÍSTICAS DE TRADING
Total Trades:        2 (1 compras, 1 ventas)
Win Rate:            0.0%
```

> **Nota**: El backtesting usa solo datos históricos disponibles (sin look-ahead bias). Es útil para evaluar estrategias técnicas simples, pero no reemplaza análisis profesional.



## 📖 Documentación

**🆕 Índice Maestro:** [docs/INDEX.md](docs/INDEX.md) - Navegación completa de toda la documentación

### Documentos Principales

#### Para Usuarios
- **[High Conviction Guide](docs/guides/HIGH_CONVICTION_GUIDE.md)** - Cómo interpretar señales de trading
- **[API Documentation](docs/guides/API_DOCUMENTATION.md)** - Referencia completa de comandos

#### Para Desarrolladores
- **[Arquitectura](docs/technical/architecture.md)** - Diseño del sistema
- **[Agent Integration](docs/technical/AGENT_INTEGRATION_PLAN.md)** - Cómo funciona el agente
- **[Backtesting Guide](docs/backtesting/how_to_run_backtesting.md)** - Ejecutar backtests

#### Fórmulas de Scoring
- **[Short-Term v4.0](docs/formulas/scoring_formula_short_term_optimized.md)** - Trading 3-6 meses (85% técnico)
- **[Long-Term v6.0](docs/formulas/scoring_formula_long_term_optimized.md)** - Inversión 3-5 años (50% técnico + 35% fundamental)

#### Estado del Proyecto
- **[Phase 4 Deployment](docs/phases/PHASE4_DEPLOYMENT_STATUS.md)** - Estado actual de producción
- **[Backtesting Results](docs/backtesting/COMPARISON_FINAL_RESULTS.md)** - Validación completa

### Métricas de Producción (27-Dic-2025)

```
🟢 Status: En Producción - Gradual Rollout
📊 Tickers Activos: 10 (Fase 1 de 3)
🎯 Thresholds: 30% strong_buy, 25% buy
📈 COMPRA Rate: 19.7% (vs 1.6% sistema antiguo - 12.3x mejora)
✅ Performance: +92% retorno, Sharpe 1.45, Win Rate 60%
```

## 🎯 Ejemplo de Salida

```
REPORTE FINANCIERO: AAPL
========================================
Precio Actual: $273.67

🤖 MI OPINIÓN PERSONAL
------------------------------
Según mi análisis, AAPL es una candidata excelente para tu portafolio...

VEREDICTO: FUERTE COMPRA 🚀 (Confianza: 30%)
Acción Sugerida: Considerar Abrir Posición (Largo)

POR QUÉ COMPRAR (Pros):
  [+] Tendencia Alcista
  [+] Dividendo atractivo (1.5%)
  [+] FCF positivo
  [+] ROE excelente (171.4%)
  [+] Ventajas competitivas detectadas
```

## 🏗️ Estructura del Proyecto

```
spectral-galileo/
├── agent.py              # Motor del análisis
├── market_data.py        # Descarga de datos (yfinance)
├── indicators.py         # Indicadores técnicos
├── macro_analysis.py     # Análisis macro
├── sentiment_analysis.py # NLP de noticias
├── portfolio_manager.py  # Gestión de portafolio
├── main.py              # CLI
├── tests/               # Suite de tests
│   ├── test_portfolio_manager.py
│   ├── test_indicators.py
│   └── test_macro_analysis.py
└── docs/                # Documentación
    ├── scoring_formula.md
    ├── ideas.md
    └── architecture.md
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Con cobertura
python -m pytest tests/ --cov=. --cov-report=html
```

## 🤝 Comandos del CLI

| Comando | Descripción |
|---------|-------------|
| `python main.py TICKER` | Analizar acción individual |
| `python main.py -s` (o `--scan`) | Escanear Top 25 S&P 500 |
| `python main.py -st` (o `--short-term`) | Modo corto plazo (3-6 meses) |
| `python main.py -p` (o `--portfolio`) | Ver estado del portafolio |
| `python main.py -a TICKER` (o `--add`) | Agregar al portafolio |
| `python main.py -aa TICKER` (o `--add-auto`) | Agregar con Risk Management automático |
| `python main.py -rm` (o `--check-rm`) | Verificar Stop Loss y Take Profit |
| `python main.py -r TICKER` (o `--remove`) | Eliminar última entrada |
| `python main.py -ra TICKER` (o `--remove-all`) | Eliminar todas las entradas |
| `python main.py -ws` (o `--watchlist`) | Escanear watchlist |
| `python main.py -w TICKER` (o `--watch`) | Agregar a watchlist |
| `python main.py -uw TICKER` (o `--unwatch`) | Quitar de watchlist |
| `python main.py -b TICKER` (o `--backtest`) | Backtesting simple |
| `python main.py --ai TICKER` | Análisis con IA (Gemini) 🤖 |
| `python main.py -h` | Ver ayuda completa |

## 🔬 Tecnologías

- **yfinance**: Datos financieros en tiempo real
- **pandas/numpy**: Manipulación de datos
- **textblob**: Análisis de sentimiento NLP
- **colorama**: Output coloreado en terminal
- **tabulate**: Tablas formateadas
- **pytest**: Testing framework

## 📊 Métricas del Agente

- **Factores Evaluados**: 12 (técnicos, fundamentales, macro, cualitativos)
- **Score Máximo**: 13.5 puntos
- **Confianza**: 0-100%
- **Verdicts**: FUERTE COMPRA, COMPRA, NEUTRAL, VENTA, FUERTE VENTA

## 🛣️ Roadmap

- [x] Backtesting framework
- [x] Integración con LLM (Gemini/GPT)
- [ ] Gráficos y visualizaciones (Próximamente)
- [ ] Alertas automáticas
- [ ] Web UI con Streamlit
- [ ] Datos intradía (15min, 1h)

## ⚠️ Disclaimer

Este agente es una herramienta de **análisis educacional y de investigación**. No constituye asesoría financiera profesional. Investiga y consulta con un asesor antes de tomar decisiones de inversión.

## 📝 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

---

**Desarrollado con ❤️ usando Python y Data Science**
