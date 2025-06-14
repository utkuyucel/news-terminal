# News Terminal 📰

A Bloomberg-style streaming news terminal optimized for traders. Features real-time news streaming with interactive topic selection, latest news at the bottom, and visual alerts for new articles.

## Features

- **📋 Interactive Topic Selection**: Choose from Economic, Middle East, Technology, Breaking News, Politics, Crypto, and Energy
- **🔄 Real-time Streaming**: Latest news appears at the bottom for easy scanning
- **⚡ Visual Flash Alerts**: Terminal flashes when new articles arrive
- **📈 Trading Optimized**: Focus on market-moving news categories
- **🕐 Live Clock**: Real-time timestamp display
- **📊 Stream Statistics**: Track article count and feed status
- **🎯 Topic-focused Feeds**: Curated RSS sources for each category
- **🚀 Concurrent Processing**: Efficient parallel news fetching

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the streaming news terminal:

```bash
python run.py
```

**Interactive Usage:**
1. Select a topic from the menu (Economic, Middle East, etc.)
2. Watch real-time news stream with latest at bottom
3. Terminal flashes when new articles arrive
4. Press `Ctrl+C` to return to topic selection or exit

**For Trading:**
- Economic news for market movements
- Middle East news for geopolitical events  
- Energy news for commodity trading
- Crypto news for digital asset trading

## Configuration

### RSS Sources (`data/rss.py`)
- Add or modify RSS feed sources
- Categorize feeds (finance, technology, general, etc.)
- Set priority levels for sources

### Application Settings (`config.py`)
- Refresh interval (default: 1 second)
- Display settings (terminal dimensions, colors)
- Network timeout settings
- Concurrent processing limits

## Project Structure

```
news-terminal/
├── run.py                 # Main entry point
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── data/
│   └── rss.py           # RSS feed sources
├── src/
│   ├── app.py           # Main application controller
│   ├── core/
│   │   ├── models.py    # Data models
│   │   └── fetcher.py   # RSS feed fetcher
│   ├── ui/
│   │   └── terminal.py  # Terminal UI components
│   └── utils/
│       ├── logging_config.py  # Logging setup
│       └── decorators.py      # Utility decorators
```

## RSS Sources Included

### Financial News
- Reuters Business
- Financial Times
- MarketWatch
- Yahoo Finance
- Bloomberg
- Wall Street Journal
- CNBC

### Technology News
- TechCrunch
- Ars Technica
- The Verge
- Wired

### General News
- BBC News
- CNN
- Reuters World
- AP News

### Science & International
- Scientific American
- MIT Technology Review
- Al Jazeera
- Guardian World

## Customization

### Adding New RSS Sources
Edit `data/rss.py` and add new `RSSSource` objects:

```python
RSSSource("Source Name", "https://example.com/rss", "category", priority)
```

### Modifying Display Settings
Edit `config.py` to change:
- Refresh intervals
- Terminal dimensions
- Color schemes
- Article limits per source

### Custom Categories
1. Add new categories in `data/rss.py`
2. Update the UI layout in `src/ui/terminal.py`

## Technical Details

- **Concurrency**: Uses ThreadPoolExecutor for parallel RSS fetching
- **UI Framework**: Rich library for beautiful terminal interfaces
- **Error Handling**: Comprehensive retry mechanisms and graceful degradation
- **Performance**: LRU caching and efficient data structures
- **Architecture**: Clean separation of concerns with modular design

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`
- Terminal with color support (recommended)

## License

See LICENSE file for details.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the news terminal.
