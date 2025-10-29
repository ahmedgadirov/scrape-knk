# Kontakt.az Enhanced Scraper v3 (Stable)

## Key Improvements Over v2

✅ **Single-threaded for maximum stability** - Eliminates threading conflicts  
✅ **Simplified WebDriver management** - Reduces session complexity  
✅ **Better error handling** - Comprehensive recovery mechanisms  
✅ **Automatic progress saving** - Resume interrupted scrapes  
✅ **Graceful interrupt handling** - Safe Ctrl+C termination  
✅ **Resource leak prevention** - Proper cleanup of WebDriver instances  

## Why v3 is More Stable

### Issues Fixed from v2:
1. **Threading deadlocks** - Removed parallel processing complexity
2. **Session management conflicts** - Simplified driver lifecycle  
3. **Resource leaks** - Better WebDriver cleanup
4. **Complex restart logic** - Streamlined session handling
5. **Anti-bot triggers** - More natural request patterns

## Usage Instructions

### 1. Add Your URLs

Open `knk_enhanced_v3.py` and find this section:

```python
# ADD YOUR URLS HERE - Replace this empty list with your URLs
urls = [
    # Add your URLs here
]
```

Add your URLs like this:

```python
urls = [
    "https://kontakt.az/product-url-1",
    "https://kontakt.az/product-url-2",
    "https://kontakt.az/product-url-3",
    # ... more URLs
]
```

### 2. Run the Scraper

```bash
python knk_enhanced_v3.py
```

### 3. Configuration Options

You can modify the configuration at the top of the script:

```python
@dataclass
class ScrapingConfig:
    max_retries: int = 3           # Retry failed URLs N times
    base_delay: float = 4.0        # Minimum delay between requests
    max_delay: float = 8.0         # Maximum delay between requests  
    timeout: int = 15              # Element wait timeout
    page_load_timeout: int = 20    # Page load timeout
    headless: bool = True          # Run browser in background
    session_restart_after: int = 25 # Restart driver after N URLs
```

## Features

### 🔄 Automatic Progress Tracking
- Saves progress every 5 successful scrapes
- Resume interrupted sessions automatically
- Tracks completed/failed URLs separately

### 🛡️ Robust Error Handling
- Automatic WebDriver restart on failures
- Multiple retry attempts per URL
- Graceful handling of timeouts and crashes

### 📊 Comprehensive Logging
- Console output with progress indicators
- Detailed log file for debugging
- Performance statistics

### 💾 Smart Data Export
- CSV export with timestamp
- JSON specifications format
- Pipe-separated image URLs

## Output Format

The scraper extracts these fields:

| Field | Description |
|-------|-------------|
| `url` | Product page URL |
| `title` | Product name |
| `sku` | Product SKU/model number |
| `brand` | Product brand |
| `category` | Breadcrumb category path |
| `price` | Current price |
| `discount` | Discount amount (if any) |
| `availability` | Stock status |
| `specifications` | JSON of product specs |
| `images` | Pipe-separated image URLs |
| `scraped_at` | Timestamp |

## File Outputs

- `kontakt_products_v3_YYYYMMDD_HHMMSS.csv` - Main results
- `scraping_progress_YYYYMMDD_HHMMSS.json` - Progress tracking
- `scraper_YYYYMMDD_HHMMSS.log` - Detailed logs

## Troubleshooting

### Common Issues:

1. **ChromeDriver not found**
   ```bash
   # Install ChromeDriver
   sudo apt-get install chromium-chromedriver  # Ubuntu/Debian
   brew install chromedriver                   # macOS
   ```

2. **Permissions error**
   ```bash
   chmod +x knk_enhanced_v3.py
   ```

3. **Memory issues**
   - Reduce `session_restart_after` to restart driver more frequently
   - Enable `headless = True` to save memory

4. **Site blocking**
   - Increase delays: `base_delay = 6.0, max_delay = 12.0`
   - Reduce `session_restart_after` to 10-15 URLs

### Recovery from Interruptions:

The scraper automatically saves progress. If interrupted:
1. Simply run the script again
2. It will resume from where it stopped
3. Check the progress JSON file for details

## Performance Tips

- **For stability**: Keep default single-threaded mode
- **For speed**: Reduce delays (but may trigger anti-bot measures)
- **For stealth**: Increase delays and reduce session length
- **For debugging**: Set `headless = False` to see browser

## Requirements

```bash
pip install selenium beautifulsoup4 requests
```

Chrome/Chromium browser must be installed.
