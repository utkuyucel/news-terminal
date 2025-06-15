#!/usr/bin/env python3
"""
News Terminal - Bloomberg-style terminal for real-time news aggregation.

A professional news terminal that aggregates news from multiple sources
including APIs and RSS feeds, displaying them in a clean terminal interface
with real-time updates.
"""
import argparse
import logging
import sys
from datetime import datetime
from typing import List

from config import DEFAULT_CONFIG
from src.aggregator import news_aggregator
from src.display import terminal_display, simple_display
from src.menu import topic_menu, simple_topic_menu


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.WARNING  # Changed from INFO to WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('news_terminal.log'),
            logging.StreamHandler() if verbose else logging.NullHandler()
        ]
    )


def validate_config() -> bool:
    """Validate application configuration."""
    if not DEFAULT_CONFIG.api.news_api_key:
        print("⚠️  Warning: No News API key found. Only free sources will be used.")
        print("   Get a free key from https://newsapi.org and add it to your .env file")
        return True  # Continue with free sources
    
    print("✅ Configuration validated successfully")
    return True


def run_terminal_mode(categories: List[str], simple_mode: bool = False, interactive: bool = True) -> None:
    """Run the terminal in live display mode."""
    print("🚀 Starting News Terminal...")
    
    if not validate_config():
        sys.exit(1)
    
    # Interactive topic selection or use provided categories
    if interactive:
        selected_categories = None
        
        while selected_categories is None:
            if simple_mode:
                selected_categories = simple_topic_menu.show_menu()
            else:
                selected_categories = topic_menu.show_menu()
            
            if selected_categories is None:
                print("👋 Goodbye!")
                return
        
        categories = selected_categories
    
    def get_news():
        """Fetch news wrapper for display."""
        return news_aggregator.fetch_news_concurrent(categories)
    
    try:
        if simple_mode:
            # Simple mode for basic terminals with loop
            simple_display.display_news_loop(get_news)
        else:
            # Rich terminal mode
            terminal_display.display_news_live(get_news)
            
        # After exiting live mode, return to menu if interactive
        if interactive:
            run_terminal_mode(categories, simple_mode, interactive)
            
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        print(f"❌ Fatal Error: {str(e)}")
        sys.exit(1)


def run_fetch_mode(categories: List[str], output_format: str = 'text') -> None:
    """Run in fetch mode - get news once and output."""
    try:
        aggregated_news = news_aggregator.fetch_news_concurrent(categories)
        
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
                for article in aggregated_news.articles
            ]
            print(json.dumps(articles_data, indent=2))
        else:
            # Text output
            print(f"📰 News Terminal - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📊 {len(aggregated_news.articles)} articles from {aggregated_news.total_sources} sources")
            print("=" * 80)
            
            for article in aggregated_news.articles:
                print(f"\n[{article.published_at.strftime('%H:%M')}] {article.source} - {article.category.upper()}")
                print(f"🔗 {article.title}")
                print(f"   {article.url}")
                if article.description:
                    print(f"   {article.description[:150]}...")
    
    except Exception as e:
        logging.error(f"Error in fetch mode: {e}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="News Terminal - Real-time news aggregation terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                          # Run terminal with default categories
  python run.py -c technology business   # Run with specific categories
  python run.py --simple                 # Run in simple mode for basic terminals
  python run.py --fetch                  # Fetch news once and exit
  python run.py --fetch --json           # Output news in JSON format
  python run.py --verbose                # Run with verbose logging
        """
    )
    
    parser.add_argument(
        '-c', '--categories',
        nargs='+',
        default=['financial', 'technology', 'business', 'earnings'],  # Trading-focused defaults
        choices=['general', 'technology', 'business', 'politics', 'science', 'sports', 'entertainment', 'financial', 'crypto', 'earnings'],
        help='News categories to display (default: financial, technology, business, earnings)'
    )
    
    parser.add_argument(
        '--simple',
        action='store_true',
        help='Use simple terminal mode (no rich formatting)'
    )
    
    parser.add_argument(
        '--fetch',
        action='store_true',
        help='Fetch news once and exit (no live updates)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format (only with --fetch)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--no-menu',
        action='store_true',
        help='Skip interactive topic selection and use provided categories'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Cache is automatically managed by the aggregator
    
    # Run in appropriate mode
    if args.fetch:
        output_format = 'json' if args.json else 'text'
        run_fetch_mode(args.categories, output_format)
    else:
        interactive = not args.no_menu
        run_terminal_mode(args.categories, args.simple, interactive)


if __name__ == "__main__":
    main()