"""Real-time streaming news terminal for trading."""

import time
from datetime import datetime
from typing import List, Deque
from collections import deque
from tzlocal import get_localzone

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

from src.core.models import Article
from data.rss import get_topic_display_name
from config import DEFAULT_CONFIG


class StreamingNewsTerminal:
    """Streaming news terminal with latest news at bottom."""
    
    def __init__(self, topic: str, max_articles: int = 50):
        self.console = Console()
        self.topic = topic
        self.max_articles = max_articles
        self.articles: Deque[Article] = deque(maxlen=max_articles)
        self.layout = Layout()
        
        # Enhanced flash and animation system
        self.flash_count = 0
        self.animation_frame = 0
        self.last_article_count = 0
        self.new_article_positions: set[int] = set()  # Track positions of new articles
        self.pulse_intensity = 0
        
        # Performance optimizations
        self._cached_sidebar: Panel | None = None
        self._sidebar_cache_time: float = 0
        self._sidebar_cache_duration = 1.0  # Cache sidebar for 1 second
        
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup the streaming terminal layout."""
        self.layout.split_column(
            Layout(name="header", size=5),
            Layout(name="news_stream", ratio=1),
            Layout(name="footer", size=3)
        )
        
        self.layout["news_stream"].split_row(
            Layout(name="articles", ratio=4),
            Layout(name="sidebar", ratio=1)
        )
    
    def add_article(self, article: Article):
        """Add new article to the stream."""
        self.articles.append(article)
        self.flash_count = 3  # Flash for 3 refresh cycles
    
    def add_articles(self, new_articles: List[Article]):
        """Add multiple new articles maintaining chronological order."""
        if not new_articles:
            return
            
        added_count = 0
        current_titles = {article.title for article in self.articles}
        
        # Collect all articles (existing + new) for proper sorting
        all_articles = list(self.articles)
        
        # Add new articles that aren't duplicates
        for article in new_articles:
            if article.title not in current_titles:
                all_articles.append(article)
                current_titles.add(article.title)
                added_count += 1
        
        # Sort all articles by publication time (oldest first)
        all_articles.sort(key=lambda x: x.published)
        
        # Rebuild the deque with sorted articles (keep only the most recent ones)
        self.articles.clear()
        recent_articles = all_articles[-self.max_articles:]
        
        for i, article in enumerate(recent_articles):
            self.articles.append(article)
            # Mark recently added articles for highlighting
            if i >= len(recent_articles) - added_count:
                self.new_article_positions.add(i)
        
        # Enhanced flash effect for new articles
        if added_count > 0:
            self.flash_count = DEFAULT_CONFIG.ui.flash_duration
            self.pulse_intensity = min(10, added_count * 2)
            self.animation_frame = 0
    
    def _create_header(self) -> Panel:
        """Create header with ultra-smooth flash effects."""
        topic_display = get_topic_display_name(self.topic)
        
        header_text = Text()
        
        # Ultra-smooth multi-stage flash effects
        if self.flash_count > 0:
            # Calculate flash intensity (0-1)
            intensity = self.flash_count / DEFAULT_CONFIG.ui.flash_duration
            
            if intensity > 0.8:  # Intense flash phase
                header_text.append("🚨 BREAKING • LIVE UPDATES 🚨", 
                                 style="bold red on bright_yellow blink")
                style = "bright_red"
            elif intensity > 0.6:  # Strong flash phase
                header_text.append("🔥 NEW MARKET DEVELOPMENTS", 
                                 style="bold yellow on bright_blue")
                style = "bright_yellow"
            elif intensity > 0.4:  # Medium flash phase
                header_text.append("📈 FRESH TRADING NEWS", 
                                 style="bold green on bright_cyan")
                style = "bright_green"
            elif intensity > 0.2:  # Fade phase
                header_text.append("✅ Stream Updated Successfully", 
                                 style="bold cyan")
                style = "bright_cyan"
            else:  # Final fade
                header_text.append("💹 Real-Time Feed Active", 
                                 style="bold white")
                style = "white"
            
            header_text.append("\n")
            header_text.append(f"🎯 {topic_display} • LIVE STREAMING", style="bold white")
        else:
            # Normal state with subtle animation
            pulse = "bright_cyan" if self.animation_frame % 40 < 20 else "cyan"
            header_text.append("📰 TRADING NEWS TERMINAL", style=f"bold {pulse}")
            header_text.append(" • ", style="dim")
            header_text.append(topic_display, style="bold green")
            header_text.append("\n")
            header_text.append("⚡ Real-time 20 FPS streaming • Latest news at bottom", 
                             style="dim italic")
            style = "bright_blue"
        
        return Panel(
            Align.center(header_text),
            style=style,
            padding=(0, 1)
        )
    
    def _create_sidebar(self) -> Panel:
        """Create sidebar with optimized clock and enhanced stats."""
        current_time = time.time()
        
        # Cache sidebar for performance (updates every second)
        if (self._cached_sidebar and 
            current_time - self._sidebar_cache_time < self._sidebar_cache_duration):
            return self._cached_sidebar
        
        # Get timezone-aware current time
        local_tz = get_localzone()
        now = datetime.now(local_tz)
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        timezone_str = now.strftime("%Z")  # Get timezone abbreviation
        
        sidebar_content = Text()
        
        # Enhanced clock with millisecond precision for ultra-smooth feel
        microseconds = now.microsecond // 100000  # Get first digit of microseconds
        sidebar_content.append("🕐 LIVE CLOCK\n", style="bold yellow")
        sidebar_content.append(f"{time_str}.{microseconds} {timezone_str}\n", style="bold white")
        sidebar_content.append(f"{date_str}\n\n", style="dim")
        
        # Enhanced stream info
        sidebar_content.append("📊 STREAM INFO\n", style="bold cyan")
        sidebar_content.append(f"Articles: {len(self.articles)}\n", style="white")
        sidebar_content.append(f"Topic: {self.topic}\n", style="white")
        sidebar_content.append(f"Max: {self.max_articles}\n", style="dim")
        sidebar_content.append("FPS: 20 (Real-time)\n", style="green")
        
        # Real-time flash indicators
        if self.flash_count > 0:
            intensity = self.flash_count / DEFAULT_CONFIG.ui.flash_duration
            if intensity > 0.7:
                sidebar_content.append("\n🚨 BREAKING!", style="bold red blink")
            elif intensity > 0.4:
                sidebar_content.append("\n🔥 NEW DATA!", style="bold yellow")
            else:
                sidebar_content.append("\n✅ Updated", style="bold green")
        
        # Performance indicator
        if self.animation_frame % 20 < 10:
            sidebar_content.append(f"\n⚡ Frame: {self.animation_frame}", style="dim")
        
        panel_style = "yellow" if self.flash_count > 0 else "cyan"
        
        sidebar = Panel(
            sidebar_content,
            title="Live Info",
            style=panel_style,
            padding=(0, 1)
        )
        
        # Cache the sidebar
        self._cached_sidebar = sidebar
        self._sidebar_cache_time = current_time
        
        return sidebar
    
    def _create_news_stream(self) -> Panel:
        """Create the main news stream with ultra-smooth visual effects."""
        if not self.articles:
            content = Text("⏳ Initializing real-time stream...", style="dim italic")
            return Panel(
                Align.center(content),
                title=f"📺 {get_topic_display_name(self.topic)} • Live Stream",
                style="bright_white"
            )
        
        # Create ultra-smooth scrolling news list (latest at bottom)
        news_text = Text()
        
        for i, article in enumerate(self.articles):
            # Show date and time for articles from previous days, time only for today
            now = datetime.now(get_localzone())
            if article.published.date() == now.date():
                time_str = article.published.strftime("[%H:%M:%S]")
            else:
                time_str = article.published.strftime("[%m/%d %H:%M]")
            
            # Enhanced highlighting system
            is_new = i in self.new_article_positions
            is_recent = i >= len(self.articles) - 5  # Last 5 articles
            is_latest = i >= len(self.articles) - 2  # Latest 2 articles
            
            # Dynamic styling based on position and newness
            if is_new and self.flash_count > 0:
                # Ultra-bright highlighting for brand new articles
                time_style = "bold red on bright_yellow"
                source_style = "bold black on bright_cyan"
                title_style = "bold black on bright_white"
            elif is_latest:
                # Latest articles - very prominent
                time_style = "bold bright_green"
                source_style = "bold bright_yellow"
                title_style = "bold bright_white"
            elif is_recent:
                # Recent articles - highlighted
                time_style = "bold green"
                source_style = "bold yellow"
                title_style = "bold white"
            else:
                # Standard articles
                time_style = "cyan"
                source_style = "yellow"
                title_style = "white"
            
            # Format with enhanced visual separation  
            news_text.append(f"{time_str} ", style=time_style)
            
            # Truncate source name for consistency
            source_name = article.source[:15].ljust(15)
            news_text.append(f"{source_name}: ", style=source_style)
            
            # Add visual indicators for truly new articles (only the very latest)
            if is_new and self.flash_count > 3:  # Only show for fresh articles
                news_text.append("🆕 ", style="bold red blink")
            elif is_latest and self.flash_count > 0:
                news_text.append("🔥 ", style="bold yellow")
            
            news_text.append(f"{article.short_title}\n", style=title_style)
        
        # Dynamic panel styling based on flash state
        if self.flash_count > 0:
            intensity = self.flash_count / DEFAULT_CONFIG.ui.flash_duration
            if intensity > 0.7:
                style = "bold red"
                title_suffix = " • 🚨 LIVE BREAKING"
            elif intensity > 0.4:
                style = "bold yellow"
                title_suffix = " • 🔥 UPDATING"
            else:
                style = "bold green"
                title_suffix = " • ✅ UPDATED"
        else:
            style = "bright_white"
            title_suffix = " • ⚡ Live Stream"
        
        return Panel(
            news_text,
            title=f"📺 {get_topic_display_name(self.topic)}{title_suffix}",
            style=style,
            padding=(1, 1)
        )
    
    def _create_footer(self) -> Panel:
        """Create footer with enhanced controls and performance info."""
        footer_text = Text()
        footer_text.append("🎯 Press ", style="dim")
        footer_text.append("Ctrl+C", style="bold red")
        footer_text.append(" to exit | ", style="dim")
        footer_text.append("Real-time 20 FPS", style="bold green")
        footer_text.append(" | Fetch every ", style="dim")
        footer_text.append("3s", style="bold cyan")
        footer_text.append(" | Latest news appears at bottom", style="dim")
        
        # Add performance indicator
        if self.animation_frame % 60 < 30:  # Blink every 3 seconds at 20 FPS
            footer_text.append(" | ", style="dim")
            footer_text.append("⚡ LIVE", style="bold bright_green")
        
        return Panel(
            Align.center(footer_text),
            style="dim"
        )
    
    def render(self) -> Layout:
        """Render the complete streaming terminal with ultra-smooth effects."""
        # Increment animation frame for smooth effects
        self.animation_frame += 1
        
        # Decrease flash counter smoothly
        if self.flash_count > 0:
            self.flash_count -= 1
            
            # Clean up new article positions as flash fades
            if self.flash_count <= 5:  # Start cleanup in last 5 frames
                fade_positions = set()
                for pos in self.new_article_positions:
                    if pos < len(self.articles) - 1:  # Keep only the very latest
                        fade_positions.add(pos)
                self.new_article_positions -= fade_positions
        
        # Update all components with enhanced effects
        self.layout["header"].update(self._create_header())
        self.layout["footer"].update(self._create_footer())
        self.layout["sidebar"].update(self._create_sidebar())
        self.layout["articles"].update(self._create_news_stream())
        
        return self.layout
    
    def clear_articles(self):
        """Clear all articles from the stream."""
        self.articles.clear()
        
    def get_article_count(self) -> int:
        """Get current number of articles in stream."""
        return len(self.articles)
