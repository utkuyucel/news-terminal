"""
Core news aggregation system that combines API and RSS sources.
"""
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

from config import DEFAULT_CONFIG
from data.api import NewsArticle, fetch_all_news
from data.rss import rss_manager


@dataclass(frozen=True)
class AggregatedNews:
    """Container for aggregated news with metadata."""
    articles: List[NewsArticle]
    last_updated: datetime
    total_sources: int
    categories: Set[str]


class NewsCache:
    """Enhanced in-memory cache for news articles with better invalidation."""
    
    def __init__(self, cache_duration_minutes: int = 5):
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self._cache: Dict[str, Tuple[List[NewsArticle], datetime]] = {}
        self._last_api_call: Dict[str, datetime] = {}
        self.min_call_interval = timedelta(seconds=10)  # Minimum 10 seconds between API calls
    
    def should_fetch(self, key: str) -> bool:
        """Check if we should make a new API call."""
        if key not in self._last_api_call:
            return True
        return datetime.now() - self._last_api_call[key] > self.min_call_interval
    
    def get(self, key: str) -> List[NewsArticle]:
        """Get cached articles if still valid."""
        if key in self._cache:
            articles, timestamp = self._cache[key]
            if datetime.now() - timestamp < self.cache_duration:
                return articles
        return []
    
    def set(self, key: str, articles: List[NewsArticle]) -> None:
        """Cache articles with timestamp."""
        self._cache[key] = (articles, datetime.now())
        self._last_api_call[key] = datetime.now()
    
    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._last_api_call.clear()


class NewsAggregator:
    """Main news aggregation service."""
    
    def __init__(self):
        self.cache = NewsCache(DEFAULT_CONFIG.news.cache_duration_minutes)
        self.executor = ThreadPoolExecutor(max_workers=DEFAULT_CONFIG.news.concurrent_workers)
        self._last_update = datetime.min
        self._current_articles: List[NewsArticle] = []
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _fetch_api_news(self, category: str = 'general') -> List[NewsArticle]:
        """Fetch news from API sources."""
        api_keys = {
            'newsapi': DEFAULT_CONFIG.api.news_api_key,
        }
        
        articles = list(fetch_all_news(
            category=category,
            limit_per_source=DEFAULT_CONFIG.news.max_articles_per_source,
            api_keys=api_keys
        ))
        
        self.logger.debug(f"Fetched {len(articles)} articles from API sources")
        return articles
    
    def _fetch_rss_news(self, category: str = 'general') -> List[NewsArticle]:
        """Fetch news from RSS sources."""
        if category == 'general':
            articles = list(rss_manager.fetch_all_news(
                limit_per_feed=DEFAULT_CONFIG.news.max_articles_per_source
            ))
        else:
            articles = list(rss_manager.fetch_category_news(
                category, DEFAULT_CONFIG.news.max_articles_per_source
            ))
        
        self.logger.debug(f"Fetched {len(articles)} articles from RSS sources")
        return articles
    
    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity."""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            # Simple deduplication by title (could be enhanced with fuzzy matching)
            title_key = article.title.lower().strip()
            if title_key not in seen_titles and len(title_key) > 10:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
    
    def fetch_news_concurrent(self, categories: List[str] | None = None) -> AggregatedNews:
        """Fetch news from all sources concurrently with intelligent caching."""
        if categories is None:
            categories = ['general', 'technology', 'business']
        
        # Check cache first and whether we should fetch new data
        cache_key = f"news_{'-'.join(sorted(categories))}"
        cached_articles = self.cache.get(cache_key)
        
        # If we have cached data and shouldn't fetch yet, return cached data
        if cached_articles and not self.cache.should_fetch(cache_key):
            self.logger.debug("Returning cached news (rate limited)")
            return AggregatedNews(
                articles=cached_articles,
                last_updated=self._last_update,
                total_sources=len(set(article.source for article in cached_articles)),
                categories=set(article.category for article in cached_articles)
            )
        
        # If cache is fresh enough, use it
        if cached_articles:
            self.logger.debug("Returning cached news")
            return AggregatedNews(
                articles=cached_articles,
                last_updated=self._last_update,
                total_sources=len(set(article.source for article in cached_articles)),
                categories=set(article.category for article in cached_articles)
            )
        
        all_articles = []
        sources_count = 0
        
        # Submit concurrent tasks for each category and source type
        futures = []
        
        for category in categories:
            # API sources
            futures.append(
                self.executor.submit(self._fetch_api_news, category)
            )
            # RSS sources  
            futures.append(
                self.executor.submit(self._fetch_rss_news, category)
            )
        
        # Collect results as they complete
        for future in as_completed(futures, timeout=DEFAULT_CONFIG.api.timeout_seconds * 2):
            try:
                articles = future.result(timeout=5)
                all_articles.extend(articles)
                sources_count += 1
            except Exception as e:
                self.logger.error(f"Failed to fetch from source: {e}")
                continue
        
        # Remove duplicates and sort
        unique_articles = self._deduplicate_articles(all_articles)
        unique_articles.sort(key=lambda x: x.published_at, reverse=True)
        
        # Limit total articles
        final_articles = unique_articles[:DEFAULT_CONFIG.terminal.max_articles_display]
        
        # Cache results
        self.cache.set(cache_key, final_articles)
        self._last_update = datetime.now()
        self._current_articles = final_articles
        
        self.logger.debug(f"Aggregated {len(final_articles)} unique articles from {sources_count} sources")
        
        return AggregatedNews(
            articles=final_articles,
            last_updated=self._last_update,
            total_sources=len(set(article.source for article in final_articles)),
            categories=set(article.category for article in final_articles)
        )
    
    def get_articles_by_category(self, category: str) -> List[NewsArticle]:
        """Get current articles filtered by category."""
        return [
            article for article in self._current_articles
            if article.category.lower() == category.lower()
        ]
    
    def search_articles(self, query: str) -> List[NewsArticle]:
        """Search current articles by query."""
        query_lower = query.lower()
        return [
            article for article in self._current_articles
            if query_lower in article.title.lower() or 
               query_lower in article.description.lower()
        ]
    
    def get_top_sources(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top news sources by article count."""
        source_counts: Dict[str, int] = defaultdict(int)
        for article in self._current_articles:
            source_counts[article.source] += 1
        
        return sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def refresh_cache(self) -> None:
        """Force refresh the news cache."""
        self.cache.clear()
        self.logger.debug("News cache cleared")
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# Global aggregator instance
news_aggregator = NewsAggregator()
