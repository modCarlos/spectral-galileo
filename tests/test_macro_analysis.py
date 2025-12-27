import unittest
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.spectral_galileo.analysis import macro_analysis

class TestMacroAnalysis(unittest.TestCase):
    
    def setUp(self):
        """Create sample macro data"""
        dates = pd.date_range('2024-01-01', periods=100)
        
        self.valid_macro_data = pd.DataFrame({
            '^VIX': 15 + np.random.randn(100) * 5,
            '^TNX': 4.0 + np.random.randn(100) * 0.5,
            '^GSPC': 4500 + np.random.randn(100).cumsum() * 10
        }, index=dates)
        
        # Ensure VIX is positive
        self.valid_macro_data['^VIX'] = self.valid_macro_data['^VIX'].abs()
    
    def test_calculate_fear_greed_index_extremes(self):
        """Test Fear & Greed Index at extremes"""
        # Extreme fear: high VIX, low RSI
        fear_index = macro_analysis.calculate_fear_greed_index(vix_price=40, gspc_rsi=20)
        self.assertLess(fear_index, 30)  # Should indicate fear
        
        # Extreme greed: low VIX, high RSI
        greed_index = macro_analysis.calculate_fear_greed_index(vix_price=10, gspc_rsi=80)
        self.assertGreater(greed_index, 70)  # Should indicate greed
    
    def test_calculate_fear_greed_index_range(self):
        """Test Fear & Greed Index stays in 0-100 range"""
        # Test various combinations
        for vix in [10, 20, 30, 40]:
            for rsi in [20, 50, 80]:
                fgi = macro_analysis.calculate_fear_greed_index(vix, rsi)
                self.assertGreaterEqual(fgi, 0)
                self.assertLessEqual(fgi, 100)
    
    def test_analyze_macro_context_valid_data(self):
        """Test macro analysis with valid data"""
        result = macro_analysis.analyze_macro_context(self.valid_macro_data)
        
        # Should not have error
        self.assertNotIn("error", result)
        
        # Should have all expected keys
        expected_keys = ['vix', 'tnx', 'tnx_trend', 'gspc_rsi', 
                        'fear_greed_index', 'fear_greed_label']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # VIX should be positive
        self.assertGreater(result['vix'], 0)
        
        # Fear & Greed Index should be in range
        self.assertGreaterEqual(result['fear_greed_index'], 0)
        self.assertLessEqual(result['fear_greed_index'], 100)
    
    def test_analyze_macro_context_empty_data(self):
        """Test macro analysis with empty data"""
        result = macro_analysis.analyze_macro_context(None)
        self.assertIn("error", result)
        
        result = macro_analysis.analyze_macro_context(pd.DataFrame())
        self.assertIn("error", result)
    
    def test_tnx_trend_detection(self):
        """Test TNX trend detection"""
        # Create data with clear uptrend
        dates = pd.date_range('2024-01-01', periods=100)
        uptrend_data = pd.DataFrame({
            '^VIX': [15] * 100,
            '^TNX': np.linspace(3.0, 5.0, 100),  # Rising rates
            '^GSPC': [4500] * 100
        }, index=dates)
        
        result = macro_analysis.analyze_macro_context(uptrend_data)
        self.assertEqual(result['tnx_trend'], "Subiendo")
        
        # Create data with clear downtrend
        downtrend_data = pd.DataFrame({
            '^VIX': [15] * 100,
            '^TNX': np.linspace(5.0, 3.0, 100),  # Falling rates
            '^GSPC': [4500] * 100
        }, index=dates)
        
        result = macro_analysis.analyze_macro_context(downtrend_data)
        self.assertEqual(result['tnx_trend'], "Bajando")
    
    def test_fear_greed_labels(self):
        """Test Fear & Greed Index labels are assigned correctly"""
        result = macro_analysis.analyze_macro_context(self.valid_macro_data)
        
        fgi = result['fear_greed_index']
        label = result['fear_greed_label']
        
        # Verify label matches score
        if fgi < 25:
            self.assertIn("Miedo Extremo", label)
        elif fgi < 45:
            self.assertIn("Miedo", label)
        elif fgi < 55:
            self.assertIn("Neutral", label)
        elif fgi < 75:
            self.assertIn("Codicia", label)
        else:
            self.assertIn("Codicia Extrema", label)

if __name__ == '__main__':
    unittest.main()
