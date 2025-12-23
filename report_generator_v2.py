"""
Report Generator V2 - Genera reportes HTML interactivos con gráficos

Funcionalidad:
- Reportes HTML completos con gráficos interactivos
- Equity curve (curva de patrimonio)
- Drawdown curve (curva de pérdidas)
- Returns distribution
- Trade analysis
- Performance comparison

Author: Spectral Galileo
Date: 2025-12-23
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReportGeneratorV2:
    """Genera reportes HTML interactivos."""
    
    def __init__(self, output_dir: str = "./backtest_results"):
        """
        Inicializa el generador de reportes.
        
        Args:
            output_dir: Directorio donde guardar reportes
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ReportGeneratorV2 inicializado en: {self.output_dir}")
    
    def generate_html_report(
        self,
        backtest_name: str,
        metrics_summary: Dict,
        daily_values: List[float],
        trades: List[Dict],
        start_date: str = None,
        end_date: str = None,
        tickers: List[str] = None
    ) -> str:
        """
        Genera reporte HTML completo.
        
        Args:
            backtest_name: Nombre del backtest
            metrics_summary: Diccionario con métricas (de AdvancedMetricsCalculator.generate_summary())
            daily_values: Lista de valores diarios
            trades: Lista de transacciones
            start_date: Fecha inicio
            end_date: Fecha final
            tickers: Lista de tickers testeados
            
        Returns:
            Ruta del archivo HTML generado
        """
        html_file = self.output_dir / f"report_{backtest_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Calcular datos para gráficos
        chart_data = self._prepare_chart_data(daily_values, trades)
        
        # Generar HTML
        html_content = self._generate_html(
            backtest_name,
            metrics_summary,
            chart_data,
            trades,
            start_date,
            end_date,
            tickers
        )
        
        # Guardar archivo
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"✓ Reporte HTML generado: {html_file}")
        return str(html_file)
    
    def _prepare_chart_data(self, daily_values: List[float], trades: List[Dict]) -> Dict:
        """Prepara datos para gráficos."""
        prices = np.array(daily_values, dtype=float)
        
        # Drawdown
        running_max = np.maximum.accumulate(prices)
        drawdown = (prices - running_max) / running_max * 100
        
        # Returns diarios
        returns = np.diff(prices) / prices[:-1] * 100
        returns = np.insert(returns, 0, 0)  # Primer día = 0
        
        return {
            'prices': prices.tolist(),
            'drawdown': drawdown.tolist(),
            'returns': returns.tolist(),
        }
    
    def _generate_html(
        self,
        backtest_name: str,
        metrics: Dict,
        chart_data: Dict,
        trades: List[Dict],
        start_date: Optional[str],
        end_date: Optional[str],
        tickers: Optional[List[str]]
    ) -> str:
        """Genera contenido HTML."""
        
        # Formatear métricas
        returns_html = self._format_returns_section(metrics['returns'])
        risk_html = self._format_risk_section(metrics['risk'])
        risk_adj_html = self._format_risk_adjusted_section(metrics['risk_adjusted'])
        trading_html = self._format_trading_section(metrics['trading'])
        stats_html = self._format_stats_section(metrics['statistics'])
        
        # Preparar datos para Chart.js
        chart_js_data = json.dumps(chart_data)
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backtest Report - {backtest_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .info-bar {{
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
        }}
        
        .info-item {{
            text-align: center;
        }}
        
        .info-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .info-value {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 5px;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.1);
        }}
        
        .metric-card.positive {{
            border-left-color: #10b981;
        }}
        
        .metric-card.negative {{
            border-left-color: #ef4444;
        }}
        
        .metric-card.neutral {{
            border-left-color: #f59e0b;
        }}
        
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        
        .metric-unit {{
            font-size: 0.8em;
            color: #999;
            margin-left: 5px;
        }}
        
        .chart-container {{
            position: relative;
            width: 100%;
            margin-bottom: 30px;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
        }}
        
        .chart-wrapper {{
            position: relative;
            height: 400px;
        }}
        
        .trades-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .trades-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .trades-table td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .trades-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .trade-positive {{
            color: #10b981;
            font-weight: bold;
        }}
        
        .trade-negative {{
            color: #ef4444;
            font-weight: bold;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
        
        .value-positive {{
            color: #10b981;
        }}
        
        .value-negative {{
            color: #ef4444;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin: 2px;
        }}
        
        .badge-success {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .badge-danger {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .badge-warning {{
            background: #fef3c7;
            color: #92400e;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Backtest Report</h1>
            <p>{backtest_name}</p>
        </header>
        
        <div class="info-bar">
            <div class="info-item">
                <div class="info-label">Total Return</div>
                <div class="info-value value-{('positive' if metrics['returns']['total_return_pct'] >= 0 else 'negative')}">
                    {metrics['returns']['total_return_pct']:.2f}%
                </div>
            </div>
            <div class="info-item">
                <div class="info-label">Annualized Return</div>
                <div class="info-value value-{('positive' if metrics['returns']['annualized_return_pct'] >= 0 else 'negative')}">
                    {metrics['returns']['annualized_return_pct']:.2f}%
                </div>
            </div>
            <div class="info-item">
                <div class="info-label">Sharpe Ratio</div>
                <div class="info-value">{metrics['risk_adjusted']['sharpe_ratio']:.2f}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Max Drawdown</div>
                <div class="info-value value-negative">{metrics['risk']['maximum_drawdown_pct']:.2f}%</div>
            </div>
            <div class="info-item">
                <div class="info-label">Win Rate</div>
                <div class="info-value">{metrics['trading']['win_rate_pct']:.1f}%</div>
            </div>
        </div>
        
        <div class="content">
            {returns_html}
            {risk_html}
            {risk_adj_html}
            {trading_html}
            {stats_html}
            
            <!-- Equity Curve -->
            <div class="section">
                <h2 class="section-title">📈 Equity Curve</h2>
                <div class="chart-container">
                    <div class="chart-wrapper">
                        <canvas id="equityChart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Drawdown -->
            <div class="section">
                <h2 class="section-title">📉 Drawdown</h2>
                <div class="chart-container">
                    <div class="chart-wrapper">
                        <canvas id="drawdownChart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Daily Returns -->
            <div class="section">
                <h2 class="section-title">📊 Daily Returns Distribution</h2>
                <div class="chart-container">
                    <div class="chart-wrapper">
                        <canvas id="returnsChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Spectral Galileo Backtesting System</p>
        </footer>
    </div>
    
    <script>
        const chartData = {chart_js_data};
        
        // Equity Chart
        const equityCtx = document.getElementById('equityChart').getContext('2d');
        new Chart(equityCtx, {{
            type: 'line',
            data: {{
                labels: Array.from({{length: chartData.prices.length}}, (_, i) => i),
                datasets: [{{
                    label: 'Portfolio Value',
                    data: chartData.prices,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    borderWidth: 2,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false,
                    }}
                }},
                scales: {{
                    y: {{
                        ticks: {{
                            callback: function(value) {{
                                return '$' + value.toLocaleString();
                            }}
                        }}
                    }},
                    x: {{
                        display: false,
                    }}
                }}
            }}
        }});
        
        // Drawdown Chart
        const drawdownCtx = document.getElementById('drawdownChart').getContext('2d');
        new Chart(drawdownCtx, {{
            type: 'bar',
            data: {{
                labels: Array.from({{length: chartData.drawdown.length}}, (_, i) => i),
                datasets: [{{
                    label: 'Drawdown %',
                    data: chartData.drawdown,
                    backgroundColor: chartData.drawdown.map(v => v < 0 ? '#ef4444' : '#10b981'),
                    borderRadius: 2,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'x',
                plugins: {{
                    legend: {{
                        display: false,
                    }}
                }},
                scales: {{
                    y: {{
                        ticks: {{
                            callback: function(value) {{
                                return value.toFixed(1) + '%';
                            }}
                        }}
                    }},
                    x: {{
                        display: false,
                    }}
                }}
            }}
        }});
        
        // Returns Histogram
        const returnsCtx = document.getElementById('returnsChart').getContext('2d');
        const bins = 50;
        const min = Math.min(...chartData.returns);
        const max = Math.max(...chartData.returns);
        const binWidth = (max - min) / bins;
        const hist = Array(bins).fill(0);
        
        chartData.returns.forEach(r => {{
            const binIndex = Math.floor((r - min) / binWidth);
            if (binIndex >= 0 && binIndex < bins) {{
                hist[binIndex]++;
            }}
        }});
        
        new Chart(returnsCtx, {{
            type: 'bar',
            data: {{
                labels: Array.from({{length: bins}}, (_, i) => 
                    (min + i * binWidth).toFixed(2) + '%'
                ),
                datasets: [{{
                    label: 'Frequency',
                    data: hist,
                    backgroundColor: '#667eea',
                    borderRadius: 2,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'x',
                plugins: {{
                    legend: {{
                        display: false,
                    }}
                }},
                scales: {{
                    x: {{
                        display: false,
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        return html
    
    def _format_returns_section(self, returns: Dict) -> str:
        """Formatea sección de retornos."""
        return f"""
        <div class="section">
            <h2 class="section-title">📈 Returns</h2>
            <div class="metrics-grid">
                <div class="metric-card positive">
                    <div class="metric-label">Total Return</div>
                    <div class="metric-value">{returns['total_return_pct']:.2f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card positive">
                    <div class="metric-label">Annualized Return</div>
                    <div class="metric-value">{returns['annualized_return_pct']:.2f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Avg Daily Return</div>
                    <div class="metric-value">{returns['avg_daily_return_pct']:.4f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card positive">
                    <div class="metric-label">Best Day</div>
                    <div class="metric-value">{returns['best_day_pct']:.2f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card negative">
                    <div class="metric-label">Worst Day</div>
                    <div class="metric-value">{returns['worst_day_pct']:.2f}<span class="metric-unit">%</span></div>
                </div>
            </div>
        </div>
        """
    
    def _format_risk_section(self, risk: Dict) -> str:
        """Formatea sección de riesgo."""
        return f"""
        <div class="section">
            <h2 class="section-title">⚠️ Risk Metrics</h2>
            <div class="metrics-grid">
                <div class="metric-card neutral">
                    <div class="metric-label">Volatility</div>
                    <div class="metric-value">{risk['volatility_pct']:.2f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card negative">
                    <div class="metric-label">Maximum Drawdown</div>
                    <div class="metric-value">{risk['maximum_drawdown_pct']:.2f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card negative">
                    <div class="metric-label">Average Drawdown</div>
                    <div class="metric-value">{risk['average_drawdown_pct']:.2f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Drawdown Duration</div>
                    <div class="metric-value">{risk['drawdown_duration_days']:.0f}<span class="metric-unit">days</span></div>
                </div>
            </div>
        </div>
        """
    
    def _format_risk_adjusted_section(self, risk_adj: Dict) -> str:
        """Formatea sección de retornos ajustados por riesgo."""
        sharpe_class = 'positive' if risk_adj['sharpe_ratio'] > 1 else 'neutral'
        calmar_class = 'positive' if risk_adj['calmar_ratio'] > 3 else 'neutral'
        
        return f"""
        <div class="section">
            <h2 class="section-title">⚖️ Risk-Adjusted Returns</h2>
            <div class="metrics-grid">
                <div class="metric-card {sharpe_class}">
                    <div class="metric-label">Sharpe Ratio</div>
                    <div class="metric-value">{risk_adj['sharpe_ratio']:.2f}</div>
                    <small style="color: #666; margin-top: 5px; display: block;">
                        {'✓ Good' if risk_adj['sharpe_ratio'] > 1 else '⚠ Below 1'}
                    </small>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Sortino Ratio</div>
                    <div class="metric-value">{risk_adj['sortino_ratio']:.2f}</div>
                </div>
                <div class="metric-card {calmar_class}">
                    <div class="metric-label">Calmar Ratio</div>
                    <div class="metric-value">{risk_adj['calmar_ratio']:.2f}</div>
                    <small style="color: #666; margin-top: 5px; display: block;">
                        {'✓ Good' if risk_adj['calmar_ratio'] > 3 else '⚠ Below 3'}
                    </small>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Recovery Factor</div>
                    <div class="metric-value">{risk_adj['recovery_factor']:.2f}</div>
                </div>
            </div>
        </div>
        """
    
    def _format_trading_section(self, trading: Dict) -> str:
        """Formatea sección de estadísticas de trading."""
        profit_class = 'positive' if trading['profit_factor'] > 1.5 else 'neutral'
        
        return f"""
        <div class="section">
            <h2 class="section-title">💹 Trading Statistics</h2>
            <div class="metrics-grid">
                <div class="metric-card neutral">
                    <div class="metric-label">Total Trades</div>
                    <div class="metric-value">{trading['total_trades']:.0f}</div>
                </div>
                <div class="metric-card positive">
                    <div class="metric-label">Win Rate</div>
                    <div class="metric-value">{trading['win_rate_pct']:.1f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card positive">
                    <div class="metric-label">Winning Trades</div>
                    <div class="metric-value">{trading['winning_trades']:.0f}</div>
                </div>
                <div class="metric-card negative">
                    <div class="metric-label">Losing Trades</div>
                    <div class="metric-value">{trading['losing_trades']:.0f}</div>
                </div>
                <div class="metric-card {profit_class}">
                    <div class="metric-label">Profit Factor</div>
                    <div class="metric-value">{trading['profit_factor']:.2f}</div>
                    <small style="color: #666; margin-top: 5px; display: block;">
                        {'✓ Good' if trading['profit_factor'] > 1.5 else '⚠ Below 1.5'}
                    </small>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Avg Win</div>
                    <div class="metric-value">${trading['avg_win']:.0f}</div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Avg Loss</div>
                    <div class="metric-value">${trading['avg_loss']:.0f}</div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Expectancy</div>
                    <div class="metric-value">${trading['expectancy']:.0f}</div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Max Consecutive Wins</div>
                    <div class="metric-value">{trading['consecutive_wins']:.0f}</div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Max Consecutive Losses</div>
                    <div class="metric-value">{trading['consecutive_losses']:.0f}</div>
                </div>
            </div>
        </div>
        """
    
    def _format_stats_section(self, stats: Dict) -> str:
        """Formatea sección de estadísticas."""
        return f"""
        <div class="section">
            <h2 class="section-title">📊 Return Distribution</h2>
            <div class="metrics-grid">
                <div class="metric-card neutral">
                    <div class="metric-label">Mean Daily Return</div>
                    <div class="metric-value">{stats['mean']:.4f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Median Daily Return</div>
                    <div class="metric-value">{stats['median']:.4f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Std Deviation</div>
                    <div class="metric-value">{stats['std']:.4f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Skewness</div>
                    <div class="metric-value">{stats['skewness']:.2f}</div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Kurtosis</div>
                    <div class="metric-value">{stats['kurtosis']:.2f}</div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Min Daily</div>
                    <div class="metric-value">{stats['min']:.2f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-label">Max Daily</div>
                    <div class="metric-value">{stats['max']:.2f}<span class="metric-unit">%</span></div>
                </div>
            </div>
        </div>
        """


# ============================================================
# CLI INTERFACE
# ============================================================

if __name__ == "__main__":
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="Report Generator V2")
    parser.add_argument("--demo", action="store_true", help="Ejecutar demo")
    
    args = parser.parse_args()
    
    if args.demo:
        print("\n🎨 Generating Sample HTML Report...")
        
        # Sample data
        np.random.seed(42)
        days = 252
        initial = 100000
        daily_returns = np.random.normal(0.0005, 0.015, days)
        daily_values = initial * np.cumprod(1 + daily_returns)
        
        trades = [
            {'action': 'BUY', 'ticker': 'AAPL'},
            {'action': 'SELL', 'ticker': 'AAPL', 'pnl': 1500},
            {'action': 'BUY', 'ticker': 'MSFT'},
            {'action': 'SELL', 'ticker': 'MSFT', 'pnl': -800},
            {'action': 'BUY', 'ticker': 'NVDA'},
            {'action': 'SELL', 'ticker': 'NVDA', 'pnl': 3200},
        ]
        
        # Mock metrics summary
        metrics = {
            'returns': {
                'total_return_pct': 8.5,
                'annualized_return_pct': 8.6,
                'avg_daily_return_pct': 0.03,
                'best_day_pct': 3.2,
                'worst_day_pct': -2.8,
            },
            'risk': {
                'volatility_pct': 18.5,
                'maximum_drawdown_pct': -12.3,
                'average_drawdown_pct': -4.2,
                'drawdown_duration_days': 15,
            },
            'risk_adjusted': {
                'sharpe_ratio': 1.45,
                'sortino_ratio': 2.1,
                'calmar_ratio': 0.7,
                'recovery_factor': 2.3,
            },
            'trading': {
                'total_trades': 6,
                'win_rate_pct': 66.7,
                'winning_trades': 4,
                'losing_trades': 2,
                'profit_factor': 2.1,
                'avg_win': 1566.67,
                'avg_loss': -800,
                'expectancy': 1066.67,
                'consecutive_wins': 3,
                'consecutive_losses': 1,
            },
            'statistics': {
                'mean': 0.0337,
                'median': 0.045,
                'std': 1.52,
                'skewness': -0.42,
                'kurtosis': 2.1,
                'min': -2.8,
                'max': 3.2,
            }
        }
        
        generator = ReportGeneratorV2()
        html_file = generator.generate_html_report(
            backtest_name="Demo Backtest",
            metrics_summary=metrics,
            daily_values=daily_values.tolist(),
            trades=trades,
            start_date="2024-01-01",
            end_date="2024-12-31",
            tickers=["AAPL", "MSFT", "NVDA"]
        )
        
        print(f"✓ Sample report generated: {html_file}\n")
