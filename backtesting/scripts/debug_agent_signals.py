#!/usr/bin/env python3
"""Debug script to test agent signal generation for PLTR"""

import sys
sys.path.insert(0, '/Users/carlosfuentes/GitHub/spectral-galileo')

from agent_backtester import AgentBacktester
from datetime import datetime, timedelta
import pandas as pd

# Test configuration
backtester = AgentBacktester(
    tickers=['PLTR', 'AAPL'],
    start_date='2025-06-26',
    end_date='2025-12-23',
    analysis_type='short_term'
)

# Load data
print("Loading data...")
backtester.load_data()

# Check data
print(f"\nData loaded for: {list(backtester.daily_data.keys())}")

if 'PLTR' in backtester.daily_data:
    pltr_data = backtester.daily_data['PLTR']
    print(f"\nPLTR data shape: {pltr_data.shape}")
    print(f"PLTR latest data:\n{pltr_data.tail()}")
    
    # Try to get signals for latest date
    latest_date = pltr_data.index[-1]
    print(f"\nTesting signal generation for {latest_date}")
    
    signals = backtester.generate_agent_signals(latest_date, {})
    print(f"\nGenerated signals: {signals}")
    
    # Check volatility
    vol = backtester._calculate_volatility('PLTR')
    print(f"\nPLTR Volatility: {vol:.4f} ({vol*100:.2f}%)")

if 'AAPL' in backtester.daily_data:
    aapl_data = backtester.daily_data['AAPL']
    print(f"\n\nAAPL data shape: {aapl_data.shape}")
    
    # Check volatility
    vol = backtester._calculate_volatility('AAPL')
    print(f"AAPL Volatility: {vol:.4f} ({vol*100:.2f}%)")
