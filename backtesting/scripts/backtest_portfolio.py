"""
Backtest Portfolio - Simulador de portafolio para backtesting

Funcionalidad:
- Gestionar posiciones (buy/sell)
- Rastrear efectivo y valor de portafolio
- Calcular P&L diario
- Registrar todas las transacciones
- Validar operaciones

Author: Spectral Galileo
Date: 2025-12-23
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BacktestPortfolio:
    """
    Simulador de portafolio para backtesting.
    
    Gestiona compras/ventas, efectivo, posiciones y cálculo de P&L.
    """
    
    def __init__(self, initial_cash: float = 100000.0):
        """
        Inicializa el portafolio.
        
        Args:
            initial_cash: Capital inicial en dólares
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = {}  # {ticker: {shares, avg_cost, current_price}}
        self.transactions = []  # Log de todas las transacciones
        self.daily_values = []  # Histórico de valor diario
        self.daily_pnl = []  # Histórico de P&L diario
        
        logger.info(f"Portafolio inicializado con ${initial_cash:,.2f}")
    
    def buy(
        self, 
        ticker: str, 
        shares: int, 
        price: float, 
        date: datetime = None
    ) -> bool:
        """
        Compra acciones.
        
        Args:
            ticker: Símbolo del ticker
            shares: Número de acciones
            price: Precio por acción
            date: Fecha de la transacción
            
        Returns:
            True si la compra fue exitosa, False si falta efectivo
        """
        if date is None:
            date = datetime.now()
        
        cost = shares * price
        
        # Validar que hay suficiente efectivo
        if cost > self.cash:
            logger.warning(f"❌ {ticker}: Efectivo insuficiente. Necesario: ${cost:,.2f}, Disponible: ${self.cash:,.2f}")
            return False
        
        # Actualizar efectivo
        self.cash -= cost
        
        # Actualizar posición
        if ticker in self.positions:
            # Aumentar posición existente
            old_shares = self.positions[ticker]['shares']
            old_cost = self.positions[ticker]['avg_cost'] * old_shares
            
            total_shares = old_shares + shares
            self.positions[ticker]['avg_cost'] = (old_cost + cost) / total_shares
            self.positions[ticker]['shares'] = total_shares
        else:
            # Nueva posición
            self.positions[ticker] = {
                'shares': shares,
                'avg_cost': price,
                'current_price': price
            }
        
        # Registrar transacción
        transaction = {
            'date': date,
            'ticker': ticker,
            'type': 'BUY',
            'shares': shares,
            'price': price,
            'total': cost,
            'cash_after': self.cash
        }
        self.transactions.append(transaction)
        
        logger.info(f"✓ BUY: {shares} {ticker} @ ${price:.2f} = ${cost:,.2f} (Cash: ${self.cash:,.2f})")
        return True
    
    def sell(
        self, 
        ticker: str, 
        shares: int, 
        price: float, 
        date: datetime = None
    ) -> Tuple[bool, float]:
        """
        Vende acciones.
        
        Args:
            ticker: Símbolo del ticker
            shares: Número de acciones
            price: Precio por acción
            date: Fecha de la transacción
            
        Returns:
            (éxito, ganancia/pérdida realizada)
        """
        if date is None:
            date = datetime.now()
        
        # Validar que exista la posición
        if ticker not in self.positions:
            logger.warning(f"❌ {ticker}: Sin posición abierta")
            return False, 0.0
        
        # Validar que hay suficientes acciones
        if shares > self.positions[ticker]['shares']:
            logger.warning(f"❌ {ticker}: Insuficientes acciones. Tenemos {self.positions[ticker]['shares']}, se solicita {shares}")
            return False, 0.0
        
        # Calcular ganancia/pérdida
        avg_cost = self.positions[ticker]['avg_cost']
        revenue = shares * price
        cost_basis = shares * avg_cost
        pnl = revenue - cost_basis
        
        # Actualizar efectivo
        self.cash += revenue
        
        # Actualizar posición
        self.positions[ticker]['shares'] -= shares
        
        # Eliminar posición si está vacía
        if self.positions[ticker]['shares'] == 0:
            del self.positions[ticker]
        
        # Registrar transacción
        transaction = {
            'date': date,
            'ticker': ticker,
            'type': 'SELL',
            'shares': shares,
            'price': price,
            'total': revenue,
            'pnl_realized': pnl,
            'cash_after': self.cash
        }
        self.transactions.append(transaction)
        
        pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
        logger.info(f"✓ SELL: {shares} {ticker} @ ${price:.2f} = ${revenue:,.2f} | P&L: ${pnl:.2f} ({pnl_pct:.1f}%) (Cash: ${self.cash:,.2f})")
        
        return True, pnl
    
    def update_price(self, ticker: str, price: float):
        """
        Actualiza el precio actual de una posición.
        
        Args:
            ticker: Símbolo del ticker
            price: Nuevo precio
        """
        if ticker in self.positions:
            self.positions[ticker]['current_price'] = price
    
    def get_position_value(self, ticker: str) -> float:
        """
        Obtiene el valor actual de una posición.
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            Valor en dólares
        """
        if ticker not in self.positions:
            return 0.0
        
        return self.positions[ticker]['shares'] * self.positions[ticker]['current_price']
    
    def get_position_pnl(self, ticker: str) -> Tuple[float, float]:
        """
        Obtiene P&L sin realizar de una posición.
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            (P&L en dólares, P&L en porcentaje)
        """
        if ticker not in self.positions:
            return 0.0, 0.0
        
        pos = self.positions[ticker]
        cost_basis = pos['shares'] * pos['avg_cost']
        current_value = pos['shares'] * pos['current_price']
        pnl = current_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
        
        return pnl, pnl_pct
    
    def get_portfolio_value(self) -> float:
        """
        Obtiene el valor total del portafolio (cash + posiciones).
        
        Returns:
            Valor en dólares
        """
        positions_value = sum(self.get_position_value(t) for t in self.positions)
        return self.cash + positions_value
    
    def get_total_pnl(self) -> Tuple[float, float]:
        """
        Obtiene el P&L total (realizado + sin realizar).
        
        Returns:
            (P&L total, P&L porcentaje)
        """
        # P&L realizado (de transacciones completadas)
        realized_pnl = sum(
            t.get('pnl_realized', 0) for t in self.transactions 
            if t['type'] == 'SELL'
        )
        
        # P&L sin realizar (posiciones actuales)
        unrealized_pnl = sum(
            self.get_position_pnl(t)[0] for t in self.positions
        )
        
        total_pnl = realized_pnl + unrealized_pnl
        portfolio_value = self.get_portfolio_value()
        total_pnl_pct = (total_pnl / self.initial_cash * 100) if self.initial_cash > 0 else 0
        
        return total_pnl, total_pnl_pct
    
    def get_positions_summary(self) -> pd.DataFrame:
        """
        Obtiene resumen de posiciones actuales.
        
        Returns:
            DataFrame con posiciones
        """
        data = []
        for ticker, pos in self.positions.items():
            pnl, pnl_pct = self.get_position_pnl(ticker)
            data.append({
                'Ticker': ticker,
                'Shares': pos['shares'],
                'Avg Cost': pos['avg_cost'],
                'Current Price': pos['current_price'],
                'Position Value': self.get_position_value(ticker),
                'Cost Basis': pos['shares'] * pos['avg_cost'],
                'P&L': pnl,
                'P&L %': pnl_pct
            })
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        return df.sort_values('Position Value', ascending=False)
    
    def get_transactions_df(self) -> pd.DataFrame:
        """
        Obtiene histórico de transacciones como DataFrame.
        
        Returns:
            DataFrame con transacciones
        """
        if not self.transactions:
            return pd.DataFrame()
        
        return pd.DataFrame(self.transactions)
    
    def record_daily_state(self, date: datetime = None):
        """
        Registra el estado del portafolio al cierre del día.
        
        Args:
            date: Fecha del registro
        """
        if date is None:
            date = datetime.now()
        
        portfolio_value = self.get_portfolio_value()
        total_pnl, total_pnl_pct = self.get_total_pnl()
        
        daily_record = {
            'Date': date,
            'Cash': self.cash,
            'Positions Value': portfolio_value - self.cash,
            'Portfolio Value': portfolio_value,
            'Total P&L': total_pnl,
            'Total P&L %': total_pnl_pct
        }
        
        self.daily_values.append(daily_record)
    
    def get_daily_values_df(self) -> pd.DataFrame:
        """
        Obtiene histórico de valores diarios como DataFrame.
        
        Returns:
            DataFrame con valores diarios
        """
        if not self.daily_values:
            return pd.DataFrame()
        
        return pd.DataFrame(self.daily_values)
    
    def get_summary(self) -> Dict:
        """
        Obtiene resumen completo del portafolio.
        
        Returns:
            Diccionario con estadísticas
        """
        total_pnl, total_pnl_pct = self.get_total_pnl()
        portfolio_value = self.get_portfolio_value()
        
        # Calcular P&L realizado
        realized_pnl = sum(
            t.get('pnl_realized', 0) for t in self.transactions 
            if t['type'] == 'SELL'
        )
        
        # Calcular ganadas/pérdidas
        winning_trades = sum(
            1 for t in self.transactions 
            if t['type'] == 'SELL' and t.get('pnl_realized', 0) > 0
        )
        losing_trades = sum(
            1 for t in self.transactions 
            if t['type'] == 'SELL' and t.get('pnl_realized', 0) < 0
        )
        total_trades = len([t for t in self.transactions if t['type'] == 'SELL'])
        
        return {
            'Initial Capital': self.initial_cash,
            'Final Value': portfolio_value,
            'Total P&L': total_pnl,
            'Total P&L %': total_pnl_pct,
            'Realized P&L': realized_pnl,
            'Unrealized P&L': total_pnl - realized_pnl,
            'Cash': self.cash,
            'Positions Value': portfolio_value - self.cash,
            'Open Positions': len(self.positions),
            'Total Trades': total_trades,
            'Winning Trades': winning_trades,
            'Losing Trades': losing_trades,
            'Win Rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0
        }
    
    def print_summary(self):
        """Imprime resumen del portafolio."""
        summary = self.get_summary()
        
        print("\n" + "="*80)
        print("RESUMEN DEL PORTAFOLIO")
        print("="*80)
        print(f"\n💰 Capital:")
        print(f"  Capital inicial:     ${summary['Initial Capital']:>15,.2f}")
        print(f"  Valor final:         ${summary['Final Value']:>15,.2f}")
        print(f"  Cash disponible:     ${summary['Cash']:>15,.2f}")
        print(f"\n📊 P&L:")
        print(f"  P&L Realizado:       ${summary['Realized P&L']:>15,.2f}")
        print(f"  P&L Sin realizar:    ${summary['Unrealized P&L']:>15,.2f}")
        print(f"  P&L Total:           ${summary['Total P&L']:>15,.2f} ({summary['Total P&L %']:>6.2f}%)")
        print(f"\n📈 Posiciones:")
        print(f"  Valor posiciones:    ${summary['Positions Value']:>15,.2f}")
        print(f"  Posiciones abiertas: {summary['Open Positions']:>15}")
        print(f"\n🎯 Trades:")
        print(f"  Total trades:        {summary['Total Trades']:>15}")
        print(f"  Ganadores:           {summary['Winning Trades']:>15}")
        print(f"  Perdedores:          {summary['Losing Trades']:>15}")
        print(f"  Win rate:            {summary['Win Rate']:>14.1f}%")
        print("\n" + "="*80)
        
        # Mostrar posiciones actuales
        if self.positions:
            print("\nPOSICIONES ABIERTAS:")
            print("-"*80)
            pos_df = self.get_positions_summary()
            print(pos_df.to_string(index=False))
    
    def close_all_positions(self, prices: Dict[str, float], date: datetime = None):
        """
        Cierra todas las posiciones abiertas a precios específicos.
        
        Args:
            prices: Dict {ticker: price}
            date: Fecha de cierre
        """
        for ticker in list(self.positions.keys()):
            if ticker in prices:
                shares = self.positions[ticker]['shares']
                self.sell(ticker, shares, prices[ticker], date=date)
    
    def validate_state(self) -> bool:
        """
        Valida que el portafolio sea consistente.
        
        Returns:
            True si es válido
        """
        # Cash debe ser >= 0
        if self.cash < 0:
            logger.error(f"❌ Cash negativo: ${self.cash}")
            return False
        
        # Posiciones deben tener shares > 0
        for ticker, pos in self.positions.items():
            if pos['shares'] <= 0:
                logger.error(f"❌ {ticker}: Shares <= 0")
                return False
        
        return True


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Backtest Portfolio Simulator")
    parser.add_argument("--test", action="store_true", help="Run example portfolio")
    
    args = parser.parse_args()
    
    if args.test:
        # Ejemplo de uso
        print("\n" + "="*80)
        print("EJEMPLO: Simulación de portafolio")
        print("="*80)
        
        portfolio = BacktestPortfolio(initial_cash=100000)
        
        # Compras
        portfolio.buy("AAPL", 100, 150.0)
        portfolio.buy("MSFT", 50, 300.0)
        portfolio.buy("NVDA", 25, 400.0)
        
        # Actualizar precios
        portfolio.update_price("AAPL", 155.0)
        portfolio.update_price("MSFT", 310.0)
        portfolio.update_price("NVDA", 420.0)
        
        # Registrar estado diario
        portfolio.record_daily_state()
        
        # Vender parcial
        portfolio.sell("AAPL", 50, 155.0)
        
        # Actualizar precios nuevamente
        portfolio.update_price("MSFT", 305.0)
        portfolio.update_price("NVDA", 410.0)
        
        # Registrar estado diario
        portfolio.record_daily_state()
        
        # Mostrar resumen
        portfolio.print_summary()
        
        # Mostrar posiciones
        print("\nPOSICIONES DETALLADAS:")
        print(portfolio.get_positions_summary())
        
        # Mostrar transacciones
        print("\nTRANSACCIONES:")
        print(portfolio.get_transactions_df().to_string(index=False))
