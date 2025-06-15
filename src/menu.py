"""
Interactive menu system for topic selection.
"""
import os
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)


class TopicMenu:
    """Interactive topic selection menu."""
    
    def __init__(self):
        self.console = Console()
        self.topics = {
            '1': {'name': 'Technology', 'categories': ['technology'], 'emoji': '💻', 'desc': 'Tech news, AI, startups, gadgets'},
            '2': {'name': 'Politics', 'categories': ['politics'], 'emoji': '🏛️', 'desc': 'Political news, elections, policy'},
            '3': {'name': 'Economy & Finance', 'categories': ['financial', 'business'], 'emoji': '💰', 'desc': 'Markets, earnings, economic indicators'},
            '4': {'name': 'Trading Focus', 'categories': ['financial', 'earnings', 'business'], 'emoji': '📈', 'desc': 'Real-time trading news, earnings, mergers'},
            '5': {'name': 'Cryptocurrency', 'categories': ['crypto', 'technology'], 'emoji': '₿', 'desc': 'Crypto markets, blockchain, DeFi'},
            '6': {'name': 'General News', 'categories': ['general'], 'emoji': '📰', 'desc': 'Breaking news, world events'},
            '7': {'name': 'Science & Health', 'categories': ['science'], 'emoji': '🔬', 'desc': 'Scientific discoveries, medical news'},
            '8': {'name': 'All Categories', 'categories': ['financial', 'technology', 'business', 'general'], 'emoji': '🌍', 'desc': 'Comprehensive news coverage'},
        }
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_menu(self) -> Optional[List[str]]:
        """Display topic selection menu and return selected categories."""
        self.clear_screen()
        
        # Create header
        header_text = Text()
        header_text.append("📰 NEWS TERMINAL ", style="bold cyan")
        header_text.append("- Topic Selection", style="white")
        
        header_panel = Panel(
            Align.center(header_text),
            style="bright_blue",
            height=3
        )
        
        # Create menu table
        table = Table(show_header=True, header_style="bold blue", box=None)
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Topic", style="bright_white", width=20)
        table.add_column("Description", style="white", width=50)
        
        for key, topic in self.topics.items():
            table.add_row(
                f"{key}",
                f"{topic['emoji']} {topic['name']}",
                topic['desc']
            )
        
        # Add exit option
        table.add_row("q", "❌ Exit", "Quit the application")
        
        menu_panel = Panel(
            table,
            title="📋 Select News Topic",
            style="bright_blue"
        )
        
        # Create footer
        footer_text = Text("Enter your choice (1-8, or 'q' to quit): ", style="bold yellow")
        footer_panel = Panel(footer_text, style="bright_black")
        
        # Display menu
        self.console.print(header_panel)
        self.console.print()
        self.console.print(menu_panel)
        self.console.print()
        self.console.print(footer_panel)
        
        # Get user input
        try:
            choice = input().strip().lower()
            
            if choice == 'q':
                return None
            
            if choice in self.topics:
                selected_topic = self.topics[choice]
                self.show_loading(selected_topic['name'])
                return selected_topic['categories']
            else:
                self.console.print(f"\n❌ Invalid choice: {choice}. Please try again.", style="bold red")
                input("Press Enter to continue...")
                return self.show_menu()  # Recursive call to show menu again
                
        except KeyboardInterrupt:
            return None
        except Exception:
            self.console.print("\n❌ Invalid input. Please try again.", style="bold red")
            input("Press Enter to continue...")
            return self.show_menu()
    
    def show_loading(self, topic_name: str):
        """Show loading screen for selected topic."""
        self.clear_screen()
        
        loading_text = Text()
        loading_text.append(f"🔄 Loading {topic_name} News...\n\n", style="bold cyan")
        loading_text.append("📡 Connecting to news sources...\n", style="white")
        loading_text.append("📊 Fetching latest articles...\n", style="white")
        loading_text.append("⚡ Processing urgent news...\n", style="yellow")
        loading_text.append("\nStarting real-time feed in 3 seconds...", style="green")
        
        panel = Panel(
            Align.center(loading_text),
            title=f"📰 News Terminal - {topic_name}",
            style="blue"
        )
        
        self.console.print(panel)
        
        # Brief pause for user experience
        import time
        time.sleep(2)


class SimpleTopicMenu:
    """Simple text-based topic menu for basic terminals."""
    
    def __init__(self):
        self.topics = {
            '1': {'name': 'Technology', 'categories': ['technology']},
            '2': {'name': 'Politics', 'categories': ['politics']},
            '3': {'name': 'Economy & Finance', 'categories': ['financial', 'business']},
            '4': {'name': 'Trading Focus', 'categories': ['financial', 'earnings', 'business']},
            '5': {'name': 'Cryptocurrency', 'categories': ['crypto', 'technology']},
            '6': {'name': 'General News', 'categories': ['general']},
            '7': {'name': 'Science & Health', 'categories': ['science']},
            '8': {'name': 'All Categories', 'categories': ['financial', 'technology', 'business', 'general']},
        }
    
    def clear_screen(self):
        """Clear screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_menu(self) -> Optional[List[str]]:
        """Display simple topic menu."""
        self.clear_screen()
        
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📰 NEWS TERMINAL - Topic Selection")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print()
        
        print(f"{Fore.YELLOW}Please select a news topic:{Style.RESET_ALL}")
        print()
        
        for key, topic in self.topics.items():
            print(f"{Fore.CYAN}[{key}]{Style.RESET_ALL} {topic['name']}")
        
        print(f"{Fore.RED}[q]{Style.RESET_ALL} Exit")
        print()
        
        try:
            choice = input(f"{Fore.YELLOW}Enter your choice (1-8, or 'q' to quit): {Style.RESET_ALL}").strip().lower()
            
            if choice == 'q':
                return None
                
            if choice in self.topics:
                selected_topic = self.topics[choice]
                print(f"\n{Fore.GREEN}🔄 Loading {selected_topic['name']} news...{Style.RESET_ALL}")
                import time
                time.sleep(1.5)
                return selected_topic['categories']
            else:
                print(f"\n{Fore.RED}❌ Invalid choice: {choice}. Please try again.{Style.RESET_ALL}")
                input("Press Enter to continue...")
                return self.show_menu()
                
        except KeyboardInterrupt:
            return None
        except Exception:
            print(f"\n{Fore.RED}❌ Invalid input. Please try again.{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return self.show_menu()


# Global menu instances
topic_menu = TopicMenu()
simple_topic_menu = SimpleTopicMenu()
