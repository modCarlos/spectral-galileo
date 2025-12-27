"""
Unit tests for category-specific thresholds (Phase 3.3)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from agent import categorize_stock_for_thresholds, dynamic_thresholds_short_term


class TestCategoryThresholds(unittest.TestCase):
    """Test category-specific threshold logic"""
    
    def test_mega_cap_stable_classification(self):
        """Test mega-cap stable stocks are correctly classified"""
        mega_caps = ['AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN', 'NVDA']
        
        for ticker in mega_caps:
            with self.subTest(ticker=ticker):
                # Use 0.20 (20%) volatility which is < 35%
                category = categorize_stock_for_thresholds(0.20, ticker)
                self.assertEqual(category, 'mega_cap_stable',
                               f'{ticker} should be mega_cap_stable with low volatility')
    
    def test_mega_cap_volatile_classification(self):
        """Test mega-caps with high volatility are correctly classified"""
        mega_caps = ['AAPL', 'MSFT', 'GOOGL']
        high_volatility = 0.50  # 50% > 35%
        
        for ticker in mega_caps:
            with self.subTest(ticker=ticker):
                category = categorize_stock_for_thresholds(high_volatility, ticker)
                self.assertEqual(category, 'mega_cap_volatile',
                               f'{ticker} should be mega_cap_volatile with high volatility')
    
    def test_high_growth_classification(self):
        """Test high-growth stocks are correctly classified"""
        high_growth = ['TSLA', 'PLTR', 'SNOW', 'COIN']
        
        for ticker in high_growth:
            with self.subTest(ticker=ticker):
                category = categorize_stock_for_thresholds(0.30, ticker)
                self.assertEqual(category, 'high_growth',
                               f'{ticker} should be high_growth')
    
    def test_defensive_classification(self):
        """Test defensive stocks are correctly classified"""
        # Only test tickers that are in the defensive list in agent.py
        defensives = ['JNJ', 'PG', 'KO', 'WMT', 'COST']
        
        for ticker in defensives:
            with self.subTest(ticker=ticker):
                category = categorize_stock_for_thresholds(0.15, ticker)
                self.assertEqual(category, 'defensive',
                               f'{ticker} should be defensive')
    
    def test_financial_classification(self):
        """Test financial stocks are correctly classified"""
        financials = ['JPM', 'BAC', 'V', 'MA', 'GS', 'MS']
        
        for ticker in financials:
            with self.subTest(ticker=ticker):
                category = categorize_stock_for_thresholds(0.25, ticker)
                self.assertEqual(category, 'financial',
                               f'{ticker} should be financial')
    
    def test_high_volatility_classification(self):
        """Test high volatility stocks are correctly classified"""
        normal_ticker = 'XYZ'  # Not in any explicit list
        high_volatility = 0.50  # 50% > 45%
        
        category = categorize_stock_for_thresholds(high_volatility, normal_ticker)
        self.assertEqual(category, 'high_volatility',
                        'High volatility stock should be classified as high_volatility')
    
    def test_normal_classification(self):
        """Test normal stocks are correctly classified"""
        normal_ticker = 'XYZ'  # Not in any explicit list
        normal_volatility = 0.30  # 30% < 45%
        
        category = categorize_stock_for_thresholds(normal_volatility, normal_ticker)
        self.assertEqual(category, 'normal',
                        'Normal stock should be classified as normal')
    
    def test_threshold_values(self):
        """Test threshold values are correct for each category"""
        expected_thresholds = {
            'mega_cap_stable': (27.0, 73.0),
            'mega_cap_volatile': (27.0, 73.0),
            'high_growth': (22.0, 78.0),
            'defensive': (27.0, 73.0),
            'financial': (28.0, 72.0),
            'high_volatility': (25.0, 75.0),
            'normal': (26.0, 74.0)
        }
        
        for category, expected in expected_thresholds.items():
            with self.subTest(category=category):
                # Test with appropriate ticker and volatility (as decimals)
                if category == 'mega_cap_stable':
                    thresholds = dynamic_thresholds_short_term(0.20, 'AAPL')
                elif category == 'mega_cap_volatile':
                    thresholds = dynamic_thresholds_short_term(0.50, 'AAPL')
                elif category == 'high_growth':
                    thresholds = dynamic_thresholds_short_term(0.30, 'TSLA')
                elif category == 'defensive':
                    thresholds = dynamic_thresholds_short_term(0.15, 'JNJ')
                elif category == 'financial':
                    thresholds = dynamic_thresholds_short_term(0.25, 'JPM')
                elif category == 'high_volatility':
                    thresholds = dynamic_thresholds_short_term(0.50, 'XYZ')
                else:  # normal
                    thresholds = dynamic_thresholds_short_term(0.30, 'XYZ')
                
                self.assertEqual(thresholds, expected,
                               f'{category} thresholds should be {expected}')
    
    def test_mega_cap_priority_over_high_volatility(self):
        """Test mega-caps are classified as mega_cap_volatile, not high_volatility"""
        mega_cap = 'AAPL'
        high_volatility = 0.50  # 50%
        
        category = categorize_stock_for_thresholds(high_volatility, mega_cap)
        self.assertEqual(category, 'mega_cap_volatile',
                        'Mega-cap should be mega_cap_volatile even with high volatility')
        self.assertNotEqual(category, 'high_volatility')
    
    def test_category_threshold_differentiation(self):
        """Test that different categories have different thresholds"""
        # Get thresholds for different categories
        mega_cap_thresh = dynamic_thresholds_short_term(0.20, 'AAPL')
        high_growth_thresh = dynamic_thresholds_short_term(0.30, 'TSLA')
        financial_thresh = dynamic_thresholds_short_term(0.25, 'JPM')
        
        # Verify they're different
        self.assertNotEqual(mega_cap_thresh, high_growth_thresh,
                          'Mega-cap and high-growth should have different thresholds')
        self.assertNotEqual(mega_cap_thresh, financial_thresh,
                          'Mega-cap and financial should have different thresholds')
        self.assertNotEqual(high_growth_thresh, financial_thresh,
                          'High-growth and financial should have different thresholds')
    
    def test_defensive_vs_mega_cap_thresholds(self):
        """Test defensive and mega-cap have same conservative thresholds"""
        defensive_thresh = dynamic_thresholds_short_term(0.15, 'JNJ')
        mega_cap_thresh = dynamic_thresholds_short_term(0.20, 'AAPL')
        
        # Both should be 27% (final optimization)
        self.assertEqual(defensive_thresh[0], 27.0)
        self.assertEqual(mega_cap_thresh[0], 27.0)
        self.assertEqual(defensive_thresh, mega_cap_thresh,
                        'Defensive and mega-cap should have same thresholds')


class TestThresholdOptimization(unittest.TestCase):
    """Test threshold optimization results"""
    
    def test_final_optimization_values(self):
        """Test that final optimized values are correct"""
        # Phase 3.3c final values
        mega_cap_buy, _ = dynamic_thresholds_short_term(0.20, 'AAPL')
        self.assertEqual(mega_cap_buy, 27.0,
                        'Mega-cap buy threshold should be 27% (final optimization)')
    
    def test_high_growth_lowest_threshold(self):
        """Test high-growth has lowest threshold (most lenient)"""
        thresholds = []
        categories = [
            ('mega_cap_stable', 0.20, 'AAPL'),
            ('high_growth', 0.30, 'TSLA'),
            ('defensive', 0.15, 'JNJ'),
            ('financial', 0.25, 'JPM'),
            ('normal', 0.30, 'XYZ')
        ]
        
        for cat, vol, ticker in categories:
            buy_thresh, _ = dynamic_thresholds_short_term(vol, ticker)
            thresholds.append((cat, buy_thresh))
        
        # High-growth should have lowest threshold
        high_growth_thresh = [t for c, t in thresholds if c == 'high_growth'][0]
        other_thresholds = [t for c, t in thresholds if c != 'high_growth']
        
        self.assertTrue(all(high_growth_thresh <= t for t in other_thresholds),
                       'High-growth should have lowest threshold')


if __name__ == '__main__':
    unittest.main()
