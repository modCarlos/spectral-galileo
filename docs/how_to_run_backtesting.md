# Backtesting System - Execution Guide

**Author:** Spectral Galileo  
**Date:** December 24, 2025  
**Version:** 3.0 (Phase 3 - Risk Management + Parameter Optimization)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Installation & Setup](#installation--setup)
4. [Running Backtests](#running-backtests)
5. [Parameter Optimization](#parameter-optimization)
6. [Risk Management Configuration](#risk-management-configuration)
7. [Analyzing Results](#analyzing-results)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)

---

## Quick Start

### 30-Second Backtest

```bash
# 1. Navigate to backtesting folder
cd /Users/carlosfuentes/GitHub/spectral-galileo/backtesting

# 2. Activate virtual environment
source ../venv/bin/activate

# 3. Run a simple backtest (8 tickers, 1 year)
python scripts/agent_backtester.py \
  --tickers AAPL MSFT META GOOGL AMZN NVDA JPM JNJ \
  --start-date 2024-06-26 \
  --end-date 2025-12-23 \
  --initial-cash 100000 \
  --analysis-type short_term

# 4. View results
open results/backtest_results_YYYYMMDD_HHMMSS.html
```

**Expected Runtime:** 3-5 minutes  
**Expected Output:** HTML report with performance metrics, charts, and trade log

---

## System Overview

### Architecture

```
backtesting/
├── scripts/           # Backtesting Python scripts
│   ├── agent_backtester.py          # Main backtesting engine
│   ├── parameter_optimizer.py       # Grid search & walk-forward
│   ├── backtest_cli.py             # Command-line interface
│   ├── advanced_metrics.py         # Performance calculations
│   └── report_generator_v2.py      # HTML report generation
├── data/              # Historical price data (CSV files)
├── results/           # Backtest results & reports
├── optimization_results/ # Parameter optimization outputs
├── reports/           # Generated HTML/PDF reports
└── tests/             # Unit tests for validation
```

### Key Components

1. **AgentBacktester**: Core backtesting engine using agent-based signals
2. **ParameterOptimizer**: Grid search and walk-forward validation
3. **BacktestDataManager**: Historical data loading and caching
4. **BacktestPortfolio**: Position tracking and P&L calculation
5. **AdvancedMetricsCalculator**: Sharpe, Sortino, Calmar ratios
6. **ReportGeneratorV2**: HTML report generation with charts

---

## Installation & Setup

### Prerequisites

- Python 3.10+
- pip package manager
- 500MB free disk space (for data)
- 8GB RAM (for parallel processing)

### Step 1: Clone Repository

```bash
git clone https://github.com/modCarlos/spectral-galileo.git
cd spectral-galileo
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required Packages:**
```
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.28
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.3.0
pytest>=7.4.0
```

### Step 4: Download Historical Data

```bash
cd backtesting
python scripts/backtest_data_manager.py \
  --download \
  --tickers AAPL MSFT META GOOGL AMZN NVDA JPM JNJ \
  --start-date 2024-01-01 \
  --end-date 2025-12-23
```

**Expected Output:**
```
📥 Downloading historical data...
✓ AAPL: 375 days downloaded
✓ MSFT: 375 days downloaded
...
✨ 8/8 tickers downloaded successfully
```

### Step 5: Verify Installation

```bash
pytest tests/test_rm_integration.py -v
```

**Expected Output:**
```
tests/test_rm_integration.py::test_calculate_atr PASSED
tests/test_rm_integration.py::test_calculate_position_size PASSED
...
======================== 8 passed in 2.34s ========================
```

---

## Running Backtests

### Basic Usage

#### Command-Line Interface

```bash
python scripts/agent_backtester.py \
  --tickers AAPL MSFT META \
  --start-date 2024-06-26 \
  --end-date 2025-12-23 \
  --initial-cash 100000 \
  --analysis-type short_term \
  --output-dir results/
```

#### Python Script

```python
from scripts.agent_backtester import AgentBacktester

# Initialize backtester
backtester = AgentBacktester(
    tickers=['AAPL', 'MSFT', 'META'],
    start_date='2024-06-26',
    end_date='2025-12-23',
    initial_cash=100000.0,
    analysis_type='short_term',  # or 'long_term'
    data_dir='./data',
    results_dir='./results'
)

# Load historical data
backtester.load_data()

# Run backtest
results = backtester.run_backtest()

# Generate report
backtester.generate_report(results)
```

### Analysis Types

#### Short-Term (3-6 months)

**Focus:** Momentum trading, technical indicators  
**Scoring:** 85% Technical, 15% Volatility, 0% Fundamental  
**Typical Return:** 2.5-4.0% per 6 months  
**Max Drawdown:** 6-9%  

```bash
python scripts/agent_backtester.py \
  --analysis-type short_term \
  --tickers PLTR NVDA META AAPL
```

#### Long-Term (2-5 years)

**Focus:** Value investing, fundamentals  
**Scoring:** 50% Technical, 35% Fundamental, 15% Sentiment  
**Typical Return:** 8-15% per year  
**Max Drawdown:** 10-18%  

```bash
python scripts/agent_backtester.py \
  --analysis-type long_term \
  --tickers AAPL MSFT JPM JNJ
```

### Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--tickers` | list | Required | Space-separated list of tickers |
| `--start-date` | str | Required | Start date (YYYY-MM-DD) |
| `--end-date` | str | Required | End date (YYYY-MM-DD) |
| `--initial-cash` | float | 100000.0 | Initial portfolio cash |
| `--analysis-type` | str | short_term | 'short_term' or 'long_term' |
| `--data-dir` | str | ./data | Historical data directory |
| `--output-dir` | str | ./results | Results output directory |
| `--enable-rm` | bool | True | Enable risk management (Phase 3) |
| `--max-risk` | float | 0.02 | Max risk per trade (2% default) |
| `--verbose` | bool | False | Enable debug logging |

---

## Parameter Optimization

### Grid Search

**Purpose:** Find optimal buy/sell thresholds for different stock categories

#### Run Grid Search

```bash
python scripts/parameter_optimizer.py \
  --mode grid_search \
  --tickers AAPL MSFT META NVDA \
  --start-date 2024-06-26 \
  --end-date 2025-12-23 \
  --output-file optimization_results/grid_search.json
```

**Process:**
1. Tests 64 threshold combinations (buy: 20-45, sell: 55-70)
2. Evaluates each combination via full backtest
3. Ranks by Sharpe ratio
4. Outputs optimal parameters by category

**Expected Runtime:** 30-45 minutes (256 backtests)

#### Grid Search Results Format

```json
{
  "ultra_conservative": {
    "buy_threshold": 25,
    "sell_threshold": 60,
    "sharpe": 1.52,
    "return": 3.2,
    "max_dd": 6.8
  },
  "conservative": {
    "buy_threshold": 35,
    "sell_threshold": 58,
    "sharpe": 1.48,
    "return": 3.0,
    "max_dd": 7.2
  },
  ...
}
```

### Walk-Forward Validation

**Purpose:** Validate parameter robustness across time

#### Run Walk-Forward Test

```bash
python scripts/phase3_walk_forward_parallel.py \
  --tickers AAPL META MSFT PLTR \
  --start-date 2024-06-26 \
  --end-date 2025-12-23 \
  --window-size 60 \
  --step-size 15 \
  --output-file results/walk_forward_validation.log
```

**Process:**
1. Splits data into 25 rolling windows
2. Optimizes parameters on in-sample (60 days)
3. Tests on out-of-sample (15 days)
4. Measures OOS performance variance

**Expected Runtime:** 2-3 hours (6,400 backtests, parallel)

#### Parallel Processing

```bash
# Automatic CPU detection (uses all cores)
python scripts/phase3_walk_forward_parallel.py --parallel

# Manual core count
python scripts/phase3_walk_forward_parallel.py --cores 8
```

**Performance:**
- Sequential: ~12 hours (1 core)
- Parallel: ~2.5 hours (8 cores)
- Speedup: 4.8x

### Interpreting Optimization Results

#### Good Parameters

✅ **Low OOS Variance:** Std dev < 0.03% (not overfit)  
✅ **Consistent Sharpe:** Sharpe > 1.0 across all windows  
✅ **Stable Drawdown:** Max DD < 10% across all windows  

#### Overfit Parameters

⚠️ **High OOS Variance:** Std dev > 0.10% (unstable)  
⚠️ **Sharpe Degradation:** In-sample 1.5 → OOS 0.8  
⚠️ **Inconsistent Returns:** -5% to +15% across windows  

---

## Risk Management Configuration

### Phase 3 Features

1. **Dynamic Position Sizing:** ATR-based, caps risk at 2% per trade
2. **Stop Loss:** Entry - (ATR × 1.5)
3. **Take Profit:** Entry + (ATR × 3.0)
4. **Daily Validation:** Checks SL/TP on every market day

### Enable/Disable Risk Management

```python
backtester = AgentBacktester(
    tickers=['AAPL', 'MSFT'],
    start_date='2024-06-26',
    end_date='2025-12-23',
    initial_cash=100000.0,
    risk_management_enabled=True  # Set to False to disable
)
```

### Configure Risk Parameters

```python
# In agent_backtester.py, modify:
self.max_risk_per_trade = 0.02  # 2% default
self.stop_loss_multiplier = 1.5  # ATR multiplier for SL
self.take_profit_multiplier = 3.0  # ATR multiplier for TP
self.max_position_size_pct = 0.20  # 20% of account max
```

### Risk Management Metrics

After running a backtest, check RM performance:

```bash
# Count RM events
grep "\[TP HIT\]" results/backtest.log | wc -l
grep "\[SL HIT\]" results/backtest.log | wc -l

# Calculate TP:SL ratio
python scripts/analyze_rm_performance.py --log-file results/backtest.log
```

**Target Metrics:**
- TP:SL Ratio: > 2.5:1 (more profitable exits than losses)
- TP Hit Rate: > 70% (most exits are profitable)
- Max Drawdown: < 10% (risk controlled)

---

## Analyzing Results

### Output Files

After running a backtest, you'll find:

```
results/
├── backtest_results_20251224_103045.html   # Main report
├── backtest_results_20251224_103045.json   # Raw data
├── backtest_log_20251224_103045.log       # Detailed log
└── trades_20251224_103045.csv             # Trade history
```

### HTML Report Sections

1. **Executive Summary**
   - Total return, Sharpe ratio, win rate
   - Portfolio value chart
   - Key metrics table

2. **Performance by Ticker**
   - Individual ticker returns
   - Trade count, win rate per ticker
   - Best/worst performers

3. **Trade Analysis**
   - Full trade log with entry/exit dates
   - P&L per trade
   - Hold duration distribution

4. **Risk Metrics**
   - Max drawdown chart
   - Volatility analysis
   - Sharpe, Sortino, Calmar ratios

5. **Signal Analysis**
   - Agent score distribution
   - Threshold effectiveness
   - False signal rate

### JSON Results Format

```json
{
  "summary": {
    "total_return_pct": 2.86,
    "sharpe_ratio": 1.28,
    "max_drawdown_pct": 9.1,
    "win_rate": 56.0,
    "total_trades": 120
  },
  "by_ticker": {
    "AAPL": {
      "return_pct": 3.5,
      "trades": 15,
      "win_rate": 60.0
    },
    ...
  },
  "trades": [
    {
      "ticker": "AAPL",
      "entry_date": "2024-07-15",
      "exit_date": "2024-08-20",
      "entry_price": 185.50,
      "exit_price": 192.30,
      "shares": 50,
      "pnl": 340.00,
      "return_pct": 3.67,
      "exit_reason": "TP_HIT"
    },
    ...
  ]
}
```

### Command-Line Result Analysis

```bash
# Quick stats
python scripts/analyze_results.py --results-file results/backtest_results.json

# Compare multiple backtests
python scripts/compare_results.py \
  --files results/phase2.json results/phase3.json

# Generate performance chart
python scripts/plot_performance.py --results-file results/backtest_results.json
```

---

## Troubleshooting

### Common Issues

#### 1. "No data loaded for ticker"

**Cause:** Missing historical data  
**Solution:**
```bash
python scripts/backtest_data_manager.py \
  --download \
  --ticker AAPL \
  --start-date 2024-01-01
```

#### 2. "Insufficient data for analysis"

**Cause:** Start date too close to end date  
**Solution:** Ensure at least 60 days between start and end dates

#### 3. "Agent timeout error"

**Cause:** Network issues or API rate limiting  
**Solution:**
```python
# In agent_backtester.py, increase timeout
agent.timeout = 30  # Default 10 seconds
```

#### 4. "MemoryError during parallel processing"

**Cause:** Too many parallel processes  
**Solution:**
```bash
# Reduce core count
python scripts/phase3_walk_forward_parallel.py --cores 4
```

#### 5. "Division by zero in Sharpe calculation"

**Cause:** Zero returns or zero volatility  
**Solution:** Check if ticker has price data for entire period

### Debug Logging

Enable verbose logging to diagnose issues:

```bash
python scripts/agent_backtester.py \
  --verbose \
  --log-file debug.log \
  --tickers AAPL
```

Check log for detailed execution trace:

```bash
tail -f debug.log
```

### Performance Issues

#### Slow Backtests

- **Reduce date range:** Test 6 months instead of 2 years
- **Reduce tickers:** Test 4 tickers instead of 8
- **Cache data:** Pre-download all historical data
- **Use parallel mode:** Enable `--parallel` flag

#### High Memory Usage

- **Process tickers sequentially:** Disable parallel mode
- **Reduce window size:** Use 30-day windows instead of 60
- **Clear cache:** Delete `.backtest_cache/` folder

---

## Advanced Usage

### Custom Scoring Functions

Override default scoring in `agent_backtester.py`:

```python
def _calculate_custom_score(self, analysis: Dict) -> float:
    """
    Custom scoring logic
    """
    score = 50  # Start at neutral
    
    # Your custom logic here
    if analysis.get('technical', {}).get('rsi', 50) < 30:
        score += 20
    
    return max(0, min(100, score))
```

### Custom Thresholds

Define your own threshold logic:

```python
def _custom_thresholds(self, ticker: str, volatility: float) -> tuple:
    """
    Custom buy/sell thresholds
    """
    if ticker in ['AAPL', 'MSFT']:
        return 30.0, 70.0  # Conservative
    elif volatility > 0.10:
        return 45.0, 55.0  # Aggressive for volatile stocks
    else:
        return 40.0, 60.0  # Default
```

### Integration with Live Trading

To use backtested parameters in production:

```python
# 1. Load optimal parameters from grid search
import json
with open('optimization_results/grid_search.json', 'r') as f:
    params = json.load(f)

# 2. Configure live agent
from agent import FinancialAgent

agent = FinancialAgent(
    ticker_symbol='AAPL',
    is_short_term=True
)

# 3. Apply optimal thresholds
conservative_params = params['conservative']
buy_threshold = conservative_params['buy_threshold']  # 35
sell_threshold = conservative_params['sell_threshold']  # 58

# 4. Generate signals using optimized thresholds
analysis = agent.run_analysis()
score = calculate_short_term_score(analysis)
signal = 'BUY' if score < buy_threshold else 'SELL' if score > sell_threshold else 'HOLD'
```

### Batch Processing

Run multiple backtests in sequence:

```bash
#!/bin/bash
# batch_backtest.sh

TICKERS=("AAPL MSFT" "META GOOGL" "JPM JNJ" "NVDA PLTR")
START="2024-06-26"
END="2025-12-23"

for ticker_group in "${TICKERS[@]}"; do
  echo "Testing: $ticker_group"
  python scripts/agent_backtester.py \
    --tickers $ticker_group \
    --start-date $START \
    --end-date $END \
    --output-dir results/batch_$(date +%Y%m%d)/
done
```

### API Integration

Expose backtesting as REST API:

```python
# api_server.py
from flask import Flask, request, jsonify
from scripts.agent_backtester import AgentBacktester

app = Flask(__name__)

@app.route('/backtest', methods=['POST'])
def run_backtest():
    data = request.json
    
    backtester = AgentBacktester(
        tickers=data['tickers'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        initial_cash=data.get('initial_cash', 100000)
    )
    
    backtester.load_data()
    results = backtester.run_backtest()
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(port=5000)
```

---

## Performance Benchmarks

### Hardware Specifications

- **CPU:** Apple M1 (8 cores)
- **RAM:** 16GB
- **Storage:** SSD

### Execution Times

| Operation | Tickers | Days | Runtime | Notes |
|-----------|---------|------|---------|-------|
| Simple Backtest | 8 | 375 | 3-5 min | Single thread |
| Grid Search | 4 | 375 | 30-45 min | 256 combinations |
| Walk-Forward (Sequential) | 4 | 375 | ~12 hours | Single thread |
| Walk-Forward (Parallel) | 4 | 375 | ~2.5 hours | 8 cores, 4.8x speedup |
| Final Validation | 8 | 375 | 15-20 min | Parallel processing |

### Optimization Tips

1. **Parallel Processing:** Use all available CPU cores
2. **Data Caching:** Pre-download all historical data
3. **Incremental Testing:** Start with 4 tickers, expand to 8
4. **Date Range:** Test 6 months first, then expand to 1 year

---

## Support & Resources

### Documentation

- **Phase 2 Results:** `../PHASE2_RESULTS_SUMMARY.md`
- **Phase 3 Results:** `../PHASE3_RESULTS.md`
- **Technical Deep Dive:** `../BACKTESTING_CODE_DEEP_DIVE.md`
- **Architecture:** `../BACKTESTING_ARCHITECTURE.md`

### Example Scripts

```bash
# Example 1: Quick 4-ticker test
python scripts/example_backtest.py

# Example 2: Long-term validation
python scripts/long_term_example.py

# Example 3: Quick agent test
python scripts/quick_agent_test.py
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_rm_integration.py -v

# Run with coverage
pytest tests/ --cov=scripts/ --cov-report=html
```

### Contact

**GitHub:** https://github.com/modCarlos/spectral-galileo  
**Issues:** https://github.com/modCarlos/spectral-galileo/issues

---

## Appendix: Configuration Reference

### Default Parameters

```python
# AgentBacktester defaults
initial_cash = 100000.0
analysis_type = 'short_term'
lookback_days = 60
max_risk_per_trade = 0.02  # 2%
max_position_size_pct = 0.20  # 20%

# Risk Management defaults
stop_loss_multiplier = 1.5
take_profit_multiplier = 3.0
atr_periods = 14

# Dynamic Thresholds (Short-Term)
ultra_conservative = (35, 65)  # META, AMZN
conservative = (38, 62)        # MSFT, NVDA
normal = (42, 58)              # JPM, JNJ, KO
high_volatility = (43, 57)     # PLTR, BABA

# Grid Search defaults
buy_range = range(20, 46, 5)    # [20, 25, 30, 35, 40, 45]
sell_range = range(55, 71, 5)   # [55, 60, 65, 70]
combinations = 64

# Walk-Forward defaults
window_size = 60  # days
step_size = 15    # days
iterations = 25
```

### Environment Variables

```bash
# Set data directory
export BACKTEST_DATA_DIR=/path/to/data

# Set results directory
export BACKTEST_RESULTS_DIR=/path/to/results

# Enable debug mode
export BACKTEST_DEBUG=1

# Set log level
export BACKTEST_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

---

**Document Status:** Complete  
**Last Updated:** December 24, 2025  
**Version:** 3.0 (Phase 3)  
**Tested With:** Python 3.14, macOS (Apple M1)
