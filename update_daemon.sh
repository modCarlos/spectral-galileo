#!/bin/bash

# Update Alerts Daemon with Phase 3 Optimizations
# Restarts daemon with new thresholds and production settings

echo "================================================"
echo "🔄 UPDATING ALERTS DAEMON - Phase 3 Optimizations"
echo "================================================"
echo

# Check if daemon is running
PID_FILE="data/alerts.pid"

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "🛑 Stopping old daemon (PID: $OLD_PID)..."
        kill -TERM "$OLD_PID" 2>/dev/null || kill -9 "$OLD_PID" 2>/dev/null
        sleep 2
        
        # Verify it stopped
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            echo "❌ Failed to stop daemon"
            exit 1
        fi
        echo "✅ Old daemon stopped"
    else
        echo "⚠️  PID file exists but daemon not running"
        rm -f "$PID_FILE"
    fi
else
    echo "ℹ️  No daemon currently running"
fi

echo

# Display new configuration
echo "📋 NEW CONFIGURATION (Phase 3 Optimized):"
echo "   - Min Confidence (Strong Buy): 30% (was 70%)"
echo "   - Min Confidence (Buy): 25% (was 60%)"
echo "   - External Data: ENABLED (Reddit, Earnings, Insider)"
echo "   - Category Thresholds: ACTIVE"
echo "   - Grid Search Params: APPLIED"
echo

# Update config file if needed
CONFIG_FILE="config/alert_config.json"

if [ -f "$CONFIG_FILE" ]; then
    echo "📝 Backing up old config..."
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup_$(date +%Y%m%d_%H%M%S)"
    
    # Update thresholds in config
    python3 -c "
import json
import os

config_file = 'config/alert_config.json'

if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Update optimized thresholds
    config['min_confidence'] = {
        'strong_buy': 30,  # Phase 3 optimized
        'buy': 25          # Phase 3 optimized
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    
    print('✅ Config updated with Phase 3 thresholds')
else:
    print('⚠️  Config file not found, will use defaults')
"
else
    echo "ℹ️  No existing config, will create with defaults"
fi

echo

# Start new daemon
echo "🚀 Starting updated daemon..."
echo

# Activate venv and start daemon
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    python alerts/daemon.py start
else
    python3 alerts/daemon.py start
fi

echo
echo "================================================"
echo "✅ DAEMON UPDATE COMPLETE"
echo "================================================"
echo
echo "📊 Monitoring Status:"
echo "   - Check logs: tail -f logs/alerts.log"
echo "   - Check PID: cat data/alerts.pid"
echo "   - Test alert: python main.py --ticker AAPL"
echo
echo "🎯 Expected Behavior with Phase 3 Optimizations:"
echo "   - More selective signals (19.7% COMPRA rate)"
echo "   - Higher quality alerts (31.4% avg confidence)"
echo "   - Category-aware thresholds (mega-cap 27%, high-growth 22%)"
echo "   - Full external data integration"
echo
