#!/usr/bin/env python3
"""
Enhanced Trading News Terminal - Real-time trading optimized news feed.

This is a specialized version optimized for stock trading with:
- Ultra-fast refresh rates (sub-second updates)
- Financial news prioritization
- Real-time market data integration
- Enhanced urgent news detection
"""
import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from realtime_trading import main

if __name__ == "__main__":
    print("🔥 ENHANCED TRADING MODE - Real-Time News Terminal")
    print("⚡ Ultra-fast updates optimized for trading")
    print("📈 Financial news prioritization enabled")
    print("=" * 60)
    
    # Force trading mode with financial categories
    sys.argv.extend(['--trading-mode', '--categories', 'financial', 'business', 'crypto'])
    main()
