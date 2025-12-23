import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sentiment_analysis

class TestSentimentHybrid(unittest.TestCase):
    
    def setUp(self):
        # Sample hybrid news data
        self.hybrid_news = [
            # yfinance format
            {'title': 'Palantir hits record high after expansion', 'publisher': 'Yahoo Finance'},
            {'title': 'Crisis in tech sector as regulation looms', 'publisher': 'Reuters'},
            # google rss format (simulated in market_data)
            {
                'title': 'Is Palantir Stock a Buy in 2026?',
                'link': 'http://example.com',
                'publisher': 'Google News',
                'providerPublishTime': 0
            }
        ]

    def test_advanced_sentiment_analysis_hybrid(self):
        """Test that advanced sentiment handles hybrid news lists"""
        res = sentiment_analysis.advanced_sentiment_analysis(self.hybrid_news)
        
        self.assertIn('score', res)
        self.assertIn('volume', res)
        self.assertEqual(res['volume'], 3)
        self.assertIn('label', res)
        
        # Check volume score (3/40)
        self.assertAlmostEqual(res['volume_score'], 3/40, places=5)

    def test_detect_regulatory_factors_all(self):
        """Test that regulation detection processes all news"""
        res = sentiment_analysis.detect_regulatory_factors(self.hybrid_news)
        
        self.assertTrue(res['has_regulatory_risk'])
        self.assertIn('regulation', res['factors_detected'])
        self.assertLess(res['sentiment_adjustment'], 0) # Negative weight for regulation

    def test_empty_news(self):
        """Test graceful handling of empty news list"""
        res = sentiment_analysis.advanced_sentiment_analysis([])
        self.assertEqual(res['volume'], 0)
        self.assertEqual(res['score'], 0)
        self.assertEqual(res['label'], 'Sin Datos')

if __name__ == '__main__':
    unittest.main()
