"""RSS feed sources for the news terminal."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RSSSource:
    """RSS feed source configuration."""
    name: str
    url: str
    category: str = "general"
    priority: int = 1


# Major news sources with reliable RSS feeds
RSS_SOURCES: List[RSSSource] = [
    # Economic/Financial News
    RSSSource("Reuters Business", "https://feeds.reuters.com/reuters/businessNews", "economic", 1),
    RSSSource("Financial Times", "https://www.ft.com/rss/home", "economic", 1),
    RSSSource("MarketWatch", "https://feeds.marketwatch.com/marketwatch/topstories/", "economic", 1),
    RSSSource("Yahoo Finance", "https://feeds.finance.yahoo.com/rss/2.0/headline", "economic", 1),
    RSSSource("Bloomberg", "https://feeds.bloomberg.com/markets/news.rss", "economic", 1),
    RSSSource("Wall Street Journal", "https://feeds.a.dj.com/rss/RSSWorldNews.xml", "economic", 1),
    RSSSource("CNBC Markets", "https://www.cnbc.com/id/100003114/device/rss/rss.html", "economic", 1),
    
    # Middle East News - Comprehensive Coverage
    RSSSource("BBC Middle East", "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml", "middle_east", 1),
    RSSSource("CNN Middle East", "http://rss.cnn.com/rss/edition_meast.rss", "middle_east", 1),
    RSSSource("Al Jazeera English", "https://www.aljazeera.com/xml/rss/all.xml", "middle_east", 1),
    RSSSource("Jerusalem Post Breaking", "https://www.jpost.com/rss/rssfeedsheadlines.aspx", "middle_east", 1),
    RSSSource("Jerusalem Post All News", "https://www.jpost.com/rss/rssallnews", "middle_east", 2),
    RSSSource("France 24 Middle East", "https://www.france24.com/en/middle-east/rss", "middle_east", 1),
    RSSSource("Gulf News Latest", "https://gulfnews.com/latest-news", "middle_east", 2),
    RSSSource("NY Times Middle East", "https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml", "middle_east", 1),
    RSSSource("Deutsche Welle World", "https://rss.dw.com/rdf/rss-en-world", "middle_east", 2),
    RSSSource("Voice of America ME", "https://www.voanews.com/api/zrbopl-vomx-tpeovm_", "middle_east", 2),
    
    # Technology News
    RSSSource("TechCrunch", "https://techcrunch.com/feed/", "technology", 1),
    RSSSource("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", "technology", 1),
    RSSSource("The Verge", "https://www.theverge.com/rss/index.xml", "technology", 1),
    RSSSource("Wired", "https://www.wired.com/feed/rss", "technology", 1),
    RSSSource("MIT Technology Review", "https://www.technologyreview.com/feed/", "technology", 2),
    
    # General/Breaking News
    RSSSource("BBC News", "https://feeds.bbci.co.uk/news/rss.xml", "breaking", 1),
    RSSSource("CNN Breaking", "http://rss.cnn.com/rss/edition.rss", "breaking", 1),
    RSSSource("Reuters Breaking", "https://feeds.reuters.com/Reuters/worldNews", "breaking", 1),
    RSSSource("AP Breaking News", "https://feeds.apnews.com/apnews/general", "breaking", 1),
    
    # Politics/Government
    RSSSource("Politico", "https://www.politico.com/rss/politicopicks.xml", "politics", 2),
    RSSSource("The Hill", "https://thehill.com/rss/syndicator/19109", "politics", 2),
    RSSSource("Guardian Politics", "https://www.theguardian.com/politics/rss", "politics", 2),
    
    # Cryptocurrency/Digital Assets
    RSSSource("CoinDesk", "https://feeds.coindesk.com/coindesk/news", "crypto", 2),
    RSSSource("Cointelegraph", "https://cointelegraph.com/rss", "crypto", 2),
    
    # Energy/Commodities
    RSSSource("Oil Price", "https://oilprice.com/rss/main", "energy", 2),
    RSSSource("Energy News", "https://www.energyvoice.com/feed/", "energy", 2),
]


TOPIC_CATEGORIES = {
    "economic": "📈 Economic & Markets",
    "middle_east": "🌍 Middle East",
    "technology": "💻 Technology",
    "breaking": "🚨 Breaking News",
    "politics": "🏛️ Politics",
    "crypto": "₿ Cryptocurrency",
    "energy": "⚡ Energy & Commodities"
}


def get_sources_by_category(category: str) -> List[RSSSource]:
    """Get RSS sources filtered by category."""
    return [source for source in RSS_SOURCES if source.category == category]


def get_priority_sources(max_priority: int = 1) -> List[RSSSource]:
    """Get RSS sources filtered by priority level."""
    return [source for source in RSS_SOURCES if source.priority <= max_priority]


def get_topics() -> List[str]:
    """Get all available topic categories."""
    return list(TOPIC_CATEGORIES.keys())


def get_topic_display_name(topic: str) -> str:
    """Get display name for a topic."""
    return TOPIC_CATEGORIES.get(topic, topic.title())