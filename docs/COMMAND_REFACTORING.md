# Command Refactoring - Simplificación de CLI

## Objetivo

Simplificar los comandos del CLI para hacerlos más memorables y fáciles de usar, usando aliases cortos y eliminando redundancias.

## Cambios Implementados

### Comandos Simplificados

| Categoría | Antes | Ahora | Descripción |
|-----------|-------|-------|-------------|
| **Análisis** | | | |
| Modo corto plazo | `--short-term` | `-st` | Mantiene `--short-term` como alias |
| **Escáner** | | | |
| Escanear mercado | `--scan`, `--reviewSP500` | `-s`, `--scan` | Eliminado alias `--reviewSP500` |
| **Watchlist** | | | |
| Agregar a watchlist | `--watch` | `-w`, `--watch` | Agregado alias corto |
| Quitar de watchlist | `--unwatch` | `-uw`, `--unwatch` | Agregado alias corto |
| Escanear watchlist | `--watchlist`, `--favs` | `-ws`, `--watchlist` | Eliminado alias `--favs` |
| **Portafolio** | | | |
| Agregar al portafolio | `--add` | `-a`, `--add` | Agregado alias corto |
| Agregar con RM auto | `--add-auto` | `-aa`, `--add-auto` | Agregado alias corto |
| Ver portafolio | `--scan-portfolio`, `--my-stocks` | `-p`, `--portfolio` | Eliminados aliases confusos |
| Quitar acción | `--remove` | `-r`, `--remove` | Agregado alias corto |
| Quitar todas | `--remove-all` | `-ra`, `--remove-all` | Agregado alias corto |
| Check Risk Management | `--check-rm`, `--check-risk` | `-rm`, `--check-rm` | Eliminado alias `--check-risk` |
| **Backtesting** | | | |
| Backtesting | `--backtest` | `-b`, `--backtest` | Agregado alias corto |
| **IA** | | | |
| Análisis con IA | `--ai` | `--ai` | Sin cambios |
| **Reportes** | | | |
| Generar HTML | `--html` | `--html` | Sin cambios |

## Ejemplos de Uso Actualizados

### Análisis
```bash
# Análisis largo plazo
python main.py AAPL

# Análisis corto plazo
python main.py AAPL -st

# Escanear mercado (largo plazo)
python main.py -s

# Escanear mercado (corto plazo)
python main.py -s -st
```

### Portafolio
```bash
# Ver portafolio
python main.py -p

# Verificar Stop Loss y Take Profit
python main.py -rm

# Agregar acción
python main.py -a AAPL
python main.py -a AAPL 150.50

# Agregar con RM automático
python main.py -aa AAPL
python main.py -aa AAPL -st

# Quitar acción
python main.py -r AAPL
python main.py -ra AAPL
python main.py -ra  # Vaciar todo
```

### Watchlist
```bash
# Agregar a watchlist
python main.py -w AAPL

# Quitar de watchlist
python main.py -uw AAPL

# Escanear watchlist
python main.py -ws
python main.py -ws -st
```

### Backtesting
```bash
# Backtesting período reciente
python main.py -b NVDA

# Backtesting período custom
python main.py -b NVDA 2024-01-01 2024-12-31
```

## Beneficios

1. **Comandos más cortos**: `-s` vs `--scan`, `-p` vs `--scan-portfolio`
2. **Más memorables**: Aliases intuitivos (s=scan, p=portfolio, w=watch)
3. **Menos confusión**: Eliminados aliases redundantes (`--reviewSP500`, `--favs`, `--my-stocks`, `--check-risk`)
4. **Consistencia**: Todos los comandos principales tienen alias cortos
5. **Backward compatible**: Los aliases largos siguen funcionando

## Cambios Internos

### Código Modificado

1. **main.py líneas 291-325**: Definición de argumentos
   - Agregados aliases cortos (`-s`, `-st`, `-w`, `-uw`, `-ws`, `-a`, `-aa`, `-p`, `-r`, `-ra`, `-rm`, `-b`)
   - Eliminados aliases redundantes (`--reviewSP500`, `--favs`, `--my-stocks`, `--check-risk`)
   - Simplificados textos de ayuda

2. **main.py línea 452**: Cambio de referencia
   - Antes: `args.scan_portfolio`
   - Ahora: `args.portfolio`

3. **main.py líneas 246-278**: Ejemplos de uso actualizados
   - Todos los ejemplos usan los nuevos comandos cortos
   - Clarificadas descripciones

## Testing

Comandos probados:
- ✅ `python main.py -s` → Escanear mercado
- ✅ `python main.py -ws` → Escanear watchlist
- ✅ `python main.py -p` → Ver portafolio
- ✅ `python main.py -h` → Help actualizado

## Compatibilidad

**Backward compatible**: Todos los comandos largos anteriores siguen funcionando:
- `--scan` ✅
- `--watchlist` ✅
- `--add` ✅
- `--add-auto` ✅
- `--portfolio` ✅ (reemplaza `--scan-portfolio`)
- `--check-rm` ✅
- `--remove` ✅
- `--remove-all` ✅
- `--backtest` ✅
- `--short-term` ✅

**Eliminados** (aliases redundantes):
- `--reviewSP500` ❌ (usar `-s` o `--scan`)
- `--favs` ❌ (usar `-ws` o `--watchlist`)
- `--my-stocks` ❌ (usar `-p` o `--portfolio`)
- `--scan-portfolio` ❌ (usar `-p` o `--portfolio`)
- `--check-risk` ❌ (usar `-rm` o `--check-rm`)

## Fecha de Implementación

24 de diciembre de 2024

## Versión

Sistema de Excelencia 2.0 - Post Phase 4C
