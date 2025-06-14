#!/usr/bin/env python3
"""
Trading News Terminal - Professional real-time news aggregator
Real-time streaming news with topic selection for trading
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.streaming_app import main

if __name__ == "__main__":
    main()