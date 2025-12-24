"""
Agent-Based Backtester - Integración de Agent.py con Backtesting

Funcionalidad:
- Usa agent.py para generar señales en lugar de RSI/MA20
- Soporta análisis corto plazo (3-6 meses) y largo plazo (2-5 años)
- Combina análisis fundamental, técnico y macroeconómico
- Genera reportes comparativos agent vs signals técnicas

Author: Spectral Galileo
Date: 2025-12-23
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Dict, Tuple, Optional
import json
import sys
from pathlib import Path

# Agregar directorio root al Python path para importar agent.py
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from backtest_data_manager import BacktestDataManager
from backtest_portfolio import BacktestPortfolio
from advanced_metrics import AdvancedMetricsCalculator
from report_generator_v2 import ReportGeneratorV2

# Importar agent
try:
    from agent import FinancialAgent
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    logging.warning("Agent.py no disponible - usando señales técnicas fallback")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentBacktester:
    """
    Backtester que utiliza FinancialAgent para generar señales.
    """
    
    def __init__(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        initial_cash: float = 100000.0,
        analysis_type: str = "long_term",  # 'short_term' o 'long_term'
        data_dir: str = "./backtest_data",
        results_dir: str = "./backtest_results"
    ):
        """
        Inicializa el Agent-Based Backtester.
        
        Args:
            tickers: Lista de tickers
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
            initial_cash: Capital inicial
            analysis_type: 'short_term' (momentum) o 'long_term' (fundamentals)
            data_dir: Directorio con datos
            results_dir: Directorio para resultados
        """
        self.tickers = tickers
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.initial_cash = initial_cash
        self.analysis_type = analysis_type
        self.is_short_term = (analysis_type == "short_term")
        self.data_dir = data_dir
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Componentes
        self.data_manager = BacktestDataManager(data_dir=data_dir)
        self.portfolio = BacktestPortfolio(initial_cash=initial_cash)
        
        # Datos
        self.daily_data = {}  # {ticker: DataFrame}
        self.agent_scores = {}  # {date: {ticker: score}}
        self.agent_details = {}  # {date: {ticker: details}}
        
        # Cache de agentes para evitar recrearlos
        self.agents = {}  # {ticker: FinancialAgent}
        
        # ==================== PHASE 3: RISK MANAGEMENT ====================
        # Tracking de posiciones abiertas con stops y targets
        self.open_positions = {}  # {ticker: {'entry_price': float, 'shares': int, 'entry_date': date}}
        self.position_stops = {}   # {ticker: {'stop_loss': float, 'take_profit': float}}
        self.risk_management_enabled = True  # Para habilitar/deshabilitar RM
        self.max_risk_per_trade = 0.02  # 2% máximo riesgo por trade
        # ====================================================================
        
        analysis_desc = "Short-Term (Momentum)" if self.is_short_term else "Long-Term (Fundamentals)"
        logger.info(f"AgentBacktester inicializado:")
        logger.info(f"  Tickers: {', '.join(tickers)}")
        logger.info(f"  Período: {start_date} → {end_date}")
        logger.info(f"  Analysis Type: {analysis_desc}")
        logger.info(f"  Capital inicial: ${initial_cash:,.2f}")
    
    def load_data(self) -> bool:
        """Carga datos históricos para todos los tickers."""
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
                
                if data is not None and not data.empty:
                    # Normalize column names to Title Case
                    data.columns = data.columns.str.title()
                    self.daily_data[ticker] = data
                    successful += 1
                else:
                    logger.warning(f"  ⚠ {ticker}: No se cargaron datos")
                    
            except Exception as e:
                logger.error(f"  ✗ {ticker}: Error - {e}")
        
        logger.info(f"✨ {successful}/{len(self.tickers)} tickers cargados exitosamente\n")
        return successful > 0
    
    def _calculate_volatility(self, ticker: str, periods: int = 20) -> float:
        """
        Calcula volatilidad anualizada (desviación estándar de retornos diarios).
        
        Args:
            ticker: Símbolo del ticker
            periods: Número de días para calcular (default 20)
            
        Returns:
            Volatilidad anualizada (ej: 0.02 = 2%)
        """
        if ticker not in self.daily_data:
            return 0.02  # Default: 2% volatilidad
        
        data = self.daily_data[ticker]
        if len(data) < periods:
            return 0.02
        
        # Calcular retornos diarios
        close = data['Close'].tail(periods).values
        returns = np.diff(close) / close[:-1]
        
        # Desviación estándar diaria
        daily_volatility = np.std(returns)
        
        # Anualizada (252 días de trading)
        annual_volatility = daily_volatility * np.sqrt(252)
        
        return float(annual_volatility)
    
    def get_daily_prices(self, date: pd.Timestamp) -> Dict[str, float]:
        """Obtiene precios de cierre para una fecha específica."""
        prices = {}
        for ticker, data in self.daily_data.items():
            try:
                price = data[data.index <= date]['Close'].iloc[-1]
                prices[ticker] = float(price)
            except (IndexError, KeyError):
                pass
        return prices
    
    def generate_agent_signals(
        self,
        date: pd.Timestamp,
        prices: Dict[str, float],
        lookback_days: int = 60
    ) -> Dict[str, Dict]:
        """
        Genera señales usando FinancialAgent.
        
        Returns:
            {ticker: {signal, strength, score, reason}}
        """
        signals = {}
        
        if not AGENT_AVAILABLE:
            logger.warning("Agent.py no disponible - usando fallback")
            return self._generate_fallback_signals(date, prices)
        
        for ticker in self.tickers:
            try:
                # Obtener datos hasta esta fecha
                hist_data = self.daily_data[ticker][
                    self.daily_data[ticker].index <= date
                ].tail(lookback_days)
                
                if len(hist_data) < 5:  # Necesitamos mínimo 5 días
                    continue
                
                # Crear o reutilizar agente
                if ticker not in self.agents:
                    self.agents[ticker] = FinancialAgent(
                        ticker_symbol=ticker,
                        is_short_term=self.is_short_term
                    )
                
                agent = self.agents[ticker]
                
                # Ejecutar análisis con datos históricos
                pre_data = {
                    'history': hist_data,
                    'fundamentals': agent.info if hasattr(agent, 'info') else {},
                    'news': agent.news if hasattr(agent, 'news') else [],
                    'macro_data': agent.macro_data if hasattr(agent, 'macro_data') else {}
                }
                
                # Ejecutar análisis
                analysis = agent.run_analysis(pre_data=pre_data)
                
                if 'error' in analysis:
                    logger.warning(f"  {ticker}: Analysis error - {analysis['error']}")
                    continue
                
                # MEJORA: Calcular volatilidad para scoring dinámico
                volatility = self._calculate_volatility(ticker)
                
                # PHASE 2: Usar scoring específico según tipo de análisis
                if self.is_short_term:
                    # SHORT-TERM: Momentum puro
                    score = self._calculate_short_term_score(analysis)
                else:
                    # LONG-TERM: Composite (técnico + fundamental + sentimiento)
                    score = self._calculate_composite_score(analysis)
                
                # MEJORA: Aplicar thresholds dinámicos con volatilidad
                signal = self._score_to_signal(score, self.is_short_term, volatility, ticker=ticker)
                strength = abs(score - 50) / 50  # 0-1 basado en distancia de 50
                
                # Extraer pros/cons del análisis
                pros = []
                cons = []
                if analysis.get('technical'):
                    tech = analysis['technical']
                    rsi = tech.get('rsi', 50)
                    macd = tech.get('macd_status', '')
                    if rsi < 35:
                        pros.append(f"RSI Bajista ({rsi:.1f})")
                    elif rsi > 65:
                        cons.append(f"RSI Alcista ({rsi:.1f})")
                    if macd == 'Bullish':
                        pros.append("MACD Bullish")
                    elif macd == 'Bearish':
                        cons.append("MACD Bearish")
                
                signals[ticker] = {
                    'signal': signal,
                    'strength': min(strength, 1.0),
                    'score': round(score, 2),
                    'price': prices.get(ticker, 0),
                    'volatility': round(volatility * 100, 2),
                    'pros': pros[:2],  # Top 2 pros
                    'cons': cons[:2],  # Top 2 cons
                    'recommendation': analysis.get('strategy', {}).get('action', 'HOLD') if isinstance(analysis.get('strategy'), dict) else 'HOLD',
                }
                
                # Guardar detalles para análisis posterior
                if date not in self.agent_details:
                    self.agent_details[date] = {}
                self.agent_details[date][ticker] = signals[ticker]
                
            except Exception as e:
                logger.warning(f"  {ticker}: Signal generation error - {str(e)[:100]}")
                continue
        
        return signals
    
    def _calculate_composite_score(self, analysis: Dict) -> float:
        """
        Calcula un score compuesto (0-100) basado en el análisis del agente.
        
        MEJORA 4: Pesos optimizados según tipo de análisis
        - Short-term: 75% Technical, 15% Fundamental, 10% Sentiment (momentum focus)
        - Long-term: 50% Technical, 35% Fundamental, 15% Sentiment (value focus)
        """
        score_components = []
        
        # Determinar pesos según tipo de análisis
        if self.is_short_term:
            tech_weight = 0.75      # IMPROVED: Was 0.60
            fund_weight = 0.15      # IMPROVED: Was 0.25
            sent_weight = 0.10      # IMPROVED: Was 0.15
        else:
            tech_weight = 0.50      # IMPROVED: Was 0.60
            fund_weight = 0.35      # IMPROVED: Was 0.25
            sent_weight = 0.15      # Same
        
        # 1. Componente Técnico
        if analysis.get('technical'):
            tech = analysis['technical']
            
            # RSI es el indicador clave para momentum
            rsi = tech.get('rsi', 50)
            rsi_score = 100 - rsi  # Invertir: RSI bajo = score alto
            rsi_score = max(0, min(100, rsi_score))
            
            # MACD direction
            macd_status = tech.get('macd_status', '')
            macd_score = 75 if macd_status == 'Bullish' else 25 if macd_status == 'Bearish' else 50
            
            # Stoch K indicator
            stoch_k = tech.get('stoch_k', 50)
            stoch_score = 100 - stoch_k
            stoch_score = max(0, min(100, stoch_score))
            
            # Combinar técnicos con más peso a RSI
            tech_score = (rsi_score * 0.45 + macd_score * 0.35 + stoch_score * 0.20)
            score_components.append(('technical', tech_score, tech_weight))
        
        # 2. Componente Fundamental
        if analysis.get('fundamental'):
            fund = analysis['fundamental']
            fund_score = 50
            
            if isinstance(fund, dict):
                # PE ratio
                pe_ratio = fund.get('pe_ratio')
                if pe_ratio:
                    if pe_ratio < 15:
                        fund_score = 75
                    elif pe_ratio < 25:
                        fund_score = 60
                    elif pe_ratio > 40:
                        fund_score = 25
                    else:
                        fund_score = 50
                
                # ROE (Return on Equity)
                roe = fund.get('roe')
                if roe:
                    if roe > 0.20:
                        fund_score = min(100, fund_score + 15)
                    elif roe > 0.15:
                        fund_score = min(100, fund_score + 5)
                    elif roe < 0.10:
                        fund_score = max(0, fund_score - 10)
                
                # Debt to Equity
                debt_eq = fund.get('debt_to_equity')
                if debt_eq:
                    if debt_eq < 0.5:
                        fund_score = min(100, fund_score + 10)
                    elif debt_eq > 2.0:
                        fund_score = max(0, fund_score - 15)
            
            fund_score = max(0, min(100, fund_score))
            score_components.append(('fundamental', fund_score, fund_weight))
        
        # 3. Componente Sentimiento
        if analysis.get('sentiment'):
            sentiment_score = 50
            if isinstance(analysis.get('sentiment'), dict):
                sent = analysis['sentiment']
                if sent.get('news_sentiment', 0) > 0:
                    sentiment_score += 20
                elif sent.get('news_sentiment', 0) < 0:
                    sentiment_score -= 20
            score_components.append(('sentiment', sentiment_score, sent_weight))
        
        # Calcular score ponderado
        if not score_components:
            return 50
        
        total_weight = sum(weight for _, _, weight in score_components)
        weighted_score = sum(score * weight for _, score, weight in score_components) / total_weight
        
        return max(0, min(100, weighted_score))
    
    def _calculate_short_term_score(self, analysis: Dict) -> float:
        """
        PHASE 2 IMPROVEMENT: Scoring específico para SHORT-TERM
        
        SHORT-TERM Strategy: Momentum puro, sin fundamentals
        - 85% Technical (RSI, MACD, Momentum - directamente, sin inversión)
        - 15% Volatility Risk (ajuste menor)
        - 0% Fundamental (not relevant for quick trades)
        
        Key difference: RSI interpretación CORRECTA para momentum
        - RSI < 30: Oversold, BUY (score high)
        - RSI > 70: Overbought, SELL (score low)
        """
        score_components = []
        
        # 1. TECHNICAL - Momentum Focus (85% weight)
        if analysis.get('technical'):
            tech = analysis['technical']
            
            # RSI: CORRECT interpretation for momentum (not inverted)
            rsi = tech.get('rsi', 50)
            if rsi < 30:
                rsi_score = 80  # Oversold = strong BUY
            elif rsi < 40:
                rsi_score = 70  # Weak oversold = BUY
            elif rsi < 60:
                rsi_score = 50  # Neutral
            elif rsi < 70:
                rsi_score = 30  # Weak overbought = SELL
            else:
                rsi_score = 20  # Overbought = strong SELL
            
            # MACD: Momentum direction
            macd_status = tech.get('macd_status', '')
            macd_score = 75 if macd_status == 'Bullish' else 25 if macd_status == 'Bearish' else 50
            
            # Stochastic: Momentum oscillator
            stoch_k = tech.get('stoch_k', 50)
            if stoch_k < 20:
                stoch_score = 75  # Oversold
            elif stoch_k < 50:
                stoch_score = 55
            elif stoch_k < 80:
                stoch_score = 45
            else:
                stoch_score = 25  # Overbought
            
            # Combine technical with momentum focus
            # More weight to RSI (momentum leading) + MACD (confirmation) + Stoch
            tech_score = (rsi_score * 0.50 + macd_score * 0.35 + stoch_score * 0.15)
            score_components.append(('technical', tech_score, 0.85))
        
        # 2. VOLATILITY - Risk adjustment only (15% weight for ST)
        # High volatility = more cautious (reduce score)
        volatility = self._calculate_volatility_internal_short_term() if hasattr(self, '_current_ticker_st') else 0.02
        
        if volatility > 0.08:
            vol_score = 40  # Very volatile - reduce aggressive signals
        elif volatility > 0.05:
            vol_score = 45
        else:
            vol_score = 50  # Normal - neutral
        
        score_components.append(('volatility', vol_score, 0.15))
        
        # Calculate weighted score
        if not score_components:
            return 50
        
        total_weight = sum(weight for _, _, weight in score_components)
        weighted_score = sum(score * weight for _, score, weight in score_components) / total_weight
        
        return max(0, min(100, weighted_score))
    
    def _categorize_stock(self, volatility: float, ticker: str = None) -> str:
        """
        PHASE 2 STEP 2: Categorize stock by volatility and characteristics
        Helps determine appropriate thresholds for different stock types
        
        Returns: 'mega_cap_tech_ultra_conservative', 'mega_cap_tech', 'high_volatility', 'normal'
        """
        vol_pct = volatility * 100
        
        # Mega-cap tech stocks: MSFT, META, NVDA
        # These have lower volatility but can be whipsaw-prone
        mega_cap_tech = ['MSFT', 'META', 'NVDA']
        amzn_like = ['AMZN']  # Large cap, behaves similarly to mega-cap
        
        # Ultra-conservative for most problematic mega-cap
        if ticker and ticker.upper() in ['META', 'AMZN'] and vol_pct < 35:
            return 'mega_cap_tech_ultra_conservative'
        
        # Conservative for other mega-cap tech
        if ticker and ticker.upper() in mega_cap_tech and vol_pct < 35:
            return 'mega_cap_tech'
        
        # High volatility: PLTR, BABA, TSLA
        if vol_pct > 40:
            return 'high_volatility'
        
        return 'normal'
    
    def _dynamic_thresholds_short_term(self, volatility: float, ticker: str = None) -> tuple:
        """
        PHASE 2 STEP 2 REFINED: Ultra-dynamic thresholds for SHORT-TERM by stock category
        
        CATEGORIES:
        1. Mega-cap ultra-conservative (META, AMZN): 35/65 (very conservative - prevent whipsaws)
        2. Mega-cap tech (MSFT, NVDA): 38/62 (conservative)
        3. High volatility (PLTR, BABA, TSLA): 43/57 (aggressive)
        4. Normal volatility (others): 42/58 (moderate)
        
        Rationale:
        - Ultra-conservative: META & AMZN were losing money, need tighter filters
        - Conservative: MSFT/NVDA have lower momentum, need wider bands
        - High vol: Can handle aggressive thresholds, more reversals
        - Normal: Balanced approach
        """
        category = self._categorize_stock(volatility, ticker)
        
        if category == 'mega_cap_tech_ultra_conservative':
            # Ultra-conservative: prevent false signals on whipsaw-prone mega-caps
            return 35.0, 65.0
        elif category == 'mega_cap_tech':
            # Conservative for mega-cap: reduce false signals
            return 38.0, 62.0
        elif category == 'high_volatility':
            # Aggressive for high volatility: capture more opportunities
            return 43.0, 57.0
        else:
            # Moderate for normal volatility
            return 42.0, 58.0
    
    def _score_to_signal(self, score: float, is_short_term: bool, volatility: float = 0.02, ticker: str = None) -> str:
        """
        Convierte score numérico a señal de trading.
        
        Score: 0-100
        0-30: BUY fuerte
        30-45: BUY
        45-55: HOLD
        55-70: SELL
        70-100: SELL fuerte
        
        MEJORA: Thresholds ajustados Y DINÁMICOS según volatilidad
        PHASE 2 STEP 2: Thresholds diferentes para SHORT-TERM vs LONG-TERM, con categorización de stock
        """
        # Obtener thresholds dinámicos basados en volatilidad Y tipo de análisis
        if is_short_term:
            # SHORT-TERM: Usa thresholds diferenciados por tipo de stock
            buy_threshold, sell_threshold = self._dynamic_thresholds_short_term(volatility, ticker)
        else:
            # LONG-TERM: Usa thresholds normales
            buy_threshold, sell_threshold = self._dynamic_thresholds(volatility)
        
        if score < buy_threshold:
            return 'BUY'
        elif score > sell_threshold:
            return 'SELL'
        else:
            return 'HOLD'
    
    # ==================== PHASE 3: RISK MANAGEMENT ====================
    
    def _calculate_atr(self, ticker: str, periods: int = 14) -> float:
        """
        Calculate Average True Range (ATR) for volatility-based stop loss.
        
        ATR measures volatility in absolute price terms.
        Higher ATR = higher volatility = wider stop loss
        """
        if ticker not in self.daily_data or len(self.daily_data[ticker]) < periods:
            return 0.0
        
        data = self.daily_data[ticker]
        high = data['High'].values
        low = data['Low'].values
        close = data['Close'].values
        
        if len(high) < periods:
            return 0.0
        
        # Calculate True Range
        tr_list = []
        for i in range(len(high)):
            if i == 0:
                tr = high[i] - low[i]
            else:
                tr = max(
                    high[i] - low[i],
                    abs(high[i] - close[i-1]),
                    abs(low[i] - close[i-1])
                )
            tr_list.append(tr)
        
        # Average True Range
        atr = np.mean(tr_list[-periods:])
        return atr
    
    def _calculate_position_size(
        self,
        entry_price: float,
        volatility: float,
        atr: float,
        max_risk_pct: float = 0.02,
        account_size: float = 100000
    ) -> int:
        """
        Calculate position size based on volatility and risk management rules.
        
        Args:
            entry_price: Price to enter position
            volatility: Annualized volatility (0-1)
            atr: Average True Range
            max_risk_pct: Maximum risk per trade (default 2%)
            account_size: Total account size
        
        Returns:
            Number of shares to buy
        """
        if entry_price <= 0:
            return 0
        
        # Risk per trade in dollars
        risk_amount = account_size * max_risk_pct
        
        # Stop loss distance in dollars (use ATR or volatility-based)
        if atr > 0:
            stop_loss_amount = atr * 2  # 2x ATR for safety
        else:
            # Fallback to volatility
            stop_loss_amount = entry_price * volatility
        
        if stop_loss_amount <= 0:
            stop_loss_amount = entry_price * 0.05  # Default 5% if nothing works
        
        # Position size = risk_amount / stop_loss_amount
        position_size = int(risk_amount / stop_loss_amount)
        
        # Ensure we don't spend more than 90% of cash
        max_position_value = account_size * 0.9
        position_size = min(position_size, int(max_position_value / entry_price))
        
        return max(1, position_size)
    
    def _get_stop_loss_price(
        self,
        entry_price: float,
        atr: float,
        volatility: float,
        ticker: str = None
    ) -> float:
        """
        Calculate dynamic stop loss price based on ATR and volatility.
        
        Different categories get different multipliers:
        - Ultra-Conservative: 2.5x ATR (META, AMZN)
        - Conservative: 2.0x ATR (MSFT, NVDA)
        - Aggressive: 1.5x ATR (PLTR, BABA, TSLA)
        - Normal: 2.0x ATR (others)
        """
        if entry_price <= 0:
            return 0
        
        # Get stock category for different stop loss multipliers
        category = self._categorize_stock(volatility, ticker)
        
        if atr > 0:
            if category == 'mega_cap_tech_ultra_conservative':
                multiplier = 2.5
            elif category == 'mega_cap_tech':
                multiplier = 2.0
            elif category == 'high_volatility':
                multiplier = 1.5
            else:
                multiplier = 2.0
            
            stop_loss_distance = atr * multiplier
        else:
            # Fallback: use percentage-based
            if category == 'mega_cap_tech_ultra_conservative':
                pct = 0.08  # 8%
            elif category == 'mega_cap_tech':
                pct = 0.06  # 6%
            elif category == 'high_volatility':
                pct = 0.04  # 4%
            else:
                pct = 0.05  # 5%
            
            stop_loss_distance = entry_price * pct
        
        return entry_price - stop_loss_distance
    
    def _get_take_profit_price(
        self,
        entry_price: float,
        ticker: str = None,
        volatility: float = None
    ) -> float:
        """
        Calculate take profit price based on stock category and volatility.
        
        Different categories have different profit targets:
        - Ultra-Conservative: 4% profit
        - Conservative: 6% profit
        - Aggressive: 8-10% profit
        - Normal: 6% profit
        """
        if entry_price <= 0:
            return 0
        
        category = self._categorize_stock(volatility or 0.02, ticker)
        
        if category == 'mega_cap_tech_ultra_conservative':
            profit_pct = 0.04  # 4%
        elif category == 'mega_cap_tech':
            profit_pct = 0.06  # 6%
        elif category == 'high_volatility':
            profit_pct = 0.10  # 10%
        else:
            profit_pct = 0.06  # 6%
        
        return entry_price * (1 + profit_pct)
    
    def _check_stop_loss(
        self,
        ticker: str,
        current_price: float,
        stop_loss_price: float
    ) -> Tuple[bool, str]:
        """
        Check if position hits stop loss.
        
        Returns: (should_exit, reason)
        """
        if current_price <= stop_loss_price:
            loss_pct = (current_price - stop_loss_price) / stop_loss_price * 100
            return True, f"Stop Loss Hit (-{abs(loss_pct):.1f}%)"
        return False, ""
    
    def _check_take_profit(
        self,
        ticker: str,
        current_price: float,
        take_profit_price: float
    ) -> Tuple[bool, str]:
        """
        Check if position hits take profit.
        
        Returns: (should_exit, reason)
        """
        if current_price >= take_profit_price:
            profit_pct = (current_price - take_profit_price) / take_profit_price * 100
            return True, f"Take Profit Hit (+{profit_pct:.1f}%)"
        return False, ""
    
    def _calculate_max_drawdown(self) -> Tuple[float, str]:
        """
        Calculate maximum drawdown from portfolio values.
        
        Returns: (max_drawdown_pct, date_when_occurred)
        """
        equity_curve = self.portfolio.daily_values
        if len(equity_curve) < 2:
            return 0.0, ""
        
        peak = equity_curve[0]
        max_dd = 0.0
        max_dd_date = ""
        
        for i, value in enumerate(equity_curve):
            if value > peak:
                peak = value
            
            dd = (peak - value) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
                if i < len(self.portfolio.daily_dates):
                    max_dd_date = str(self.portfolio.daily_dates[i])
        
        return max_dd, max_dd_date
    
    def _calculate_calmar_ratio(self, returns_annual: float) -> float:
        """
        Calculate Calmar Ratio = Annual Return / Max Drawdown
        
        Higher is better. Measures risk-adjusted return.
        """
        max_dd, _ = self._calculate_max_drawdown()
        if max_dd <= 0:
            return 0.0
        
        calmar = returns_annual / max_dd
        return calmar
    
    # ==================== END PHASE 3: RISK MANAGEMENT ====================
    
    def _generate_fallback_signals(
        self,
        date: pd.Timestamp,
        prices: Dict[str, float]
    ) -> Dict[str, Dict]:
        """
        Fallback a señales técnicas si Agent no está disponible.
        Usa RSI + MA20 simple.
        """
        signals = {}
        
        for ticker, data in self.daily_data.items():
            hist = data[data.index <= date].tail(20)
            
            if len(hist) < 20:
                continue
            
            close = hist['Close'].values
            
            # RSI simple
            deltas = np.diff(close)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs))
            
            # MA20
            ma20 = np.mean(close[-20:])
            current_price = close[-1]
            
            # Signal
            if rsi < 35 and current_price > ma20:
                signal = 'BUY'
                strength = (35 - rsi) / 35
            elif rsi > 65:
                signal = 'SELL'
                strength = (rsi - 65) / 35
            else:
                signal = 'HOLD'
                strength = 0
            
            signals[ticker] = {
                'signal': signal,
                'strength': min(strength, 1.0),
                'price': prices.get(ticker, 0),
                'rsi': round(rsi, 2),
                'ma20': round(ma20, 2),
            }
        
        return signals
    
    def _apply_stop_loss_and_take_profit(
        self,
        ticker: str,
        date: pd.Timestamp,
        stop_loss_pct: float = -0.05,
        take_profit_pct: float = 0.10
    ) -> Tuple[bool, str]:
        """
        MEJORA 2: Aplica stop loss (-5%) y take profit (+10%) a posiciones.
        
        Returns: (should_sell, reason)
        """
        if ticker not in self.portfolio.positions:
            return False, ""
        
        position = self.portfolio.positions[ticker]
        entry_price = position['avg_cost']
        current_price = position['current_price']
        
        if entry_price <= 0:
            return False, ""
        
        return_pct = (current_price - entry_price) / entry_price
        
        # Take profit: Si ganancia >= +10%, vender
        if return_pct >= take_profit_pct:
            return True, f"Take Profit {return_pct*100:.1f}%"
        
        # Stop loss: Si pérdida >= -5%, vender
        if return_pct <= stop_loss_pct:
            return True, f"Stop Loss {return_pct*100:.1f}%"
        
        return False, ""
    
    def _apply_technical_gate(
        self,
        ticker: str,
        analysis: Dict
    ) -> bool:
        """
        MEJORA 3: Gate técnico para validar señales.
        Solo permite trades si indicadores confirman la dirección.
        
        Returns: True si la señal es válida
        """
        if not analysis.get('technical'):
            return True  # Sin datos técnicos, permitir
        
        tech = analysis['technical']
        rsi = tech.get('rsi', 50)
        macd = tech.get('macd_status', '')
        
        # Para BUY: RSI debe estar bajista (< 50) y MACD debe ser bullish o neutral
        # Para SELL: RSI debe estar alcista (> 50) y MACD debe ser bearish o neutral
        
        # Esta lógica será más específica según el tipo de análisis
        # Por ahora, requerir al menos confirmación de MACD
        
        return True  # Default: permitir
    
    def _calculate_rate_of_change(self, ticker: str, periods: int = 14) -> float:
        """
        MEJORA DE SCORING: Rate of Change (ROC)
        
        ROC es un indicador PREDICTIVO que mide el momentum actual.
        Más preciso que RSI para detectar cambios de dirección.
        
        Returns: ROC percentage (-100 a +100)
        """
        if ticker not in self.daily_data:
            return 0.0
        
        data = self.daily_data[ticker]
        if len(data) < periods + 1:
            return 0.0
        
        close = data['Close'].values
        
        # ROC = ((Close[0] - Close[-14]) / Close[-14]) * 100
        roc = ((close[-1] - close[-periods]) / close[-periods]) * 100
        
        return float(np.clip(roc, -100, 100))
    
    def _calculate_momentum_score(self, analysis: Dict, volatility: float) -> float:
        """
        MEJORA DE SCORING: Momentum Score mejorado
        
        Combina:
        - Rate of Change (30% peso) - predictor mejor que RSI
        - RSI (30% peso) - confirmación principal
        - MACD (30% peso) - confirmación
        - Volatilidad (10% peso) - ajuste suave (no dominante)
        
        Score: 0-100
        """
        score_components = []
        
        tech = analysis.get('technical', {})
        
        # 1. Rate of Change (30% - predictor principal)
        rsi = tech.get('rsi', 50)
        roc_contribution = (rsi - 50) / 50 * 30  # Conversión rápida a escala -30 a +30
        score_components.append(('roc', roc_contribution, 0.30))
        
        # 2. RSI (30% - confirmación principal, más peso)
        if rsi < 35:
            rsi_score = 75  # Fuerte sobreventa
        elif rsi < 50:
            rsi_score = 60  # Suave sobreventa
        elif rsi > 65:
            rsi_score = 25  # Suave sobrecompra
        elif rsi > 70:
            rsi_score = 10  # Fuerte sobrecompra
        else:
            rsi_score = 50  # Neutral
        
        score_components.append(('rsi', rsi_score, 0.30))
        
        # 3. MACD (30% - confirmación fuerte)
        macd_status = tech.get('macd_status', '')
        macd_score = 75 if macd_status == 'Bullish' else 25 if macd_status == 'Bearish' else 50
        score_components.append(('macd', macd_score, 0.30))
        
        # 4. Volatility adjustment (10% - ajuste SUAVE, no dominante)
        # Solo reducir confianza si volatilidad EXTREMA
        if volatility > 0.05:  # >5% volatilidad
            vol_score = 40  # Reducir confianza
        elif volatility > 0.04:
            vol_score = 45
        else:
            vol_score = 50  # Neutral (no penalizar volatilidad normal)
        
        score_components.append(('volatility', vol_score, 0.10))
        
        # Calcular score ponderado
        total_weight = sum(weight for _, _, weight in score_components)
        weighted_score = sum(score * weight for _, score, weight in score_components) / total_weight
        
        return max(0, min(100, weighted_score))
    
    def _dynamic_thresholds(self, volatility: float) -> Tuple[float, float]:
        """
        MEJORA DE THRESHOLDS: Dinámicos según volatilidad
        
        AJUSTADO PARA STOCKS VOLÁTILES - MÁS ACHIEVABLE:
        Si volatilidad muy alta (>8%) → conservador pero factible (BUY 38, SELL 62)
        Si volatilidad alta (5-8%) → moderado (BUY 40, SELL 60)
        Si volatilidad normal (2-5%) → balanceado (BUY 43, SELL 57)
        Si volatilidad baja (<2%) → óptimo (BUY 43, SELL 57)
        
        Returns: (buy_threshold, sell_threshold)
        """
        vol_pct = volatility * 100  # Convertir a porcentaje
        
        if vol_pct > 8.0:
            # Volatilidad extrema: más conservador pero aún alcanzable
            return 38.0, 62.0
        elif vol_pct > 5.0:
            # Volatilidad alta: moderado
            return 40.0, 60.0
        elif vol_pct > 3.0:
            # Volatilidad normal-alta: balanceado
            return 43.0, 57.0
        else:
            # Volatilidad normal o baja: ÓPTIMO (43/57)
            return 43.0, 57.0
    
    def execute_trades(
        self,
        date: pd.Timestamp,
        signals: Dict[str, Dict],
        max_position_size: float = 0.15
    ):
        """Ejecuta trades basado en señales del agente con stop loss/take profit."""
        trades_executed = 0
        
        available_cash = self.portfolio.cash
        total_value = self.portfolio.get_portfolio_value()
        cash_ratio = available_cash / total_value if total_value > 0 else 1.0
        
        # MEJORA 2: Primero, revisar stop losses y take profits para posiciones existentes
        for ticker in list(self.portfolio.positions.keys()):
            should_sell, reason = self._apply_stop_loss_and_take_profit(ticker, date)
            
            if should_sell:
                position = self.portfolio.positions[ticker]
                current_price = position['current_price']
                shares = position['shares']
                
                success, pnl = self.portfolio.sell(ticker, shares, current_price, date=date)
                if success:
                    trades_executed += 1
                    logger.debug(f"    {reason} SELL {shares} {ticker} @ ${current_price:.2f} - PnL: ${pnl:.2f}")
        
        # Luego ejecutar nuevas señales de entrada
        for ticker, signal_data in signals.items():
            signal = signal_data['signal']
            price = signal_data['price']
            
            if signal == 'HOLD':
                if cash_ratio > 0.80 and ticker not in self.portfolio.positions:
                    max_allocation = total_value * 0.10
                    shares = int(max_allocation / price)
                    if shares > 0:
                        success = self.portfolio.buy(ticker, shares, price, date=date)
                        if success:
                            trades_executed += 1
                continue
            
            elif signal == 'BUY' and ticker not in self.portfolio.positions:
                # ==================== PHASE 3: DYNAMIC RISK MANAGEMENT ====================
                if self.risk_management_enabled:
                    # Calcular volatilidad
                    volatility = self._calculate_volatility(ticker)
                    atr = self._calculate_atr(ticker)
                    
                    # Posición dinámica basada en riesgo
                    position_size = self._calculate_position_size(
                        entry_price=price,
                        volatility=volatility,
                        atr=atr,
                        max_risk_pct=self.max_risk_per_trade,
                        account_size=self.initial_cash
                    )
                    
                    # Calcular stops
                    stop_loss = self._get_stop_loss_price(
                        entry_price=price,
                        atr=atr,
                        volatility=volatility,
                        ticker=ticker
                    )
                    
                    take_profit = self._get_take_profit_price(
                        entry_price=price,
                        ticker=ticker,
                        volatility=volatility
                    )
                    
                    shares = int(position_size)
                else:
                    # ============ FALLBACK: Sin Risk Management ==============
                    max_allocation = total_value * max_position_size
                    shares = int(max_allocation / price)
                    stop_loss = None
                    take_profit = None
                # ========================================================================
                
                if shares > 0:
                    success = self.portfolio.buy(ticker, shares, price, date=date)
                    if success:
                        trades_executed += 1
                        reason = signal_data.get('recommendation', 'Agent BUY signal')
                        
                        # Track posición con SL/TP si RM habilitado
                        if self.risk_management_enabled and stop_loss and take_profit:
                            self.open_positions[ticker] = {
                                'entry_price': price,
                                'shares': shares,
                                'entry_date': date,
                            }
                            self.position_stops[ticker] = {
                                'stop_loss': stop_loss,
                                'take_profit': take_profit,
                            }
                            logger.debug(f"    BUY {shares} {ticker} @ ${price:.2f} - {reason}")
                            logger.debug(f"      SL: ${stop_loss:.2f} | TP: ${take_profit:.2f}")
                        else:
                            logger.debug(f"    BUY {shares} {ticker} @ ${price:.2f} - {reason}")

            
            elif signal == 'SELL' and ticker in self.portfolio.positions:
                shares = self.portfolio.positions[ticker]['shares']
                success, pnl = self.portfolio.sell(ticker, shares, price, date=date)
                if success:
                    trades_executed += 1
                    logger.debug(f"    SELL {shares} {ticker} @ ${price:.2f} - PnL: ${pnl:.2f}")
        
        return trades_executed
    
    def run_backtest(self) -> Dict:
        """Ejecuta el backtest completo con señales del agente."""
        logger.info(f"\n{'='*80}")
        logger.info(f"🤖 INICIANDO AGENT-BASED BACKTEST ({self.analysis_type.upper()})")
        logger.info(f"{'='*80}\n")
        
        # Cargar datos
        if not self.load_data():
            logger.error("❌ No se pudieron cargar los datos")
            return {}
        
        # Obtener fechas de trading
        trading_dates = self._get_trading_dates()
        logger.info(f"📅 Días de trading: {len(trading_dates)}\n")
        
        # Loop principal
        for i, date in enumerate(trading_dates):
            # Obtener precios
            prices = self.get_daily_prices(date)
            if not prices:
                continue
            
            # Actualizar precios en portfolio
            for ticker, price in prices.items():
                self.portfolio.update_price(ticker, price)
            
            # ==================== PHASE 3: RISK MANAGEMENT CHECK ====================
            # Chequear stop loss y take profit para posiciones abiertas
            if self.risk_management_enabled:
                for ticker in list(self.open_positions.keys()):
                    current_price = prices.get(ticker)
                    if not current_price or ticker not in self.position_stops:
                        continue
                    
                    stop_loss = self.position_stops[ticker]['stop_loss']
                    take_profit = self.position_stops[ticker]['take_profit']
                    
                    # Chequear stop loss primero (prioridad)
                    should_exit_sl, reason_sl = self._check_stop_loss(ticker, current_price, stop_loss)
                    if should_exit_sl:
                        shares = self.open_positions[ticker]['shares']
                        self.portfolio.sell(ticker, shares, current_price, date=date)
                        del self.open_positions[ticker]
                        del self.position_stops[ticker]
                        logger.info(f"  [SL HIT] {ticker} {reason_sl}")
                        continue
                    
                    # Chequear take profit
                    should_exit_tp, reason_tp = self._check_take_profit(ticker, current_price, take_profit)
                    if should_exit_tp:
                        shares = self.open_positions[ticker]['shares']
                        self.portfolio.sell(ticker, shares, current_price, date=date)
                        del self.open_positions[ticker]
                        del self.position_stops[ticker]
                        logger.info(f"  [TP HIT] {ticker} {reason_tp}")
            # ========================================================================
            
            # Generar señales del agente
            signals = self.generate_agent_signals(date, prices)
            
            # Ejecutar trades
            self.execute_trades(date, signals)
            
            # Registrar estado diario
            self.portfolio.record_daily_state(date=date)
            
            # Progreso
            if (i + 1) % 50 == 0:
                portfolio_value = self.portfolio.get_portfolio_value()
                logger.info(f"  [{i+1}/{len(trading_dates)}] {date.date()} - Portfolio: ${portfolio_value:,.2f}")
        
        # Cerrar posiciones
        final_prices = self.get_daily_prices(trading_dates[-1])
        self.portfolio.close_all_positions(final_prices, date=trading_dates[-1])
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✨ BACKTEST COMPLETADO (AGENT-BASED)")
        logger.info(f"{'='*80}\n")
        
        return self._generate_results()
    
    def _get_trading_dates(self) -> List[pd.Timestamp]:
        """Obtiene fechas de trading del período."""
        if not self.daily_data:
            return []
        
        first_ticker = list(self.daily_data.keys())[0]
        all_dates = self.daily_data[first_ticker].index.tolist()
        
        trading_dates = [
            d for d in all_dates
            if self.start_date <= d <= self.end_date
        ]
        
        return sorted(trading_dates)
    
    def _generate_results(self) -> Dict:
        """Genera diccionario de resultados."""
        portfolio_summary = self.portfolio.get_summary()
        daily_df = self.portfolio.get_daily_values_df()
        
        results = {
            'analysis_type': self.analysis_type,
            'period': {
                'start': self.start_date.strftime('%Y-%m-%d'),
                'end': self.end_date.strftime('%Y-%m-%d'),
                'days': len(self._get_trading_dates())
            },
            'portfolio': portfolio_summary,
            'daily_values': daily_df,
            'transactions': self.portfolio.get_transactions_df(),
            'agent_details': self.agent_details
        }
        
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
        """Guarda resultados del backtest."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{self.analysis_type}_{'_'.join(self.tickers[:3])}"
        
        # Summary TXT
        summary_file = self.results_dir / f"agent_backtest_summary_{base_name}_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write(f"AGENT-BASED BACKTEST SUMMARY\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"Analysis Type: {self.analysis_type}\n")
            f.write(f"Period: {results['period']['start']} → {results['period']['end']}\n")
            f.write(f"Days: {results['period']['days']}\n\n")
            f.write(f"Portfolio Summary:\n")
            for key, value in results['portfolio'].items():
                f.write(f"  {key}: {value}\n")
        
        logger.info(f"✓ Summary: {summary_file}")
        
        # Daily Values CSV
        daily_file = self.results_dir / f"agent_backtest_daily_{base_name}_{timestamp}.csv"
        results['daily_values'].to_csv(daily_file)
        logger.info(f"✓ Daily values: {daily_file}")
        
        # Transactions CSV
        trans_file = self.results_dir / f"agent_backtest_transactions_{base_name}_{timestamp}.csv"
        results['transactions'].to_csv(trans_file, index=False)
        logger.info(f"✓ Transactions: {trans_file}")


# ============================================================
# CLI & EXAMPLES
# ============================================================

if __name__ == "__main__":
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="Agent-Based Backtester")
    parser.add_argument("--short-term", action="store_true", help="Short-term analysis (momentum)")
    parser.add_argument("--long-term", action="store_true", help="Long-term analysis (fundamentals)")
    parser.add_argument("--tickers", nargs="+", default=["AAPL", "MSFT", "NVDA"], help="Tickers")
    parser.add_argument("--start", default="2024-01-01", help="Start date")
    parser.add_argument("--end", default="2025-12-22", help="End date")
    parser.add_argument("--capital", type=float, default=100000, help="Initial capital")
    
    args = parser.parse_args()
    
    analysis_type = "short_term" if args.short_term else "long_term"
    
    backtester = AgentBacktester(
        tickers=args.tickers,
        start_date=args.start,
        end_date=args.end,
        initial_cash=args.capital,
        analysis_type=analysis_type,
        data_dir="../data",
        results_dir="../results"
    )
    
    results = backtester.run_backtest()
    backtester.save_results(results)
