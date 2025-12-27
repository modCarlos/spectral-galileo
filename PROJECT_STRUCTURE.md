# 📁 Project Structure Guide - Spectral Galileo

**Last Updated**: December 27, 2024  
**Version**: 4.0.0

## 📂 Root Directory (Clean)

```
spectral-galileo/
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── LICENSE                    # License file
└── ...                        # Config files (.plist, .sh)
```

## 🏗️ Main Directories

### `/src/spectral_galileo/` - Source Code (Modular Structure)

```
src/spectral_galileo/
├── __init__.py                # Package exports
│
├── core/                      # Core components
│   ├── agent.py               # FinancialAgent (main analysis engine)
│   ├── portfolio_manager.py   # Portfolio management
│   ├── watchlist_manager.py   # Watchlist management
│   └── data_manager.py        # Data management utilities
│
├── analysis/                  # Analysis modules
│   ├── indicators.py          # Technical indicators (50+)
│   ├── timeframe_analysis.py  # Multi-timeframe analysis
│   ├── macro_analysis.py      # Macroeconomic analysis
│   ├── regime_detection.py    # Market regime detection
│   └── sentiment_analysis.py  # Sentiment analysis
│
├── data/                      # Data handling
│   ├── market_data.py         # Yahoo Finance integration
│   └── report_generator.py    # Report generation
│
├── external/                  # External data sources
│   ├── reddit_sentiment.py    # Reddit sentiment scraping
│   ├── earnings_calendar.py   # Earnings data
│   └── insider_trading.py     # Insider trading activity
│
├── utils/                     # Utilities
│   └── llm_agent.py           # Gemini AI integration
│
└── trading/                   # Trading strategies (future)
    └── (placeholder)
```

### `/config/` - Configuration Files

```
config/
├── alert_config.json          # Alert system configuration
├── portfolio_config.json      # Portfolio settings (account value, risk)
├── watchlist.json             # Active watchlist
└── watchlist_phase3_test10.json  # Testing watchlist
```

**Referenced by:**
- `src/spectral_galileo/core/portfolio_manager.py` → `config/portfolio_config.json`
- `src/spectral_galileo/core/watchlist_manager.py` → `config/watchlist.json`
- Backtesting scripts → `config/watchlist.json`

### `/data/` - Active Data

```
data/
├── portfolio.json             # Active portfolio positions
├── alerts_history.json        # Historical alerts
├── alerts_performance.json    # Alert performance metrics
├── alerts_state.json          # Current alert state
├── alerts_tracker.json        # Alert tracking data
└── watchlist_scan_results.txt # Scan results output
```

**Referenced by:**
- `src/spectral_galileo/core/portfolio_manager.py` → `data/portfolio.json`
- Alert system → `data/alerts_*.json`

### `/backtesting/` - Backtesting Results & Tools

```
backtesting/
├── final_backtesting_20251227_020655.json  # Results
├── final_backtesting_20251227_021851.json  # Results
├── grid_search_results_sequential.json     # Optimization results
├── archived/                               # Historical results
├── data/                                   # Backtesting data (CSV files)
├── documentation/                          # Backtesting docs
├── optimization_results/                   # Optimization outputs
├── results/                                # Result files
└── scripts/                                # Backtesting scripts
```

### `/scripts/` - Utility Scripts

```
scripts/
├── backtesting/               # Backtesting scripts
│   ├── backtesting_comparison.py     # Compare strategies
│   ├── final_backtesting.py          # Final backtesting run
│   └── grid_search_optimizer.py      # Hyperparameter optimization
│
└── tools/                     # Utility tools
    ├── create_icon.py         # Icon creation
    ├── download_missing_data.py  # Data download utility
    └── update_tracker.py      # Tracker update utility
```

### `/tests/` - Test Suite

```
tests/
├── test_agent_comprehensive.py
├── test_agent_scoring.py
├── test_alert_system.py
├── test_indicators.py
├── test_portfolio_manager.py
└── ... (15+ test files)
```

### `/alerts/` - Alert System

```
alerts/
├── __init__.py
├── config.py                  # Alert configuration
├── daemon.py                  # Daemon process
├── market_hours.py            # Market hours checker
├── notifier.py                # macOS notifications
├── state.py                   # State management
└── tracker.py                 # Alert tracking
```

### `/docs/` - Documentation

```
docs/
├── INDEX.md                   # Master documentation index
├── formulas/                  # Scoring formulas
├── backtesting/               # Backtesting docs
├── guides/                    # User guides
├── technical/                 # Technical documentation
├── phases/                    # Development phases
└── archive/                   # Historical docs
```

### `/archive/` - Archived Files

```
archive/
└── backups/                   # Old backups
    ├── agent.py.backup_20251224_171811
    └── watchlist.json.backup_full
```

## 🔗 Important File Paths (for reference)

### Configuration Files
```python
PORTFOLIO_CONFIG = "config/portfolio_config.json"
WATCHLIST_FILE = "config/watchlist.json"
ALERT_CONFIG = "config/alert_config.json"
```

### Data Files
```python
PORTFOLIO_DATA = "data/portfolio.json"
ALERTS_HISTORY = "data/alerts_history.json"
ALERTS_STATE = "data/alerts_state.json"
```

### Backtesting Results
```python
BACKTESTING_DIR = "backtesting/"
RESULTS_DIR = "backtesting/results/"
ARCHIVED_RESULTS = "backtesting/archived/"
```

## 📝 Key Points

### Clean Root
- ✅ Only essential files in root (main.py, requirements.txt, README, LICENSE)
- ✅ All JSON/TXT files organized into subdirectories
- ✅ Backups archived appropriately

### Modular Code Structure
- ✅ Source code in `src/spectral_galileo/`
- ✅ Clear separation of concerns (core, analysis, data, external)
- ✅ Easy to navigate and maintain
- ✅ Ready for PyPI distribution

### Configuration Management
- ✅ All configs centralized in `config/`
- ✅ Easy to find and modify settings
- ✅ Clear naming conventions

### Data Organization
- ✅ Active data separated from results
- ✅ Historical data archived
- ✅ Clear distinction between config and data

## 🚀 Usage Examples

### Import Modules
```python
# Core
from src.spectral_galileo.core.agent import FinancialAgent
from src.spectral_galileo.core import portfolio_manager

# Analysis
from src.spectral_galileo.analysis import indicators
from src.spectral_galileo.data import market_data

# External
from src.spectral_galileo.external import reddit_sentiment
```

### Access Configuration
```python
import json

# Load portfolio config
with open('config/portfolio_config.json') as f:
    config = json.load(f)

# Load watchlist
with open('config/watchlist.json') as f:
    watchlist = json.load(f)
```

### Run Analysis
```bash
# Single ticker
python main.py AAPL

# Multiple tickers from watchlist
python main.py -ws

# Backtesting
venv/bin/python scripts/backtesting/final_backtesting.py
```

## 📊 File Organization Benefits

1. **Clean Root**: Easy to see what's important
2. **Logical Grouping**: Related files together
3. **Easy Navigation**: Clear directory structure
4. **Maintainability**: Easy to find and modify files
5. **Scalability**: Easy to add new features
6. **Professional**: Industry-standard structure

---
*For more information, see [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) and [docs/INDEX.md](docs/INDEX.md)*
