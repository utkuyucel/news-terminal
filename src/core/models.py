"""News article data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Article:
    """News article data structure."""
    title: str
    link: str
    published: datetime
    source: str
    summary: Optional[str] = None
    author: Optional[str] = None
    category: str = "general"
    
    def __str__(self) -> str:
        time_str = self.published.strftime("%H:%M")
        return f"[{time_str}] {self.source}: {self.title}"
    
    @property
    def short_title(self) -> str:
        """Truncated title for display."""
        return self.title[:80] + "..." if len(self.title) > 80 else self.title
