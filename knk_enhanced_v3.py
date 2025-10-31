import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, InvalidSessionIdException
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import json
import re
from time import sleep
import random
import time
import os
import logging
import signal
import sys
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

# Simplified logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# ADD YOUR URLS HERE - Replace this empty list with your URLs
urls = [
"https://kontakt.az/cehiz-desti-schafer-new-honor-celik-13-parca-8699131760420",
"https://kontakt.az/honor-200-12-512-gb-black",
"https://kontakt.az/honor-200-12-512-gb-emerald-green",
"https://kontakt.az/honor-200-12-512-gb-moonlight-white",
"https://kontakt.az/honor-200-8-256-gb-black",
"https://kontakt.az/honor-200-8-256-gb-emerald-green",
"https://kontakt.az/honor-200-8-256-gb-moonlight-white",
"https://kontakt.az/honor-200-lite-8-256-gb-cyan-lake",
"https://kontakt.az/honor-200-lite-8-256-gb-midnight-black",
"https://kontakt.az/honor-200-lite-8-256-gb-starry-blue",
"https://kontakt.az/honor-200-pro-12-512-gb-black",
"https://kontakt.az/honor-200-pro-12-512-gb-moonlight-white",
"https://kontakt.az/honor-200-pro-12-512-gb-ocean-cyan",
"https://kontakt.az/honor-2020-modelleri",
"https://kontakt.az/honor-2021",
"https://kontakt.az/honor-400-12-256-gb-black",
"https://kontakt.az/honor-400-12-256-gb-gold",
"https://kontakt.az/honor-400-12-256-gb-white",
"https://kontakt.az/honor-400-12-512-gb-black",
"https://kontakt.az/honor-400-12-512-gb-gold",
"https://kontakt.az/honor-400-12-512-gb-white",
"https://kontakt.az/honor-400-8-256-gb-black",
"https://kontakt.az/honor-400-8-256-gb-gold",
"https://kontakt.az/honor-400-8-256-gb-white",
"https://kontakt.az/honor-400-lite-8-256-gb-black",
"https://kontakt.az/honor-400-lite-8-256-gb-green",
"https://kontakt.az/honor-400-lite-8-256-gb-grey",
"https://kontakt.az/honor-400-pro-12-256-gb-black",
"https://kontakt.az/honor-400-pro-12-256-gb-grey",
"https://kontakt.az/honor-400-pro-12-512-gb-black",
"https://kontakt.az/honor-400-pro-12-512-gb-grey",
"https://kontakt.az/honor-50-lite-6-128-gb-black",
"https://kontakt.az/honor-50-lite-6-128-gb-blue",
"https://kontakt.az/honor-70-8-128-gb-black",
"https://kontakt.az/honor-70-8-256-gb-black",
"https://kontakt.az/honor-70-8-256-gb-silver",
"https://kontakt.az/honor-70-8-gb-256-gb-green",
"https://kontakt.az/honor-70-8gb-128gb-green",
"https://kontakt.az/honor-8a-2-32-gb-black",
"https://kontakt.az/honor-8a-3-64gb",
"https://kontakt.az/honor-8a-prime-3-64-gb-black",
"https://kontakt.az/honor-8s-3-64gb",
"https://kontakt.az/honor-90-12-512-gb-emerald-green",
"https://kontakt.az/honor-90-12-512-gb-midnight-black",
"https://kontakt.az/honor-90-8-256-gb-midnight-black",
"https://kontakt.az/honor-90-8-256-gb-peacock-blue",
"https://kontakt.az/honor-90-lite-8-256-gb-cyan-lake",
"https://kontakt.az/honor-90-lite-8-256-gb-midnight-black",
"https://kontakt.az/honor-90-lite-8-256-gb-titanium-silver",
"https://kontakt.az/honor-9x-4-128-gb-black",
"https://kontakt.az/honor-9x-4-128-gb-blue",
"https://kontakt.az/honor-9x-lite-4-128gb-black",
"https://kontakt.az/honor-band-9-black-rhe-b19",
"https://kontakt.az/honor-band-9-blue-rhe-b19",
"https://kontakt.az/honor-band-9-purple-rhe-b19",
"https://kontakt.az/honor-choice-portable-bt-speaker-red-vna-00",
"https://kontakt.az/honor-choice-watch-2i-kch-wb01-black",
"https://kontakt.az/honor-choice-watch-2i-kch-wb01-white",
"https://kontakt.az/honor-choice-watch-black-bot-wb01",
"https://kontakt.az/honor-choice-watch-white-bot-wb01",
"https://kontakt.az/honor-magic-5-pro-512-gb-black",
"https://kontakt.az/honor-magic-5-pro-512-gb-meadow-green",
"https://kontakt.az/honor-magic-6-pro-12-512gb-black",
"https://kontakt.az/honor-magic-6-pro-12-512gb-sage-green",
"https://kontakt.az/honor-magic-pad-2-12-256-gb-black",
"https://kontakt.az/honor-magic7-12-256-gb-black",
"https://kontakt.az/honor-magic7-12-256-gb-grey",
"https://kontakt.az/honor-magic7-12-256-gb-white",
"https://kontakt.az/honor-magic7-pro-12-512-gb-black",
"https://kontakt.az/honor-magic7-pro-12-512-gb-breeze-blue",
"https://kontakt.az/honor-magic7-pro-12-512-gb-lunar-shadow-grey",
"https://kontakt.az/honor-pad-10-5g-8-256-gb-with-keyboard-gray",
"https://kontakt.az/honor-pad-10-8-128-gb-gray",
"https://kontakt.az/honor-pad-10-8-256-gb-gray",
"https://kontakt.az/honor-pad-8-6gb-128gb-blue",
"https://kontakt.az/honor-pad-8-flip-cover-black",
"https://kontakt.az/honor-pad-9-8-128-gb-cyan-lake",
"https://kontakt.az/honor-pad-9-8-128-gb-space-gray",
"https://kontakt.az/honor-pad-9-lte-8-128-gb-space-gray",
"https://kontakt.az/honor-pad-x8a-4-128-gb-space-grey",
"https://kontakt.az/honor-pad-x8a-4-64-gb-space-grey",
"https://kontakt.az/honor-pad-x8a-lte-4-128-gb-space-grey",
"https://kontakt.az/honor-pad-x8a-lte-4-64-gb-space-grey",
"https://kontakt.az/honor-pad-x9-4-128-gb-space-gray",
"https://kontakt.az/honor-pad-x9-lte-4-128-gb-space-gray",
"https://kontakt.az/honor-pad-x9-lte-4-64-gb-space-gray",
"https://kontakt.az/honor-pad-x9a-6-128-gb-gray",
"https://kontakt.az/honor-pad-x9a-8-256-gb-gray",
"https://kontakt.az/honor-pad-x9a-lte-6-128-gb-gray",
"https://kontakt.az/honor-pad-x9a-lte-8-256-gb-gray",
"https://kontakt.az/honor-pad-x9a-lte-8-256-gb-w-keyboard-gray",
"https://kontakt.az/honor-qiymeti",
"https://kontakt.az/honor-qiymetleri",
"https://kontakt.az/honor-telefon",
"https://kontakt.az/honor-telefon-qiymetleri",
"https://kontakt.az/honor-telefonlari",
"https://kontakt.az/honor-telefonlari-2",
"https://kontakt.az/honor-watch-4-black-tma-b19",
"https://kontakt.az/honor-watch-4-white-tma-b19",
"https://kontakt.az/honor-watch-5-black",
"https://kontakt.az/honor-watch-5-gold",
"https://kontakt.az/honor-watch-5-green",
"https://kontakt.az/honor-watch-gs3-classic-gold-mus-b19",
"https://kontakt.az/honor-watch-gs3-mus-b19-mus-b19",
"https://kontakt.az/honor-x5-plus-4-128-gb-ocean-blue",
"https://kontakt.az/honor-x5-plus-4-64-gb-cyan-lake",
"https://kontakt.az/honor-x5-plus-4-64-gb-midnight-black",
"https://kontakt.az/honor-x5b-4-64-gb-midnight-black",
"https://kontakt.az/honor-x5b-4-64-gb-ocean-blue",
"https://kontakt.az/honor-x5b-plus-4-128-gb-midnight-black",
"https://kontakt.az/honor-x5c-4-64-gb-meteor-silver",
"https://kontakt.az/honor-x5c-4-64-gb-midnight-black",
"https://kontakt.az/honor-x5c-plus-4-128-gb-meteor-silver",
"https://kontakt.az/honor-x5c-plus-4-128-gb-midnight-black",
"https://kontakt.az/honor-x6-4-64-gb-midnight-black",
"https://kontakt.az/honor-x6-4-64-gb-ocean-blue",
"https://kontakt.az/honor-x6-4-64-gb-titanium-silver",
"https://kontakt.az/honor-x6a-6-128-gb-black",
"https://kontakt.az/honor-x6a-6-128-gb-silver",
"https://kontakt.az/honor-x6b-4-128-gb-forest-green",
"https://kontakt.az/honor-x6b-4-128-gb-midnight-black",
"https://kontakt.az/honor-x6b-6-256-gb-forest-green",
"https://kontakt.az/honor-x6b-6-256-gb-midnight-black",
"https://kontakt.az/honor-x6c-6-128-gb-midnight-black",
"https://kontakt.az/honor-x6c-6-128-gb-ocean-cyan",
"https://kontakt.az/honor-x6c-6-256-gb-midnight-black",
"https://kontakt.az/honor-x6c-6-256-gb-moonlight-white",
"https://kontakt.az/honor-x6c-6-256-gb-ocean-cyan",
"https://kontakt.az/honor-x7-4-gb-128-gb-black",
"https://kontakt.az/honor-x7-4gb-128gb-silver",
"https://kontakt.az/honor-x7a-4-128-gb-midnight-black",
"https://kontakt.az/honor-x7a-4-128-gb-ocean-blue",
"https://kontakt.az/honor-x7a-4-128-gb-titanium-silver",
"https://kontakt.az/honor-x7a-plus-6-128-gb-midnight-black",
"https://kontakt.az/honor-x7a-plus-6-128-gb-ocean-blue",
"https://kontakt.az/honor-x7a-plus-6-128-gb-titanium-silver",
"https://kontakt.az/honor-x7b-8-128-gb-emerald-green",
"https://kontakt.az/honor-x7b-8-128-gb-flowing-silver",
"https://kontakt.az/honor-x7b-8-128-gb-midnight-black",
"https://kontakt.az/honor-x7c-6-128-gb-forest-green",
"https://kontakt.az/honor-x7c-6-128-gb-midnight-black",
"https://kontakt.az/honor-x7c-8-256-gb-forest-green",
"https://kontakt.az/honor-x7c-8-256-gb-midnight-black",
"https://kontakt.az/honor-x7c-8-256-gb-moonlight-white",
"https://kontakt.az/honor-x7d-8-128-gb-desert-gold",
"https://kontakt.az/honor-x7d-8-128-gb-desert-gold-68bf1da9c8118",
"https://kontakt.az/honor-x7d-8-128-gb-meteor-silver",
"https://kontakt.az/honor-x7d-8-128-gb-velvet-black",
"https://kontakt.az/honor-x7d-8-256-gb-meteor-silver",
"https://kontakt.az/honor-x7d-8-256-gb-velvet-black",
"https://kontakt.az/honor-x8-6-128-gb-silver",
"https://kontakt.az/honor-x8-6gb-128gb-black",
"https://kontakt.az/honor-x8-6gb-128gb-blue",
"https://kontakt.az/honor-x8a-6-128-cyan-lake",
"https://kontakt.az/honor-x8a-6-128-gb-titanium-silver",
"https://kontakt.az/honor-x8a-6-128gb-midnight-black",
"https://kontakt.az/honor-x8b-8-128-gb-glamorous-green",
"https://kontakt.az/honor-x8b-8-128-gb-midnight-black",
"https://kontakt.az/honor-x8b-8-128-gb-titanium-silver",
"https://kontakt.az/honor-x8b-8-256-gb-glamorous-green",
"https://kontakt.az/honor-x8b-8-256-gb-midnight-black",
"https://kontakt.az/honor-x8b-8-256-gb-titanium-silver",
"https://kontakt.az/honor-x8c-8-128-gb-marss-green",
"https://kontakt.az/honor-x8c-8-128-gb-midnight-black",
"https://kontakt.az/honor-x8c-8-128-gb-moonlight-white",
"https://kontakt.az/honor-x8c-8-256-gb-marss-green",
"https://kontakt.az/honor-x8c-8-256-gb-midnight-black",
"https://kontakt.az/honor-x8c-8-256-gb-moonlight-white",
"https://kontakt.az/honor-x9-6gb-128gb-black",
"https://kontakt.az/honor-x9-6gb-128gb-blue",
"https://kontakt.az/honor-x9-6gb-128gb-silver",
"https://kontakt.az/honor-x9a-6-128-gb-emerald-green",
"https://kontakt.az/honor-x9a-6-128-gb-midnight-black",
"https://kontakt.az/honor-x9a-6-128-gb-titanium-silver",
"https://kontakt.az/honor-x9a-8-256-gb-emerald-green",
"https://kontakt.az/honor-x9a-8-256-gb-midnight-black",
"https://kontakt.az/honor-x9b-12-256-gb-midnight-black",
"https://kontakt.az/honor-x9b-12-256-gb-sunrise-orange",
"https://kontakt.az/honor-x9b-8-256-gb-emerald-green",
"https://kontakt.az/honor-x9b-8-256-gb-midnight-black",
"https://kontakt.az/honor-x9b-8-256-gb-sunrise-orange",
"https://kontakt.az/honor-x9c-12-256-gb-jade-cyan",
"https://kontakt.az/honor-x9c-12-256-gb-titanium-black",
"https://kontakt.az/honor-x9c-12-256-gb-titanium-purple",
"https://kontakt.az/honor-x9c-8-256-gb-jade-cyan",
"https://kontakt.az/honor-x9c-8-256-gb-titanium-black",
"https://kontakt.az/honor-x9c-8-256-gb-titanium-purple",
"https://kontakt.az/honor-x9c-smart-8-256-gb-black",
"https://kontakt.az/honor-x9c-smart-8-256-gb-cyan",
"https://kontakt.az/honor-x9c-smart-8-256-gb-white",
"https://kontakt.az/notbuk-honor-magicbook-art-14-mra-521-emerald-green",
"https://kontakt.az/notbuk-honor-magicbook-art-14-mra-721-emerald-green",
"https://kontakt.az/notbuk-honor-magicbook-art-14-mra-721-sunrise-white",
"https://kontakt.az/notbuk-honor-magicbook-pro-x16-dra-54-purple",
"https://kontakt.az/notbuk-honor-magicbook-pro-x16-dra-54-white",
"https://kontakt.az/notbuk-honor-magicbook-x14-ndr-wdh",
"https://kontakt.az/notbuk-honor-magicbook-x14-ndr-wdi",
"https://kontakt.az/notbuk-honor-magicbook-x15-bdr-wdh",
"https://kontakt.az/notbuk-honor-magicbook-x15-bdr-wdi",
"https://kontakt.az/notbuk-honor-magicbook-x16-brn-f56",
"https://kontakt.az/notbuk-honor-magicbook-x16-brn-f56-win11",
"https://kontakt.az/notbuk-honor-magicbook-x16-brn-f58",
"https://kontakt.az/notbuk-honor-magicbook-x16-brn-f58-win11",
"https://kontakt.az/piko-full-glass-honor-9x-black",
"https://kontakt.az/portativ-akustika-honor-choice-portable-bt-speaker-black-vna-00",
"https://kontakt.az/qazan-desti-schafer-new-honor-qara-8699131760420",
"https://kontakt.az/qoruyucu-ortuk-hard-honor-x9b-fata",
"https://kontakt.az/qoruyucu-ortuk-hard-honor-x9b-peruvian-mix",
"https://kontakt.az/qoruyucu-ortuk-hard-honor-x9b-remember",
"https://kontakt.az/qoruyucu-ortuk-hard-honor-x9b-the-beginning",
"https://kontakt.az/qoruyucu-ortuk-honor-90-lite",
"https://kontakt.az/qoruyucu-ortuk-honor-magic6-pro-hard-case-pu-bracket-case-black-nat",
"https://kontakt.az/qoruyucu-ortuk-honor-magic6-pro-hard-case-pu-bracket-case-green-nat",
"https://kontakt.az/qoruyucu-ortuk-honor-x9b-orange",
"https://kontakt.az/qulaqliq-honor-choice-earbuds-x3-gray",
"https://kontakt.az/qulaqliq-honor-choice-earbuds-x3-white",
"https://kontakt.az/qulaqliq-honor-choice-earbuds-x5-lite-white-lst-me00",
"https://kontakt.az/qulaqliq-honor-choice-earbuds-x5-pro-gray-btv-me10",
"https://kontakt.az/qulaqliq-honor-choice-earbuds-x5-pro-whiite-btv-me10",
"https://kontakt.az/qulaqliq-honor-choice-earbuds-x5-white-lctws005",
"https://kontakt.az/qulaqliq-honor-choice-earbuds-x5e-blue-trn-me00",
"https://kontakt.az/qulaqliq-honor-choice-earbuds-x5e-white-trn-me00",
"https://kontakt.az/qulaqliq-honor-choice-earbuds-x7-lite-white",
"https://kontakt.az/qulaqliq-honor-choice-ows-black-orl-me00",
"https://kontakt.az/qulaqliq-honor-earbuds-x3-lite-wt50106-01",
"https://kontakt.az/robot-tozsoran-honor-choce-robot-cleaner-r2s",
"https://kontakt.az/robot-tozsoran-honor-choice-robot-cleaner-r2s-lite",
"https://kontakt.az/robot-tozsoran-honor-choice-robot-cleaner-r2s-plus",
"https://kontakt.az/smartfon-honor",
"https://kontakt.az/telefon-honor",
]

# Simplified Configuration
@dataclass
class ScrapingConfig:
    max_retries: int = 3
    base_delay: float = 4.0
    max_delay: float = 8.0
    timeout: int = 15
    page_load_timeout: int = 20
    headless: bool = True
    session_restart_after: int = 25  # Restart driver after N URLs

config = ScrapingConfig()

class ProgressTracker:
    """Simple progress tracking with file persistence"""
    
    def __init__(self):
        self.progress_file = f"scraping_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.completed_urls = set()
        self.failed_urls = set()
        self.results = []
        self.current_position = 0
        self.load_progress()
    
    def load_progress(self):
        """Load existing progress if available"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.completed_urls = set(data.get('completed_urls', []))
                    self.failed_urls = set(data.get('failed_urls', []))
                    self.results = data.get('results', [])
                    self.current_position = data.get('current_position', 0)
                    logger.info(f"🔄 Resumed: {len(self.completed_urls)} completed, {len(self.failed_urls)} failed")
        except Exception as e:
            logger.warning(f"Could not load progress: {e}")
    
    def save_progress(self):
        """Save current progress"""
        try:
            data = {
                'completed_urls': list(self.completed_urls),
                'failed_urls': list(self.failed_urls),
                'results': self.results,
                'current_position': self.current_position,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save progress: {e}")
    
    def add_result(self, url: str, result: Optional[Dict]):
        """Add scraping result"""
        if result:
            self.results.append(result)
            self.completed_urls.add(url)
            if url in self.failed_urls:
                self.failed_urls.remove(url)
        else:
            self.failed_urls.add(url)
        
        self.current_position += 1
        
        # Save every 5 successful results
        if len(self.results) % 5 == 0:
            self.save_progress()
    
    def get_pending_urls(self, all_urls: List[str]) -> List[str]:
        """Get URLs that still need to be scraped"""
        return [url for url in all_urls if url not in self.completed_urls]

# Simplified User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

class SimpleWebDriver:
    """Simplified WebDriver with better resource management"""
    
    def __init__(self):
        self.driver = None
        self.session_count = 0
        self.max_session_uses = config.session_restart_after
        self.create_driver()
    
    def create_driver(self):
        """Create a clean WebDriver instance"""
        self.quit_driver()
        
        chrome_options = Options()
        
        if config.headless:
            chrome_options.add_argument("--headless=new")
        
        # Essential options only
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        
        # Random user agent
        user_agent = random.choice(USER_AGENTS)
        chrome_options.add_argument(f"--user-agent={user_agent}")
        chrome_options.add_argument("--window-size=1366,768")
        
        # Disable unnecessary features for speed
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set reasonable timeouts
            self.driver.set_page_load_timeout(config.page_load_timeout)
            self.driver.implicitly_wait(5)
            
            # Hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.session_count = 0
            logger.info("✅ WebDriver created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create WebDriver: {e}")
            self.driver = None
            raise
    
    def get_page(self, url: str) -> bool:
        """Navigate to page with proper error handling"""
        try:
            # Restart driver if overused
            if self.session_count >= self.max_session_uses:
                logger.info(f"🔄 Restarting driver after {self.session_count} uses")
                self.create_driver()
            
            if not self.driver:
                return False
            
            self.driver.get(url)
            self.session_count += 1
            return True
            
        except TimeoutException:
            logger.error(f"❌ Page load timeout: {url}")
            return False
        except (InvalidSessionIdException, WebDriverException) as e:
            logger.error(f"❌ WebDriver session error: {e}")
            try:
                self.create_driver()
                if self.driver:
                    self.driver.get(url)
                    self.session_count += 1
                    return True
            except Exception:
                pass
            return False
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False
    
    def quit_driver(self):
        """Safely quit the driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.debug(f"Error quitting driver: {e}")
            finally:
                self.driver = None

def extract_price(soup):
    """Extract price with fallback methods"""
    # Method 1: GTM data
    try:
        gtm_elements = soup.select(".product-gtm-data")
        for gtm_elem in gtm_elements:
            gtm_data = gtm_elem.get("data-gtm")
            if gtm_data:
                try:
                    gtm_json = json.loads(gtm_data)
                    price = gtm_json.get("price")
                    discount = gtm_json.get("discount")
                    if price:
                        return str(price), str(discount) if discount else None
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    
    # Method 2: Price display elements
    price_selectors = [
        ".prodCart__prices strong b",
        ".prodCart__prices b", 
        ".price-final_price .price",
        ".regular-price .price"
    ]
    
    for selector in price_selectors:
        try:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'([\d.,]+)', price_text.replace('₼', '').replace(',', '.'))
                if price_match:
                    return price_match.group(1), None
        except Exception:
            continue
    
    return None, None

def extract_specifications(soup):
    """Extract product specifications"""
    specs = {}
    
    try:
        spec_rows = soup.select(".har .har__row")
        for row in spec_rows:
            title_elem = row.select_one(".har__title")
            value_elem = row.select_one(".har__znach")
            if title_elem and value_elem:
                key = title_elem.get_text(strip=True)
                value = value_elem.get_text(strip=True)
                if key and value and len(key) < 100 and len(value) < 500:
                    specs[key] = value
    except Exception:
        pass
    
    return specs

def extract_images(soup):
    """Extract product images"""
    images = []
    
    try:
        gallery_selectors = [
            ".slider111__thumbs .item",
            ".product-image-gallery .item img"
        ]
        
        for selector in gallery_selectors:
            elements = soup.select(selector)
            for elem in elements:
                if elem.name == 'a':
                    href = elem.get("href")
                    if href and "kontakt.az" in href:
                        images.append(href)
                elif elem.name == 'img':
                    src = elem.get("src") or elem.get("data-src")
                    if src and "kontakt.az" in src:
                        images.append(src)
    except Exception:
        pass
    
    return list(set(images))  # Remove duplicates

def scrape_product(driver: SimpleWebDriver, url: str, attempt: int = 1):
    """Scrape single product with retry logic"""
    
    for retry in range(config.max_retries):
        try:
            logger.info(f"🔍 Scraping [{attempt}] (attempt {retry+1}): {url.split('/')[-1][:50]}")
            
            # Navigate to page
            if not driver.get_page(url):
                if retry < config.max_retries - 1:
                    sleep(random.uniform(3, 6))
                    continue
                else:
                    return None
            
            # Wait for page elements
            try:
                wait = WebDriverWait(driver.driver, config.timeout)
                wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".page-title")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".prodCart__code"))
                    )
                )
            except TimeoutException:
                logger.debug(f"Timeout waiting for page elements")
            
            # Brief wait for dynamic content
            sleep(random.uniform(2, 4))
            
            # Get page source
            html = driver.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract data
            title_elem = soup.select_one(".page-title .base, .page-title, h1")
            title = title_elem.get_text(strip=True) if title_elem else None
            
            sku_elem = soup.select_one(".prodCart__code")
            sku = sku_elem.get_text(strip=True).replace('№', '').strip() if sku_elem else None
            
            price, discount = extract_price(soup)
            
            # Category from breadcrumb
            category = None
            try:
                breadcrumb = soup.select(".breadcrumb a")
                if breadcrumb:
                    category = " / ".join([c.get_text(strip=True) for c in breadcrumb])
            except Exception:
                pass
            
            # Brand
            brand = None
            try:
                brand_elem = soup.select_one(".product-brand-relation-link__brand, [itemprop='brand']")
                if brand_elem:
                    brand = brand_elem.get_text(strip=True)
            except Exception:
                pass
            
            # Specifications
            specs = extract_specifications(soup)
            
            # Images
            images = extract_images(soup)
            
            # Availability
            availability = "In Stock"
            try:
                if soup.select_one(".product-alert-stock__button, .out-of-stock"):
                    availability = "Pre-order / Out of Stock"
            except Exception:
                pass
            
            # Build result
            result = {
                "url": url,
                "title": title,
                "sku": sku,
                "brand": brand,
                "category": category,
                "price": price,
                "discount": discount,
                "availability": availability,
                "specifications": json.dumps(specs, ensure_ascii=False) if specs else None,
                "images": "|".join(images) if images else None,
                "scraped_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Attempt {retry+1} failed: {str(e)}")
            if retry < config.max_retries - 1:
                sleep(random.uniform(4, 8))
                continue
    
    return None

def handle_interrupt(signum, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("\n🛑 Interrupted by user. Saving progress...")
    sys.exit(0)

def main():
    """Main scraping function - single threaded for reliability"""
    if not urls:
        print("❌ No URLs found! Please add URLs to the 'urls' list at the top of the script.")
        return
    
    # Setup interrupt handler
    signal.signal(signal.SIGINT, handle_interrupt)
    
    print("🚀 Starting Enhanced Kontakt.az scraper v3 (Stable)...")
    print(f"📋 Total URLs: {len(urls)}")
    print(f"🎯 Single-threaded for maximum stability")
    print(f"⚡ Delays: {config.base_delay}-{config.max_delay}s")
    print(f"🔄 Driver restart every {config.session_restart_after} URLs")
    
    # Initialize components
    tracker = ProgressTracker()
    driver = None
    
    # Get pending URLs
    pending_urls = tracker.get_pending_urls(urls)
    
    if not pending_urls:
        print("✅ All URLs already completed!")
        return
    
    print(f"📋 Pending URLs: {len(pending_urls)}")
    
    start_time = time.time()
    
    try:
        driver = SimpleWebDriver()
        
        for i, url in enumerate(pending_urls):
            try:
                result = scrape_product(driver, url, i + 1)
                tracker.add_result(url, result)
                
                if result:
                    logger.info(f"✅ [{i+1}/{len(pending_urls)}] {result.get('title', 'Unknown')[:50]}")
                else:
                    logger.warning(f"❌ [{i+1}/{len(pending_urls)}] Failed: {url}")
                
                # Adaptive delay
                if result:
                    delay = random.uniform(config.base_delay, config.max_delay)
                else:
                    delay = random.uniform(config.max_delay, config.max_delay * 1.5)
                
                logger.debug(f"😴 Sleeping {delay:.1f}s")
                sleep(delay)
                
            except KeyboardInterrupt:
                logger.info("🛑 Interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                tracker.add_result(url, None)
    
    finally:
        if driver:
            driver.quit_driver()
        
        # Save final progress
        tracker.save_progress()
        
        # Save results to CSV
        if tracker.results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kontakt_products_v3_{timestamp}.csv"
            
            print(f"\n💾 Saving {len(tracker.results)} products to {filename}")
            
            with open(filename, "w", newline="", encoding="utf-8") as f:
                if tracker.results:
                    writer = csv.DictWriter(f, fieldnames=tracker.results[0].keys())
                    writer.writeheader()
                    writer.writerows(tracker.results)
            
            print(f"✅ Data saved to {filename}")
        
        # Final statistics
        end_time = time.time()
        duration = end_time - start_time
        total_completed = len(tracker.completed_urls)
        total_failed = len(tracker.failed_urls)
        
        print(f"\n📊 Final Summary:")
        print(f"   Total URLs: {len(urls)}")
        print(f"   Completed: {total_completed}")
        print(f"   Failed: {total_failed}")
        if total_completed + total_failed > 0:
            print(f"   Success rate: {total_completed/(total_completed + total_failed)*100:.1f}%")
        print(f"   Duration: {duration/60:.1f} minutes")
        if total_completed > 0:
            print(f"   Average time per URL: {duration/total_completed:.1f}s")

if __name__ == "__main__":
    main()
