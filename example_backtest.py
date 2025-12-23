"""
Example Backtest - Demostración de funcionalidad completa

Ejecuta un backtest simple con señales más agresivas para demostrar:
- Carga de datos
- Generación de señales
- Ejecución de trades
- Cálculo de P&L
- Reportes

Author: Spectral Galileo
Date: 2025-12-23
"""

import pandas as pd
from datetime import datetime
from backtester import Backtester
from backtest_portfolio import BacktestPortfolio
from backtest_data_manager import BacktestDataManager


def run_simple_demo():
    """Demostración simple de portfolio."""
    print("\n" + "="*80)
    print("DEMO 1: PORTFOLIO SIMULATOR (Sin backtester)")
    print("="*80)
    
    portfolio = BacktestPortfolio(initial_cash=50000.0)
    
    # Simulación manual de trades
    trades = [
        ("BUY", "AAPL", 100, 150.0),
        ("BUY", "MSFT", 50, 300.0),
        ("UPDATE", "AAPL", 155.0),
        ("UPDATE", "MSFT", 310.0),
        ("SELL", "AAPL", 50, 155.0),
        ("UPDATE", "MSFT", 305.0),
    ]
    
    for trade in trades:
        if trade[0] == "BUY":
            portfolio.buy(trade[1], trade[2], trade[3])
        elif trade[0] == "SELL":
            portfolio.sell(trade[1], trade[2], trade[3])
        elif trade[0] == "UPDATE":
            portfolio.update_price(trade[1], trade[2])
        
        portfolio.record_daily_state()
    
    portfolio.print_summary()
    return portfolio


def run_aggressive_backtest():
    """Backtest con señales más agresivas."""
    print("\n" + "="*80)
    print("DEMO 2: BACKTEST CON SEÑALES AGRESIVAS")
    print("="*80)
    
    class AggressiveBacktester(Backtester):
        """Backtester con umbral de RSI más agresivo."""
        
        def generate_signals(self, date, prices, lookback_days=30):
            """Usa umbrales de RSI más agresivos."""
            signals = {}
            
            for ticker, data in self.daily_data.items():
                if ticker not in prices:
                    continue
                
                hist_data = data[data.index <= date].tail(lookback_days)
                
                if len(hist_data) < lookback_days:
                    continue
                
                # Simpler signals: solo basado en precio vs media móvil
                ma_20 = hist_data['Close'].rolling(20).mean().iloc[-1]
                current_price = prices[ticker]
                
                signal = 'HOLD'
                strength = 0.0
                reason = ""
                
                # Señal más agresiva: compra si baja 3%, vende si sube 3%
                if ticker not in self.portfolio.positions and current_price < ma_20 * 0.97:
                    signal = 'BUY'
                    strength = 0.5
                    reason = f"Precio < MA20 * 0.97 ({current_price:.2f} < {ma_20*0.97:.2f})"
                
                elif ticker in self.portfolio.positions and current_price > ma_20 * 1.03:
                    signal = 'SELL'
                    strength = 0.5
                    reason = f"Precio > MA20 * 1.03 ({current_price:.2f} > {ma_20*1.03:.2f})"
                
                signals[ticker] = {
                    'signal': signal,
                    'strength': strength,
                    'reason': reason,
                    'price': current_price,
                    'ma_20': ma_20
                }
            
            return signals
    
    # Ejecutar backtest agresivo
    backtester = AggressiveBacktester(
        tickers=["AAPL", "MSFT"],
        start_date="2024-12-23",
        end_date="2025-12-22",
        initial_cash=50000.0
    )
    
    results = backtester.run_backtest()
    backtester.print_results(results)
    backtester.save_results(results)
    
    return backtester, results


def run_basic_backtest():
    """Backtest básico con datos reales."""
    print("\n" + "="*80)
    print("DEMO 3: BACKTEST BÁSICO (Año completo)")
    print("="*80)
    
    backtester = Backtester(
        tickers=["AAPL"],
        start_date="2024-12-23",
        end_date="2025-12-22",
        initial_cash=50000.0
    )
    
    results = backtester.run_backtest()
    backtester.print_results(results)
    backtester.save_results(results)
    
    return backtester, results


def run_multi_ticker_backtest():
    """Backtest con múltiples tickers."""
    print("\n" + "="*80)
    print("DEMO 4: BACKTEST MULTI-TICKER")
    print("="*80)
    
    backtester = Backtester(
        tickers=["AAPL", "MSFT", "NVDA", "GOOGL", "META"],
        start_date="2024-12-23",
        end_date="2025-12-22",
        initial_cash=100000.0
    )
    
    results = backtester.run_backtest()
    backtester.print_results(results)
    backtester.save_results(results)
    
    return backtester, results


def verify_data_integration():
    """Verifica integración con data manager."""
    print("\n" + "="*80)
    print("VERIFICACIÓN: Integración con Data Manager")
    print("="*80)
    
    manager = BacktestDataManager()
    tickers = manager.list_available_tickers()
    
    print(f"\nTickers disponibles: {len(tickers)}")
    print(f"Tickers: {', '.join(tickers[:5])}...\n")
    
    # Verificar que data_manager y backtester usan los mismos datos
    for ticker in ["AAPL", "MSFT", "NVDA"]:
        info = manager.get_ticker_info(ticker)
        data = manager.get_historical_range(ticker, auto_download=False)
        
        print(f"✓ {ticker}:")
        print(f"    - Días: {info['days']}")
        print(f"    - Rango: {info['start_date']} → {info['end_date']}")
        print(f"    - Tamaño: {info['file_size_kb']} KB")
        print(f"    - Columnas: {', '.join(info['columns'])}")


if __name__ == "__main__":
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "FASE 2: BACKTESTER ENGINE - DEMOSTRACIONES COMPLETAS".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # 1. Portfolio demo
    portfolio = run_simple_demo()
    
    # 2. Verificar data integration
    verify_data_integration()
    
    # 3. Basic backtest
    print("\n" + "."*80)
    backtester, results = run_basic_backtest()
    
    # 4. Multi-ticker backtest
    print("\n" + "."*80)
    backtester2, results2 = run_multi_ticker_backtest()
    
    # 5. Aggressive backtest
    print("\n" + "."*80)
    backtester3, results3 = run_aggressive_backtest()
    
    print("\n" + "="*80)
    print("✨ TODAS LAS DEMOSTRACIONES COMPLETADAS")
    print("="*80)
    print("\nResultados guardados en: ./backtest_results/")
