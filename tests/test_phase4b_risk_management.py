"""
Phase 4B: Risk Management Integration Tests

Tests validate:
1. ATR calculation
2. Position sizing based on risk (2% max, 20% max position)
3. Stop Loss calculation (Entry - 1.5 * ATR)
4. Take Profit calculation (Entry + 3.0 * ATR)
5. Risk Management metrics in analysis_results
6. Portfolio Manager TP/SL monitoring
"""

import pytest
import numpy as np
from agent import (
    calculate_atr, 
    calculate_position_size_risk_based,
    calculate_stop_loss_price,
    calculate_take_profit_price
)


class TestATRCalculation:
    """Test ATR (Average True Range) calculation"""
    
    def test_atr_basic_calculation(self):
        """Test ATR with simple price data"""
        high = np.array([110, 112, 115, 113, 116])
        low = np.array([108, 109, 111, 110, 112])
        close = np.array([109, 111, 114, 112, 115])
        
        atr = calculate_atr(high, low, close, periods=3)
        
        assert atr > 0, "ATR should be positive"
        assert atr < 10, "ATR should be reasonable for this price range"
    
    def test_atr_with_gaps(self):
        """Test ATR calculation with price gaps (high true range)"""
        high = np.array([100, 105, 110, 108, 115])
        low = np.array([95, 98, 102, 100, 105])
        close = np.array([98, 103, 108, 105, 112])
        
        atr = calculate_atr(high, low, close, periods=3)
        
        # ATR should capture the gaps
        assert atr > 4, "ATR should reflect high volatility from gaps"
    
    def test_atr_insufficient_data_fallback(self):
        """Test ATR with insufficient data uses 2% fallback"""
        high = np.array([100])
        low = np.array([95])
        close = np.array([98])
        
        atr = calculate_atr(high, low, close, periods=14)
        
        # Should use 2% of last close as fallback
        expected_fallback = 98 * 0.02
        assert abs(atr - expected_fallback) < 0.01, "Should use 2% fallback"
    
    def test_atr_default_periods(self):
        """Test ATR uses 14 periods by default"""
        high = np.array([100 + i for i in range(20)])
        low = np.array([95 + i for i in range(20)])
        close = np.array([98 + i for i in range(20)])
        
        atr = calculate_atr(high, low, close)  # No periods specified
        
        assert atr > 0, "ATR should calculate with default 14 periods"


class TestPositionSizing:
    """Test position sizing based on risk management"""
    
    def test_position_size_basic(self):
        """Test basic position sizing calculation"""
        entry_price = 100.0
        atr = 2.0
        account_value = 100000
        
        position_size = calculate_position_size_risk_based(
            entry_price, atr, account_value, max_risk_per_trade=0.02
        )
        
        # Max risk = $2000 (2% of $100k)
        # Risk per share = 1.5 * ATR = 3.0
        # Max shares = 2000 / 3.0 = 666 shares
        # BUT: 20% cap = $20,000 / $100 = 200 shares (this overrides)
        # Position value = 200 * 100 = $20,000 (at 20% cap)
        expected_shares = 200  # 20% cap dominates
        
        assert position_size == expected_shares, f"Expected {expected_shares} shares"
        assert position_size * entry_price <= account_value * 0.20 + 1, "Should respect 20% cap"
    
    def test_position_size_respects_20_percent_cap(self):
        """Test position sizing respects 20% portfolio allocation cap"""
        entry_price = 10.0  # Cheap stock
        atr = 0.2  # Low volatility
        account_value = 100000
        
        position_size = calculate_position_size_risk_based(
            entry_price, atr, account_value, max_risk_per_trade=0.02
        )
        
        position_value = position_size * entry_price
        max_position = account_value * 0.20  # $20,000
        
        assert position_value <= max_position + 0.01, f"Position ${position_value} exceeds 20% cap ${max_position}"
    
    def test_position_size_high_volatility(self):
        """Test position sizing with high volatility (large ATR)"""
        entry_price = 100.0
        atr = 10.0  # High volatility
        account_value = 100000
        
        position_size = calculate_position_size_risk_based(
            entry_price, atr, account_value, max_risk_per_trade=0.02
        )
        
        # Risk per share = 1.5 * 10 = 15
        # Max shares = 2000 / 15 = 133 shares
        expected_shares = int(2000 / 15.0)
        
        assert position_size == expected_shares, "Should reduce position size for high volatility"
        assert position_size < 200, "High volatility should result in smaller position"
    
    def test_position_size_different_risk_tolerance(self):
        """Test position sizing with different risk tolerance"""
        entry_price = 50.0  # Lower price to avoid hitting 20% cap
        atr = 1.0
        account_value = 100000
        
        # Conservative: 1% risk
        position_conservative = calculate_position_size_risk_based(
            entry_price, atr, account_value, max_risk_per_trade=0.01
        )
        
        # Aggressive: 3% risk (capped at 2%)
        position_aggressive = calculate_position_size_risk_based(
            entry_price, atr, account_value, max_risk_per_trade=0.03
        )
        
        # With lower price, both should be capped at 20% = $20k / $50 = 400 shares
        # But conservative should have fewer if not at cap
        assert position_conservative <= position_aggressive, "Conservative should be smaller or equal"
        assert position_aggressive * entry_price <= account_value * 0.20 + 1, "Should respect 20% cap"


class TestStopLossTakeProfit:
    """Test Stop Loss and Take Profit calculations"""
    
    def test_stop_loss_calculation(self):
        """Test Stop Loss = Entry - (1.5 * ATR)"""
        entry_price = 100.0
        atr = 2.0
        
        stop_loss = calculate_stop_loss_price(entry_price, atr)
        
        expected_sl = 100 - (1.5 * 2.0)  # 97.0
        assert abs(stop_loss - expected_sl) < 0.01, f"Expected SL {expected_sl}, got {stop_loss}"
    
    def test_take_profit_calculation(self):
        """Test Take Profit = Entry + (3.0 * ATR)"""
        entry_price = 100.0
        atr = 2.0
        
        take_profit = calculate_take_profit_price(entry_price, atr)
        
        expected_tp = 100 + (3.0 * 2.0)  # 106.0
        assert abs(take_profit - expected_tp) < 0.01, f"Expected TP {expected_tp}, got {take_profit}"
    
    def test_risk_reward_ratio_2_to_1(self):
        """Test that TP/SL maintains 2:1 risk/reward ratio"""
        entry_price = 100.0
        atr = 2.0
        
        stop_loss = calculate_stop_loss_price(entry_price, atr)
        take_profit = calculate_take_profit_price(entry_price, atr)
        
        risk = entry_price - stop_loss  # 3.0
        reward = take_profit - entry_price  # 6.0
        rr_ratio = reward / risk
        
        assert abs(rr_ratio - 2.0) < 0.01, f"Expected 2:1 R/R, got {rr_ratio:.2f}:1"
    
    def test_stop_loss_always_below_entry(self):
        """Test SL is always below entry for long positions"""
        test_cases = [
            (50.0, 1.0),
            (100.0, 5.0),
            (200.0, 10.0),
        ]
        
        for entry_price, atr in test_cases:
            stop_loss = calculate_stop_loss_price(entry_price, atr)
            assert stop_loss < entry_price, f"SL {stop_loss} should be below entry {entry_price}"
    
    def test_take_profit_always_above_entry(self):
        """Test TP is always above entry for long positions"""
        test_cases = [
            (50.0, 1.0),
            (100.0, 5.0),
            (200.0, 10.0),
        ]
        
        for entry_price, atr in test_cases:
            take_profit = calculate_take_profit_price(entry_price, atr)
            assert take_profit > entry_price, f"TP {take_profit} should be above entry {entry_price}"


class TestRiskManagementIntegration:
    """Integration tests for Risk Management in agent analysis"""
    
    def test_analysis_results_includes_rm_section(self):
        """Test that analysis_results includes risk_management section"""
        from agent import FinancialAgent
        
        # Use a real ticker with data
        agent = FinancialAgent("AAPL", is_short_term=True)
        
        results = agent.run_analysis()
        
        assert "risk_management" in results, "analysis_results should include risk_management section"
    
    def test_rm_section_has_required_fields(self):
        """Test that risk_management section has all required fields"""
        from agent import FinancialAgent
        
        agent = FinancialAgent("AAPL", is_short_term=True)
        results = agent.run_analysis()
        
        rm = results["risk_management"]
        
        required_fields = [
            "atr", "position_size_shares", "position_value",
            "stop_loss_price", "take_profit_price",
            "risk_per_share", "reward_per_share", "risk_reward_ratio",
            "max_portfolio_allocation", "max_risk_per_trade"
        ]
        
        for field in required_fields:
            assert field in rm, f"risk_management should include {field}"
    
    def test_rm_values_are_reasonable(self):
        """Test that RM values are within reasonable ranges"""
        from agent import FinancialAgent
        
        agent = FinancialAgent("AAPL", is_short_term=True)
        results = agent.run_analysis()
        
        rm = results["risk_management"]
        current_price = results["current_price"]
        
        # ATR should be positive and reasonable (< 20% of price)
        assert rm["atr"] > 0, "ATR should be positive"
        assert rm["atr"] < current_price * 0.20, "ATR should be reasonable"
        
        # Position size should be positive
        assert rm["position_size_shares"] > 0, "Position size should be positive"
        
        # Stop Loss should be below current price
        assert rm["stop_loss_price"] < current_price, "Stop Loss should be below entry"
        
        # Take Profit should be above current price
        assert rm["take_profit_price"] > current_price, "Take Profit should be above entry"
        
        # Risk/Reward should be approximately 2:1
        assert 1.9 < rm["risk_reward_ratio"] < 2.1, f"R/R should be ~2:1, got {rm['risk_reward_ratio']:.2f}"
        
        # Max allocation and risk should match constants
        assert rm["max_portfolio_allocation"] == 0.20, "Max allocation should be 20%"
        assert rm["max_risk_per_trade"] == 0.02, "Max risk should be 2%"


class TestPortfolioManagerRMFunctions:
    """Test Portfolio Manager Risk Management functions"""
    
    def test_add_stock_with_rm_parameters(self):
        """Test adding stock with RM parameters"""
        import portfolio_manager
        
        # Clean slate
        portfolio_manager.save_portfolio([])
        
        # Add stock with RM
        msg = portfolio_manager.add_stock(
            ticker="TEST",
            price=100.0,
            stop_loss=97.0,
            take_profit=106.0,
            position_size=100
        )
        
        assert "Stop Loss: $97.00" in msg
        assert "Take Profit: $106.00" in msg
        assert "100 acciones" in msg
        
        # Verify stored
        portfolio = portfolio_manager.load_portfolio()
        assert len(portfolio) == 1
        assert portfolio[0]["stop_loss"] == 97.0
        assert portfolio[0]["take_profit"] == 106.0
        assert portfolio[0]["position_size"] == 100
        
        # Cleanup
        portfolio_manager.save_portfolio([])
    
    def test_check_stop_loss_take_profit_empty_portfolio(self):
        """Test RM check with empty portfolio"""
        import portfolio_manager
        
        portfolio_manager.save_portfolio([])
        alerts = portfolio_manager.check_stop_loss_take_profit()
        
        assert len(alerts["stop_loss_hit"]) == 0
        assert len(alerts["take_profit_hit"]) == 0
        assert len(alerts["no_rm"]) == 0
        assert len(alerts["active"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
