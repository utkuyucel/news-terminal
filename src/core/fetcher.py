"""RSS feed fetcher with concurrent processing."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Generator, Optional
from functools import lru_cache

import feedparser
import requests
from dateutil import parser as date_parser
from tzlocal import get_localzone

from src.core.models import Article
from data.rss import RSSSource
from config import DEFAULT_CONFIG


logger = logging.getLogger(__name__)


class FeedFetcher:
    """Handles RSS feed fetching and parsing."""
    
    def __init__(self, timeout: Optional[int] = None, max_workers: Optional[int] = None):
        self.timeout = timeout or DEFAULT_CONFIG.request_timeout
        self.max_workers = max_workers or DEFAULT_CONFIG.concurrent_feeds
        
    def fetch_source(self, source: RSSSource) -> List[Article]:
        """Fetch articles from a single RSS source."""
        try:
            response = requests.get(
                source.url, 
                timeout=self.timeout,
                headers={'User-Agent': 'NewsTerminal/1.0'}
            )
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            articles = []
            for entry in feed.entries[:DEFAULT_CONFIG.ui.max_articles_per_source]:
                article = self._parse_entry(entry, source)
                if article:
                    articles.append(article)
            return articles
            
        except Exception as e:
            logger.warning(f"Failed to fetch {source.name}: {e}")
            return []
    
    def _parse_entry(self, entry, source: RSSSource) -> Optional[Article]:
        """Parse RSS entry into Article object."""
        try:
            # Parse publication date
            published = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'published'):
                try:
                    published = date_parser.parse(entry.published)
                except Exception:
                    pass
            # Convert to local timezone if not already tz-aware
            local_tz = get_localzone()
            if published.tzinfo is None:
                published = published.replace(tzinfo=local_tz)
            else:
                published = published.astimezone(local_tz)
            return Article(
                title=entry.get('title', 'No title').strip(),
                link=entry.get('link', ''),
                published=published,
                source=source.name,
                summary=entry.get('summary', ''),
                author=entry.get('author'),
                category=source.category
            )
        except Exception as e:
            logger.debug(f"Failed to parse entry from {source.name}: {e}")
            return None
    
    def fetch_all_sources(self, sources: List[RSSSource]) -> Generator[Article, None, None]:
        """Fetch articles from all sources concurrently."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_source = {
                executor.submit(self.fetch_source, source): source 
                for source in sources
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    articles = future.result()
                    yield from articles
                except Exception as e:
                    logger.error(f"Error processing {source.name}: {e}")


@lru_cache(maxsize=1)
def get_feed_fetcher() -> FeedFetcher:
    """Get cached feed fetcher instance."""
    return FeedFetcher()
