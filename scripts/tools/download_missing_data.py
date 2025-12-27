#!/usr/bin/env python3
"""Download missing ticker data for backtesting"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def download_ticker_data(ticker: str, data_dir: str = "backtest_data") -> bool:
    """Download 5 years of historical data for a ticker"""
    try:
        print(f"\n📥 Downloading {ticker}...", end=" ", flush=True)
        
        # Calculate date range (5 years)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)
        
        # Download data using Ticker object for more control
        tick = yf.Ticker(ticker)
        data = tick.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )
        
        if data.empty:
            print(f"❌ No data")
            return False
        
        # Ensure proper column names (should be: Open, High, Low, Close, Volume)
        # Normalize column names
        data.columns = data.columns.str.lower()
        
        # Remove timezone from index
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        
        # Ensure index is properly named
        data.index.name = 'Date'
        
        # Select only standard columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        available_cols = [c for c in required_cols if c in data.columns]
        data = data[available_cols]
        
        # Save to CSV with proper formatting
        filepath = os.path.join(data_dir, f"{ticker}.csv")
        data.to_csv(filepath)
        
        print(f"✅ {len(data)} rows ({data.index.min().date()} to {data.index.max().date()})")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)[:80]}")
        return False

def main():
    # Tickers to download
    tickers = ['PLTR', 'BABA', 'TSLA', 'NVDA', 'META', 'MSFT']
    
    print("=" * 70)
    print("DOWNLOADING HISTORICAL DATA FOR BACKTESTING")
    print("=" * 70)
    
    success_count = 0
    for ticker in tickers:
        if download_ticker_data(ticker):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ COMPLETED: {success_count}/{len(tickers)} tickers downloaded successfully")
    print("=" * 70)

if __name__ == "__main__":
    main()

def main():
    # Tickers to download
    tickers = ['PLTR', 'BABA', 'TSLA', 'NVDA', 'META', 'MSFT']
    
    print("=" * 70)
    print("DOWNLOADING HISTORICAL DATA FOR BACKTESTING")
    print("=" * 70)
    
    success_count = 0
    for ticker in tickers:
        if download_ticker_data(ticker):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ COMPLETED: {success_count}/{len(tickers)} tickers downloaded successfully")
    print("=" * 70)

if __name__ == "__main__":
    main()
