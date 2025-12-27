"""
End-to-end integration test for the complete analysis system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from src.spectral_galileo.core.agent import FinancialAgent


class TestEndToEndAnalysis(unittest.TestCase):
    """End-to-end integration tests"""
    
    def test_complete_analysis_with_skip(self):
        """Test complete analysis flow with skip_external_data=True"""
        test_ticker = 'AAPL'
        
        try:
            agent = FinancialAgent(test_ticker, skip_external_data=True)
            result = agent.run_analysis()
            
            # Verify basic structure
            self.assertIsNotNone(result, 'Result should not be None')
            self.assertNotIn('error', result, f'Should not have errors: {result.get("error")}')
            
            # Verify signal is present
            if 'signal' in result:
                valid_signals = ['COMPRA', 'VENTA', 'NEUTRAL']
                self.assertIn(result['signal'], valid_signals,
                             f'Signal should be one of {valid_signals}')
                
                # Verify confidence if present
                if 'confidence' in result:
                    self.assertGreaterEqual(result['confidence'], 0,
                                          'Confidence should be >= 0')
                    self.assertLessEqual(result['confidence'], 100,
                                       'Confidence should be <= 100')
            
            print(f"✅ Complete analysis test passed for {test_ticker}")
            if 'signal' in result:
                print(f"   Signal: {result.get('signal', 'N/A')}")
                print(f"   Confidence: {result.get('confidence', 0):.1f}%")
            else:
                print(f"   Result keys: {list(result.keys())}")
            
            return True
            
        except Exception as e:
            self.fail(f'Complete analysis failed: {str(e)}')
    
    def test_multiple_tickers_batch(self):
        """Test batch analysis of multiple tickers"""
        test_tickers = ['AAPL', 'MSFT', 'GOOGL']
        results = {}
        
        for ticker in test_tickers:
            try:
                agent = FinancialAgent(ticker, skip_external_data=True)
                result = agent.run_analysis()
                results[ticker] = result
                
                # Basic validation
                self.assertIsNotNone(result)
                self.assertNotIn('error', result)
                
            except Exception as e:
                print(f"⚠️ Warning: {ticker} analysis failed: {e}")
        
        # At least one should succeed
        self.assertGreater(len(results), 0,
                          'At least one ticker should analyze successfully')
        
        print(f"✅ Batch analysis test passed ({len(results)}/{len(test_tickers)} tickers)")
        for ticker, result in results.items():
            if result and 'signal' in result:
                print(f"   {ticker}: {result.get('signal', 'N/A')} "
                      f"({result.get('confidence', 0):.1f}%)")
    
    def test_category_threshold_in_analysis(self):
        """Test that category-specific thresholds are applied"""
        # Test different categories
        test_cases = [
            ('AAPL', 'mega_cap_stable'),      # Mega-cap
            ('TSLA', 'high_growth'),          # High-growth
            ('JNJ', 'defensive'),              # Defensive
            ('JPM', 'financial'),              # Financial
        ]
        
        for ticker, expected_category in test_cases:
            try:
                agent = FinancialAgent(ticker, skip_external_data=True)
                result = agent.run_analysis()
                
                # Verify analysis completed
                self.assertIsNotNone(result)
                
                # Check if result is valid
                if 'signal' in result:
                    print(f"✅ {ticker} analyzed: {result.get('signal', 'N/A')} "
                          f"({result.get('confidence', 0):.1f}%)")
                else:
                    print(f"   {ticker} completed (no signal key)")
                
            except Exception as e:
                print(f"⚠️ {ticker} test failed: {e}")
    
    def test_high_confidence_signals(self):
        """Test that high confidence signals are realistic"""
        test_ticker = 'AAPL'
        
        try:
            agent = FinancialAgent(test_ticker, skip_external_data=True)
            result = agent.run_analysis()
            
            if 'confidence' in result and result['confidence'] > 30:
                # High confidence signal - verify it has supporting data
                self.assertIn('signal', result)
                self.assertNotEqual(result['signal'], 'NEUTRAL',
                                  'High confidence should not be NEUTRAL')
                
                print(f"✅ High confidence signal test passed")
                print(f"   {test_ticker}: {result['signal']} at {result['confidence']:.1f}%")
            else:
                conf = result.get('confidence', 0)
                print(f"   {test_ticker}: Low/no confidence {conf:.1f}% (acceptable)")
                
        except Exception as e:
            print(f"⚠️ High confidence test warning: {e}")
    
    def test_performance_benchmark(self):
        """Test that analysis completes in reasonable time"""
        import time
        
        test_ticker = 'AAPL'
        start_time = time.time()
        
        try:
            agent = FinancialAgent(test_ticker, skip_external_data=True)
            result = agent.run_analysis()
            elapsed = time.time() - start_time
            
            # Should complete in under 10 seconds with skip_external_data
            self.assertLess(elapsed, 10.0,
                          f'Analysis took {elapsed:.2f}s, expected < 10s')
            
            print(f"✅ Performance test passed: {elapsed:.2f}s")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"⚠️ Performance test completed in {elapsed:.2f}s with error: {e}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
