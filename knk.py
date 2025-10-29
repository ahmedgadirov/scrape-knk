import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import json
import re
from time import sleep
import random
import time

# List of URLs to scrape
urls = [
"https://kontakt.az/adapter-apple-30w-usb-c-power-a2164-mw2g3zm-a",
"https://kontakt.az/adapter-apple-35w-dual-usb-c-power-a2676-mw2k3zm-a",
"https://kontakt.az/adapter-apple-96w-usb-c-mx0j2zm-a",
"https://kontakt.az/adapter-apple-dual-usb-c-mnwp3zm-a",
"https://kontakt.az/apple-12w-power-adapter-md836",
"https://kontakt.az/apple-12w-usb-adapter-mgn03za-a",
"https://kontakt.az/apple-140w-usb-c-power-adapter-mlyu3zm-a",
"https://kontakt.az/apple-20w-usb-c-adapter-mhje3zm-a",
"https://kontakt.az/apple-30w-usb-c-adapter-macbook-12",
"https://kontakt.az/apple-40mm-black-unity-sport-band-m-l-muq63zm-a",
]

# More realistic browser headers
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
}

def safe_get_text(element):
    """Safely extract text from element"""
    return element.text.strip() if element else None

def extract_price(soup):
    """Extract price with multiple fallback methods"""
    # Method 1: From GTM data
    gtm_data = soup.select_one(".product-gtm-data")
    if gtm_data:
        try:
            gtm_json = json.loads(gtm_data.get("data-gtm", "{}"))
            price = gtm_json.get("price")
            discount = gtm_json.get("discount")
            if price:
                return str(price), str(discount) if discount else None
        except:
            pass
    
    # Method 2: From price elements
    price_elem = soup.select_one(".prodCart__prices strong b, .price")
    if price_elem:
        price_text = price_elem.text.strip()
        price_match = re.search(r'([\d.,]+)', price_text)
        if price_match:
            return price_match.group(1).replace(',', '.'), None
    
    return None, None

def extract_specifications(soup):
    """Extract all specifications from various possible locations"""
    specs = {}
    
    # Method 1: From .har tables
    spec_rows = soup.select(".har .har__row")
    for row in spec_rows:
        title_elem = row.select_one(".har__title")
        value_elem = row.select_one(".har__znach")
        if title_elem and value_elem:
            key = title_elem.text.strip()
            value = value_elem.text.strip()
            if key and value:
                specs[key] = value
    
    # Method 2: From attribute tables (fallback)
    if not specs:
        attr_rows = soup.select(".product-attribute tr, .data.table tr")
        for row in attr_rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                key = cells[0].text.strip()
                value = cells[1].text.strip()
                if key and value:
                    specs[key] = value
    
    return specs

def extract_images(soup):
    """Extract product images from various sources"""
    images = []
    
    # Method 1: From gallery thumbnails
    gallery_images = soup.select(".slider111__thumbs .item")
    for img_link in gallery_images:
        href = img_link.get("href")
        if href and "kontakt.az" in href:
            if href not in images:
                images.append(href)
    
    # Method 2: From main product image
    if not images:
        main_img = soup.select_one(".main-image img, .product-image-photo")
        if main_img:
            src = main_img.get("src") or main_img.get("data-src")
            if src:
                images.append(src)
    
    # Method 3: From all product images
    if not images:
        all_imgs = soup.select(".product-image-container img, .gallery-placeholder img")
        for img in all_imgs:
            src = img.get("src") or img.get("data-src")
            if src and "kontakt.az" in src:
                if src not in images:
                    images.append(src)
    
    return images

def extract_options(soup, option_type="color"):
    """Extract product options (colors, memory, etc.)"""
    options = []
    
    if option_type == "color":
        selectors = [
            ".product-swatch .swatch-option",
            ".swatch-attribute-options .swatch-option",
            "[class*='color'] .swatch-option"
        ]
    elif option_type == "memory":
        selectors = [
            ".swatches-memory span",
            ".prodCartSelectedOptions button",
            "[class*='memory'] span"
        ]
    else:
        return options
    
    for selector in selectors:
        elements = soup.select(selector)
        for elem in elements:
            value = elem.get("title") or elem.text.strip()
            if value and value not in options:
                options.append(value)
        if options:
            break
    
    return options

def extract_related_products(soup):
    """Extract related/bundle products"""
    related = []
    
    # Check multiple possible locations
    selectors = [
        "#slider-related-products .product-item",
        ".related-products .product-item",
        ".block-related .product-item"
    ]
    
    for selector in selectors:
        items = soup.select(selector)
        if items:
            for item in items:
                prod_title = item.select_one(".prodItem__title, .product-item-name")
                prod_sku = item.get("data-sku")
                prod_price = item.select_one(".prodItem__prices b, .price")
                
                if prod_title:
                    related.append({
                        "title": prod_title.text.strip(),
                        "sku": prod_sku,
                        "price": prod_price.text.strip() if prod_price else None
                    })
            break
    
    return related

def scrape_product(session, url):
    """Scrape a single product page with retry logic"""
    max_retries = 2
    timeout = 20
    
    for attempt in range(max_retries + 1):
        try:
            print(f"\n🔍 Scraping: {url}")
            if attempt > 0:
                print(f"   Retry attempt {attempt}/{max_retries}")
                # Longer wait between retries
                sleep_time = random.uniform(5, 10)
                print(f"   Waiting {sleep_time:.1f}s before retry...")
                sleep(sleep_time)
            
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract breadcrumb category
            breadcrumb = soup.select(".breadcrumb a")
            category = " / ".join([c.text.strip() for c in breadcrumb if c.text.strip()])
            
            # Product title
            title_selectors = [
                ".page-title .base",
                ".product-name",
                "h1.page-title",
                "[data-ui-id='page-title-wrapper']"
            ]
            title = None
            for selector in title_selectors:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.text.strip()
                    break
            
            # SKU
            sku_elem = soup.select_one(".prodCart__code, .product-sku, [itemprop='sku']")
            sku = None
            if sku_elem:
                sku = sku_elem.text.strip().replace("SKU:", "").replace("№", "").strip()
            
            # Brand
            brand_elem = soup.select_one(
                ".product-brand-relation-link__brand, [itemprop='brand'], .brand"
            )
            brand = safe_get_text(brand_elem)
            
            # Rating
            rating_elem = soup.select_one(".product-rating, [itemprop='ratingValue']")
            rating = safe_get_text(rating_elem)
            
            # Reviews count
            reviews_elem = soup.select_one(".rating-count-info, [itemprop='reviewCount']")
            reviews_count = safe_get_text(reviews_elem)
            
            # Price and discount
            price, discount = extract_price(soup)
            
            # Specifications
            specs = extract_specifications(soup)
            
            # Images
            images = extract_images(soup)
            
            # Availability
            availability = "In Stock"
            out_of_stock = soup.select_one(".product-alert-stock__button, .out-of-stock")
            if out_of_stock:
                availability = "Pre-order / Out of Stock"
            
            # Warranty
            warranty = specs.get("Zəmanət") or specs.get("Warranty") or specs.get("Гарантия")
            
            # Color options
            colors = extract_options(soup, "color")
            
            # Memory options
            memory_options = extract_options(soup, "memory")
            
            # Related products
            related_products = extract_related_products(soup)
            
            # Installment options
            installment_options = []
            installment_circles = soup.select(".calks__circle")
            for circle in installment_circles:
                period = circle.get("data-period")
                monthly = circle.get("data-mountly-payment")
                if period and monthly:
                    installment_options.append({
                        "period": period,
                        "monthly_payment": monthly
                    })
            
            # Product type detection
            product_type = "Unknown"
            if category:
                cat_lower = category.lower()
                if "telefon" in cat_lower or "smartphone" in cat_lower:
                    product_type = "Smartphone"
                elif "adapter" in cat_lower or "зарядка" in cat_lower:
                    product_type = "Accessory"
                elif "qulaqlıq" in cat_lower or "наушник" in cat_lower:
                    product_type = "Headphones"
                elif "kompüter" in cat_lower or "ноутбук" in cat_lower:
                    product_type = "Computer"
            
            result = {
                "url": url,
                "category": category,
                "product_type": product_type,
                "title": title,
                "sku": sku,
                "brand": brand,
                "price": price,
                "discount": discount,
                "rating": rating,
                "reviews_count": reviews_count,
                "availability": availability,
                "warranty": warranty,
                "colors": "|".join(colors) if colors else None,
                "memory_options": "|".join(memory_options) if memory_options else None,
                "specifications": json.dumps(specs, ensure_ascii=False) if specs else None,
                "images": "|".join(images) if images else None,
                "related_products": json.dumps(related_products, ensure_ascii=False) if related_products else None,
                "installment_options": json.dumps(installment_options, ensure_ascii=False) if installment_options else None,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
            print(f"✅ Success: {title}")
            print(f"   Category: {category}")
            print(f"   SKU: {sku}")
            print(f"   Price: {price}")
            print(f"   Images: {len(images)}")
            print(f"   Specs: {len(specs)}")
            
            return result
            
        except Exception as e:
            if attempt < max_retries:
                print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
                continue
            else:
                print(f"❌ Final failure for {url}: {str(e)}")
                return None

# Main execution
print("🚀 Starting Kontakt.az scraper...")
print(f"📋 URLs to scrape: {len(urls)}")
print("🎯 Using ethical scraping with human-like behavior")

# Create session with headers
session = requests.Session()
session.headers.update(headers)

results = []
failed_urls = []

for i, url in enumerate(urls, 1):
    print(f"\n[{i}/{len(urls)}]")
    result = scrape_product(session, url)
    if result:
        results.append(result)
    else:
        failed_urls.append(url)
    
    # Human-like delay between requests (3-8 seconds)
    if i < len(urls):
        delay = random.uniform(3, 8)
        print(f"⏳ Waiting {delay:.1f}s before next request...")
        sleep(delay)
        
        # Occasional longer break every 5-10 requests
        if i % random.randint(5, 10) == 0:
            long_break = random.uniform(15, 30)
            print(f"💤 Taking a longer break of {long_break:.1f}s...")
            sleep(long_break)

# Save all results to CSV
if results:
    print(f"\n💾 Saving {len(results)} products to CSV...")
    
    with open("kontakt_products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print("✅ Done! Data saved to kontakt_products.csv")
    
    # Save failed URLs for retry if needed
    if failed_urls:
        with open("failed_urls.txt", "w", encoding="utf-8") as f:
            for url in failed_urls:
                f.write(url + "\n")
        print(f"📝 Failed URLs saved to failed_urls.txt for retry")
    
    print(f"\n📊 Summary:")
    print(f"   Total URLs: {len(urls)}")
    print(f"   Successful: {len(results)}")
    print(f"   Failed: {len(failed_urls)}")
    if failed_urls:
        print(f"   Failed URLs: {', '.join(failed_urls)}")
else:
    print("\n⚠️ No data was scraped!")
