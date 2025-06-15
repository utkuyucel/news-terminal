"""
Configuration settings for News Terminal application.
"""
import os
from dataclasses import dataclass
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass(frozen=True)
class APIConfig:
    """Configuration for API endpoints."""
    news_api_key: Optional[str] = os.getenv("NEWS_API_KEY")  # Loaded from .env file
    alpha_vantage_key: Optional[str] = os.getenv("ALPHA_VANTAGE_KEY")  # For financial news
    rate_limit_requests_per_minute: int = 60
    timeout_seconds: int = 10


@dataclass(frozen=True)
class TerminalConfig:
    """Terminal display configuration."""
    refresh_interval: float = 0.1  # REAL-TIME: 100ms refresh for trading
    news_fetch_interval: float = 1.0  # Real-time news every 1 second
    trading_news_fetch_interval: float = 0.5  # Ultra-fast for critical trading sources
    max_articles_display: int = 150  # More articles for high-frequency trading
    flash_on_new_article: bool = True
    show_clock: bool = True
    clock_format: str = "%H:%M:%S"  # Precision clock for trading
    date_format: str = "%Y-%m-%d %H:%M:%S"
    highlight_urgent_keywords: bool = True
    show_market_hours: bool = True


@dataclass(frozen=True)
class NewsConfig:
    """News fetching configuration."""
    max_articles_per_source: int = 20  # More articles for real-time trading
    cache_duration_minutes: int = 1  # Ultra-short cache for real-time updates
    concurrent_workers: int = 12  # More workers for faster real-time fetching
    retry_attempts: int = 2  # Faster retries for real-time
    retry_delay_seconds: float = 0.2  # Minimal retry delay
    real_time_sources: Optional[List[str]] = None  # Priority real-time sources
    trading_keywords: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.trading_keywords is None:
            # Keywords that matter for stock trading
            object.__setattr__(self, 'trading_keywords', [
                'earnings', 'revenue', 'profit', 'loss', 'merger', 'acquisition',
                'ipo', 'buyback', 'dividend', 'guidance', 'forecast', 'outlook',
                'fda approval', 'drug approval', 'clinical trial', 'partnership',
                'deal', 'contract', 'settlement', 'lawsuit', 'investigation',
                'ceo', 'cfo', 'executive', 'resignation', 'appointment',
                'bankruptcy', 'restructuring', 'delisting', 'halt', 'suspend',
                'beat estimates', 'miss estimates', 'raised guidance', 'lowered guidance',
                'upgrade', 'downgrade', 'price target', 'analyst', 'rating'
            ])


@dataclass(frozen=True)
class AppConfig:
    """Main application configuration."""
    api: APIConfig
    terminal: TerminalConfig
    news: NewsConfig


# Default configuration instance
DEFAULT_CONFIG = AppConfig(
    api=APIConfig(),
    terminal=TerminalConfig(),
    news=NewsConfig()
)

# API endpoints
API_ENDPOINTS = {
    'newsapi': 'https://newsapi.org/v2',
    'guardian': 'https://content.guardianapis.com',
    'reddit': 'https://www.reddit.com',
    'hackernews': 'https://hacker-news.firebaseio.com/v0'
}

# Categories for news filtering
NEWS_CATEGORIES = [
    'general',
    'business',
    'technology',
    'science',
    'health',
    'sports',
    'entertainment'
]

# RSS Feed categories
RSS_CATEGORIES = {
    'financial': ['bloomberg', 'reuters', 'wsj', 'ft'],
    'technology': ['techcrunch', 'verge', 'ars'],
    'general': ['bbc', 'cnn', 'reuters'],
    'crypto': ['coindesk', 'cointelegraph'],
    'politics': ['politico', 'axios']
}