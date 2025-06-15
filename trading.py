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
    
    parser.add_argument(
        '--earnings-only',
        action='store_true',
        help='Focus only on earnings and financial news'
    )
    
    parser.add_argument(
        '--crypto',
        action='store_true',
        help='Include cryptocurrency news'
    )
    
    parser.add_argument(
        '--fetch',
        action='store_true',
        help='Fetch news once and exit (for quick trading decisions)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format (only with --fetch)'
    )
    
    parser.add_argument(
        '--simple',
        action='store_true',
        help='Use simple terminal mode'
    )
    
    args = parser.parse_args()
    
    # Set trading-focused categories
    if args.earnings_only:
        categories = ['earnings', 'financial']
    elif args.crypto:
        categories = ['financial', 'earnings', 'crypto', 'technology']
    else:
        categories = ['financial', 'earnings', 'business', 'technology']
    
    # Build sys.argv for the main run.py function
    sys.argv = ['run.py', '-c'] + categories
    
    if args.fetch:
        sys.argv.append('--fetch')
    if args.json:
        sys.argv.append('--json')
    if args.simple:
        sys.argv.append('--simple')
    
    # Call the main function
    run_main()

if __name__ == "__main__":
    trading_main()
