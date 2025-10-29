#!/usr/bin/env python3
"""
knk_chromium_manjaro.py
Threaded, resilient Kontakt.az scraper optimized for Chromium on Manjaro Linux.
Features: webdriver-manager, UA rotation, optional proxy support, atomic progress saving.
"""
import os
import sys
import json
import csv
import time
import random
import logging
import signal
import threading
import queue
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import re

# Selenium + webdriver-manager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, InvalidSessionIdException

from bs4 import BeautifulSoup

# ----------------- Logging -----------------
LOG_FILENAME = f"scraper_chromium_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(threadName)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(LOG_FILENAME)]
)
logger = logging.getLogger(__name__)

# ----------------- Config -----------------
DEFAULT_CONFIG = {
    "threads": 3,
    "max_retries": 3,
    "base_delay": 3.0,
    "max_delay": 6.0,
    "timeout": 12,
    "page_load_timeout": 25,
    "headless": True,
    "restart_after": 30,
    "ua_rotate_after": 5,
    "progress_file": "progress.json",
    "results_csv": "kontakt_products_chromium.csv",
    "use_proxies": False,
    "proxy_cycle_after": 10,
    "human_scroll": True,
    "chromium_path": "/usr/bin/chromium"  # Default Chromium path on Manjaro
}

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# ----------------- Helpers -----------------
def atomic_write_json(path: str, data: dict):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def load_json_safe(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load {path}: {e}")
        return default

def find_chromium_binary():
    """Find Chromium binary on Manjaro/Arch Linux systems."""
    possible_paths = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found browser binary at: {path}")
            return path
    
    logger.warning("Could not find Chromium/Chrome binary, will use system default")
    return None

def find_chromedriver():
    """Find chromedriver on Manjaro/Arch Linux systems."""
    possible_paths = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
        os.path.expanduser("~/.local/bin/chromedriver")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found chromedriver at: {path}")
            return path
    
    return None

# ----------------- Dataclasses -----------------
@dataclass
class ScraperConfig:
    threads: int = DEFAULT_CONFIG["threads"]
    max_retries: int = DEFAULT_CONFIG["max_retries"]
    base_delay: float = DEFAULT_CONFIG["base_delay"]
    max_delay: float = DEFAULT_CONFIG["max_delay"]
    timeout: int = DEFAULT_CONFIG["timeout"]
    page_load_timeout: int = DEFAULT_CONFIG["page_load_timeout"]
    headless: bool = DEFAULT_CONFIG["headless"]
    restart_after: int = DEFAULT_CONFIG["restart_after"]
    ua_rotate_after: int = DEFAULT_CONFIG["ua_rotate_after"]
    progress_file: str = DEFAULT_CONFIG["progress_file"]
    results_csv: str = DEFAULT_CONFIG["results_csv"]
    use_proxies: bool = DEFAULT_CONFIG["use_proxies"]
    proxy_cycle_after: int = DEFAULT_CONFIG["proxy_cycle_after"]
    human_scroll: bool = DEFAULT_CONFIG["human_scroll"]
    chromium_path: str = DEFAULT_CONFIG["chromium_path"]

# ----------------- Progress Manager -----------------
class ProgressManager:
    def __init__(self, path: str):
        self.path = path
        self.lock = threading.Lock()
        self.data = {"completed": [], "failed": [], "results": [], "pos": 0, "timestamp": None}
        self._load()

    def _load(self):
        saved = load_json_safe(self.path, None)
        if saved:
            self.data.update(saved)
            logger.info(f"Loaded progress: {len(self.data['completed'])} completed, {len(self.data['failed'])} failed")

    def save(self):
        with self.lock:
            self.data["timestamp"] = datetime.now().isoformat()
            atomic_write_json(self.path, self.data)

    def add_result(self, url: str, result: Optional[dict]):
        with self.lock:
            if result:
                self.data["results"].append(result)
                if url not in self.data["completed"]:
                    self.data["completed"].append(url)
                if url in self.data["failed"]:
                    self.data["failed"].remove(url)
            else:
                if url not in self.data["failed"]:
                    self.data["failed"].append(url)
            self.data["pos"] += 1
            if (len(self.data["results"]) % 5) == 0:
                self.save()

# ----------------- Simple rotating proxy manager -----------------
class ProxyPool:
    def __init__(self, proxies: List[str]):
        self.proxies = proxies or []
        self.lock = threading.Lock()
        self.idx = 0

    def get(self):
        with self.lock:
            if not self.proxies:
                return None
            p = self.proxies[self.idx % len(self.proxies)]
            self.idx += 1
            return p

# ----------------- Thread-safe queue worker -----------------
class Worker(threading.Thread):
    def __init__(self, name: str, q: queue.Queue, config: ScraperConfig, progress: ProgressManager,
                 proxies: ProxyPool = None, all_urls_count: int = 0):
        super().__init__(name=name)
        self.q = q
        self.config = config
        self.progress = progress
        self.proxies = proxies
        self.driver = None
        self.uses = 0
        self.all_urls_count = all_urls_count
        self.stop_event = threading.Event()
        self.ua_switch_counter = 0
        self.current_ua = random.choice(USER_AGENTS)

    def human_scroll(self):
        try:
            if not self.driver:
                return
            body_h = self.driver.execute_script("return document.body.scrollHeight")
            viewport = random.randint(600, 1000)
            steps = random.randint(2, 6)
            for s in range(steps):
                y = int((body_h - viewport) * (s + 1) / steps)
                self.driver.execute_script(f"window.scrollTo(0, {y});")
                time.sleep(random.uniform(0.3, 0.9))
            self.driver.execute_script("window.scrollTo(0, 0);")
        except Exception:
            pass

    def create_driver(self, proxy: Optional[str] = None):
        try:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None

            chrome_options = Options()
            
            # Set Chromium binary location
            chromium_binary = find_chromium_binary()
            if chromium_binary:
                chrome_options.binary_location = chromium_binary
            
            # Headless mode
            if self.config.headless:
                chrome_options.add_argument("--headless=new")
            
            # Essential arguments for Chromium on Linux
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            
            # Randomize viewport
            w = random.choice([1200, 1366, 1400, 1536, 1920])
            h = random.choice([700, 768, 800, 900, 1080])
            chrome_options.add_argument(f"--window-size={w},{h}")

            # Rotate user agent
            self.current_ua = random.choice(USER_AGENTS)
            chrome_options.add_argument(f"--user-agent={self.current_ua}")

            # Disable images for faster loading
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Proxy support
            if proxy:
                chrome_options.add_argument(f'--proxy-server={proxy}')

            # Try to find local chromedriver first, otherwise use webdriver-manager
            chromedriver_path = find_chromedriver()
            
            if chromedriver_path:
                service = ChromeService(executable_path=chromedriver_path)
                logger.info(f"Using local chromedriver: {chromedriver_path}")
            else:
                # Fall back to webdriver-manager
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = ChromeService(ChromeDriverManager().install())
                    logger.info("Using webdriver-manager to download chromedriver")
                except ImportError:
                    logger.error("webdriver-manager not installed. Install with: pip install webdriver-manager")
                    raise
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.config.page_load_timeout)
            self.driver.implicitly_wait(4)
            
            # Hide webdriver flag
            try:
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                    """
                })
            except Exception:
                pass

            self.uses = 0
            logger.info(f"Created WebDriver with Chromium (UA: {self.current_ua[:50]}...)")
            
        except Exception as e:
            logger.error(f"Failed to create driver: {e}")
            self.driver = None
            raise

    def run(self):
        proxy = None
        if self.proxies:
            proxy = self.proxies.get()
        
        try:
            self.create_driver(proxy)
        except Exception:
            logger.error("Initial driver creation failed, worker exiting.")
            return

        while not self.stop_event.is_set():
            try:
                url = self.q.get_nowait()
            except queue.Empty:
                break

            success = None
            for attempt in range(self.config.max_retries):
                try:
                    if not self.driver:
                        proxy = self.proxies.get() if self.proxies else None
                        self.create_driver(proxy)

                    self.ua_switch_counter += 1
                    if self.ua_switch_counter >= self.config.ua_rotate_after:
                        self.ua_switch_counter = 0
                        proxy = self.proxies.get() if self.proxies else None
                        try:
                            self.create_driver(proxy)
                        except Exception:
                            pass

                    logger.info(f"Scraping: {url} (attempt {attempt+1})")
                    
                    # Set a hard timeout for page loading
                    start_time = time.time()
                    self.driver.get(url)
                    self.uses += 1
                    
                    # Check if we're taking too long
                    if time.time() - start_time > self.config.page_load_timeout:
                        logger.warning(f"Page load exceeded timeout for {url}")
                        raise TimeoutException("Page load timeout")

                    try:
                        wait = WebDriverWait(self.driver, self.config.timeout)
                        # Wait for page to be ready
                        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                        # Give it a moment for dynamic content
                        time.sleep(1)
                    except TimeoutException:
                        logger.debug("Page load wait timed out (continuing)")

                    if self.config.human_scroll:
                        self.human_scroll()

                    html = self.driver.page_source
                    soup = BeautifulSoup(html, "html.parser")

                    result = self.parse_product(soup, url)
                    self.progress.add_result(url, result)
                    success = True
                    break

                except (TimeoutException, WebDriverException, InvalidSessionIdException) as e:
                    logger.error(f"WebDriver error scraping {url}: {e}")
                    try:
                        proxy = self.proxies.get() if self.proxies else None
                        self.create_driver(proxy)
                    except Exception:
                        time.sleep(random.uniform(2, 5))
                except Exception as e:
                    logger.error(f"Unexpected error scraping {url}: {e}")
                    time.sleep(random.uniform(2, 5))

            if not success:
                logger.warning(f"Failed after retries: {url}")
                self.progress.add_result(url, None)

            delay = random.uniform(self.config.base_delay, self.config.max_delay)
            time.sleep(delay)
            self.q.task_done()

            if self.uses >= self.config.restart_after:
                try:
                    proxy = self.proxies.get() if self.proxies else None
                    self.create_driver(proxy)
                except Exception:
                    pass

        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass
        logger.info("Worker finished")

    def parse_product(self, soup, url):
        def safe_text(sel):
            try:
                el = soup.select_one(sel)
                return el.get_text(strip=True) if el else None
            except Exception:
                return None

        title = safe_text(".page-title .base, .page-title, h1")
        sku = safe_text(".prodCart__code")
        if sku:
            sku = sku.replace("№", "").strip()
        
        price = None
        discount = None
        
        try:
            gtm = soup.select_one(".product-gtm-data")
            if gtm and gtm.get("data-gtm"):
                try:
                    jd = json.loads(gtm.get("data-gtm"))
                    price = str(jd.get("price"))
                    discount = str(jd.get("discount")) if jd.get("discount") else None
                except Exception:
                    pass
        except Exception:
            pass

        if not price:
            price_selectors = [
                ".prodCart__prices strong b", 
                ".prodCart__prices b", 
                ".price-final_price .price", 
                ".regular-price .price"
            ]
            for sel in price_selectors:
                txt = safe_text(sel)
                if txt:
                    m = re.search(r'([\d.,]+)', txt.replace('₼', '').replace(',', '.'))
                    if m:
                        price = m.group(1)
                        break

        specs = {}
        try:
            rows = soup.select(".har .har__row")
            for r in rows:
                k = r.select_one(".har__title")
                v = r.select_one(".har__znach")
                if k and v:
                    specs[k.get_text(strip=True)] = v.get_text(strip=True)
        except Exception:
            pass

        images = []
        try:
            for sel in [".slider111__thumbs .item", ".product-image-gallery .item img"]:
                for el in soup.select(sel):
                    if el.name == "a":
                        href = el.get("href")
                        if href:
                            images.append(href)
                    else:
                        src = el.get("src") or el.get("data-src")
                        if src:
                            images.append(src)
            images = list(dict.fromkeys(images))
        except Exception:
            pass

        availability = "In Stock"
        try:
            if soup.select_one(".product-alert-stock__button, .out-of-stock"):
                availability = "Pre-order / Out of Stock"
        except Exception:
            pass

        category = None
        try:
            bc = soup.select(".breadcrumb a")
            if bc:
                category = " / ".join([x.get_text(strip=True) for x in bc])
        except Exception:
            pass

        brand = None
        try:
            be = soup.select_one(".product-brand-relation-link__brand, [itemprop='brand']")
            if be:
                brand = be.get_text(strip=True)
        except Exception:
            pass

        return {
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

# ----------------- Main -----------------
def main(urls: List[str], config_path: str = "config.json", proxies_path: str = "proxies.json"):
    user_conf = load_json_safe(config_path, {})
    conf = ScraperConfig(**{**DEFAULT_CONFIG, **user_conf})

    proxies_list = []
    if conf.use_proxies:
        proxies_list = load_json_safe(proxies_path, [])
    proxy_pool = ProxyPool(proxies_list) if proxies_list else None

    progress = ProgressManager(conf.progress_file)

    q = queue.Queue()
    pending = [u for u in urls if u not in progress.data["completed"]]
    for u in pending:
        q.put(u)

    logger.info(f"Total URLs: {len(urls)}, Pending: {q.qsize()}, Threads: {conf.threads}")
    logger.info(f"Running on Manjaro Linux with Chromium")

    stop_event = threading.Event()
    
    def sigint(signum, frame):
        logger.info("SIGINT received, will stop after current tasks.")
        stop_event.set()
    
    signal.signal(signal.SIGINT, sigint)

    workers = []
    for i in range(conf.threads):
        w = Worker(
            name=f"Worker-{i+1}", 
            q=q, 
            config=conf, 
            progress=progress, 
            proxies=proxy_pool, 
            all_urls_count=len(urls)
        )
        w.daemon = True
        workers.append(w)
        w.start()

    try:
        while any(w.is_alive() for w in workers):
            if stop_event.is_set():
                logger.info("Stop event set - telling workers to finish.")
                for w in workers:
                    w.stop_event.set()
                break
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt - telling workers to stop.")
        for w in workers:
            w.stop_event.set()

    q.join()

    logger.info("Saving final progress and CSV.")
    progress.save()

    if progress.data["results"]:
        csv_file = conf.results_csv
        write_header = not os.path.exists(csv_file)
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=progress.data["results"][0].keys())
            if write_header:
                writer.writeheader()
            writer.writerows(progress.data["results"])
        logger.info(f"Wrote {len(progress.data['results'])} results to {csv_file}")

    logger.info("All done.")

if __name__ == "__main__":
    urls_file = "urls.json"
    urls = load_json_safe(urls_file, None)
    if not urls:
        urls = [
            "https://kontakt.az/adapter-apple-30w-usb-c-power-a2164-mw2g3zm-a",
            "https://kontakt.az/adapter-apple-35w-dual-usb-c-power-a2676-mw2k3zm-a"
        ]
    main(urls)