import asyncio
import calendar
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Tuple
import requests
from dateutil.parser import parse

import feedparser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.layout import Layout

console = Console()
REFRESH_INTERVAL = 30  # seconds
MAX_TITLE_LENGTH = 80
MAX_ITEMS_DISPLAY = 30
_seen_hashes = set()
TARGET_TZ = timezone(timedelta(hours=3))

@dataclass(frozen=True)
class NewsSource:
    name: str
    url: str

@dataclass(frozen=True)
class NewsTopic:
    name: str
    sources: List[NewsSource]

TOPICS: List[NewsTopic] = [
    NewsTopic(
        "Middle East",
        [
            NewsSource("Al Jazeera English", "https://www.aljazeera.com/xml/rss/all.xml"),
            NewsSource("BBC Middle East", "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml"),
            NewsSource("The New Arab", "https://www.newarab.com/rss.xml"),
            NewsSource("Jerusalem Post", "https://www.jpost.com//rss/rssfeedsfrontpage.aspx"),
        ],
    ),
]

def _hash_entry(entry: feedparser.FeedParserDict) -> str:
    return hashlib.md5((entry.get("title", "") + entry.get("link", "")).encode()).hexdigest()

def _parse_datetime(entry: feedparser.FeedParserDict) -> datetime:
    """Parse datetime from RSS entry and convert to local timezone."""
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        dt = datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)
    else:
        # Try parsing the published string as fallback
        published_str = entry.get("published") or entry.get("updated")
        if published_str:
            try:
                dt = parse(published_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
            except Exception:
                dt = datetime.now(tz=timezone.utc)
        else:
            dt = datetime.now(tz=timezone.utc)
    return dt.astimezone(TARGET_TZ)

def _is_valid_news_time(dt: datetime) -> bool:
    """Filter out future dates that are clearly invalid."""
    now = datetime.now(TARGET_TZ)
    max_future = now + timedelta(hours=1)
    min_past = now - timedelta(days=30)
    return min_past <= dt <= max_future

def _format_time(dt: datetime) -> str:
    """Format datetime in a clean, readable format."""
    return dt.strftime("%m/%d %H:%M")

def _truncate_title(title: str) -> str:
    """Truncate title to fit display while preserving readability."""
    if len(title) <= MAX_TITLE_LENGTH:
        return title
    return title[:MAX_TITLE_LENGTH-3] + "..."

def _create_header(topic_name: str) -> Panel:
    """Create a beautiful header panel."""
    current_time = datetime.now(TARGET_TZ).strftime("%Y-%m-%d %H:%M:%S UTC+3")
    header_text = Text()
    header_text.append("📰 ", style="bold yellow")
    header_text.append(f"Live {topic_name} News", style="bold cyan")
    header_text.append("\n")
    header_text.append(f"🕒 {current_time}", style="dim white")
    
    return Panel(
        Align.center(header_text),
        style="bold blue",
        border_style="cyan",
        padding=(1, 2)
    )

def _create_news_table(articles: List[Tuple[datetime, str, str]]) -> Table:
    """Create a styled news table."""
    table = Table(show_header=True, header_style="bold magenta", border_style="dim white")
    table.add_column("🕒 Time", style="cyan", width=12, no_wrap=True)
    table.add_column("📰 Title", style="white", min_width=50)
    table.add_column("📺 Source", style="green", width=20, no_wrap=True)
    
    # Sort by time (newest first) and limit display
    sorted_articles = sorted(articles, key=lambda x: x[0], reverse=True)[:MAX_ITEMS_DISPLAY]
    
    for dt, title, source in sorted_articles:
        time_str = _format_time(dt)
        truncated_title = _truncate_title(title)
        
        # Add some visual flair based on recency
        now = datetime.now(TARGET_TZ)
        age = now - dt
        if age < timedelta(minutes=30):
            time_style = "bold red"  # Very recent
            title_style = "bold white"
        elif age < timedelta(hours=2):
            time_style = "bold yellow"  # Recent
            title_style = "white"
        else:
            time_style = "cyan"  # Older
            title_style = "dim white"
        
        table.add_row(
            Text(time_str, style=time_style),
            Text(truncated_title, style=title_style),
            Text(source, style="green")
        )
    
    return table

async def _fetch_feed(source: NewsSource) -> Tuple[feedparser.FeedParserDict, NewsSource]:
    """Fetch a single RSS feed."""
    try:
        response = await asyncio.to_thread(requests.get, source.url, timeout=10)
        response.raise_for_status()
        result = await asyncio.to_thread(feedparser.parse, response.content)
        return result, source
    except Exception as e:
        console.print(f"[red]Error fetching {source.name}: {e}[/red]")
        return feedparser.FeedParserDict(), source

async def _gather_feeds(sources: List[NewsSource]) -> List[Tuple[feedparser.FeedParserDict, NewsSource]]:
    """Gather all feeds concurrently."""
    tasks = [_fetch_feed(src) for src in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    valid = []
    for res in results:
        if isinstance(res, Exception):
            console.print(f"[red]Error gathering feeds:[/red] {res}")
        else:
            valid.append(res)
    return valid

def _create_layout(topic: NewsTopic, articles: List[Tuple[datetime, str, str]]) -> Layout:
    """Create the main layout with header and news table."""
    layout = Layout()
    
    layout.split_column(
        Layout(_create_header(topic.name), name="header", size=5),
        Layout(_create_news_table(articles), name="main")
    )
    
    return layout

async def _stream_topic(topic: NewsTopic) -> None:
    """Stream news for a specific topic with live updates."""
    articles = []
    
    # Initial load
    console.print("[yellow]Loading news feeds...[/yellow]")
    
    with Live(_create_layout(topic, articles), refresh_per_second=1, screen=True) as live:
        while True:
            try:
                feeds = await _gather_feeds(topic.sources)
                new_items = []
                
                for feed, src in feeds:
                    for entry in feed.entries:
                        key = _hash_entry(entry)
                        if key not in _seen_hashes:
                            _seen_hashes.add(key)
                            dt = _parse_datetime(entry)
                            
                            # Only add if it's a valid time
                            if _is_valid_news_time(dt):
                                title = entry.get("title", "No Title")
                                new_items.append((dt, title, src.name))
                
                # Add new items to our collection
                if new_items:
                    articles.extend(new_items)
                    console.bell()  # Audio notification for new articles
                
                # Update the display
                live.update(_create_layout(topic, articles))
                
                # Clean up old articles to prevent memory bloat
                if len(articles) > MAX_ITEMS_DISPLAY * 3:
                    articles = sorted(articles, key=lambda x: x[0], reverse=True)[:MAX_ITEMS_DISPLAY * 2]
                
                await asyncio.sleep(REFRESH_INTERVAL)
                
            except Exception as e:
                console.print(f"[red]Error in news stream: {e}[/red]")
                await asyncio.sleep(5)  # Wait a bit before retrying

def _select_topic() -> NewsTopic:
    """Allow user to select a news topic."""
    console.print("\n[bold yellow]📰 News Terminal[/bold yellow]")
    console.print("[dim]Select a news topic to follow:[/dim]\n")
    
    for idx, topic in enumerate(TOPICS, start=1):
        console.print(f"  [cyan]{idx}.[/cyan] {topic.name}")
    
    console.print()
    try:
        choice = int(console.input("[bold]Enter topic number: [/bold]")) - 1
        if 0 <= choice < len(TOPICS):
            return TOPICS[choice]
        else:
            console.print("[red]Invalid selection.[/red]")
            raise SystemExit(1)
    except (ValueError, KeyboardInterrupt):
        console.print("[red]Invalid selection or interrupted.[/red]")
        raise SystemExit(1)

def main() -> None:
    """Main entry point."""
    try:
        topic = _select_topic()
        console.clear()
        console.print(f"[green]Starting live feed for {topic.name}...[/green]")
        console.print("[dim]Press Ctrl+C to exit[/dim]\n")
        
        asyncio.run(_stream_topic(topic))
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Thanks for using News Terminal![/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise SystemExit(1)

if __name__ == "__main__":
    main()

