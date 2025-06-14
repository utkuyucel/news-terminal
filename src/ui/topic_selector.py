"""Topic selection CLI interface for the news terminal."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.align import Align

from data.rss import get_topics, get_topic_display_name


class TopicSelector:
    """Interactive topic selection interface."""
    
    def __init__(self):
        self.console = Console()
    
    def display_welcome(self):
        """Display welcome message and instructions."""
        welcome_text = Text()
        welcome_text.append("📰 NEWS TERMINAL", style="bold blue")
        welcome_text.append("\n")
        welcome_text.append("Real-time news streaming for traders", style="dim")
        welcome_text.append("\n")
        welcome_text.append("Latest news appears at the bottom • Press Ctrl+C to exit", style="italic")
        
        welcome_panel = Panel(
            Align.center(welcome_text),
            style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(welcome_panel)
        self.console.print()
    
    def display_topics(self) -> Table:
        """Display available topics in a formatted table."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Topic", style="white", width=30)
        table.add_column("Description", style="dim", width=40)
        
        descriptions = {
            "economic": "Financial markets, stocks, economy, trading",
            "middle_east": "Middle East politics, conflicts, regional news",
            "technology": "Tech companies, startups, innovations",
            "breaking": "Breaking news, urgent updates",
            "politics": "Government, elections, policy",
            "crypto": "Bitcoin, Ethereum, digital assets",
            "energy": "Oil, gas, renewable energy, commodities"
        }
        
        topics = get_topics()
        for i, topic in enumerate(topics, 1):
            display_name = get_topic_display_name(topic)
            description = descriptions.get(topic, "General news category")
            table.add_row(str(i), display_name, description)
        
        return table
    
    def select_topic(self) -> str:
        """Interactive topic selection."""
        self.display_welcome()
        
        # Display topics table
        topics_table = self.display_topics()
        topic_panel = Panel(
            topics_table,
            title="📋 Available News Topics",
            style="bright_white"
        )
        self.console.print(topic_panel)
        self.console.print()
        
        topics = get_topics()
        
        while True:
            try:
                choice = Prompt.ask(
                    "🎯 Select a topic",
                    choices=[str(i) for i in range(1, len(topics) + 1)],
                    default="1"
                )
                
                selected_topic = topics[int(choice) - 1]
                display_name = get_topic_display_name(selected_topic)
                
                # Confirmation
                self.console.print()
                confirm_text = Text()
                confirm_text.append("✅ Selected: ", style="green")
                confirm_text.append(display_name, style="bold green")
                self.console.print(confirm_text)
                self.console.print()
                
                return selected_topic
                
            except (ValueError, IndexError):
                self.console.print("❌ Invalid selection. Please try again.", style="red")
            except KeyboardInterrupt:
                self.console.print("\n👋 Goodbye!")
                raise SystemExit(0)
