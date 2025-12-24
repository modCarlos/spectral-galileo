"""
Backtester - Orquestador principal de backtesting

Funcionalidad:
- Loop diario de backtesting
- Integración con agent.py para análisis
- Ejecución de trades basado en señales
- Generación de reportes
- Tracking de performance

Author: Spectral Galileo
Date: 2025-12-23
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Dict, Tuple, Optional

from backtest_data_manager import BacktestDataManager
from backtest_portfolio import BacktestPortfolio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Backtester:
    """
    Orquestador principal de backtesting.
    
    Ejecuta un loop diario que:
    1. Obtiene datos históricos
    2. Ejecuta análisis (agent)
    3. Genera señales de compra/venta
    4. Ejecuta trades
    5. Registra estado diario
    """
    
    def __init__(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        initial_cash: float = 100000.0,
        data_dir: str = "./backtest_data",
        results_dir: str = "./backtest_results"
    ):
        """
        Inicializa el backtester.
        
        Args:
            tickers: Lista de tickers a testear
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
            initial_cash: Capital inicial
            data_dir: Directorio con datos históricos
            results_dir: Directorio para guardar resultados
        """
        self.tickers = tickers
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.initial_cash = initial_cash
        self.data_dir = data_dir
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar componentes
        self.data_manager = BacktestDataManager(data_dir=data_dir)
        self.portfolio = BacktestPortfolio(initial_cash=initial_cash)
        
        # Datos y análisis
        self.daily_data = {}  # {ticker: DataFrame}
        self.daily_analysis = {}  # {date: {ticker: analysis_result}}
        
        logger.info(f"Backtester inicializado:")
        logger.info(f"  Tickers: {', '.join(tickers)}")
        logger.info(f"  Período: {start_date} → {end_date}")
        logger.info(f"  Capital inicial: ${initial_cash:,.2f}")
    
    def load_data(self) -> bool:
        """
        Carga datos históricos para todos los tickers.
        
        Returns:
            True si cargó exitosamente, False si hay errores
        """
        logger.info(f"\n📥 Cargando datos históricos para {len(self.tickers)} tickers...")
        
        successful = 0
        for ticker in self.tickers:
            try:
                data = self.data_manager.get_historical_range(
                    ticker,
                    start_date=self.start_date.strftime('%Y-%m-%d'),
                    end_date=self.end_date.strftime('%Y-%m-%d'),
                    auto_download=False
                )
                
                if data.empty:
                    logger.warning(f"⚠ {ticker}: Sin datos en el período")
                    continue
                
                self.daily_data[ticker] = data
                successful += 1
                logger.info(f"✓ {ticker}: {len(data)} días cargados")
                
            except Exception as e:
                logger.error(f"✗ {ticker}: Error cargando - {str(e)}")
        
        logger.info(f"\n✨ {successful}/{len(self.tickers)} tickers cargados exitosamente")
        return successful > 0
    
    def get_daily_prices(self, date: pd.Timestamp) -> Dict[str, float]:
        """
        Obtiene los precios de cierre para una fecha específica.
        
        Args:
            date: Fecha
            
        Returns:
            Dict {ticker: close_price}
        """
        prices = {}
        
        for ticker, data in self.daily_data.items():
            if date in data.index:
                prices[ticker] = data.loc[date, 'Close']
        
        return prices
    
    def generate_signals(
        self, 
        date: pd.Timestamp,
        prices: Dict[str, float],
        lookback_days: int = 30
    ) -> Dict[str, Dict]:
        """
        Genera señales de compra/venta basado en análisis técnico simple.
        
        Esta es una implementación básica. En producción, usarías agent.py.
        
        Args:
            date: Fecha actual
            prices: Precios actuales
            lookback_days: Días hacia atrás para análisis
            
        Returns:
            Dict {ticker: {signal, strength, reason}}
        """
        signals = {}
        
        for ticker, data in self.daily_data.items():
            if ticker not in prices:
                continue
            
            # Filtrar datos hasta la fecha actual
            hist_data = data[data.index <= date].tail(lookback_days)
            
            if len(hist_data) < lookback_days:
                continue
            
            # Señal simple: media móvil 20 vs precio actual
            ma_20 = hist_data['Close'].rolling(20).mean().iloc[-1]
            current_price = prices[ticker]
            
            # RSI simple (70/30 overbought/oversold)
            delta = hist_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Generar señal
            signal = 'HOLD'
            strength = 0.0
            reason = ""
            
            if current_rsi < 30 and current_price > ma_20:
                signal = 'BUY'
                strength = (30 - current_rsi) / 30  # Mayor fuerza si RSI más bajo
                reason = f"RSI Oversold ({current_rsi:.1f}), Price > MA20"
            
            elif current_rsi > 70 and ticker in self.portfolio.positions:
                signal = 'SELL'
                strength = (current_rsi - 70) / 30  # Mayor fuerza si RSI más alto
                reason = f"RSI Overbought ({current_rsi:.1f})"
            
            signals[ticker] = {
                'signal': signal,
                'strength': strength,
                'reason': reason,
                'price': current_price,
                'rsi': current_rsi,
                'ma_20': ma_20
            }
        
        return signals
    
    def execute_trades(
        self, 
        date: pd.Timestamp,
        signals: Dict[str, Dict],
        max_position_size: float = 0.2  # 20% del portfolio por posición
    ):
        """
        Ejecuta trades basado en las señales.
        
        Args:
            date: Fecha de ejecución
            signals: Señales generadas
            max_position_size: Máximo % del portfolio por posición
        """
        trades_executed = 0
        
        for ticker, signal_data in signals.items():
            signal = signal_data['signal']
            strength = signal_data['strength']
            price = signal_data['price']
            
            if signal == 'HOLD':
                continue
            
            elif signal == 'BUY' and ticker not in self.portfolio.positions:
                # Calcular cantidad de acciones
                max_allocation = self.portfolio.get_portfolio_value() * max_position_size
                shares = int(max_allocation / price)
                
                if shares > 0:
                    success = self.portfolio.buy(ticker, shares, price, date=date)
                    if success:
                        trades_executed += 1
            
            elif signal == 'SELL' and ticker in self.portfolio.positions:
                # Vender toda la posición
                shares = self.portfolio.positions[ticker]['shares']
                success, pnl = self.portfolio.sell(ticker, shares, price, date=date)
                if success:
                    trades_executed += 1
        
        return trades_executed
    
    def run_backtest(self) -> Dict:
        """
        Ejecuta el backtest completo.
        
        Returns:
            Diccionario con resultados
        """
        logger.info(f"\n{'='*80}")
        logger.info("🚀 INICIANDO BACKTEST")
        logger.info(f"{'='*80}\n")
        
        # Cargar datos
        if not self.load_data():
            logger.error("❌ No se pudieron cargar los datos")
            return {}
        
        # Obtener fechas de trading
        trading_dates = self._get_trading_dates()
        logger.info(f"📅 Días de trading: {len(trading_dates)}\n")
        
        # Loop principal
        trades_by_date = {}
        
        for i, date in enumerate(trading_dates):
            # Obtener precios del día
            prices = self.get_daily_prices(date)
            
            if not prices:
                continue
            
            # Actualizar precios en el portfolio
            for ticker, price in prices.items():
                self.portfolio.update_price(ticker, price)
            
            # Generar señales
            signals = self.generate_signals(date, prices)
            
            # Ejecutar trades
            trades = self.execute_trades(date, signals)
            if trades > 0:
                trades_by_date[date] = trades
            
            # Registrar estado diario
            self.portfolio.record_daily_state(date=date)
            
            # Progreso
            if (i + 1) % 50 == 0:
                portfolio_value = self.portfolio.get_portfolio_value()
                logger.info(f"  [{i+1}/{len(trading_dates)}] {date.date()} - Portafolio: ${portfolio_value:,.2f}")
        
        # Cerrar posiciones al final
        final_prices = self.get_daily_prices(trading_dates[-1])
        self.portfolio.close_all_positions(final_prices, date=trading_dates[-1])
        
        # Resumen final
        logger.info(f"\n{'='*80}")
        logger.info("✨ BACKTEST COMPLETADO")
        logger.info(f"{'='*80}")
        
        results = self._generate_results()
        
        return results
    
    def _get_trading_dates(self) -> List[pd.Timestamp]:
        """
        Obtiene todas las fechas de trading en el período.
        
        Returns:
            Lista de fechas
        """
        # Usar las fechas del primer ticker disponible
        if not self.daily_data:
            return []
        
        first_ticker = list(self.daily_data.keys())[0]
        all_dates = self.daily_data[first_ticker].index.tolist()
        
        # Filtrar por período
        trading_dates = [
            d for d in all_dates 
            if self.start_date <= d <= self.end_date
        ]
        
        return sorted(trading_dates)
    
    def _generate_results(self) -> Dict:
        """
        Genera resultado final del backtest.
        
        Returns:
            Diccionario con métricas
        """
        # Obtener resumen del portfolio
        portfolio_summary = self.portfolio.get_summary()
        
        # Obtener valores diarios
        daily_df = self.portfolio.get_daily_values_df()
        
        # Calcular métricas adicionales
        results = {
            'period': {
                'start': self.start_date.strftime('%Y-%m-%d'),
                'end': self.end_date.strftime('%Y-%m-%d'),
                'days': len(self._get_trading_dates())
            },
            'portfolio': portfolio_summary,
            'daily_values': daily_df,
            'transactions': self.portfolio.get_transactions_df()
        }
        
        # Calcular rendimiento anualizado (simple)
        if len(daily_df) > 1:
            first_value = daily_df.iloc[0]['Portfolio Value']
            last_value = daily_df.iloc[-1]['Portfolio Value']
            total_return = (last_value - first_value) / first_value
            days = len(daily_df)
            years = days / 252
            annual_return = (total_return / years) if years > 0 else total_return
            
            results['metrics'] = {
                'total_return': total_return,
                'annual_return': annual_return,
                'days_traded': days
            }
        
        return results
    
    def save_results(self, results: Dict):
        """
        Guarda los resultados del backtest.
        
        Args:
            results: Resultados del backtest
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Guardar resumen
        summary_file = self.results_dir / f"backtest_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("RESUMEN DEL BACKTEST\n")
            f.write("="*80 + "\n\n")
            
            f.write("PERÍODO\n")
            f.write("-"*80 + "\n")
            period = results['period']
            f.write(f"Inicio: {period['start']}\n")
            f.write(f"Fin: {period['end']}\n")
            f.write(f"Días de trading: {period['days']}\n\n")
            
            f.write("PORTAFOLIO\n")
            f.write("-"*80 + "\n")
            portfolio = results['portfolio']
            f.write(f"Capital inicial: ${portfolio['Initial Capital']:,.2f}\n")
            f.write(f"Valor final: ${portfolio['Final Value']:,.2f}\n")
            f.write(f"P&L Total: ${portfolio['Total P&L']:,.2f} ({portfolio['Total P&L %']:.2f}%)\n")
            f.write(f"Win Rate: {portfolio['Win Rate']:.1f}%\n")
            f.write(f"Total Trades: {portfolio['Total Trades']}\n")
        
        logger.info(f"✓ Resumen guardado: {summary_file}")
        
        # Guardar valores diarios
        if 'daily_values' in results and not results['daily_values'].empty:
            csv_file = self.results_dir / f"backtest_daily_{timestamp}.csv"
            results['daily_values'].to_csv(csv_file, index=False)
            logger.info(f"✓ Valores diarios guardados: {csv_file}")
        
        # Guardar transacciones
        if 'transactions' in results and not results['transactions'].empty:
            txn_file = self.results_dir / f"backtest_transactions_{timestamp}.csv"
            results['transactions'].to_csv(txn_file, index=False)
            logger.info(f"✓ Transacciones guardadas: {txn_file}")
    
    def print_results(self, results: Dict):
        """
        Imprime los resultados del backtest.
        
        Args:
            results: Resultados del backtest
        """
        print("\n" + "="*80)
        print("RESULTADOS DEL BACKTEST")
        print("="*80)
        
        period = results['period']
        print(f"\n📅 PERÍODO")
        print(f"  Inicio: {period['start']}")
        print(f"  Fin: {period['end']}")
        print(f"  Días: {period['days']}")
        
        portfolio = results['portfolio']
        print(f"\n💰 PORTAFOLIO")
        print(f"  Capital inicial:  ${portfolio['Initial Capital']:>15,.2f}")
        print(f"  Valor final:      ${portfolio['Final Value']:>15,.2f}")
        print(f"  Cash disponible:  ${portfolio['Cash']:>15,.2f}")
        
        print(f"\n📈 RETORNO")
        print(f"  P&L Total:        ${portfolio['Total P&L']:>15,.2f}")
        print(f"  P&L %:            {portfolio['Total P&L %']:>15.2f}%")
        
        if 'metrics' in results:
            metrics = results['metrics']
            print(f"  Return anual:     {metrics['annual_return']*100:>15.2f}%")
        
        print(f"\n🎯 TRADES")
        print(f"  Total trades:     {portfolio['Total Trades']:>15}")
        print(f"  Ganadores:        {portfolio['Winning Trades']:>15}")
        print(f"  Perdedores:       {portfolio['Losing Trades']:>15}")
        print(f"  Win Rate:         {portfolio['Win Rate']:>14.1f}%")
        
        print("\n" + "="*80)


# CLI Interface
if __name__ == "__main__":
    import argparse
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="Backtester Engine")
    parser.add_argument("--tickers", nargs="+", required=True, help="Tickers a testear")
    parser.add_argument("--start", required=True, help="Fecha inicio (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="Fecha fin (YYYY-MM-DD)")
    parser.add_argument("--capital", type=float, default=100000, help="Capital inicial")
    
    args = parser.parse_args()
    
    backtester = Backtester(
        tickers=args.tickers,
        start_date=args.start,
        end_date=args.end,
        initial_cash=args.capital
    )
    
    results = backtester.run_backtest()
    backtester.print_results(results)
    backtester.save_results(results)
