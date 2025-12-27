"""
Spectral Galileo - Advanced Financial Analysis System

A modular trading system with technical analysis, fundamental analysis,
external data integration, and backtesting capabilities.
"""

__version__ = "4.0.0"
__author__ = "Carlos Fuentes"

# Core classes and modules
from src.spectral_galileo.core.agent import FinancialAgent
from src.spectral_galileo.core.data_manager import DataManager
from src.spectral_galileo.core import portfolio_manager
from src.spectral_galileo.core import watchlist_manager

# Analysis modules
from src.spectral_galileo.analysis import indicators
from src.spectral_galileo.analysis import timeframe_analysis
from src.spectral_galileo.analysis import macro_analysis
from src.spectral_galileo.analysis import regime_detection
from src.spectral_galileo.analysis import sentiment_analysis

# Data modules
from src.spectral_galileo.data import market_data
from src.spectral_galileo.data import report_generator

# External data modules
from src.spectral_galileo.external import reddit_sentiment
from src.spectral_galileo.external import earnings_calendar
from src.spectral_galileo.external import insider_trading

# Utils
from src.spectral_galileo.utils import llm_agent

__all__ = [
    # Core
    'FinancialAgent',
    'DataManager',
    'portfolio_manager',
    'watchlist_manager',
    # Analysis
    'indicators',
    'timeframe_analysis',
    'macro_analysis',
    'regime_detection',
    'sentiment_analysis',
    # Data
    'market_data',
    'report_generator',
    # External
    'reddit_sentiment',
    'earnings_calendar',
    'insider_trading',
    # Utils
    'llm_agent',
]
