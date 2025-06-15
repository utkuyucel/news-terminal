#!/usr/bin/env python3
"""
Example usage of the News Terminal API
"""
from src.aggregator import news_aggregator

def main():
    """Example usage."""
    print("🔄 Fetching latest news...")
    
    # Fetch news from specific categories
    categories = ['technology', 'business']
    aggregated_news = news_aggregator.fetch_news_concurrent(categories)
    
    print(f"📊 Retrieved {len(aggregated_news.articles)} articles from {aggregated_news.total_sources} sources")
    print(f"📅 Last updated: {aggregated_news.last_updated}")
    print(f"🏷️  Categories: {', '.join(aggregated_news.categories)}")
    print()
    
    # Show top 5 articles
    print("🔥 Top 5 Latest Articles:")
    print("=" * 80)
    
    for i, article in enumerate(aggregated_news.articles[:5], 1):
        print(f"{i}. [{article.published_at.strftime('%H:%M')}] {article.source}")
        print(f"   📰 {article.title}")
        print(f"   🔗 {article.url}")
        print(f"   🏷️  {article.category.upper()}")
        print()
    
    # Show source statistics
    top_sources = news_aggregator.get_top_sources(5)
    print("📈 Top Sources:")
    for source, count in top_sources:
        print(f"   • {source}: {count} articles")

if __name__ == "__main__":
    main()
