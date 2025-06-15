"""
Terminal display system for the news terminal - Enhanced for stock trading.
"""
import os
import time
from datetime import datetime, timezone
from typing import List, Optional, Set
import shutil

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from colorama import init, Fore, Style

from config import DEFAULT_CONFIG
from data.api import NewsArticle
from src.aggregator import AggregatedNews

# Initialize colorama for cross-platform color support
init(autoreset=True)


class TerminalDisplay:
    """Manages the terminal display for news - Enhanced for stock trading."""
    
    def __init__(self):
        self.console = Console()
        terminal_size = shutil.get_terminal_size()
        self.terminal_width = terminal_size.columns
        self.terminal_height = terminal_size.lines
        self.current_articles: List[NewsArticle] = []
        self.last_update: Optional[datetime] = None
        self.new_articles_count = 0
        self.trading_keywords = DEFAULT_CONFIG.news.trading_keywords or []
        self.last_clock_update = ""  # Track last clock update to prevent unnecessary refreshes
        
    def _is_market_hours(self) -> tuple[bool, str]:
        """Check if markets are open (US market hours: 9:30 AM - 4:00 PM ET)."""
        now = datetime.now()
        # Simplified - in reality you'd handle timezones properly
        current_hour = now.hour
        current_minute = now.minute
        
        # Market hours: 9:30 AM to 4:00 PM (16:00)
        market_open = (current_hour > 9) or (current_hour == 9 and current_minute >= 30)
        market_close = current_hour < 16
        is_open = market_open and market_close
        
        # Also check if it's a weekday
        is_weekday = now.weekday() < 5  # Monday = 0, Sunday = 6
        
        if is_weekday and is_open:
            return True, "🟢 MARKET OPEN"
        elif is_weekday:
            return False, "🔴 MARKET CLOSED"
        else:
            return False, "🔴 WEEKEND"
    
    def _is_urgent_news(self, article: NewsArticle) -> bool:
        """Check if news article contains urgent trading keywords."""
        title_lower = article.title.lower()
        desc_lower = (article.description or "").lower()
        
        return any(
            keyword in title_lower or keyword in desc_lower
            for keyword in self.trading_keywords
        )
        
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def create_header(self) -> Panel:
        """Create the header panel with title, market status, and current time with seconds."""
        current_time = datetime.now().strftime(DEFAULT_CONFIG.terminal.clock_format)
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get market status
        is_open, market_status = self._is_market_hours()
        
        header_text = Text()
        header_text.append("📰 NEWS TERMINAL ", style="bold cyan")
        header_text.append(f"| {current_date} ", style="white")
        header_text.append(f"⏰ {current_time} ", style="bold yellow")
        header_text.append(f"| {market_status}", style="bold green" if is_open else "bold red")
        
        return Panel(
            Align.center(header_text),
            style="bright_blue",
            height=3,
            padding=(0, 1),  # Add padding to reduce visual jitter
            title_align="center",  # Stable title position
            border_style="bright_blue"  # Consistent border
        )
    
    def create_status_bar(self, aggregated_news: AggregatedNews) -> Panel:
        """Create status bar with statistics and trading indicators."""
        if not aggregated_news.articles:
            status_text = Text("⚠️  No news articles loaded", style="bold red")
        else:
            # Count urgent news
            urgent_count = sum(1 for article in aggregated_news.articles if self._is_urgent_news(article))
            
            status_text = Text()
            status_text.append(f"📊 {len(aggregated_news.articles)} articles ", style="green")
            status_text.append(f"from {aggregated_news.total_sources} sources ", style="cyan")
            
            if urgent_count > 0:
                status_text.append(f"| ⚡ {urgent_count} URGENT ", style="bold red blink")
            
            status_text.append(f"| Categories: {', '.join(sorted(aggregated_news.categories))} ", style="magenta")
            
            if self.last_update:
                time_diff = datetime.now() - aggregated_news.last_updated
                seconds_ago = int(time_diff.total_seconds())
                if seconds_ago < 60:
                    status_text.append(f"| Updated {seconds_ago}s ago", style="yellow")
                else:
                    minutes_ago = int(seconds_ago / 60)
                    status_text.append(f"| Updated {minutes_ago}m ago", style="yellow")
        
        return Panel(
            status_text,
            style="bright_black",
            height=3
        )
    
    def create_news_table(self, articles: List[NewsArticle]) -> Table:
        """Create a table of news articles with trading highlights."""
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Time", style="cyan", width=8)
        table.add_column("Source", style="magenta", width=15)
        table.add_column("Category", style="yellow", width=10)
        table.add_column("🚨", style="red", width=3)  # Urgent indicator
        table.add_column("Title", style="white", width=self.terminal_width - 50)
        
        for article in articles[:DEFAULT_CONFIG.terminal.max_articles_display]:
            # Format time with seconds for precision
            time_str = article.published_at.strftime("%H:%M:%S")
            
            # Truncate title if too long
            title = article.title
            max_title_length = self.terminal_width - 55
            if len(title) > max_title_length:
                title = title[:max_title_length-3] + "..."
            
            # Color code by category
            category_style = self._get_category_style(article.category)
            
            # Check if urgent
            is_urgent = self._is_urgent_news(article)
            urgent_indicator = "⚡" if is_urgent else ""
            
            # Highlight urgent news in red
            title_style = "bold red" if is_urgent else "white"
            
            table.add_row(
                time_str,
                article.source[:14],  # Truncate source name
                Text(article.category.upper(), style=category_style),
                urgent_indicator,
                Text(title, style=title_style)
            )
        
        return table
    
    def _get_category_style(self, category: str) -> str:
        """Get color style for category."""
        category_colors = {
            'business': 'green',
            'technology': 'bright_blue',
            'general': 'white',
            'politics': 'red',
            'science': 'bright_cyan',
            'sports': 'bright_green',
            'entertainment': 'bright_magenta'
        }
        return category_colors.get(category.lower(), 'white')
    
    def create_layout(self, aggregated_news: AggregatedNews) -> Layout:
        """Create the main layout."""
        layout = Layout()
        
        # Create main sections
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="status", size=3),
        )
        
        # Populate sections
        layout["header"].update(self.create_header())
        layout["status"].update(self.create_status_bar(aggregated_news))
        
        # Body with news table
        if aggregated_news.articles:
            news_table = self.create_news_table(aggregated_news.articles)
            
            # Count urgent news for title
            urgent_count = sum(1 for article in aggregated_news.articles if self._is_urgent_news(article))
            title = "📈 Live Trading News Feed"
            if urgent_count > 0:
                title += f" | ⚡ {urgent_count} URGENT"
            
            layout["body"].update(Panel(news_table, title=title, style="bright_blue"))
        else:
            layout["body"].update(
                Panel(
                    Align.center(Text("No news articles available", style="bold red")),
                    title="📈 Live Trading News Feed"
                )
            )
        
        return layout
    
    def show_loading(self) -> None:
        """Show loading screen."""
        self.clear_screen()
        loading_text = Text()
        loading_text.append("🔄 Loading News Terminal...\n", style="bold cyan")
        loading_text.append("Fetching latest news from multiple sources...", style="white")
        
        panel = Panel(
            Align.center(loading_text),
            title="News Terminal",
            style="blue"
        )
        
        self.console.print(panel)
    
    def show_error(self, error_message: str) -> None:
        """Show error message."""
        error_text = Text()
        error_text.append("❌ Error: ", style="bold red")
        error_text.append(error_message, style="white")
        
        panel = Panel(
            Align.center(error_text),
            title="Error",
            style="red"
        )
        
        self.console.print(panel)
    
    def display_news_live(self, get_news_func) -> None:
        """Display news with seamless live updates optimized for trading."""
        try:
            # Get initial data
            aggregated_news = get_news_func()
            self.current_articles = aggregated_news.articles
            self.last_update = aggregated_news.last_updated
            
            with Live(
                self.create_layout(aggregated_news), 
                console=self.console, 
                refresh_per_second=10,  # High refresh rate for real-time trading
                auto_refresh=False,  # Manual control for precise updates
                transient=False,  # Don't clear on exit
                vertical_overflow="visible"  # Prevent layout shifts
            ) as live:
                while True:
                    try:
                        current_time_str = datetime.now().strftime(DEFAULT_CONFIG.terminal.clock_format)
                        clock_changed = current_time_str != self.last_clock_update
                        
                        # REAL-TIME MODE: Fetch news much more frequently
                        content_changed = False
                        fetch_interval = DEFAULT_CONFIG.terminal.trading_news_fetch_interval
                        
                        if not hasattr(self, '_last_news_fetch') or (time.time() - self._last_news_fetch) > fetch_interval:
                            new_aggregated_news = get_news_func()
                            self._last_news_fetch = time.time()
                            
                            # Check for content changes
                            if not self.current_articles or len(new_aggregated_news.articles) != len(self.current_articles):
                                content_changed = True
                            else:
                                new_titles = {article.title for article in new_aggregated_news.articles}
                                old_titles = {article.title for article in self.current_articles}
                                if new_titles != old_titles:
                                    content_changed = True
                            
                            if content_changed:
                                self.current_articles = new_aggregated_news.articles
                                self.last_update = new_aggregated_news.last_updated
                        else:
                            # Use cached data for rapid clock updates
                            new_aggregated_news = AggregatedNews(
                                articles=self.current_articles,
                                last_updated=self.last_update or datetime.now(),
                                total_sources=len(set(article.source for article in self.current_articles)) if self.current_articles else 0,
                                categories=set(article.category for article in self.current_articles) if self.current_articles else set()
                            )
                        
                        # Update display for any changes (clock or content)
                        if clock_changed or content_changed:
                            layout = self.create_layout(new_aggregated_news)
                            live.update(layout, refresh=True)
                            self.last_clock_update = current_time_str
                        
                        # Ultra-fast sleep for real-time performance
                        time.sleep(DEFAULT_CONFIG.terminal.refresh_interval)
                        
                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        # Show error but continue - no screen clearing
                        error_layout = Layout()
                        error_layout.split(
                            Layout(name="header", size=3),
                            Layout(name="error"),
                            Layout(name="status", size=3),
                        )
                        error_layout["header"].update(self.create_header())
                        error_layout["error"].update(
                            Panel(
                                Align.center(Text(f"❌ Error: {str(e)}", style="bold red")),
                                title="Connection Error - Retrying..."
                            )
                        )
                        error_layout["status"].update(
                            Panel(Text("Press Ctrl+C to exit | Auto-retry in 3s", style="yellow"))
                        )
                        live.update(error_layout)
                        time.sleep(3)  # Wait before retrying
                        
        except KeyboardInterrupt:
            # Clean exit message
            self.console.print("\n👋 Returning to topic selection...", style="bold yellow")
        except Exception as e:
            self.console.print(f"\n❌ Fatal Error: {str(e)}", style="bold red")
    
    def show_article_details(self, article: NewsArticle) -> None:
        """Show detailed view of an article."""
        details_text = Text()
        details_text.append(f"Title: {article.title}\n\n", style="bold white")
        details_text.append(f"Source: {article.source}\n", style="cyan")
        details_text.append(f"Category: {article.category}\n", style="yellow")
        details_text.append(f"Published: {article.published_at.strftime(DEFAULT_CONFIG.terminal.date_format)}\n", style="green")
        details_text.append(f"URL: {article.url}\n\n", style="blue")
        details_text.append(f"Description:\n{article.description}", style="white")
        
        panel = Panel(
            details_text,
            title="📄 Article Details",
            style="bright_blue"
        )
        
        self.console.print(panel)


class SimpleTerminalDisplay:
    """Simplified terminal display for basic terminals."""
    
    def __init__(self):
        self.width = shutil.get_terminal_size().columns
    
    def clear_screen(self) -> None:
        """Clear screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_news_loop(self, get_news_func) -> None:
        """Display news in simple format with seamless updates."""
        try:
            while True:
                try:
                    aggregated_news = get_news_func()
                    self.display_news(aggregated_news)
                    time.sleep(DEFAULT_CONFIG.terminal.refresh_interval)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"{Fore.RED}❌ Connection error: {str(e)}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Retrying in 3 seconds...{Style.RESET_ALL}")
                    time.sleep(3)
                    
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Returning to topic selection...{Style.RESET_ALL}")
    
    def display_news(self, aggregated_news: AggregatedNews) -> None:
        """Display news in simple format with trading enhancements."""
        # Use \033[H to move cursor to top instead of clearing screen
        print("\033[H", end="")  # Move cursor to top-left
        
        # Header with precise time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{Fore.CYAN}{'='*self.width}")
        print(f"{Fore.CYAN}📰 TRADING NEWS TERMINAL - {current_time}")
        print(f"{Fore.CYAN}{'='*self.width}{Style.RESET_ALL}")
        
        # Market status
        now = datetime.now()
        current_hour = now.hour
        is_market_hours = 9 <= current_hour < 16 and now.weekday() < 5
        market_status = f"{Fore.GREEN}🟢 MARKET OPEN" if is_market_hours else f"{Fore.RED}🔴 MARKET CLOSED"
        
        # Status with urgent count
        if aggregated_news.articles:
            urgent_count = sum(1 for article in aggregated_news.articles 
                             if any(keyword in article.title.lower() 
                                   for keyword in ['earnings', 'merger', 'acquisition', 'fda', 'guidance']))
            
            print(f"{Fore.GREEN}📊 {len(aggregated_news.articles)} articles from {aggregated_news.total_sources} sources")
            print(f"{market_status}")
            if urgent_count > 0:
                print(f"{Fore.RED}⚡ {urgent_count} URGENT TRADING NEWS{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}⚠️  No articles loaded{Style.RESET_ALL}")
        
        print()
        
        # Articles with urgency indicators
        for i, article in enumerate(aggregated_news.articles[:30], 1):  # Show more for trading
            time_str = article.published_at.strftime("%H:%M:%S")  # Include seconds
            category_color = Fore.YELLOW if article.category == 'technology' else Fore.GREEN if article.category == 'business' else Fore.WHITE
            
            # Check for urgent keywords
            is_urgent = any(keyword in article.title.lower() 
                          for keyword in ['earnings', 'merger', 'acquisition', 'fda', 'guidance', 'halt'])
            
            urgent_prefix = f"{Fore.RED}⚡ " if is_urgent else ""
            
            print(f"{Fore.CYAN}[{time_str}]{Style.RESET_ALL} {category_color}[{article.category.upper()}]{Style.RESET_ALL} {Fore.MAGENTA}{article.source}{Style.RESET_ALL}")
            print(f"  {urgent_prefix}{article.title}{Style.RESET_ALL}")
            print()
        
        # Clear any remaining lines from previous display
        print("\033[J", end="")  # Clear from cursor to end of screen
        
        print(f"{Fore.YELLOW}Press Ctrl+C to return to menu... Refreshing every {DEFAULT_CONFIG.terminal.refresh_interval}s{Style.RESET_ALL}")


# Global display instance
terminal_display = TerminalDisplay()
simple_display = SimpleTerminalDisplay()
