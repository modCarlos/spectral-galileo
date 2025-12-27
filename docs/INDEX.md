# Spectral Galileo - Índice de Documentación 📚

**Última actualización:** 27 Diciembre 2025  
**Status:** 🟢 En Producción - Fase 1 (10 tickers)

---

## 🚀 Inicio Rápido

### Para Usuarios Nuevos
1. **[README.md](../README.md)** - Introducción al proyecto
2. **[Guía de Convicción](guides/HIGH_CONVICTION_GUIDE.md)** - Cómo interpretar las señales
3. **[API Documentation](guides/API_DOCUMENTATION.md)** - Referencia de comandos

### Para Desarrolladores
1. **[Arquitectura](technical/architecture.md)** - Diseño del sistema
2. **[Integración Agent](technical/AGENT_INTEGRATION_PLAN.md)** - Cómo funciona el agente
3. **[Backtesting Guide](backtesting/how_to_run_backtesting.md)** - Ejecutar backtests

---

## 📊 Documentación por Categoría

### 🎯 Fórmulas de Scoring (Núcleo del Sistema)

Las fórmulas de scoring son el corazón del sistema de trading:

| Documento | Versión | Descripción |
|-----------|---------|-------------|
| **[Short-Term Optimized](formulas/scoring_formula_short_term_optimized.md)** | v4.0 | Fórmula para 3-6 meses, 85% técnico |
| **[Long-Term Optimized](formulas/scoring_formula_long_term_optimized.md)** | v6.0 | Fórmula para 3-5 años, 50% técnico + 35% fundamental |

**Estado:** ✅ En producción con thresholds optimizados (30%/25%)

**Características Phase 4:**
- External Data: Reddit, Earnings, Insider Trading
- Multi-timeframe: Daily, Weekly, Monthly confluence
- API Timeouts: 15s Reddit, 10s per timeframe
- Category Thresholds: Mega-cap (35/65) a High-vol (43/57)
- COMPRA Rate: 19.7% (vs 1.6% sistema antiguo)

---

### 🧪 Backtesting (Validación)

Documentación sobre el proceso de validación del sistema:

| Documento | Descripción |
|-----------|-------------|
| **[How to Run](backtesting/how_to_run_backtesting.md)** | Guía práctica para ejecutar backtests |
| **[Backtesting Guide](backtesting/BACKTESTING_PRACTICAL_GUIDE.md)** | Guía detallada del proceso |
| **[Formula Validation](backtesting/backtesting_vs_scoring_formulas.md)** | Comparación viejo vs nuevo sistema |
| **[Final Results](backtesting/COMPARISON_FINAL_RESULTS.md)** | Resultados finales Phase 3 |
| **[Latest Results](backtesting/BACKTESTING_RESULTS_NEW.md)** | Últimos resultados de backtesting |

**Métricas Validadas:**
- 6,656+ backtests ejecutados
- +92% mejora en retorno promedio
- Sharpe ratio: 1.45
- Win rate: 60%

**Ver también:** [backtesting/documentation/](../backtesting/documentation/) - 40+ documentos técnicos

---

### 📖 Guías de Usuario

Documentación para usuarios finales:

| Documento | Audiencia | Descripción |
|-----------|-----------|-------------|
| **[High Conviction Guide](guides/HIGH_CONVICTION_GUIDE.md)** | Traders | Cómo interpretar señales de alta convicción |
| **[API Documentation](guides/API_DOCUMENTATION.md)** | Desarrolladores | Referencia completa de comandos CLI |

---

### 🔧 Documentación Técnica

Arquitectura y diseño del sistema:

| Documento | Descripción |
|-----------|-------------|
| **[Architecture](technical/architecture.md)** | Diseño general del sistema |
| **[Agent Integration](technical/AGENT_INTEGRATION_PLAN.md)** | Cómo funciona el agente de trading |
| **[Alert System](technical/ALERT_TRACKING_SYSTEM.md)** | Sistema de alertas en tiempo real |
| **[Daemon Installation](technical/DAEMON_INSTALLATION_LOG.md)** | Log de instalación del daemon |
| **[CLI Refactoring](technical/CLI_REFACTORING_SUMMARY.md)** | Refactorización de comandos |
| **[Command System](technical/COMMAND_REFACTORING.md)** | Sistema de comandos mejorado |

---

### 📅 Fases del Proyecto

Estado actual y reportes de completación:

| Phase | Status | Documento Principal |
|-------|--------|---------------------|
| **Phase 1** | ✅ Complete | Multi-timeframe Analysis |
| **Phase 2** | ✅ Complete | External Data Integration |
| **Phase 3** | ✅ Complete | Category Thresholds + Grid Search |
| **Phase 4** | 🟢 In Progress | **[Deployment Status](phases/PHASE4_DEPLOYMENT_STATUS.md)** |
| **Phase 5** | ⏳ Pending | Real-world Validation (1-2 semanas) |

**Phase 4 Current Status:**
- ✅ Step 1: Merge to main (37 files)
- ✅ Step 2: Daemon configuration (30%/25%)
- 🟢 Step 3.1: Gradual rollout (10 tickers active)
- ⏳ Step 3.2: Expand to 30 tickers (48h)
- ⏳ Step 3.3: Full rollout 62 tickers (96h)

**Archived Reports:** [archive/](archive/) - Reportes de phases completadas

---

## 🗂️ Estructura de Carpetas

```
docs/
├── INDEX.md                    # Este archivo
├── formulas/                   # Fórmulas de scoring (2)
│   ├── scoring_formula_short_term_optimized.md
│   └── scoring_formula_long_term_optimized.md
├── backtesting/                # Documentación de backtesting (5)
│   ├── how_to_run_backtesting.md
│   ├── BACKTESTING_PRACTICAL_GUIDE.md
│   ├── backtesting_vs_scoring_formulas.md
│   ├── COMPARISON_FINAL_RESULTS.md
│   └── BACKTESTING_RESULTS_NEW.md
├── guides/                     # Guías de usuario (2)
│   ├── HIGH_CONVICTION_GUIDE.md
│   └── API_DOCUMENTATION.md
├── technical/                  # Docs técnicas (6)
│   ├── architecture.md
│   ├── AGENT_INTEGRATION_PLAN.md
│   ├── ALERT_TRACKING_SYSTEM.md
│   ├── DAEMON_INSTALLATION_LOG.md
│   ├── CLI_REFACTORING_SUMMARY.md
│   └── COMMAND_REFACTORING.md
├── phases/                     # Reportes de phases (1)
│   └── PHASE4_DEPLOYMENT_STATUS.md
└── archive/                    # Docs históricas (12)
    └── [Planes y reportes completados]
```

---

## 🔍 Búsqueda Rápida por Tema

### Trading & Estrategia
- Fórmulas de scoring: [formulas/](formulas/)
- High conviction: [guides/HIGH_CONVICTION_GUIDE.md](guides/HIGH_CONVICTION_GUIDE.md)
- Backtesting results: [backtesting/COMPARISON_FINAL_RESULTS.md](backtesting/COMPARISON_FINAL_RESULTS.md)

### Desarrollo & Integración
- Arquitectura: [technical/architecture.md](technical/architecture.md)
- Agent: [technical/AGENT_INTEGRATION_PLAN.md](technical/AGENT_INTEGRATION_PLAN.md)
- API: [guides/API_DOCUMENTATION.md](guides/API_DOCUMENTATION.md)

### Operaciones & Deployment
- Production status: [phases/PHASE4_DEPLOYMENT_STATUS.md](phases/PHASE4_DEPLOYMENT_STATUS.md)
- Alert system: [technical/ALERT_TRACKING_SYSTEM.md](technical/ALERT_TRACKING_SYSTEM.md)
- Daemon: [technical/DAEMON_INSTALLATION_LOG.md](technical/DAEMON_INSTALLATION_LOG.md)

### Testing & Validación
- How to run: [backtesting/how_to_run_backtesting.md](backtesting/how_to_run_backtesting.md)
- Practical guide: [backtesting/BACKTESTING_PRACTICAL_GUIDE.md](backtesting/BACKTESTING_PRACTICAL_GUIDE.md)
- Formula validation: [backtesting/backtesting_vs_scoring_formulas.md](backtesting/backtesting_vs_scoring_formulas.md)

---

## 📊 Métricas Clave (Actualizado: 27-Dic-2025)

### Sistema en Producción
```
🟢 Daemon: Running (PID: 33327)
📊 Watchlist: 10 tickers activos
🎯 Thresholds: strong_buy=30%, buy=25%
⏰ Intervalo: 30 minutos
📅 Próximo scan: Lunes apertura
```

### Performance Validado
```
COMPRA Rate:        19.7% (vs 1.6% old)    12.3x improvement
Avg Confidence:     31.4%                   Realistic threshold
Sharpe Ratio:       1.45                    +71% vs old
Win Rate:           60%                     +11% vs old
Max Drawdown:       7.3%                    -35% vs old
```

### API Reliability
```
Reddit Sentiment:   15s timeout            ✅ No hangs
Timeframe Analysis: 10s per timeframe      ✅ No hangs
Insider Trading:    Respects skip flag     ✅ No hangs
All APIs:           Graceful degradation   ✅ Production ready
```

---

## 🚀 Próximos Pasos

1. **Monitorear Fase 1** (24-48h)
   - 10 tickers en producción
   - Verificar frecuencia de alertas
   - Validar confidence levels

2. **Expandir a Fase 2** (Si Fase 1 exitosa)
   - Agregar 20 tickers más (total: 30)
   - Monitorear otras 24-48h

3. **Rollout Completo Fase 3** (Si Fase 2 exitosa)
   - Restaurar 62 tickers completos
   - Validación en tiempo real (Phase 5)

---

## 📞 Contacto & Soporte

- **Repositorio:** [spectral-galileo](https://github.com/modCarlos/spectral-galileo)
- **Issues:** GitHub Issues
- **Documentación adicional:** [backtesting/documentation/](../backtesting/documentation/)

---

**Última actualización:** 27 Diciembre 2025  
**Versión del sistema:** v4.0 (Production)  
**Total documentos:** 28 archivos activos + 12 archivados
