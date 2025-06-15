"""
RSS feed handlers for various news sources.
"""
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Dict, Generator, List, Optional

import feedparser
from dateutil import parser

from data.api import NewsArticle


@dataclass(frozen=True)
class RSSFeed:
    """RSS feed configuration."""
    name: str
    url: str
    category: str
    priority: int = 1  # Higher number = higher priority


class RSSFeedManager:
    """Manager for RSS feed operations."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._feeds = self._get_default_feeds()
    
    @staticmethod
    @lru_cache(maxsize=1)
    def _get_default_feeds() -> Dict[str, List[RSSFeed]]:
        """Get default RSS feeds organized by category."""
        return {
            'financial': [
                RSSFeed('Reuters Business', 'https://feeds.reuters.com/reuters/businessNews', 'business', 3),
                RSSFeed('MarketWatch', 'https://feeds.marketwatch.com/marketwatch/realtimeheadlines/', 'business', 3),
                RSSFeed('Yahoo Finance', 'https://feeds.finance.yahoo.com/rss/2.0/headline', 'business', 2),
                RSSFeed('CNN Business', 'http://rss.cnn.com/rss/money_latest.rss', 'business', 2),
                RSSFeed('Bloomberg', 'https://feeds.bloomberg.com/markets/news.rss', 'business', 3),
                RSSFeed('Financial Times', 'https://www.ft.com/rss/home', 'business', 3),
                RSSFeed('Wall Street Journal', 'https://feeds.wsj.com/wsj/xml/rss/3_7085.xml', 'business', 3),
                RSSFeed('Seeking Alpha', 'https://seekingalpha.com/api/sa/combined/A.xml', 'business', 2),
            ],
            'earnings': [
                RSSFeed('Earnings Whispers', 'https://www.earningswhispers.com/rss/epsrss.asp', 'business', 3),
                RSSFeed('Yahoo Earnings', 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=earnings', 'business', 3),
            ],
            'technology': [
                RSSFeed('TechCrunch', 'https://feeds.feedburner.com/TechCrunch/', 'technology', 3),
                RSSFeed('Ars Technica', 'https://feeds.arstechnica.com/arstechnica/index', 'technology', 3),
                RSSFeed('The Verge', 'https://www.theverge.com/rss/index.xml', 'technology', 2),
                RSSFeed('Wired', 'https://www.wired.com/feed/rss', 'technology', 2),
                RSSFeed('VentureBeat', 'https://venturebeat.com/feed/', 'technology', 2),
            ],
            'crypto': [
                RSSFeed('CoinDesk', 'https://feeds.coindesk.com/coindesk-results', 'business', 3),
                RSSFeed('Cointelegraph', 'https://cointelegraph.com/rss', 'business', 2),
                RSSFeed('Decrypt', 'https://decrypt.co/feed', 'business', 2),
                RSSFeed('CryptoNews', 'https://cryptonews.com/news/feed/', 'business', 2),
            ],
            'general': [
                RSSFeed('BBC News', 'http://feeds.bbci.co.uk/news/rss.xml', 'general', 3),
                RSSFeed('Reuters World', 'https://feeds.reuters.com/Reuters/worldNews', 'general', 3),
                RSSFeed('AP News', 'https://feeds.apnews.com/apnews/World', 'general', 2),
                RSSFeed('NPR', 'https://feeds.npr.org/1001/rss.xml', 'general', 2),
            ],
            'politics': [
                RSSFeed('Politico', 'https://www.politico.com/rss/politics08.xml', 'politics', 3),
                RSSFeed('Reuters Politics', 'https://feeds.reuters.com/reuters/politicsNews', 'politics', 2),
                RSSFeed('The Hill', 'https://thehill.com/news/feed/', 'politics', 2),
            ],
            'energy': [
                RSSFeed('Oil & Gas Journal', 'https://www.ogj.com/rss.xml', 'business', 2),
                RSSFeed('Energy News', 'https://www.energy-news.co.uk/feed/', 'business', 2),
            ]
        }
    
    def add_feed(self, category: str, feed: RSSFeed) -> None:
        """Add a new RSS feed to a category."""
        if category not in self._feeds:
            self._feeds[category] = []
        self._feeds[category].append(feed)
    
    def get_feeds_by_category(self, category: str) -> List[RSSFeed]:
        """Get all feeds for a specific category."""
        return self._feeds.get(category, [])
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories."""
        return list(self._feeds.keys())
    
    def fetch_from_feed(self, feed: RSSFeed, limit: int = 10) -> List[NewsArticle]:
        """Fetch articles from a single RSS feed."""
        try:
            parsed_feed = feedparser.parse(feed.url)
            
            if not parsed_feed.entries:
                return []
            
            articles = []
            for entry in parsed_feed.entries[:limit]:
                # Parse publication date
                pub_date = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'published') and entry.published:
                    try:
                        pub_date = parser.parse(entry.published).replace(tzinfo=None)
                    except (ValueError, TypeError):
                        pass
                
                articles.append(
                    NewsArticle(
                        title=entry.get('title', 'No title'),
                        description=entry.get('summary', '')[:300] if entry.get('summary') else '',
                        url=entry.get('link', ''),
                        source=feed.name,
                        published_at=pub_date,
                        category=feed.category
                    )
                )
            
            return articles
            
        except Exception:
            return []
    
    def fetch_category_news(self, category: str, limit_per_feed: int = 5) -> Generator[NewsArticle, None, None]:
        """Fetch news from all feeds in a category."""
        feeds = self.get_feeds_by_category(category)
        
        # Sort by priority (higher first)
        feeds.sort(key=lambda f: f.priority, reverse=True)
        
        for feed in feeds:
            articles = self.fetch_from_feed(feed, limit_per_feed)
            yield from articles
    
    def fetch_all_news(self, limit_per_feed: int = 3) -> Generator[NewsArticle, None, None]:
        """Fetch news from all feeds across all categories."""
        for category in self._feeds:
            yield from self.fetch_category_news(category, limit_per_feed)


# Create global RSS manager instance
rss_manager = RSSFeedManager()
