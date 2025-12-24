"""
Advanced Metrics Calculator - Calcula métricas sofisticadas para backtesting

Funcionalidad:
- Sharpe Ratio (rendimiento ajustado por riesgo)
- Maximum Drawdown (máxima pérdida desde peak)
- Calmar Ratio (retorno / drawdown)
- Profit Factor (ganancias / pérdidas)
- Return Statistics (media, volatilidad, skew, kurtosis)
- Visualization (equity curve, drawdown curve)

Author: Spectral Galileo
Date: 2025-12-23
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AdvancedMetricsCalculator:
    """Calcula métricas avanzadas para backtesting y análisis de rendimiento."""
    
    def __init__(self, daily_values: List[float], trades: List[Dict] = None, risk_free_rate: float = 0.04):
        """
        Inicializa el calculador de métricas.
        
        Args:
            daily_values: Lista de valores diarios del portafolio
            trades: Lista de transacciones {'date', 'ticker', 'action', 'shares', 'price', 'pnl'}
            risk_free_rate: Tasa libre de riesgo anual (default 4%)
        """
        self.daily_values = np.array(daily_values, dtype=float)
        self.trades = trades or []
        self.risk_free_rate = risk_free_rate
        
        # Validación
        if len(self.daily_values) < 2:
            raise ValueError("Se necesitan al menos 2 valores diarios")
        
        logger.info(f"Calculador de métricas inicializado con {len(daily_values)} días")
    
    # ========== MÉTRICAS DE RETORNO ==========
    
    def total_return(self) -> float:
        """Retorno total en porcentaje."""
        initial = self.daily_values[0]
        final = self.daily_values[-1]
        if initial == 0:
            return 0
        return ((final - initial) / initial) * 100
    
    def annualized_return(self) -> float:
        """Retorno anualizado (asumiendo 252 días de trading por año)."""
        total_days = len(self.daily_values) - 1
        years = total_days / 252.0
        
        if years == 0:
            return 0
        
        total_ret = self.total_return() / 100
        annualized = ((1 + total_ret) ** (1 / years) - 1) * 100
        return annualized
    
    def average_daily_return(self) -> float:
        """Retorno diario promedio en porcentaje."""
        daily_returns = self.calculate_daily_returns()
        if len(daily_returns) == 0:
            return 0
        return np.mean(daily_returns) * 100
    
    # ========== MÉTRICAS DE RIESGO ==========
    
    def calculate_daily_returns(self) -> np.ndarray:
        """Calcula retornos diarios."""
        prices = np.array(self.daily_values, dtype=float)
        # Evitar división por cero
        with np.errstate(divide='ignore', invalid='ignore'):
            returns = np.diff(prices) / prices[:-1]
            returns = np.nan_to_num(returns)
        return returns
    
    def volatility(self) -> float:
        """Volatilidad diaria anualizada en porcentaje."""
        daily_returns = self.calculate_daily_returns()
        daily_vol = np.std(daily_returns)
        # Anualizar (252 días de trading)
        annualized_vol = daily_vol * np.sqrt(252) * 100
        return annualized_vol
    
    def sharpe_ratio(self) -> float:
        """
        Sharpe Ratio: (rendimiento - tasa libre de riesgo) / volatilidad
        
        Interpretación:
        - > 1: Bueno
        - > 2: Muy bueno
        - > 3: Excelente
        """
        daily_returns = self.calculate_daily_returns()
        avg_daily_return = np.mean(daily_returns)
        daily_vol = np.std(daily_returns)
        
        if daily_vol == 0:
            return 0
        
        # Convertir tasa anual a diaria (252 días de trading)
        daily_risk_free = self.risk_free_rate / 252
        
        sharpe = (avg_daily_return - daily_risk_free) / daily_vol
        # Anualizar
        sharpe_annual = sharpe * np.sqrt(252)
        
        return sharpe_annual
    
    def sortino_ratio(self, target_return: float = 0.0) -> float:
        """
        Sortino Ratio: similar a Sharpe pero solo cuenta volatilidad downside
        
        Más relevante que Sharpe para análisis de riesgo (penaliza volatilidad negativa)
        """
        daily_returns = self.calculate_daily_returns()
        
        # Retornos por debajo del target
        downside_returns = np.minimum(daily_returns - target_return / 252, 0)
        downside_vol = np.std(downside_returns)
        
        if downside_vol == 0:
            return 0
        
        avg_daily_return = np.mean(daily_returns)
        daily_risk_free = self.risk_free_rate / 252
        
        sortino = (avg_daily_return - daily_risk_free) / downside_vol
        # Anualizar
        sortino_annual = sortino * np.sqrt(252)
        
        return sortino_annual
    
    # ========== MÉTRICAS DE DRAWDOWN ==========
    
    def maximum_drawdown(self) -> Tuple[float, int, int]:
        """
        Máximo drawdown desde peak en porcentaje.
        
        Returns:
            (drawdown_pct, start_idx, end_idx)
        """
        prices = np.array(self.daily_values, dtype=float)
        
        # Calcular el peak corriente hasta cada día
        running_max = np.maximum.accumulate(prices)
        
        # Drawdown = (precio - peak) / peak
        drawdown = (prices - running_max) / running_max
        
        # Encontrar máximo drawdown
        max_dd_idx = np.argmin(drawdown)
        max_dd = drawdown[max_dd_idx]
        
        # Encontrar el peak antes del drawdown
        peak_idx = np.argmax(prices[:max_dd_idx + 1])
        
        return max_dd * 100, peak_idx, max_dd_idx
    
    def average_drawdown(self) -> float:
        """Promedio de todos los drawdowns."""
        prices = np.array(self.daily_values, dtype=float)
        running_max = np.maximum.accumulate(prices)
        drawdowns = (prices - running_max) / running_max
        
        # Solo contar drawdowns negativos
        negative_drawdowns = drawdowns[drawdowns < 0]
        if len(negative_drawdowns) == 0:
            return 0
        
        return np.mean(negative_drawdowns) * 100
    
    def recovery_factor(self) -> float:
        """
        Recovery Factor: Retorno Total / Máximo Drawdown
        
        Cuántos dolares ganamos por cada dólar de drawdown
        - > 2: Bueno
        - > 3: Muy bueno
        """
        max_dd, _, _ = self.maximum_drawdown()
        total_ret = self.total_return()
        
        if max_dd == 0:
            return float('inf') if total_ret > 0 else 0
        
        # max_dd ya es negativo, así que dividimos directamente
        return total_ret / abs(max_dd)
    
    def calmar_ratio(self) -> float:
        """
        Calmar Ratio: Retorno Anualizado / |Máximo Drawdown|
        
        Mide retorno por unidad de riesgo de drawdown
        - > 3: Bueno
        - > 5: Muy bueno
        """
        annualized_ret = self.annualized_return()
        max_dd, _, _ = self.maximum_drawdown()
        
        if max_dd == 0:
            return float('inf') if annualized_ret > 0 else 0
        
        return annualized_ret / abs(max_dd)
    
    # ========== MÉTRICAS DE TRADING ==========
    
    def win_rate(self) -> Tuple[float, int, int]:
        """
        Win rate de los trades.
        
        Returns:
            (win_rate_pct, num_winners, num_losers)
        """
        if not self.trades:
            return 0, 0, 0
        
        # Filtrar solo SELL (que tienen P&L)
        sells = [t for t in self.trades if t.get('action') == 'SELL']
        
        if not sells:
            return 0, 0, 0
        
        winners = [t for t in sells if t.get('pnl', 0) > 0]
        losers = [t for t in sells if t.get('pnl', 0) < 0]
        
        win_rate = (len(winners) / len(sells)) * 100 if sells else 0
        
        return win_rate, len(winners), len(losers)
    
    def profit_factor(self) -> Tuple[float, float, float]:
        """
        Profit Factor: Ganancias Brutas / Pérdidas Brutas
        
        - > 1.5: Viable
        - > 2.0: Bueno
        - > 3.0: Excelente
        
        Returns:
            (profit_factor, gross_profit, gross_loss)
        """
        if not self.trades:
            return 0, 0, 0
        
        sells = [t for t in self.trades if t.get('action') == 'SELL']
        if not sells:
            return 0, 0, 0
        
        pnls = [t.get('pnl', 0) for t in sells]
        gross_profit = sum([p for p in pnls if p > 0])
        gross_loss = sum([abs(p) for p in pnls if p < 0])
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0, gross_profit, 0
        
        profit_factor = gross_profit / gross_loss
        
        return profit_factor, gross_profit, gross_loss
    
    def average_win_loss(self) -> Tuple[float, float]:
        """Promedio de ganancias y pérdidas por trade."""
        if not self.trades:
            return 0, 0
        
        sells = [t for t in self.trades if t.get('action') == 'SELL']
        if not sells:
            return 0, 0
        
        pnls = [t.get('pnl', 0) for t in sells]
        
        winners = [p for p in pnls if p > 0]
        losers = [p for p in pnls if p < 0]
        
        avg_win = np.mean(winners) if winners else 0
        avg_loss = np.mean(losers) if losers else 0
        
        return avg_win, avg_loss
    
    def expectancy(self) -> float:
        """
        Expectancy: Ganancia esperada por trade
        
        (Win Rate × Avg Win) - (Loss Rate × |Avg Loss|)
        """
        win_rate, _, num_losers = self.win_rate()
        num_trades = sum(1 for t in self.trades if t.get('action') == 'SELL')
        
        if num_trades == 0:
            return 0
        
        avg_win, avg_loss = self.average_win_loss()
        loss_rate = 1 - (win_rate / 100)
        
        expectancy = (win_rate / 100 * avg_win) - (loss_rate * abs(avg_loss))
        
        return expectancy
    
    # ========== ESTADÍSTICAS ADICIONALES ==========
    
    def return_distribution(self) -> Dict:
        """Estadísticas de distribución de retornos."""
        daily_returns = self.calculate_daily_returns() * 100  # Convertir a porcentaje
        
        return {
            'mean': float(np.mean(daily_returns)),
            'median': float(np.median(daily_returns)),
            'std': float(np.std(daily_returns)),
            'min': float(np.min(daily_returns)),
            'max': float(np.max(daily_returns)),
            'skewness': float(self._skewness(daily_returns)),
            'kurtosis': float(self._kurtosis(daily_returns))
        }
    
    @staticmethod
    def _skewness(returns: np.ndarray) -> float:
        """Calcula skewness de distribución de retornos."""
        mean = np.mean(returns)
        std = np.std(returns)
        if std == 0:
            return 0
        return np.mean(((returns - mean) / std) ** 3)
    
    @staticmethod
    def _kurtosis(returns: np.ndarray) -> float:
        """Calcula kurtosis de distribución de retornos."""
        mean = np.mean(returns)
        std = np.std(returns)
        if std == 0:
            return 0
        return np.mean(((returns - mean) / std) ** 4) - 3
    
    def best_day(self) -> Tuple[float, int]:
        """Mejor día en porcentaje."""
        daily_returns = self.calculate_daily_returns() * 100
        if len(daily_returns) == 0:
            return 0, 0
        best_idx = np.argmax(daily_returns)
        return daily_returns[best_idx], best_idx
    
    def worst_day(self) -> Tuple[float, int]:
        """Peor día en porcentaje."""
        daily_returns = self.calculate_daily_returns() * 100
        if len(daily_returns) == 0:
            return 0, 0
        worst_idx = np.argmin(daily_returns)
        return daily_returns[worst_idx], worst_idx
    
    def consecutive_wins(self) -> int:
        """Mayor racha de trades ganadores."""
        if not self.trades:
            return 0
        
        sells = [t for t in self.trades if t.get('action') == 'SELL']
        if not sells:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in sells:
            if trade.get('pnl', 0) > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def consecutive_losses(self) -> int:
        """Mayor racha de trades perdedores."""
        if not self.trades:
            return 0
        
        sells = [t for t in self.trades if t.get('action') == 'SELL']
        if not sells:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in sells:
            if trade.get('pnl', 0) < 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    # ========== RESUMEN COMPLETO ==========
    
    def generate_summary(self) -> Dict:
        """Genera resumen completo de métricas."""
        max_dd, dd_start, dd_end = self.maximum_drawdown()
        win_rate, wins, losses = self.win_rate()
        profit_factor, gross_profit, gross_loss = self.profit_factor()
        avg_win, avg_loss = self.average_win_loss()
        best, best_idx = self.best_day()
        worst, worst_idx = self.worst_day()
        
        summary = {
            'returns': {
                'total_return_pct': round(self.total_return(), 2),
                'annualized_return_pct': round(self.annualized_return(), 2),
                'avg_daily_return_pct': round(self.average_daily_return(), 4),
                'best_day_pct': round(best, 2),
                'worst_day_pct': round(worst, 2),
            },
            'risk': {
                'volatility_pct': round(self.volatility(), 2),
                'maximum_drawdown_pct': round(max_dd, 2),
                'average_drawdown_pct': round(self.average_drawdown(), 2),
                'drawdown_duration_days': int(dd_end - dd_start),
            },
            'risk_adjusted': {
                'sharpe_ratio': round(self.sharpe_ratio(), 2),
                'sortino_ratio': round(self.sortino_ratio(), 2),
                'calmar_ratio': round(self.calmar_ratio(), 2),
                'recovery_factor': round(self.recovery_factor(), 2),
            },
            'trading': {
                'total_trades': int(len([t for t in self.trades if t.get('action') == 'SELL'])),
                'win_rate_pct': round(win_rate, 2),
                'winning_trades': int(wins),
                'losing_trades': int(losses),
                'profit_factor': round(profit_factor, 2),
                'avg_win': round(avg_win, 2),
                'avg_loss': round(avg_loss, 2),
                'expectancy': round(self.expectancy(), 2),
                'consecutive_wins': int(self.consecutive_wins()),
                'consecutive_losses': int(self.consecutive_losses()),
            },
            'statistics': self.return_distribution(),
        }
        
        return summary
    
    def print_summary(self):
        """Imprime resumen formateado."""
        summary = self.generate_summary()
        
        print("\n" + "="*80)
        print(" "*25 + "📊 BACKTEST ANALYSIS SUMMARY 📊")
        print("="*80)
        
        # Returns
        print("\n📈 RETURNS")
        print("-" * 80)
        print(f"  Total Return:           {summary['returns']['total_return_pct']:>10.2f}%")
        print(f"  Annualized Return:      {summary['returns']['annualized_return_pct']:>10.2f}%")
        print(f"  Avg Daily Return:       {summary['returns']['avg_daily_return_pct']:>10.4f}%")
        print(f"  Best Day:               {summary['returns']['best_day_pct']:>10.2f}%")
        print(f"  Worst Day:              {summary['returns']['worst_day_pct']:>10.2f}%")
        
        # Risk
        print("\n⚠️  RISK")
        print("-" * 80)
        print(f"  Volatility (annualized): {summary['risk']['volatility_pct']:>10.2f}%")
        print(f"  Maximum Drawdown:       {summary['risk']['maximum_drawdown_pct']:>10.2f}%")
        print(f"  Average Drawdown:       {summary['risk']['average_drawdown_pct']:>10.2f}%")
        print(f"  Drawdown Duration:      {summary['risk']['drawdown_duration_days']:>10} days")
        
        # Risk-Adjusted
        print("\n⚖️  RISK-ADJUSTED RETURNS")
        print("-" * 80)
        print(f"  Sharpe Ratio:           {summary['risk_adjusted']['sharpe_ratio']:>10.2f}")
        print(f"  Sortino Ratio:          {summary['risk_adjusted']['sortino_ratio']:>10.2f}")
        print(f"  Calmar Ratio:           {summary['risk_adjusted']['calmar_ratio']:>10.2f}")
        print(f"  Recovery Factor:        {summary['risk_adjusted']['recovery_factor']:>10.2f}")
        
        # Trading
        print("\n💹 TRADING STATISTICS")
        print("-" * 80)
        print(f"  Total Trades:           {summary['trading']['total_trades']:>10.0f}")
        print(f"  Win Rate:               {summary['trading']['win_rate_pct']:>10.2f}%")
        print(f"  Winning Trades:         {summary['trading']['winning_trades']:>10.0f}")
        print(f"  Losing Trades:          {summary['trading']['losing_trades']:>10.0f}")
        print(f"  Profit Factor:          {summary['trading']['profit_factor']:>10.2f}")
        print(f"  Avg Win:                ${summary['trading']['avg_win']:>9.2f}")
        print(f"  Avg Loss:               ${summary['trading']['avg_loss']:>9.2f}")
        print(f"  Expectancy:             ${summary['trading']['expectancy']:>9.2f}")
        print(f"  Max Consecutive Wins:   {summary['trading']['consecutive_wins']:>10.0f}")
        print(f"  Max Consecutive Losses: {summary['trading']['consecutive_losses']:>10.0f}")
        
        # Distribution
        print("\n📊 RETURN DISTRIBUTION")
        print("-" * 80)
        print(f"  Mean Daily Return:      {summary['statistics']['mean']:>10.4f}%")
        print(f"  Median Daily Return:    {summary['statistics']['median']:>10.4f}%")
        print(f"  Std Dev:                {summary['statistics']['std']:>10.4f}%")
        print(f"  Skewness:               {summary['statistics']['skewness']:>10.2f}")
        print(f"  Kurtosis:               {summary['statistics']['kurtosis']:>10.2f}")
        print(f"  Min Daily:              {summary['statistics']['min']:>10.2f}%")
        print(f"  Max Daily:              {summary['statistics']['max']:>10.2f}%")
        
        print("\n" + "="*80 + "\n")
        
        return summary


# ============================================================
# CLI INTERFACE
# ============================================================

if __name__ == "__main__":
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="Advanced Metrics Calculator")
    parser.add_argument("--demo", action="store_true", help="Ejecutar demo")
    parser.add_argument("--daily-csv", help="Ruta a CSV con valores diarios")
    parser.add_argument("--trades-csv", help="Ruta a CSV con transacciones")
    
    args = parser.parse_args()
    
    if args.demo:
        # Demo con datos simulados
        print("\n🧪 Running Advanced Metrics Demo...")
        
        # Simular portafolio que crece con volatilidad
        np.random.seed(42)
        days = 252  # 1 año
        initial = 100000
        daily_returns = np.random.normal(0.0005, 0.015, days)
        daily_values = initial * np.cumprod(1 + daily_returns)
        
        # Simular algunos trades
        trades = [
            {'action': 'BUY', 'ticker': 'AAPL', 'date': '2024-01-01'},
            {'action': 'SELL', 'ticker': 'AAPL', 'date': '2024-02-01', 'pnl': 1500},
            {'action': 'BUY', 'ticker': 'MSFT', 'date': '2024-02-15'},
            {'action': 'SELL', 'ticker': 'MSFT', 'date': '2024-03-20', 'pnl': -800},
            {'action': 'BUY', 'ticker': 'NVDA', 'date': '2024-04-01'},
            {'action': 'SELL', 'ticker': 'NVDA', 'date': '2024-05-10', 'pnl': 3200},
        ]
        
        calculator = AdvancedMetricsCalculator(daily_values, trades)
        summary = calculator.generate_summary()
        calculator.print_summary()
        
        # Guardar resumen como JSON
        summary_file = Path("backtest_results/metrics_demo.json")
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Metrics saved to: {summary_file}\n")
    
    elif args.daily_csv and args.trades_csv:
        # Leer desde archivos
        daily_df = pd.read_csv(args.daily_csv)
        trades_df = pd.read_csv(args.trades_csv)
        
        daily_values = daily_df.iloc[:, 0].values
        trades = trades_df.to_dict('records')
        
        calculator = AdvancedMetricsCalculator(daily_values, trades)
        calculator.print_summary()
    
    else:
        parser.print_help()
