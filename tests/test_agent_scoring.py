import unittest
import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.spectral_galileo.core.agent import FinancialAgent

class TestAgentScoring(unittest.TestCase):
    
    def setUp(self):
        """Mock data for agent tests"""
        self.ticker_symbol = "AAPL"
        
        # Mocking yfinance Ticker object
        self.mock_ticker = MagicMock()
        
        # Real-ish info mock
        self.mock_ticker.info = {
            'currentPrice': 200.0,
            'recommendationKey': 'strong_buy',
            'pegRatio': 0.8,
            'debtToEquity': 20.0,
            'currentRatio': 2.0,
            'dividendYield': 0.02,
            'dividendRate': 1.0,
            'payoutRatio': 0.2,
            'revenueGrowth': 0.2,
            'earningsGrowth': 0.25,
            'returnOnEquity': 0.3,
            'marketCap': 150_000_000_000,
            'averageVolume': 2_000_000,
            'averageVolume10days': 2_500_000,
            'beta': 1.1,
            'sector': 'Technology',
            'heldPercentInsiders': 0.02,
            'companyOfficers': [{'name': 'John Doe', 'age': 65}, {'name': 'Jane Doe', 'age': 62}],
            'longBusinessSummary': 'Global leader and dominant brand in proprietary technology and innovation with high network effect and market leader status.'
        }
        
        # Mock history data
        dates = pd.date_range('2024-01-01', periods=300)
        self.mock_history = pd.DataFrame({
            'Open': [100.0]*300,
            'High': [102.0]*300,
            'Low': [98.0]*300,
            'Close': [100.0 + i*0.5 for i in range(300)], # Strong uptrend
            'Volume': [1000000]*300
        }, index=dates)

    @patch('market_data.get_ticker_data')
    @patch('market_data.get_historical_data')
    @patch('market_data.get_macro_data')
    @patch('sentiment_analysis.advanced_sentiment_analysis')
    @patch('sentiment_analysis.detect_regulatory_factors')
    @patch('macro_analysis.analyze_macro_context')
    def test_run_analysis_uptrend_strong(self, mock_macro, mock_reg, mock_sent, mock_macro_raw, mock_hist_raw, mock_ticker_raw):
        """Test scoring in a strong fundamental and technical uptrend"""
        mock_ticker_raw.return_value = self.mock_ticker
        mock_hist_raw.return_value = self.mock_history
        
        mock_sent.return_value = {'score': 0.5, 'label': 'Positivo', 'volume': 20}
        mock_reg.return_value = {'has_regulatory_risk': False, 'sentiment_adjustment': 0}
        mock_macro.return_value = {
            'fear_greed_index': 50, 
            'tnx_trend': 'Lateral', 
            'vix': 14.0,
            'tnx': 4.0,
            'yield_spread': 0.5
        }
        
        agent = FinancialAgent(self.ticker_symbol, is_short_term=False)
        agent.ticker = self.mock_ticker
        agent.data = self.mock_history
        
        result = agent.run_analysis()
        
        self.assertIn("COMPRA", result['strategy']['verdict'])
        self.assertGreater(result['strategy']['confidence'], 25)
        self.assertIn("Largo Plazo (3-5 años)", result['strategy']['horizon'])

    @patch('market_data.get_ticker_data')
    @patch('market_data.get_historical_data')
    @patch('market_data.get_macro_data')
    @patch('sentiment_analysis.advanced_sentiment_analysis')
    @patch('sentiment_analysis.detect_regulatory_factors')
    @patch('macro_analysis.analyze_macro_context')
    def test_run_analysis_timing_adverso(self, mock_macro, mock_reg, mock_sent, mock_macro_raw, mock_hist_raw, mock_ticker_raw):
        """Test the 'Timing Adverso' narrative"""
        mock_ticker_raw.return_value = self.mock_ticker
        
        downtrend_history = self.mock_history.copy()
        # Ensure price is below SMA 200 (SMA 200 of a linear sequence is the middle value)
        downtrend_history['Close'] = [300.0 - i*0.8 for i in range(300)] 
        mock_hist_raw.return_value = downtrend_history
        self.mock_ticker.info['currentPrice'] = downtrend_history['Close'].iloc[-1]
        
        mock_sent.return_value = {'score': 0.1, 'label': 'Neutral', 'volume': 10}
        mock_reg.return_value = {'has_regulatory_risk': False, 'sentiment_adjustment': 0}
        mock_macro.return_value = {
            'fear_greed_index': 20, 
            'tnx_trend': 'Lateral', 
            'vix': 20.0,
            'tnx': 4.0,
            'yield_spread': 0.5
        }
        
        agent = FinancialAgent(self.ticker_symbol, is_short_term=False)
        agent.ticker = self.mock_ticker
        agent.data = downtrend_history
        
        # Force neutral RSI to avoid 'Oportunidad de Recuperación' and hit 'Timing Adverso'
        with patch('agent.indicators.calculate_rsi', return_value=pd.Series([50.0]*300)):
            result = agent.run_analysis()
            self.assertIn("Timing Adverso", result['strategy']['horizon'])

    @patch('market_data.get_ticker_data')
    @patch('market_data.get_historical_data')
    @patch('market_data.get_macro_data')
    @patch('sentiment_analysis.advanced_sentiment_analysis')
    @patch('sentiment_analysis.detect_regulatory_factors')
    @patch('macro_analysis.analyze_macro_context')
    def test_run_analysis_rsi_divergence(self, mock_macro, mock_reg, mock_sent, mock_macro_raw, mock_hist_raw, mock_ticker_raw):
        """Test RSI Divergence penalty in CP mode"""
        mock_ticker_raw.return_value = self.mock_ticker
        mock_hist_raw.return_value = self.mock_history
        
        # Mock macro data
        mock_macro.return_value = {
            'fear_greed_index': 50, 'tnx_trend': 'Lateral', 'vix': 14.0, 'tnx': 4.0, 'yield_spread': 0.5
        }
        mock_sent.return_value = {'score': 0.5, 'label': 'Positivo', 'volume': 10}
        mock_reg.return_value = {'has_regulatory_risk': False, 'sentiment_adjustment': 0}
        
        # Force RSI Divergence in indicators
        with patch('indicators.detect_rsi_divergence', return_value=True):
            agent = FinancialAgent(self.ticker_symbol, is_short_term=True)
            result = agent.run_analysis()
            
            # Use 'cons' or 'strategy' to check if detected
            cons_str = " ".join(result['strategy']['cons'])
            self.assertIn("Divergencia Bajista", cons_str)

    @patch('market_data.get_ticker_data')
    @patch('market_data.get_historical_data')
    @patch('market_data.get_macro_data')
    @patch('sentiment_analysis.advanced_sentiment_analysis')
    @patch('sentiment_analysis.detect_regulatory_factors')
    @patch('macro_analysis.analyze_macro_context')
    @patch('market_data.get_earnings_surprise')
    def test_run_analysis_earnings_penalization(self, mock_surprise, mock_macro, mock_reg, mock_sent, mock_macro_raw, mock_hist_raw, mock_ticker_raw):
        """Test fundamental penalization in CP mode"""
        mock_ticker_raw.return_value = self.mock_ticker
        mock_hist_raw.return_value = self.mock_history
        
        # Mock bad earnings surprise
        mock_surprise.return_value = -0.15 # -15% surprise
        mock_sent.return_value = {'score': 0.1, 'label': 'Neutral', 'volume': 10}
        mock_reg.return_value = {'has_regulatory_risk': False, 'sentiment_adjustment': 0}
        mock_macro.return_value = {
            'fear_greed_index': 50, 'tnx_trend': 'Lateral', 'vix': 35.0, 'tnx': 4.0, 'yield_spread': 0.5
        } # High VIX penalty
        
        agent = FinancialAgent(self.ticker_symbol, is_short_term=True)
        result = agent.run_analysis()
        
        cons_str = " ".join(result['strategy']['cons'])
        self.assertIn("Sorpresas Negativas", cons_str)

    @patch('market_data.get_ticker_data')
    @patch('market_data.get_historical_data')
    @patch('market_data.get_macro_data')
    @patch('sentiment_analysis.advanced_sentiment_analysis')
    @patch('sentiment_analysis.detect_regulatory_factors')
    @patch('macro_analysis.analyze_macro_context')
    def test_run_analysis_peg_fallback(self, mock_macro, mock_reg, mock_sent, mock_macro_raw, mock_hist_raw, mock_ticker_raw):
        """Test PEG fallback using Forward PE vs Industry"""
        mock_ticker_raw.return_value = self.mock_ticker
        mock_hist_raw.return_value = self.mock_history
        
        # Remove PEG, set good Forward PE
        self.mock_ticker.info['pegRatio'] = None
        self.mock_ticker.info['forwardPE'] = 15.0 # Benchmark for Tech is 30
        self.mock_ticker.info['sector'] = 'Technology'
        
        mock_sent.return_value = {'score': 0.1, 'label': 'Neutral', 'volume': 10}
        mock_reg.return_value = {'has_regulatory_risk': False, 'sentiment_adjustment': 0}
        mock_macro.return_value = {
            'fear_greed_index': 50, 'tnx_trend': 'Lateral', 'vix': 14.0, 'tnx': 4.0, 'yield_spread': 0.5
        }
        
        agent = FinancialAgent(self.ticker_symbol, is_short_term=False)
        result = agent.run_analysis()
        
        pros_str = " ".join(result['strategy']['pros'])
        self.assertIn("Valuación Atractiva vs Sector", pros_str)

    @patch('market_data.get_ticker_data')
    @patch('market_data.get_historical_data')
    @patch('market_data.get_macro_data')
    @patch('sentiment_analysis.advanced_sentiment_analysis')
    @patch('sentiment_analysis.detect_regulatory_factors')
    @patch('macro_analysis.analyze_macro_context')
    def test_run_analysis_trend_gate_buffer(self, mock_macro, mock_reg, mock_sent, mock_macro_raw, mock_hist_raw, mock_ticker_raw):
        """Test Trend Gate buffer (±5% near SMA200 and oversold)"""
        mock_ticker_raw.return_value = self.mock_ticker
        
        # Setup history where price is 3% below SMA200
        # SMA200 of 100 constant is 100. Let's make it 100.
        # Set current price to 97.
        base_history = pd.DataFrame({
            'Open': [100.0]*300,
            'High': [100.0]*300,
            'Low': [100.0]*300,
            'Close': [100.0]*300,
            'Volume': [1000000]*300
        }, index=pd.date_range('2024-01-01', periods=300))
        
        # Force the last price to be 97 (3% below SMA200)
        base_history.loc[base_history.index[-1], 'Close'] = 97.0
        mock_hist_raw.return_value = base_history
        self.mock_ticker.info['currentPrice'] = 97.0
        
        mock_sent.return_value = {'score': 0.1, 'label': 'Neutral', 'volume': 10}
        mock_reg.return_value = {'has_regulatory_risk': False, 'sentiment_adjustment': 0}
        mock_macro.return_value = {
            'fear_greed_index': 50, 'tnx_trend': 'Lateral', 'vix': 14.0, 'tnx': 4.0, 'yield_spread': 0.5
        }
        
        # Prepare mocks for indicators
        def mock_add_indicators(df):
            df['SMA_200'] = 100.0
            df['SMA_50'] = 100.0
            df['RSI'] = 30.0
            df['MACD'] = 1.0
            df['MACD_Signal'] = 0.5
            df['Stoch_K'] = 20.0
            df['ATR'] = 1.0
            df['ADX'] = 30.0
            df['SMA_Slope'] = 1.0
            df['OBV'] = 1000000.0
            df['MFI'] = 50.0
            df['BB_Upper'] = 110.0
            df['BB_Lower'] = 90.0
            return df

        # Force indicators to ensure logic hits the buffer
        with patch('agent.indicators.add_all_indicators', side_effect=mock_add_indicators):
            agent = FinancialAgent(self.ticker_symbol, is_short_term=False)
            agent.data = base_history # Explicitly set data
            agent.info = self.mock_ticker.info
            agent.info['currentPrice'] = 97.0 # Explicitly set price
            result = agent.run_analysis()
            
            pros_str = " ".join(result['strategy']['pros'])
            self.assertIn("Cercanía a SMA 200", pros_str)
            self.assertEqual(result['strategy']['horizon'], "Largo Plazo / Oportunidad de Recuperación")

if __name__ == '__main__':
    unittest.main()
