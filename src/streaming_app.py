"""Real-time news streaming application for trading terminals."""

import asyncio
import signal
import time
import sys
from typing import List, Set, Dict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from rich.live import Live
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.core.fetcher import get_feed_fetcher
from src.core.models import Article
from src.ui.streaming_terminal import StreamingNewsTerminal
from src.ui.topic_selector import TopicSelector
from src.utils.logging_config import setup_logging, get_logger
from data.rss import get_sources_by_category
from config import DEFAULT_CONFIG


logger = get_logger('streaming_app')


class StreamingNewsApp:
    """Real-time streaming news application optimized for trading terminals."""
    
    def __init__(self):
        self.running = True
        self.fetcher = get_feed_fetcher()
        self.seen_articles: Set[str] = set()
        self.articles_cache: List[Article] = []
        
        # Ultra-smooth timing parameters
        self.fetch_interval = 3.0        # Fetch every 3 seconds
        self.display_fps = 20            # 20 FPS for smooth display
        self.display_interval = 1.0 / self.display_fps  # 0.05 seconds
        
        # Performance tracking
        self.last_fetch_time = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Background executor for non-blocking operations
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Shutting down news stream...")
        self.running = False
    
    def _select_topic(self) -> str:
        """Interactive topic selection with enhanced UI."""
        console = Console()
        console.print("\n🎯 [bold cyan]Trading News Terminal[/bold cyan]")
        console.print("=" * 50)
        
        selector = TopicSelector()
        return selector.select_topic()
    
    async def _fetch_articles_async(self, topic: str) -> List[Article]:
        """Asynchronously fetch articles without blocking the UI."""
        loop = asyncio.get_event_loop()
        
        try:
            # Run RSS fetching in background thread
            future = loop.run_in_executor(
                self.executor, 
                self._fetch_new_articles_sync, 
                topic
            )
            return await future
            
        except Exception as e:
            logger.error(f"Async fetch error: {e}")
            return []
    
    def _fetch_new_articles_sync(self, topic: str) -> List[Article]:
        """Synchronous article fetching for thread executor."""
        try:
            sources = get_sources_by_category(topic)
            if not sources:
                return []
            
            all_articles = list(self.fetcher.fetch_all_sources(sources))
            
            # Advanced deduplication with multiple criteria
            new_articles = []
            for article in all_articles:
                # Create sophisticated unique ID
                article_id = f"{article.source}:{hash(article.title[:100])}"
                content_hash = f"{article.source}:{article.title[:50]}:{article.published.timestamp()}"
                
                if (article_id not in self.seen_articles and 
                    content_hash not in self.seen_articles):
                    new_articles.append(article)
                    self.seen_articles.add(article_id)
                    self.seen_articles.add(content_hash)
            
            # Sort by publication time (oldest first for proper chronological order)
            return sorted(new_articles, key=lambda x: x.published)
            
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            return []
    
    async def _show_startup_sequence(self):
        """Professional startup sequence."""
        console = Console()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Startup sequence
            startup_task = progress.add_task("🚀 Initializing Trading News Terminal...", total=100)
            await asyncio.sleep(0.5)
            progress.update(startup_task, advance=20)
            
            progress.update(startup_task, description="📡 Connecting to news sources...")
            await asyncio.sleep(0.3)
            progress.update(startup_task, advance=30)
            
            progress.update(startup_task, description="⚡ Optimizing real-time engine...")
            await asyncio.sleep(0.3)
            progress.update(startup_task, advance=30)
            
            progress.update(startup_task, description="🎯 Preparing streaming interface...")
            await asyncio.sleep(0.2)
            progress.update(startup_task, advance=20)
            
            progress.update(startup_task, description="✅ Ready for live streaming!")
            await asyncio.sleep(0.2)
        
        console.print("\n🔥 [bold green]Real-Time Stream Ready![/bold green]")
        await asyncio.sleep(0.5)
    
    async def run(self):
        """Run the flawless streaming application."""
        console = Console()
        
        try:
            await self._show_startup_sequence()
            
            # Topic selection
            topic = self._select_topic()
            console.print(f"✅ [bold green]Topic Selected:[/bold green] {topic}")
            await asyncio.sleep(0.3)
            
            # Initialize terminal with optimized settings
            terminal = StreamingNewsTerminal(topic, max_articles=150)
            
            # Initial data load
            console.print("📊 [bold yellow]Loading initial news feed...[/bold yellow]")
            initial_articles = await self._fetch_articles_async(topic)
            
            if initial_articles:
                # Take the most recent 20 articles and ensure proper chronological order
                recent_articles = sorted(initial_articles, key=lambda x: x.published)[-20:]
                terminal.add_articles(recent_articles)
                console.print(f"✅ [bold green]Loaded {len(recent_articles)} articles[/bold green]")
            
            self.last_fetch_time = time.time()
            console.print("\n🎯 [bold cyan]Starting real-time stream...[/bold cyan]")
            await asyncio.sleep(0.5)
            
            # Ultra-smooth live display with precise timing
            with Live(
                terminal.render(),
                refresh_per_second=self.display_fps,
                console=console,
                auto_refresh=False,
                vertical_overflow="visible"
            ) as live:
                
                last_update_time = time.time()
                fetch_task = None
                
                while self.running:
                    try:
                        current_time = time.time()
                        
                        # Non-blocking background fetching
                        if (current_time - self.last_fetch_time >= self.fetch_interval and 
                            (fetch_task is None or fetch_task.done())):
                            
                            fetch_task = asyncio.create_task(
                                self._fetch_articles_async(topic)
                            )
                            self.last_fetch_time = current_time
                        
                        # Process completed fetch results
                        if fetch_task and fetch_task.done():
                            try:
                                new_articles = await fetch_task
                                if new_articles:
                                    terminal.add_articles(new_articles)
                                    console.print(f"🔥 [bold red]{len(new_articles)} new articles![/bold red] "
                                                f"(Frame {self.frame_count})")
                                fetch_task = None
                            except Exception as e:
                                logger.error(f"Error processing fetch result: {e}")
                                fetch_task = None
                        
                        # Ultra-smooth display updates with precise timing
                        if current_time - last_update_time >= self.display_interval:
                            live.update(terminal.render())
                            live.refresh()
                            last_update_time = current_time
                            self.frame_count += 1
                        
                        # Precise async sleep for smooth performance
                        await asyncio.sleep(0.01)  # 10ms precision
                        
                    except KeyboardInterrupt:
                        self.running = False
                        break
                    except Exception as e:
                        logger.error(f"Stream error: {e}")
                        await asyncio.sleep(0.1)
        
        except KeyboardInterrupt:
            console.print("\n👋 [bold yellow]Stream stopped by user[/bold yellow]")
        except Exception as e:
            console.print(f"❌ [bold red]Critical error:[/bold red] {e}")
        finally:
            # Performance summary
            elapsed = time.time() - self.start_time
            avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
            
            console.print(f"📊 [bold cyan]Performance Summary:[/bold cyan]")
            console.print(f"   • Frames rendered: {self.frame_count}")
            console.print(f"   • Average FPS: {avg_fps:.2f}")
            console.print(f"   • Runtime: {elapsed:.2f}s")
            console.print("🏁 [bold green]News Terminal stopped.[/bold green]")
            
            # Cleanup
            self.executor.shutdown(wait=False)


def main():
    """Entry point for the streaming news application."""
    # Minimal logging for maximum performance
    setup_logging("WARNING")
    
    # Optimize asyncio event loop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    app = StreamingNewsApp()
    
    try:
        # Run with high-performance event loop
        asyncio.run(app.run(), debug=False)
    except KeyboardInterrupt:
        print("\n✅ [bold green]Shutdown complete[/bold green]")
    except Exception as e:
        print(f"❌ Startup error: {e}")


if __name__ == "__main__":
    main()
