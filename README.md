# News Terminal 📰

A professional Bloomberg-style terminal for real-time news aggregation from multiple sources. Built with Python, it combines API feeds and RSS sources to provide comprehensive news coverage with live updates.

## Features

- **� Real-time Updates**: Automatic refresh every second with live news feed
- **� Multi-source Aggregation**: Combines News API, RSS feeds, and free sources
- **🎯 Category Filtering**: Technology, Business, General, Politics, Science, and more
- **⚡ Rich Terminal UI**: Beautiful terminal interface with Rich library
- **🕐 Live Clock**: Real-time timestamp and status display
- **� Deduplication**: Smart removal of duplicate articles
- **⚡ Concurrent Processing**: Efficient parallel news fetching
- **💾 Intelligent Caching**: Reduces API calls with smart caching
- **🌐 Multiple Output Formats**: Terminal UI, simple mode, or JSON output

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/utkuyucel/news-terminal
   cd news-terminal
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API key** (optional but recommended)
   - Get a free API key from [NewsAPI.org](https://newsapi.org)
   - The key is already configured in `.env` file
   - Without API key, only free sources (RSS, Hacker News, Reddit) will be used

4. **Run the terminal**
   ```bash
   python run.py
   ```

## Usage Examples

### Trading Mode (NEW!)

For stock traders, use the specialized trading terminal:

```bash
# Ultra-fast trading terminal (0.5s refresh)
python trading.py

# Focus only on earnings news
python trading.py --earnings-only

# Include cryptocurrency news
python trading.py --crypto

# Quick fetch for trading decisions
python trading.py --fetch
```

**Trading Features:**
- ⚡ **0.5-second refresh rate** for ultra-real-time updates
- 🕐 **Precise clock with seconds** for timing trades
- 🟢 **Market hours indicator** (US markets 9:30 AM - 4:00 PM ET)
- ⚡ **Urgent news highlighting** with trading keywords (earnings, mergers, FDA approvals, etc.)
- 📈 **Trading-focused categories**: Financial, Earnings, Crypto
- 🔴 **Visual alerts** for market-moving news
- 📊 **Extended article display** (100 articles vs 50 in regular mode)

### Basic Usage
```bash
# Run with default categories (general, technology, business)
python run.py

# Run with specific categories
python run.py -c technology business politics

# Simple mode for basic terminals
python run.py --simple
```

### Fetch Mode (No Live Updates)
```bash
# Fetch news once and display
python run.py --fetch

# Output in JSON format
python run.py --fetch --json

# Fetch specific categories
python run.py --fetch -c technology
```

### Advanced Options
```bash
# Verbose logging
python run.py --verbose

# Force refresh cache
python run.py --refresh-cache

# Help and all options
python run.py --help
```

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
