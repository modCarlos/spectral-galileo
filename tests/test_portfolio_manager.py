import unittest
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.spectral_galileo.core import portfolio_manager

class TestPortfolioManager(unittest.TestCase):
    
    def setUp(self):
        """Setup test environment before each test"""
        self.test_file = "test_portfolio.json"
        portfolio_manager.PORTFOLIO_FILE = self.test_file
        # Clear test portfolio
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def tearDown(self):
        """Cleanup after each test"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_load_empty_portfolio(self):
        """Test loading non-existent portfolio returns empty list"""
        result = portfolio_manager.load_portfolio()
        self.assertEqual(result, [])
    
    def test_add_stock_with_price(self):
        """Test adding stock with custom price"""
        msg = portfolio_manager.add_stock("AAPL", "150.00")
        self.assertIn("AAPL", msg)
        self.assertIn("150.00", msg)
        self.assertIn("personalizado", msg)
        
        portfolio = portfolio_manager.load_portfolio()
        self.assertEqual(len(portfolio), 1)
        self.assertEqual(portfolio[0]['symbol'], "AAPL")
        self.assertEqual(portfolio[0]['buy_price'], 150.00)
    
    def test_add_stock_invalid_price(self):
        """Test adding stock with invalid price"""
        msg = portfolio_manager.add_stock("AAPL", "invalid")
        self.assertIn("Error", msg)
        self.assertIn("inválido", msg)
    
    def test_add_stock_negative_price(self):
        """Test adding stock with negative price"""
        msg = portfolio_manager.add_stock("AAPL", "-10")
        self.assertIn("Error", msg)
        self.assertIn("mayor a 0", msg)
    
    def test_get_portfolio_tickers(self):
        """Test getting unique tickers"""
        portfolio_manager.add_stock("AAPL", "150")
        portfolio_manager.add_stock("MSFT", "300")
        portfolio_manager.add_stock("AAPL", "155")  # Duplicate
        
        tickers = portfolio_manager.get_portfolio_tickers()
        self.assertEqual(set(tickers), {"AAPL", "MSFT"})
    
    def test_remove_last_stock(self):
        """Test removing last entry of a stock"""
        portfolio_manager.add_stock("AAPL", "150")
        portfolio_manager.add_stock("AAPL", "155")
        
        msg = portfolio_manager.remove_last_stock("AAPL")
        self.assertIn("155", msg)
        
        portfolio = portfolio_manager.load_portfolio()
        self.assertEqual(len(portfolio), 1)
        self.assertEqual(portfolio[0]['buy_price'], 150.00)
    
    def test_remove_nonexistent_stock(self):
        """Test removing stock that doesn't exist"""
        msg = portfolio_manager.remove_last_stock("TSLA")
        self.assertIn("No se encontró", msg)
    
    def test_remove_all_stock(self):
        """Test removing all entries of a stock"""
        portfolio_manager.add_stock("AAPL", "150")
        portfolio_manager.add_stock("AAPL", "155")
        portfolio_manager.add_stock("MSFT", "300")
        
        msg = portfolio_manager.remove_all_stock("AAPL")
        self.assertIn("2 entrada", msg)
        
        portfolio = portfolio_manager.load_portfolio()
        self.assertEqual(len(portfolio), 1)
        self.assertEqual(portfolio[0]['symbol'], "MSFT")
    
    def test_clear_portfolio(self):
        """Test clearing entire portfolio"""
        portfolio_manager.add_stock("AAPL", "150")
        portfolio_manager.add_stock("MSFT", "300")
        
        msg = portfolio_manager.clear_portfolio()
        self.assertIn("vaciado", msg)
        
        portfolio = portfolio_manager.load_portfolio()
        self.assertEqual(len(portfolio), 0)
    
    def test_get_holdings(self):
        """Test getting holdings for specific ticker"""
        portfolio_manager.add_stock("AAPL", "150")
        portfolio_manager.add_stock("AAPL", "155")
        portfolio_manager.add_stock("MSFT", "300")
        
        aapl_holdings = portfolio_manager.get_holdings("AAPL")
        self.assertEqual(len(aapl_holdings), 2)
        
        msft_holdings = portfolio_manager.get_holdings("MSFT")
        self.assertEqual(len(msft_holdings), 1)

if __name__ == '__main__':
    unittest.main()
