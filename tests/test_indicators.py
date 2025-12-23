import unittest
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import indicators

class TestIndicators(unittest.TestCase):
    
    def setUp(self):
        """Create sample data for testing"""
        dates = pd.date_range('2024-01-01', periods=100)
        np.random.seed(42)
        
        # Generate realistic OHLCV data
        self.df = pd.DataFrame({
            'Open': 100 + np.random.randn(100).cumsum(),
            'High': 102 + np.random.randn(100).cumsum(),
            'Low': 98 + np.random.randn(100).cumsum(),
            'Close': 100 + np.random.randn(100).cumsum(),
            'Volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        
        # Ensure OHLC relationships are valid
        self.df['High'] = self.df[['Open', 'Close']].max(axis=1) + abs(np.random.randn(100))
        self.df['Low'] = self.df[['Open', 'Close']].min(axis=1) - abs(np.random.randn(100))
    
    def test_calculate_sma(self):
        """Test Simple Moving Average calculation"""
        sma_20 = indicators.calculate_sma(self.df, window=20)
        
        # SMA should have NaN for first 19 values
        self.assertTrue(pd.isna(sma_20.iloc[0]))
        self.assertFalse(pd.isna(sma_20.iloc[-1]))
        
        # Last SMA value should be close to mean of last 20 closes
        expected = self.df['Close'].iloc[-20:].mean()
        self.assertAlmostEqual(sma_20.iloc[-1], expected, places=5)
    
    def test_calculate_rsi(self):
        """Test RSI calculation"""
        rsi = indicators.calculate_rsi(self.df, window=14)
        
        # RSI should be between 0 and 100
        valid_rsi = rsi.dropna()
        self.assertTrue((valid_rsi >= 0).all())
        self.assertTrue((valid_rsi <= 100).all())
    
    def test_calculate_macd(self):
        """Test MACD calculation"""
        macd, signal, hist = indicators.calculate_macd(self.df)
        
        # All arrays should have same length
        self.assertEqual(len(macd), len(signal))
        self.assertEqual(len(macd), len(hist))
        
        # Histogram should be difference of MACD and signal
        diff = macd - signal
        np.testing.assert_array_almost_equal(hist.dropna(), diff.dropna(), decimal=5)
    
    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        upper, lower = indicators.calculate_bollinger_bands(self.df, window=20, num_std=2)
        
        # Upper should always be greater than lower
        valid_mask = ~(upper.isna() | lower.isna())
        self.assertTrue((upper[valid_mask] > lower[valid_mask]).all())
    
    def test_calculate_atr(self):
        """Test ATR calculation"""
        atr = indicators.calculate_atr(self.df, window=14)
        
        # ATR should always be positive
        valid_atr = atr.dropna()
        self.assertTrue((valid_atr > 0).all())
    
    def test_calculate_stochastic(self):
        """Test Stochastic Oscillator"""
        k, d = indicators.calculate_stochastic(self.df, window=14)
        
        # K and D should be between 0 and 100
        valid_k = k.dropna()
        valid_d = d.dropna()
        
        self.assertTrue((valid_k >= 0).all() and (valid_k <= 100).all())
        self.assertTrue((valid_d >= 0).all() and (valid_d <= 100).all())
    
    def test_calculate_obv(self):
        """Test On-Balance Volume"""
        obv = indicators.calculate_obv(self.df)
        
        # OBV should have same length as input
        self.assertEqual(len(obv), len(self.df))
        
        # First value should be 0 (our implementation starts at 0)
        self.assertEqual(obv.iloc[0], 0)
    
    def test_add_all_indicators(self):
        """Test adding all indicators at once"""
        df_with_indicators = indicators.add_all_indicators(self.df.copy())
        
        # Check all expected columns are present
        expected_cols = ['SMA_50', 'SMA_200', 'RSI', 'MACD', 'MACD_Signal', 
                        'MACD_Hist', 'BB_Upper', 'BB_Lower', 'ATR', 
                        'Stoch_K', 'Stoch_D', 'OBV', 'MFI', 'HistVol',
                        'ADX', 'SMA_Slope']
        
        for col in expected_cols:
            self.assertIn(col, df_with_indicators.columns)
    
    def test_calculate_mfi(self):
        """Test Money Flow Index calculation"""
        mfi = indicators.calculate_mfi(self.df, window=14)
        
        # MFI should be between 0 and 100
        valid_mfi = mfi.dropna()
        self.assertTrue((valid_mfi >= 0).all())
        self.assertTrue((valid_mfi <= 100).all())
        
        # Should have NaN for first values
        self.assertTrue(pd.isna(mfi.iloc[0]))
    
    def test_calculate_historical_volatility(self):
        """Test Historical Volatility calculation"""
        hist_vol = indicators.calculate_historical_volatility(self.df, window=20)
        
        # Volatility should be positive
        valid_vol = hist_vol.dropna()
        self.assertTrue((valid_vol >= 0).all())
        
        # Should have NaN for first values
        self.assertTrue(pd.isna(hist_vol.iloc[0]))

    def test_calculate_adx(self):
        """Test ADX calculation"""
        adx = indicators.calculate_adx(self.df, window=14)
        
        # ADX should be between 0 and 100
        valid_adx = adx.dropna()
        self.assertTrue((valid_adx >= 0).all())
        self.assertTrue((valid_adx <= 100).all())

    def test_calculate_sma_slope(self):
        """Test SMA Slope calculation"""
        # Slope should be calculated for a given SMA
        sma = indicators.calculate_sma(self.df, window=20)
        slope = indicators.calculate_sma_slope(sma, window=5)
        
        # Slope can be positive or negative
        self.assertEqual(len(slope), len(self.df))
        # Should have NaN initially
        self.assertTrue(pd.isna(slope.iloc[0]))

if __name__ == '__main__':
    unittest.main()
