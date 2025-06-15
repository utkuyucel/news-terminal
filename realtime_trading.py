#!/usr/bin/env python3
"""
Real-Time Trading News Terminal - Ultra-fast news updates for trading.

High-frequency news aggregation with sub-second updates for professional trading.
"""
import argparse
import asyncio
import logging
import sys
from datetime import datetime
from typing import List

from config import DEFAULT_CONFIG
from src.realtime_aggregator import realtime_aggregator, RealTimeNews
from src.display import terminal_display, simple_display
from src.menu import TopicMenu


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for real-time trading application."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler('realtime_trading.log'),
            logging.StreamHandler() if verbose else logging.NullHandler()
        ]
    )


def validate_config() -> bool:
    """Validate application configuration for real-time trading."""
    if not DEFAULT_CONFIG.api.news_api_key:
        print("⚠️  Warning: No News API key found. Only free sources will be used.")
        print("   Get a free key from https://newsapi.org for enhanced real-time data")
        return True
    
    print("✅ Real-time trading configuration validated")
    return True


def run_realtime_trading_mode(categories: List[str], simple_mode: bool = False) -> None:
    """Run terminal in real-time trading mode with ultra-fast updates."""
    print("🚀 Starting Real-Time Trading News Terminal...")
    print(f"📊 Categories: {', '.join(categories)}")
    print(f"⚡ Update interval: {DEFAULT_CONFIG.terminal.trading_news_fetch_interval}s")
    print(f"🔄 Display refresh: {DEFAULT_CONFIG.terminal.refresh_interval}s")
    
    if not validate_config():
        sys.exit(1)
    
    # Create sync wrapper for the display system
    def get_news_sync():
        # Use the faster aggregation but in sync mode
        try:
            # Import here to avoid circular import
            from src.aggregator import news_aggregator
            return news_aggregator.fetch_news_concurrent(categories)
        except Exception as e:
            logging.error(f"Error fetching news: {e}")
            # Return empty news
            from src.aggregator import AggregatedNews
            return AggregatedNews(
                articles=[],
                last_updated=datetime.now(),
                total_sources=0,
                categories=set()
            )
    
    try:
        print("🎯 Entering real-time trading mode...")
        print("📈 Press Ctrl+C to exit")
        print("=" * 80)
        
        if simple_mode:
            # Simple mode for basic terminals
            simple_display.display_news_loop(get_news_sync)
        else:
            # Rich terminal mode with real-time updates
            terminal_display.display_news_live(get_news_sync)
            
    except KeyboardInterrupt:
        print("\n👋 Real-time trading terminal stopped")
    except Exception as e:
        logging.error(f"Fatal error in real-time mode: {e}")
        print(f"❌ Fatal Error: {str(e)}")
        sys.exit(1)


def run_realtime_fetch_mode(categories: List[str], output_format: str = 'text') -> None:
    """Run in real-time fetch mode - continuous news output."""
    async def fetch_and_display():
        print(f"📊 Real-Time News Feed - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📡 Categories: {', '.join(categories)}")
        print("=" * 80)
        
        try:
            while True:
                news = await realtime_aggregator.fetch_real_time_news(categories)
                
                if output_format == 'json':
                    import json
                    articles_data = [
                        {
                            'title': article.title,
                            'description': article.description,
                            'url': article.url,
                            'source': article.source,
                            'published_at': article.published_at.isoformat(),
                            'category': article.category
                        }
                        for article in news.articles[:10]  # Latest 10 for real-time
                    ]
                    print(json.dumps(articles_data, indent=2))
                else:
                    # Real-time text output
                    print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} | "
                          f"📊 {len(news.articles)} articles | "
                          f"🔥 {news.breaking_news_count} breaking | "
                          f"⚡ {news.update_frequency:.1f} updates/sec")
                    
                    for article in news.articles[:5]:  # Show top 5 for real-time
                        breaking_indicator = "🚨 " if any(
                            keyword in article.title.lower() 
                            for keyword in ['breaking', 'urgent', 'alert']
                        ) else ""
                        
                        print(f"\n{breaking_indicator}[{article.published_at.strftime('%H:%M')}] "
                              f"{article.source} - {article.category.upper()}")
                        print(f"🔗 {article.title}")
                        print(f"   {article.url}")
                
                # Real-time interval
                await asyncio.sleep(DEFAULT_CONFIG.terminal.trading_news_fetch_interval)
                
        except KeyboardInterrupt:
            print("\n👋 Real-time feed stopped")
    
    # Run the async fetch loop
    asyncio.run(fetch_and_display())


def main():
    """Main entry point for real-time trading terminal."""
    parser = argparse.ArgumentParser(
        description="Real-Time Trading News Terminal - Ultra-fast news for trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Interactive topic selection
  %(prog)s --categories financial    # Real-time financial news
  %(prog)s --fetch --format json     # JSON output mode
  %(prog)s --simple                  # Simple terminal mode
  %(prog)s --trading-mode             # Ultra-fast trading mode
        """
    )
    
    parser.add_argument('--categories', '-c', nargs='+', 
                       choices=['general', 'business', 'technology', 'financial', 'crypto'],
                       help='News categories to fetch')
    parser.add_argument('--fetch', action='store_true', 
                       help='Run in continuous fetch mode')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format for fetch mode')
    parser.add_argument('--simple', action='store_true', 
                       help='Use simple terminal display mode')
    parser.add_argument('--no-menu', action='store_true', 
                       help='Skip interactive menu')
    parser.add_argument('--trading-mode', action='store_true',
                       help='Enable ultra-fast trading mode')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Determine categories
    if args.categories:
        categories = args.categories
    elif args.no_menu:
        categories = ['financial', 'business']  # Default for trading
    else:
        # Interactive menu
        menu = TopicMenu()
        if args.simple:
            # Simple menu for basic terminals
            print("Select topic:")
            print("1. Technology  2. Politics  3. Economy & Finance")
            print("4. Trading Focus  5. Cryptocurrency  6. General News")
            choice = input("Enter choice (1-6): ").strip()
            category_map = {
                '1': ['technology'], '2': ['politics'], '3': ['financial', 'business'],
                '4': ['financial', 'business'], '5': ['crypto'], '6': ['general']
            }
            categories = category_map.get(choice, ['financial', 'business'])
        else:
            categories = menu.show_menu()
        
        if not categories:
            print("👋 Goodbye!")
            sys.exit(0)
    
    # Trading mode gets priority for financial categories
    if args.trading_mode:
        categories = ['financial', 'business', 'crypto']
        print("🔥 ULTRA-FAST TRADING MODE ENABLED")
    
    # Run appropriate mode
    if args.fetch:
        run_realtime_fetch_mode(categories, args.format)
    else:
        # Run real-time terminal
        run_realtime_trading_mode(categories, args.simple)


if __name__ == "__main__":
    main()
