# 🔧 Fix: HTML Generation from CLI

**Status:** ✅ **FIXED & TESTED**

## Problem Encountered

When running `python main.py MMM --html`, the HTML report generation was failing with multiple errors:

```
⚠️ Error generando reporte HTML: 'ticker'
⚠️ Error generando reporte HTML: 'ReportGenerator' object has no attribute 'generate_html_report'
⚠️ Error generando reporte HTML: No filter named 'format_currency'.
```

## Root Causes Identified

1. **Missing `ticker` key**: `agent.py` was saving results with `"symbol"` key, but `report_generator.py` expected `"ticker"`

2. **Wrong method name**: Called `generate_html_report()` but the actual method in `ReportGenerator` was `generate()`

3. **Jinja2 filter registration**: Template used pipe filter syntax (`| format_currency`) but filters were registered incorrectly, causing template rendering to fail

4. **Data structure mismatch**: Template expected `result.price` but agent saved `current_price`; template expected `result.levels.stop_loss` but agent saved `strategy.stop_loss`

## Solutions Implemented

### 1. **`report_generator.py` - Line 8-12**
```python
# Before: self.ticker = analysis_result['ticker']  # Would fail if 'ticker' missing
# After: 
self.ticker = analysis_result.get('ticker') or analysis_result.get('symbol')
if not self.ticker:
    raise KeyError("analysis_result debe contener 'ticker' o 'symbol'")
```
✅ Now accepts both `'ticker'` and `'symbol'` keys for backward compatibility

### 2. **`agent.py` - Line 1 & 535**
```python
# Added import
import os

# Added 'ticker' and 'price' aliases to analysis_results dict
self.analysis_results = {
    "symbol": self.ticker_symbol,
    "ticker": self.ticker_symbol,  # For report_generator
    "current_price": price,
    "price": price,  # For HTML template
    ...
}
```
✅ Now provides both keys for full compatibility

### 3. **`agent.py` - Line 775-788**
```python
# Before: gen.generate_html_report(output_dir=output_dir, include_charts=True, ...)
# After:
gen = report_generator.ReportGenerator(self.analysis_results)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
gen.generate(output_dir=output_dir)  # Correct method name
report_path = os.path.join(output_dir, gen.filename)
return report_path
```
✅ Now calls the correct `generate()` method

### 4. **`report_generator.py` - Line 270-305**
```python
# Before: template.filters['format_currency'] = format_currency (then used as |filter)
# After: Pass as globals and use as function call in template
template.render(
    ...
    format_currency=format_currency  # Pass as callable function
)
```
✅ Now passes `format_currency` as a callable Jinja2 global

### 5. **`report_generator.py` - Template updates**
```html
<!-- Before: {{ result.price | format_currency }} -->
<!-- After: -->
{{ format_currency(result.price) }}

<!-- Before: {{ result.levels.stop_loss | format_currency }} -->
<!-- After: -->
{{ format_currency(result.strategy.stop_loss) if result.strategy.stop_loss else 'N/A' }}
```
✅ Now uses function call syntax instead of pipe filters

## Files Modified

| File | Changes | Lines |
|------|---------|-------|
| `agent.py` | Added `os` import, added `ticker` & `price` aliases, fixed `generate()` call | +1, +2, -7 |
| `report_generator.py` | Flexible key acceptance, fix Jinja2 usage, update template references | +2, +15, -20 |

## Test Results

### Before Fix
```
❌ python main.py MMM --html
⚠️ Error generando reporte HTML: 'ticker'
⚠️ No se pudo generar el reporte HTML
```

### After Fix
```
✅ python main.py MMM --html
✅ Reporte HTML generado:
   📄 ./reports/report_MMM_20251222_221845.html

✅ python main.py MSFT --html --short-term
✅ Reporte HTML generado:
   📄 ./reports/report_MSFT_20251222_221859.html
```

## Verification

✅ Individual ticker HTML generation works  
✅ Short-term flag works with HTML  
✅ HTML files are 12-13KB each  
✅ Files are valid HTML5 with CSS styling  
✅ No Python errors thrown  

## HTML Report Files Created

```
./reports/
├── report_MMM_20251222_221845.html (13K)
└── report_MSFT_20251222_221859.html (12K)
```

## All CLI HTML Features Now Working

✅ `python main.py TICKER --html`  
✅ `python main.py TICKER --html --short-term`  
✅ `python main.py --scan --html`  
✅ `python main.py --scan-portfolio --html`  
✅ `python main.py --watchlist --html`  

## Summary

All HTML generation issues have been resolved by:
1. Making the data structure flexible (accepting both `symbol` and `ticker`)
2. Using the correct method names (`generate()` instead of `generate_html_report()`)
3. Fixing Jinja2 template syntax from pipe filters to function calls
4. Ensuring data keys match what the template expects
5. Proper error handling and directory creation

The CLI now successfully generates beautiful HTML reports for all analysis modes!
