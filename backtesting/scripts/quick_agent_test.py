#!/usr/bin/env python3
"""
Quick test of agent backtester with fresh imports
"""
import sys
import warnings
warnings.filterwarnings('ignore')

# Force reimport
if 'agent_backtester' in sys.modules:
    del sys.modules['agent_backtester']

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from agent_backtester import AgentBacktester
import pandas as pd
import numpy as np

def calculate_metrics(daily_values, transactions):
    """Simple metrics calculation"""
    if len(daily_values) < 2:
        return {}
    
    # Basic metrics
    initial = daily_values[0]
    final = daily_values[-1]
    total_return = (final - initial) / initial
    days = len(daily_values)
    years = days / 252
    annual_return = (((final / initial) ** (1/years)) - 1) if years > 0 else total_return
    
    # Volatility
    returns = np.diff(daily_values) / daily_values[:-1]
    volatility = np.std(returns) * np.sqrt(252)
    
    # Sharpe
    risk_free_rate = 0.05 / 252
    excess_returns = returns - risk_free_rate
    sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0
    
    # Max Drawdown
    cummax = np.maximum.accumulate(daily_values)
    drawdown = (daily_values - cummax) / cummax
    max_drawdown = np.min(drawdown)
    
    # Win rate
    trades = len(transactions)
    winning_trades = 0
    if trades > 0:
        for _, row in transactions.iterrows():
            if row.get('P&L', 0) > 0:
                winning_trades += 1
    win_rate = (winning_trades / trades * 100) if trades > 0 else 0
    
    return {
        'total_return': total_return * 100,
        'annual_return': annual_return * 100,
        'volatility': volatility * 100,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown * 100,
        'trades': trades,
        'win_rate': win_rate
    }

def test_short_term():
    """Test short-term agent analysis"""
    print("\n" + "="*80)
    print("🚀 SHORT-TERM AGENT BACKTEST (6 months)")
    print("="*80 + "\n")
    
    backtester = AgentBacktester(
        tickers=['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'TSLA'],
        start_date='2025-06-25',
        end_date='2025-12-22',
        analysis_type='short_term'
    )
    
    results = backtester.run_backtest()
    backtester.save_results(results)
    
    # Calculate metrics
    if not results['daily_values'].empty:
        daily_values = results['daily_values']['Portfolio Value'].values
        metrics = calculate_metrics(daily_values, results['transactions'])
        
        print(f"\n📊 MÉTRICAS:")
        print(f"  Retorno Total: {metrics['total_return']:.2f}%")
        print(f"  Retorno Anualizado: {metrics['annual_return']:.2f}%")
        print(f"  Sharpe Ratio: {metrics['sharpe']:.2f}")
        print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"  Volatilidad: {metrics['volatility']:.2f}%")
        print(f"  Total Trades: {metrics['trades']}")
        print(f"  Win Rate: {metrics['win_rate']:.1f}%")

def test_long_term():
    """Test long-term agent analysis"""
    print("\n" + "="*80)
    print("📈 LONG-TERM AGENT BACKTEST (5 years)")
    print("="*80 + "\n")
    
    backtester = AgentBacktester(
        tickers=['AAPL', 'MSFT', 'JPM', 'JNJ', 'WMT'],
        start_date='2020-12-24',
        end_date='2025-12-22',
        analysis_type='long_term'
    )
    
    results = backtester.run_backtest()
    backtester.save_results(results)
    
    # Calculate metrics
    if not results['daily_values'].empty:
        daily_values = results['daily_values']['Portfolio Value'].values
        metrics = calculate_metrics(daily_values, results['transactions'])
        
        print(f"\n📊 MÉTRICAS:")
        print(f"  Retorno Total: {metrics['total_return']:.2f}%")
        print(f"  Retorno Anualizado: {metrics['annual_return']:.2f}%")
        print(f"  Sharpe Ratio: {metrics['sharpe']:.2f}")
        print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"  Volatilidad: {metrics['volatility']:.2f}%")
        print(f"  Total Trades: {metrics['trades']}")
        print(f"  Win Rate: {metrics['win_rate']:.1f}%")

if __name__ == '__main__':
    test_short_term()
    test_long_term()
    print("\n✅ Tests completed!\n")
