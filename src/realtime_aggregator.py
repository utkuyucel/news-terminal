"""
Real-time news aggregation system for high-frequency trading.
Uses async/await and streaming for sub-second news updates.
"""
import asyncio
import logging
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import time
from dataclasses import dataclass
from threading import Lock, Thread
import aiohttp

from config import DEFAULT_CONFIG
from data.api import NewsArticle, fetch_all_news
from data.rss import rss_manager


@dataclass(frozen=True)
class RealTimeNews:
    """Container for real-time news with streaming metadata."""
    articles: List[NewsArticle]
    last_updated: datetime
    total_sources: int
    categories: Set[str]
    update_frequency: float  # Updates per second
    breaking_news_count: int


class RealTimeCache:
    """Ultra-fast cache for real-time news with streaming updates."""
    
    def __init__(self, cache_duration_seconds: int = 30):
        self.cache_duration = timedelta(seconds=cache_duration_seconds)
        self._cache: Dict[str, tuple] = {}
        self._lock = Lock()
        self._last_fetch_times: Dict[str, float] = {}
        self.min_fetch_interval = 0.5  # 500ms minimum between fetches
    
    def should_fetch(self, key: str) -> bool:
        """Check if we should make a new real-time fetch."""
        with self._lock:
            last_fetch = self._last_fetch_times.get(key, 0)
            return (time.time() - last_fetch) >= self.min_fetch_interval
    
    def get(self, key: str) -> Optional[List[NewsArticle]]:
        """Get cached articles if still valid."""
        with self._lock:
            if key in self._cache:
                articles, timestamp = self._cache[key]
                if datetime.now() - timestamp < self.cache_duration:
                    return articles
        return None
    
    def set(self, key: str, articles: List[NewsArticle]) -> None:
        """Cache articles with timestamp."""
        with self._lock:
            self._cache[key] = (articles, datetime.now())
            self._last_fetch_times[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cached data."""
        with self._lock:
            self._cache.clear()
            self._last_fetch_times.clear()


class RealTimeNewsAggregator:
    """High-frequency real-time news aggregation service."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = RealTimeCache(cache_duration_seconds=30)
        self.executor = ThreadPoolExecutor(max_workers=DEFAULT_CONFIG.news.concurrent_workers)
        self._last_update = datetime.now()
        self._update_count = 0
        self._start_time = time.time()
        self._breaking_news_keywords = [
            'breaking', 'urgent', 'alert', 'flash', 'developing',
            'halt', 'suspend', 'emergency', 'crash', 'surge'
        ]
        
        # Real-time news queue for streaming updates
        self._news_queue = deque(maxlen=1000)
        self._queue_lock = Lock()
        
        # Priority sources for real-time updates
        self._priority_sources = [
            'Bloomberg', 'Reuters', 'Financial Times', 'MarketWatch',
            'Yahoo Finance', 'CNBC', 'Wall Street Journal'
        ]
    
    async def _fetch_async_news(self, session: aiohttp.ClientSession, category: str) -> List[NewsArticle]:
        """Async fetch for real-time performance."""
        try:
            # This would be enhanced with real WebSocket streams in production
            # For now, we'll use rapid async HTTP polling
            articles = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._fetch_sync_news, category
            )
            return articles
        except Exception as e:
            self.logger.error(f"Async fetch error for {category}: {e}")
            return []
    
    def _fetch_sync_news(self, category: str) -> List[NewsArticle]:
        """Synchronous news fetch for executor."""
        try:
            # Combine API and RSS sources
            api_articles = fetch_all_news([category])
            rss_articles = rss_manager.fetch_category_news(category)
            
            all_articles = api_articles + rss_articles
            
            # Filter for real-time relevance
            recent_articles = []
            cutoff_time = datetime.now() - timedelta(hours=2)  # Only very recent news
            
            for article in all_articles:
                if article.published_at > cutoff_time:
                    recent_articles.append(article)
            
            return recent_articles
        except Exception as e:
            self.logger.error(f"Sync fetch error for {category}: {e}")
            return []
    
    def _is_breaking_news(self, article: NewsArticle) -> bool:
        """Identify breaking/urgent news for priority display."""
        title_lower = article.title.lower()
        desc_lower = (article.description or "").lower()
        
        return any(
            keyword in title_lower or keyword in desc_lower
            for keyword in self._breaking_news_keywords
        )
    
    def _is_priority_source(self, article: NewsArticle) -> bool:
        """Check if article is from a priority real-time source."""
        return any(
            priority_source.lower() in article.source.lower()
            for priority_source in self._priority_sources
        )
    
    async def fetch_real_time_news(self, categories: List[str]) -> RealTimeNews:
        """Fetch news with real-time streaming performance."""
        cache_key = f"realtime_news_{'-'.join(sorted(categories))}"
        
        # Check if we should fetch new data
        if not self.cache.should_fetch(cache_key):
            cached_articles = self.cache.get(cache_key)
            if cached_articles:
                self.logger.debug("Returning cached real-time news")
                return self._create_realtime_response(cached_articles)
        
        # Async fetch from multiple sources concurrently
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_async_news(session, category)
                for category in categories
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and process results
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            else:
                self.logger.error(f"Async task failed: {result}")
        
        # Deduplicate and sort by priority
        unique_articles = self._deduplicate_and_prioritize(all_articles)
        
        # Cache the results
        self.cache.set(cache_key, unique_articles)
        
        # Update metrics
        self._update_count += 1
        self._last_update = datetime.now()
        
        return self._create_realtime_response(unique_articles)
    
    def _deduplicate_and_prioritize(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicates and sort by priority for real-time display."""
        seen_titles = set()
        prioritized_articles = []
        breaking_news = []
        priority_news = []
        regular_news = []
        
        for article in articles:
            title_key = article.title.lower().strip()
            if title_key in seen_titles or len(title_key) < 10:
                continue
            
            seen_titles.add(title_key)
            
            # Categorize by priority
            if self._is_breaking_news(article):
                breaking_news.append(article)
            elif self._is_priority_source(article):
                priority_news.append(article)
            else:
                regular_news.append(article)
        
        # Sort each category by recency
        breaking_news.sort(key=lambda x: x.published_at, reverse=True)
        priority_news.sort(key=lambda x: x.published_at, reverse=True)
        regular_news.sort(key=lambda x: x.published_at, reverse=True)
        
        # Combine in priority order
        prioritized_articles = breaking_news + priority_news + regular_news
        
        return prioritized_articles[:DEFAULT_CONFIG.terminal.max_articles_display]
    
    def _create_realtime_response(self, articles: List[NewsArticle]) -> RealTimeNews:
        """Create real-time news response with metrics."""
        elapsed_time = time.time() - self._start_time
        update_frequency = self._update_count / elapsed_time if elapsed_time > 0 else 0
        
        breaking_count = sum(1 for article in articles if self._is_breaking_news(article))
        
        return RealTimeNews(
            articles=articles,
            last_updated=self._last_update,
            total_sources=len(set(article.source for article in articles)),
            categories=set(article.category for article in articles),
            update_frequency=update_frequency,
            breaking_news_count=breaking_count
        )
    
    def start_streaming(self, categories: List[str], callback=None):
        """Start continuous real-time news streaming in background thread."""
        def stream_worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            while True:
                try:
                    news = loop.run_until_complete(
                        self.fetch_real_time_news(categories)
                    )
                    
                    if callback:
                        callback(news)
                    
                    # Add to queue for main thread consumption
                    with self._queue_lock:
                        self._news_queue.append(news)
                    
                    # Sleep for real-time interval
                    time.sleep(DEFAULT_CONFIG.terminal.trading_news_fetch_interval)
                    
                except Exception as e:
                    self.logger.error(f"Streaming error: {e}")
                    time.sleep(1.0)  # Brief pause on error
        
        # Start streaming in background thread
        stream_thread = Thread(target=stream_worker, daemon=True)
        stream_thread.start()
        return stream_thread
    
    def get_latest_from_queue(self) -> Optional[RealTimeNews]:
        """Get the latest news from the streaming queue."""
        with self._queue_lock:
            if self._news_queue:
                return self._news_queue[-1]  # Get most recent
        return None


# Global real-time aggregator instance
realtime_aggregator = RealTimeNewsAggregator()
