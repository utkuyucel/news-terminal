"""Configuration settings for the news terminal application."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UIConfig:
    """UI layout and appearance settings."""
    refresh_interval: float = 0.05  # 20 FPS for smooth streaming
    max_articles_per_source: int = 15
    terminal_width: int = 140
    terminal_height: int = 35
    clock_format: str = "%Y-%m-%d %H:%M:%S"
    show_source_labels: bool = True
    color_scheme: str = "dark"
    animation_frames: int = 60  # Smooth animations
    flash_duration: int = 12    # Flash effect duration (shorter for less intensity)


@dataclass(frozen=True)
class AppConfig:
    """Main application configuration."""
    ui: UIConfig
    request_timeout: int = 10
    concurrent_feeds: int = 5
    retry_attempts: int = 3
    log_level: str = "INFO"


# Default configuration instance
DEFAULT_CONFIG = AppConfig(
    ui=UIConfig(),
    request_timeout=10,
    concurrent_feeds=5,
    retry_attempts=3,
    log_level="INFO"
)
