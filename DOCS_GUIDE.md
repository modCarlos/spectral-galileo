# 📚 Guía Rápida de Documentación

**Última actualización:** 27 Diciembre 2025

## 🎯 Acceso Rápido

### Empezar Aquí
- **[README.md](README.md)** - Introducción y setup del proyecto
- **[docs/INDEX.md](docs/INDEX.md)** - 📖 **ÍNDICE MAESTRO** de toda la documentación

### Documentos Más Usados

| Propósito | Documento | Ubicación |
|-----------|-----------|-----------|
| 🚀 **Estado Actual** | Phase 4 Deployment Status | [docs/phases/](docs/phases/PHASE4_DEPLOYMENT_STATUS.md) |
| 📐 **Fórmulas** | Short-Term v4.0 / Long-Term v6.0 | [docs/formulas/](docs/formulas/) |
| 🧪 **Backtesting** | How to Run / Results | [docs/backtesting/](docs/backtesting/) |
| 📚 **Guías** | High Conviction / API Docs | [docs/guides/](docs/guides/) |
| 🔧 **Técnico** | Architecture / Agent | [docs/technical/](docs/technical/) |

---

## 📁 Estructura

```
docs/
├── INDEX.md              ⭐ Índice maestro (empieza aquí)
├── formulas/            (2) Scoring formulas ST/LT
├── backtesting/         (5) Guías y resultados
├── guides/              (2) Guías de usuario
├── technical/           (6) Docs técnicas
├── phases/              (1) Status actual
└── archive/            (12) Docs históricas
```

---

## 🟢 Sistema en Producción

```
Status:        🟢 ACTIVO - Gradual Rollout Fase 1
Tickers:       10 activos (MSFT, ARM, ORCL, META, etc.)
Thresholds:    30% strong_buy, 25% buy
Daemon:        Running (PID: 33327)
Next Scan:     Lunes apertura de mercado
```

**Ver detalles:** [docs/phases/PHASE4_DEPLOYMENT_STATUS.md](docs/phases/PHASE4_DEPLOYMENT_STATUS.md)

---

## 📊 Métricas Validadas

| Métrica | Valor | vs Antiguo |
|---------|-------|------------|
| COMPRA Rate | 19.7% | 12.3x mejora |
| Avg Confidence | 31.4% | Realista |
| Sharpe Ratio | 1.45 | +71% |
| Win Rate | 60% | +11% |
| Backtests | 6,656+ | Validado |

---

## 🔍 Búsqueda por Tema

### Para Trading
- Señales de alta convicción → [docs/guides/HIGH_CONVICTION_GUIDE.md](docs/guides/HIGH_CONVICTION_GUIDE.md)
- Fórmulas de scoring → [docs/formulas/](docs/formulas/)
- Resultados backtesting → [docs/backtesting/COMPARISON_FINAL_RESULTS.md](docs/backtesting/COMPARISON_FINAL_RESULTS.md)

### Para Desarrollo
- Arquitectura → [docs/technical/architecture.md](docs/technical/architecture.md)
- Agente → [docs/technical/AGENT_INTEGRATION_PLAN.md](docs/technical/AGENT_INTEGRATION_PLAN.md)
- Alertas → [docs/technical/ALERT_TRACKING_SYSTEM.md](docs/technical/ALERT_TRACKING_SYSTEM.md)

### Para Operaciones
- Status producción → [docs/phases/PHASE4_DEPLOYMENT_STATUS.md](docs/phases/PHASE4_DEPLOYMENT_STATUS.md)
- Ejecutar backtests → [docs/backtesting/how_to_run_backtesting.md](docs/backtesting/how_to_run_backtesting.md)
- Comandos API → [docs/guides/API_DOCUMENTATION.md](docs/guides/API_DOCUMENTATION.md)

---

## 📝 Comandos Útiles

```bash
# Ver toda la documentación
ls -R docs/

# Buscar en la documentación
grep -r "keyword" docs/

# Ver índice maestro
cat docs/INDEX.md

# Ver status actual
cat docs/phases/PHASE4_DEPLOYMENT_STATUS.md
```

---

**Desarrollado con ❤️ - Spectral Galileo v4.0**
