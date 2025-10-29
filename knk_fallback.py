import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import json
import re
from time import sleep
import random
import time
import logging
from urllib.parse import urlparse

# Enhanced logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# First 5 URLs for testing
urls = [
    "https://kontakt.az/samsung-galaxy-s25-ultra-sm-s938b-12-256-gb-titanium-white-silver",
    "https://kontakt.az/samsung-galaxy-s25-ultra-sm-s938b-12-512-gb-titanium-white-silver",
    "https://kontakt.az/samsung-galaxy-s25-fe-sm-s731-8-128-gb-dark-blue",
    "https://kontakt.az/samsung-galaxy-s25-fe-sm-s731-8-128-gb-black",
    "https://kontakt.az/samsung-galaxy-s25-fe-sm-s731-8-256-gb-black"
]

# Enhanced browser headers with rotation
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

def create_session():
    """Create an enhanced requests session with anti-detection measures"""
    session = requests.Session()
    
    # Random user agent
    user_agent = random.choice(USER_AGENTS)
    
    # Enhanced headers
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9,az;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    }
    
    session.headers.update(headers)
    
    # Set timeouts
    session.timeout = 20
    
    return session

def safe_get_text(element):
    """Safely extract text from element"""
    if not element:
        return None
    try:
        return element.get_text(strip=True) if element else None
    except:
        return None

def extract_price_fallback(soup):
    """Enhanced price extraction using multiple methods"""
    logger.debug("Starting price extraction...")
    
    # Method 1: GTM data (most reliable)
    try:
        gtm_elements = soup.select(".product-gtm-data")
        logger.debug(f"Found {len(gtm_elements)} GTM elements")
        for gtm_elem in gtm_elements:
            gtm_data_attr = gtm_elem.get("data-gtm")
            if gtm_data_attr:
                logger.debug(f"GTM data found: {gtm_data_attr[:100]}...")
                try:
                    gtm_json = json.loads(gtm_data_attr)
                    price = gtm_json.get("price")
                    discount = gtm_json.get("discount")
                    if price:
                        logger.info(f"✅ Price extracted from GTM: {price}")
                        return str(price), str(discount) if discount else None
                except json.JSONDecodeError as e:
                    logger.debug(f"JSON decode error: {e}")
                    continue
    except Exception as e:
        logger.debug(f"GTM extraction failed: {e}")

    # Method 2: Price elements with enhanced selectors
    price_selectors = [
        ".prodCart__prices strong b",
        ".prodCart__prices b", 
        ".prodCart__prices .price",
        ".price-final_price .price",
        ".regular-price .price",
        ".special-price .price",
        ".price-box .price",
        "[data-price-amount]",
        ".price"
    ]
    
    for selector in price_selectors:
        try:
            price_elems = soup.select(selector)
            logger.debug(f"Selector '{selector}': found {len(price_elems)} elements")
            for price_elem in price_elems:
                price_text = price_elem.get_text(strip=True)
                logger.debug(f"Price text: '{price_text}'")
                
                # Extract numeric price
                price_match = re.search(r'([\d.,]+)', price_text.replace('₼', '').replace(' ', ''))
                if price_match:
                    price = price_match.group(1).replace(',', '.')
                    logger.info(f"✅ Price extracted from '{selector}': {price}")
                    return price, None
        except Exception as e:
            logger.debug(f"Price extraction failed for '{selector}': {e}")

    logger.warning("❌ No price found with any method")
    return None, None

def extract_specifications_fallback(soup):
    """Enhanced specification extraction"""
    specs = {}
    logger.debug("Starting specification extraction...")
    
    # Method 1: .har table structure (primary)
    try:
        spec_rows = soup.select(".har .har__row")
        logger.info(f"Found {len(spec_rows)} specification rows in .har structure")
        
        for row in spec_rows:
            title_elem = row.select_one(".har__title")
            value_elem = row.select_one(".har__znach")
            
            if title_elem and value_elem:
                key = title_elem.get_text(strip=True)
                value = value_elem.get_text(strip=True)
                
                # Validate and clean data
                if key and value and len(key) < 100 and len(value) < 500:
                    specs[key] = value
                    logger.debug(f"Spec: {key} = {value}")
        
        if specs:
            logger.info(f"✅ Extracted {len(specs)} specifications via .har method")
            return specs
            
    except Exception as e:
        logger.debug(f"Specification extraction (.har) failed: {e}")

    # Method 2: Generic table structures (fallback)
    table_selectors = [
        ".product-attribute tr",
        ".data.table tr",
        ".additional-attributes tr",
        ".specifications tr",
        ".spec-table tr",
        "table tr"
    ]
    
    for selector in table_selectors:
        try:
            rows = soup.select(selector)
            if rows:
                logger.debug(f"Found {len(rows)} rows with selector: {selector}")
                temp_specs = {}
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        if (key and value and 
                            len(key) < 100 and len(value) < 500 and
                            not key.lower() in ['', 'title', 'name']):
                            temp_specs[key] = value
                
                if temp_specs:
                    logger.info(f"✅ Extracted {len(temp_specs)} specs via {selector}")
                    specs.update(temp_specs)
                    break
                    
        except Exception as e:
            logger.debug(f"Table extraction failed for '{selector}': {e}")
    
    logger.info(f"Total specifications extracted: {len(specs)}")
    return specs

def extract_product_details_fallback(soup):
    """Extract all basic product details"""
    details = {}
    
    # Title extraction with multiple selectors
    title_selectors = [
        ".page-title .base",
        ".page-title",
        "h1.page-title", 
        "[data-ui-id='page-title-wrapper'] .base",
        ".product-name",
        ".product-title",
        "h1"
    ]
    
    for selector in title_selectors:
        elem = soup.select_one(selector)
        if elem:
            title = elem.get_text(strip=True)
            if title and len(title) > 5:
                details['title'] = title
                logger.info(f"✅ Title found: {title[:50]}...")
                break
    
    # SKU extraction
    sku_selectors = [
        ".prodCart__code",
        ".product-sku",
        "[itemprop='sku']",
        ".sku",
        ".product-code"
    ]
    
    for selector in sku_selectors:
        elem = soup.select_one(selector)
        if elem:
            sku_text = elem.get_text(strip=True)
            sku = re.sub(r'^(SKU:|№|Code:)', '', sku_text, flags=re.IGNORECASE).strip()
            if sku:
                details['sku'] = sku
                logger.info(f"✅ SKU found: {sku}")
                break
    
    # Brand extraction
    brand_selectors = [
        ".product-brand-relation-link__brand",
        "[itemprop='brand']",
        ".brand",
        ".product-brand",
        ".manufacturer"
    ]
    
    for selector in brand_selectors:
        elem = soup.select_one(selector)
        if elem:
            brand = elem.get_text(strip=True)
            if brand:
                details['brand'] = brand
                logger.info(f"✅ Brand found: {brand}")
                break
    
    # Category from breadcrumb
    try:
        breadcrumb = soup.select(".breadcrumb a, .breadcrumbs a")
        if breadcrumb:
            category = " / ".join([c.get_text(strip=True) for c in breadcrumb if c.get_text(strip=True)])
            if category:
                details['category'] = category
                logger.info(f"✅ Category found: {category}")
    except Exception as e:
        logger.debug(f"Category extraction failed: {e}")
    
    # Rating and reviews
    rating_elem = soup.select_one(".product-rating, [itemprop='ratingValue']")
    if rating_elem:
        details['rating'] = safe_get_text(rating_elem)
    
    reviews_elem = soup.select_one(".rating-count-info, [itemprop='reviewCount']")
    if reviews_elem:
        details['reviews_count'] = safe_get_text(reviews_elem)
    
    return details

def scrape_product_fallback(session, url):
    """Enhanced product scraping with fallback methods"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🔍 Attempt {attempt + 1}/{max_retries}: {url}")
            
            # Add random delay to mimic human behavior
            if attempt > 0:
                delay = random.uniform(3, 8)
                logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                sleep(delay)
            
            # Make request with timeout
            response = session.get(url, timeout=20)
            response.raise_for_status()
            
            # Check if we got meaningful content
            if len(response.text) < 10000:  # Suspiciously small page
                logger.warning(f"Suspiciously small response ({len(response.text)} chars)")
                raise requests.RequestException("Response too small - possible blocking")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Check for common blocking indicators
            if soup.select_one("title"):
                title_text = soup.select_one("title").get_text().lower()
                if any(indicator in title_text for indicator in ["blocked", "access denied", "captcha", "robot"]):
                    logger.warning(f"Blocking detected in title: {title_text}")
                    raise requests.RequestException("Access blocked")
            
            logger.info("✅ Page fetched successfully, extracting data...")
            
            # Extract product details
            details = extract_product_details_fallback(soup)
            
            # Extract price
            price, discount = extract_price_fallback(soup)
            details['price'] = price
            details['discount'] = discount
            
            # Extract specifications
            specs = extract_specifications_fallback(soup)
            
            # Extract images
            images = []
            try:
                # Gallery images
                gallery_imgs = soup.select(".slider111__thumbs .item")
                for img_link in gallery_imgs:
                    href = img_link.get("href")
                    if href and "kontakt.az" in href and href not in images:
                        images.append(href)
                
                # Fallback to other image sources
                if not images:
                    img_selectors = [".main-image img", ".product-image img"]
                    for selector in img_selectors:
                        imgs = soup.select(selector)
                        for img in imgs:
                            src = img.get("src") or img.get("data-src")
                            if src and "kontakt.az" in src and src not in images:
                                images.append(src)
                                
            except Exception as e:
                logger.debug(f"Image extraction failed: {e}")
            
            # Availability
            availability = "In Stock"
            out_of_stock = soup.select_one(".product-alert-stock__button, .out-of-stock")
            if out_of_stock:
                availability = "Pre-order / Out of Stock"
            
            # Build final result
            result = {
                "url": url,
                "category": details.get('category'),
                "title": details.get('title'),
                "sku": details.get('sku'),
                "brand": details.get('brand'),
                "price": details.get('price'),
                "discount": details.get('discount'),
                "rating": details.get('rating'),
                "reviews_count": details.get('reviews_count'),
                "availability": availability,
                "specifications": json.dumps(specs, ensure_ascii=False) if specs else None,
                "images": "|".join(images) if images else None,
                "fetched_at": datetime.now().isoformat()
            }
            
            # Log success
            success_msg = f"✅ SUCCESS: {details.get('title', 'Unknown')}"
            logger.info(success_msg)
            logger.info(f"   SKU: {details.get('sku', 'N/A')}")
            logger.info(f"   Price: {details.get('price', 'N/A')}")
            logger.info(f"   Specs: {len(specs)} items")
            logger.info(f"   Images: {len(images)} items")
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"❌ Request failed (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                # Exponential backoff
                delay = 2 ** attempt + random.uniform(1, 3)
                logger.info(f"⏳ Backoff delay: {delay:.1f}s")
                sleep(delay)
        except Exception as e:
            logger.error(f"❌ Unexpected error (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                sleep(random.uniform(2, 5))

    logger.error(f"❌ All attempts failed for {url}")
    return None

def main():
    """Main function"""
    print("🚀 Starting Enhanced Fallback Kontakt.az scraper...")
    print(f"📋 URLs to scrape: {len(urls)}")
    print("🎯 Using enhanced requests with anti-detection")
    
    # Create session
    session = create_session()
    
    results = []
    failed_urls = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url.split('/')[-1]}")
        
        result = scrape_product_fallback(session, url)
        if result:
            results.append(result)
        else:
            failed_urls.append(url)
        
        # Human-like delay
        if i < len(urls):
            delay = random.uniform(5, 12)
            print(f"⏳ Waiting {delay:.1f}s before next request...")
            sleep(delay)
    
    # Save results
    if results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kontakt_products_fallback_{timestamp}.csv"
        
        print(f"\n💾 Saving {len(results)} products to {filename}")
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        
        print(f"✅ Data saved to {filename}")
        
        # Summary
        print(f"\n📊 Final Summary:")
        print(f"   Total URLs: {len(urls)}")
        print(f"   Successful: {len(results)}")
        print(f"   Failed: {len(failed_urls)}")
        print(f"   Success rate: {len(results)/len(urls)*100:.1f}%")
        
    else:
        print("\n⚠️ No data was scraped successfully!")
        print("This likely means Kontakt.az is blocking requests.")
        print("Try the Selenium version (knk_enhanced.py) instead.")

if __name__ == "__main__":
    main()
