"""Logging configuration for the news terminal."""

import logging
import sys
from typing import Optional

from config import DEFAULT_CONFIG


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration."""
    log_level = level or DEFAULT_CONFIG.log_level
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return logging.getLogger('news_terminal')


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f'news_terminal.{name}')
