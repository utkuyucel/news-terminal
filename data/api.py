"""
API handlers for fetching news from various sources.
"""
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Generator, List, Optional, Dict, Any

import requests
from dateutil import parser


@dataclass(frozen=True)
class NewsArticle:
    """Immutable news article data structure."""
    title: str
    description: str
    url: str
    source: str
    published_at: datetime
    category: str = 'general'
    
    @property
    def formatted_time(self) -> str:
        """Format publication time for display."""
        return self.published_at.strftime("%H:%M")


class APIClient(ABC):
    """Abstract base class for API clients."""
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
    
    @abstractmethod
    def fetch_news(self, category: str = 'general', limit: int = 10) -> List[NewsArticle]:
        """Fetch news articles from the API."""
        pass
    
    def _make_request(self, url: str, params: Optional[dict] = None) -> Optional[dict]:
        """Make HTTP request with error handling."""
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None


class NewsAPIClient(APIClient):
    """Client for NewsAPI.org - requires free API key."""
    
    BASE_URL = 'https://newsapi.org/v2'
    
    def __init__(self, api_key: str, timeout: int = 10):
        super().__init__(api_key, timeout)
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    def fetch_news(self, category: str = 'general', limit: int = 10) -> List[NewsArticle]:
        """Fetch top headlines from NewsAPI."""
        if not self.api_key:
            return []
        
        params = {
            'category': category,
            'language': 'en',
            'pageSize': min(limit, 100)
        }
        
        data = self._make_request(f"{self.BASE_URL}/top-headlines", params)
        if not data or 'articles' not in data:
            return []
        
        return [
            NewsArticle(
                title=article['title'] or 'No title',
                description=article['description'] or '',
                url=article['url'] or '',
                source=article['source']['name'] if article.get('source') else 'NewsAPI',
                published_at=parser.parse(article['publishedAt']).replace(tzinfo=None) if article.get('publishedAt') else datetime.now(),
                category=category
            )
            for article in data['articles']
            if article.get('title') and article.get('title') != '[Removed]'
        ]


class HackerNewsClient(APIClient):
    """Client for Hacker News API - free, no key required."""
    
    BASE_URL = 'https://hacker-news.firebaseio.com/v0'
    
    def fetch_news(self, category: str = 'technology', limit: int = 10) -> List[NewsArticle]:
        """Fetch top stories from Hacker News."""
        # Get top story IDs
        story_ids = self._make_request(f"{self.BASE_URL}/topstories.json")
        if not story_ids:
            return []
        
        articles = []
        for story_id in story_ids[:limit]:
            story = self._make_request(f"{self.BASE_URL}/item/{story_id}.json")
            if story and story.get('type') == 'story' and story.get('url'):
                articles.append(
                    NewsArticle(
                        title=story.get('title', 'No title'),
                        description=story.get('text', '')[:200] if story.get('text') else '',
                        url=story.get('url', ''),
                        source='Hacker News',
                        published_at=datetime.fromtimestamp(story.get('time', time.time())),
                        category=category
                    )
                )
        
        return articles


class RedditNewsClient(APIClient):
    """Client for Reddit API - free, no key required."""
    
    BASE_URL = 'https://www.reddit.com'
    
    def fetch_news(self, category: str = 'general', limit: int = 10) -> List[NewsArticle]:
        """Fetch top posts from news subreddits."""
        subreddit_map = {
            'general': 'news',
            'technology': 'technology',
            'business': 'business',
            'science': 'science',
            'politics': 'politics'
        }
        
        subreddit = subreddit_map.get(category, 'news')
        data = self._make_request(f"{self.BASE_URL}/r/{subreddit}/hot.json", {'limit': limit})
        
        if not data or 'data' not in data:
            return []
        
        articles = []
        for post in data['data']['children']:
            post_data = post['data']
            if not post_data.get('is_self') and post_data.get('url'):
                articles.append(
                    NewsArticle(
                        title=post_data.get('title', 'No title'),
                        description=post_data.get('selftext', '')[:200] if post_data.get('selftext') else '',
                        url=post_data.get('url', ''),
                        source=f"r/{subreddit}",
                        published_at=datetime.fromtimestamp(post_data.get('created_utc', time.time())),
                        category=category
                    )
                )
        
        return articles


class GuardianAPIClient(APIClient):
    """Client for Guardian API - free, but requires API key."""
    
    BASE_URL = 'https://content.guardianapis.com'
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        super().__init__(api_key, timeout)
    
    def fetch_news(self, category: str = 'general', limit: int = 10) -> List[NewsArticle]:
        """Fetch articles from Guardian API."""
        # Guardian has free tier without API key for basic search
        params = {
            'q': self._get_search_term(category),
            'page-size': min(limit, 50),
            'show-fields': 'headline,standfirst,webUrl',
            'order-by': 'newest'
        }
        
        if self.api_key:
            params['api-key'] = self.api_key
        
        data = self._make_request(f"{self.BASE_URL}/search", params)
        if not data or 'response' not in data:
            return []
        
        articles = []
        for item in data['response'].get('results', []):
            articles.append(
                NewsArticle(
                    title=item.get('webTitle', 'No title'),
                    description=item.get('fields', {}).get('standfirst', '') or '',
                    url=item.get('webUrl', ''),
                    source='The Guardian',
                    published_at=parser.parse(item['webPublicationDate']).replace(tzinfo=None) if item.get('webPublicationDate') else datetime.now(),
                    category=category
                )
            )
        
        return articles
    
    @staticmethod
    def _get_search_term(category: str) -> str:
        """Map category to Guardian search term."""
        mapping = {
            'business': 'business finance',
            'technology': 'technology',
            'science': 'science',
            'politics': 'politics',
            'general': 'news'
        }
        return mapping.get(category, 'news')


@lru_cache(maxsize=128)
def get_api_clients(news_api_key: Optional[str] = None, 
                   guardian_api_key: Optional[str] = None) -> List[APIClient]:
    """Get configured API clients."""
    clients = [
        HackerNewsClient(),
        RedditNewsClient()
    ]
    
    if news_api_key:
        clients.append(NewsAPIClient(news_api_key))
    
    if guardian_api_key:
        clients.append(GuardianAPIClient(guardian_api_key))
    
    return clients


def fetch_all_news(category: str = 'general', 
                  limit_per_source: int = 5,
                  api_keys: Optional[dict] = None) -> Generator[NewsArticle, None, None]:
    """Fetch news from all available sources."""
    api_keys = api_keys or {}
    clients = get_api_clients(
        news_api_key=api_keys.get('newsapi'),
        guardian_api_key=api_keys.get('guardian')
    )
    
    for client in clients:
        try:
            articles = client.fetch_news(category, limit_per_source)
            yield from articles
        except Exception:
            # Skip failed sources silently
            continue
