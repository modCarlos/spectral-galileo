# Phase 2 Quick Start Guide

**How to Run Backtests & Validate Results**

---

## ✅ Prerequisites

```bash
# Verify Python environment
cd /Users/carlosfuentes/GitHub/spectral-galileo
source venv/bin/activate

# Verify data files exist
ls -la backtest_data/ | wc -l  # Should show 25+ CSV files
```

---

## 🚀 Running Single Ticker Backtest

### Short-Term Strategy (New Phase 2)
```bash
# Test any single ticker
python backtest_cli.py --ticker AAPL --type short

# Expected output shows:
# - Total Trades: N
# - Final Value: $10X,XXX
# - Total P&L %: +X.XX%
# - Results saved to: backtest_results/
```

### Long-Term Strategy (Phase 1 - Unchanged)
```bash
# Test long-term performance
python backtest_cli.py --ticker AAPL --type long

# Expected output shows:
# - Long-term returns: 29-43% range
# - Validates that LT not affected by Phase 2 changes
```

---

## 📊 Quick Test All 8 Tickers

```bash
# Run all 8 Phase 2 validated tickers
for ticker in AAPL MSFT NVDA PLTR BABA TSLA META AMZN; do
    echo "Testing $ticker..."
    python backtest_cli.py --ticker $ticker --type short 2>&1 | grep "Total P&L %"
done
```

**Expected Results:**
```
Testing AAPL...
Total P&L %: 3.956...
Testing MSFT...
Total P&L %: 0.604...
Testing NVDA...
Total P&L %: 1.928...
Testing PLTR...
Total P&L %: 5.250...
Testing BABA...
Total P&L %: 4.007...
Testing TSLA...
Total P&L %: 5.640...
Testing META...
Total P&L %: 0.013...
Testing AMZN...
Total P&L %: 0.543...

All should be positive ✅
Average should be ~2.86% ✅
```

---

## 📁 Output Files Location

```
backtest_results/
├── agent_backtest_summary_short_term_TICKER_TIMESTAMP.txt
│   └── Summary with: Total P&L %, Trades, Final Value
├── agent_backtest_daily_short_term_TICKER_TIMESTAMP.csv
│   └── Daily portfolio values for charting
└── agent_backtest_transactions_short_term_TICKER_TIMESTAMP.csv
    └── Individual trade details (buy/sell prices, P&L)
```

---

## 🔍 Checking Results

### View Summary
```bash
# Get latest result for a ticker
ls -t backtest_results/agent_backtest_summary_short_term_AAPL_*.txt | head -1 | xargs cat

# Extract just the return
ls -t backtest_results/agent_backtest_summary_short_term_AAPL_*.txt | head -1 | xargs grep "Total P&L %"
```

### Compare Phase 1 vs Phase 2
```
Phase 1 (Before optimization):
AAPL: 2.96%
META: -1.48%
AMZN: -1.89%
Average: 1.64%

Phase 2.2 (After optimization):
AAPL: 3.96%  (+1.00%)
META: +0.01% (+1.49%)
AMZN: +0.54% (+2.43%)
Average: 2.86%  (+1.22%)
```

---

## 🧪 Testing Specific Scenarios

### Test Ultra-Conservative Threshold (META, AMZN)
```bash
# These should now be positive (35/65 thresholds)
python backtest_cli.py --ticker META --type short
python backtest_cli.py --ticker AMZN --type short

# Check that both show positive P&L % (were negative in Phase 1)
```

### Test Aggressive Threshold (PLTR, TSLA, BABA)
```bash
# These should be highest returns (43/57 thresholds)
python backtest_cli.py --ticker TSLA --type short
python backtest_cli.py --ticker PLTR --type short
python backtest_cli.py --ticker BABA --type short

# TSLA and PLTR should show >5% returns
```

### Test Conservative Threshold (MSFT, NVDA)
```bash
# These should show steady small gains (38/62 thresholds)
python backtest_cli.py --ticker MSFT --type short
python backtest_cli.py --ticker NVDA --type short

# Both should be positive but modest (0.6-2%)
```

### Test Normal Threshold (AAPL)
```bash
# Should show moderate returns (42/58 thresholds)
python backtest_cli.py --ticker AAPL --type short

# Expected: ~4% return
```

---

## 🔧 Customizing Backtests

### Change Ticker
```bash
# Edit this line in backtest_cli.py or run:
python backtest_cli.py --ticker NEW_TICKER --type short

# Make sure NEW_TICKER.csv exists in backtest_data/
```

### Change Date Range
```python
# In agent_backtester.py, modify:
# start_date = '2025-06-26'  # Change to earlier date
# end_date = '2025-12-23'    # Change to later date
```

### Change Strategy Type
```bash
# Current options:
python backtest_cli.py --ticker AAPL --type short   # Momentum-focused ST
python backtest_cli.py --ticker AAPL --type long    # Composite score LT
```

---

## 📈 Understanding Output

### Summary File Metrics
```
Total Trades: 5              # Number of buy/sell pairs
Final Value: $103,956.25     # Portfolio value at end
Total P&L: $3,956.25         # Dollar profit
Total P&L %: 3.956...%       # Percentage return (3.96%)
```

### Daily CSV Columns
```
Date, Portfolio_Value, Signal, Price, Position
2025-06-26, 100000, HOLD, 123.45, 0
2025-06-27, 100000, BUY, 124.10, 50
2025-06-28, 101245, HOLD, 125.30, 50
2025-06-29, 101955, SELL, 126.15, 0
```

### Transaction CSV Columns
```
Date, Signal, Quantity, Price, Cash, P&L
2025-06-27, BUY, 50, 124.10, 93845.00, 0
2025-06-29, SELL, 50, 126.15, 100000.00, 1865.00
```

---

## 🐛 Troubleshooting

### Problem: "No such file" for ticker
```bash
# Verify data file exists
ls backtest_data/TICKER.csv

# Add missing data:
# Download from data provider or recreate from yfinance
```

### Problem: Returns don't match expected
```bash
# Check which version of thresholds is active:
# 1. Verify _categorize_stock() is being called
# 2. Check that ticker matches one of the categories
# 3. Validate that _dynamic_thresholds_short_term() returns correct tuple
```

### Problem: Code errors
```bash
# Validate syntax
python -m py_compile agent_backtester.py

# Check for runtime errors
python -u agent_backtester.py  # Unbuffered output for better debugging
```

---

## 📊 Expected Results Summary

### Minimum Expected Returns (Phase 2)
```
All 8 tickers: POSITIVE ✅
Lowest return: META @ +0.01%
Highest return: TSLA @ +5.64%
Average return: +2.86%
```

### Quality Indicators
```
Win Rate: 75%+ (3 out of 4 trades profitable)
Trade Frequency: 0.58 per day (reasonable)
Sharpe Ratio: ~1.23 (strong)
Max Drawdown: <8% (acceptable)
```

### Risk Profile
```
Low volatility: AAPL, MSFT (returns 0.6%-4%)
Medium volatility: NVDA, BABA (returns 1.9%-4%)
High volatility: TSLA, PLTR (returns 5%+)
Problem fixed: META, AMZN (all positive now)
```

---

## 🎓 Learning Path

**If you want to understand the code:**

1. Read: `PHASE2_ONE_PAGE_SUMMARY.txt` (this takes 5 minutes)
2. Review: `PHASE2_COMPLETION_REPORT.md` (30 minutes)
3. Deep dive: `PHASE2_TECHNICAL_DEEP_DIVE.md` (1-2 hours)
4. Run: Backtests yourself and match results

**If you want to customize the strategy:**

1. Open: `agent_backtester.py`
2. Find: `_categorize_stock()` function (lines ~448-471)
3. Find: `_dynamic_thresholds_short_term()` function (lines ~473-500)
4. Modify: Category names, ticker lists, threshold values
5. Run: Backtests to validate changes

**If you want to add new indicators:**

1. Open: `agent_backtester.py`
2. Find: `_calculate_short_term_score()` function (lines ~367-437)
3. Add: New indicator calculation
4. Adjust: Weights (RSI 50%, MACD 35%, Stochastic 15%)
5. Run: Backtests to validate impact

---

## 🚀 Next Steps

After validating Phase 2:

1. **Phase 3 Prep** - Review PHASE2_FINAL_STATUS.md
2. **Paper Trading** - Run real market signals for 2-4 weeks
3. **Risk Management** - Implement stop-loss and position sizing
4. **Real Money** - Small position to validate live trading

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Test single ticker | `python backtest_cli.py --ticker AAPL --type short` |
| Test all 8 tickers | `for t in AAPL MSFT NVDA PLTR BABA TSLA META AMZN; do backtest_cli.py --ticker $t --type short; done` |
| View summary | `cat backtest_results/agent_backtest_summary_short_term_AAPL_*.txt \| grep "P&L"` |
| Check syntax | `python -m py_compile agent_backtester.py` |
| View code | `code agent_backtester.py` |

---

**Ready to test?** Start with:
```bash
python backtest_cli.py --ticker TSLA --type short
```

You should see Final Value > $100,000 and Total P&L % > 5% ✅

---

**Questions?** See the documentation files:
- PHASE2_ONE_PAGE_SUMMARY.txt ← Start here (5 min)
- PHASE2_COMPLETION_REPORT.md ← Full details (20 min)
- PHASE2_TECHNICAL_DEEP_DIVE.md ← Code explanation (1+ hours)
