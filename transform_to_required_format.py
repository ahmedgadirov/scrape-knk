#!/usr/bin/env python3
"""
Transform scraped Kontakt.az data to required database format
"""

import pandas as pd
import json
import re
import sys
from datetime import datetime
from urllib.parse import urlparse
import os
import requests
import time
import uuid
import hashlib

# CloudFlare Configuration
CLOUDFLARE_ACCOUNT_ID = 'c49da900168b8b1a0d8e253af01d9c99'
CLOUDFLARE_API_TOKEN = 'aMYkdEy_OYjeg88bGrITlAHf6pNe9W2HIItUcYmJ'
CLOUDFLARE_ACCOUNT_HASH = '6xZ2gdbIq4j34kSGM6PEuA'
CLOUDFLARE_API_URL = f'https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/images/v1'

# Image upload statistics
upload_stats = {'success': 0, 'failed': 0, 'cached': 0}

def enable_flexible_variants():
    """Enable flexible variants for CloudFlare Images"""
    url = f'https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/images/v1/config'
    headers = {
        'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'flexible_variants': True
    }
    
    try:
        response = requests.patch(url, json=data, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get('success', False)
        else:
            print(f"⚠️  Warning: Failed to enable flexible variants (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"⚠️  Warning: Error enabling flexible variants: {e}")
        return False

def upload_image_to_cloudflare(image_url):
    """Upload a single image to CloudFlare and return the optimized URL"""
    if not image_url or image_url.strip() == "":
        return image_url
    
    # Check if it's already a CloudFlare URL
    if 'imagedelivery.net' in image_url:
        upload_stats['cached'] += 1
        return image_url
    
    max_retries = 5
    retry_delay = 1.0  # Start with 1 second delay
    
    for attempt in range(max_retries):
        try:
            # Generate boundary for multipart form data
            boundary = str(uuid.uuid4())
            
            # Create multipart form data payload
            payload_parts = []
            payload_parts.append(f'--{boundary}')
            payload_parts.append('Content-Disposition: form-data; name="url"')
            payload_parts.append('')
            payload_parts.append(image_url)
            payload_parts.append(f'--{boundary}')
            payload_parts.append('Content-Disposition: form-data; name="metadata"')
            payload_parts.append('')
            payload_parts.append('{"source": "python_transform"}')
            payload_parts.append(f'--{boundary}')
            payload_parts.append('Content-Disposition: form-data; name="requireSignedURLs"')
            payload_parts.append('')
            payload_parts.append('false')
            payload_parts.append(f'--{boundary}--')
            
            payload = '\r\n'.join(payload_parts)
            
            headers = {
                'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            }
            
            response = requests.post(
                CLOUDFLARE_API_URL, 
                data=payload.encode('utf-8'),
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    image_id = response_data['result']['id']
                    flexible_url = f'https://imagedelivery.net/{CLOUDFLARE_ACCOUNT_HASH}/{image_id}/w=auto,q=auto,f=auto'
                    upload_stats['success'] += 1
                    return flexible_url
                else:
                    error_msg = response_data.get('errors', [{}])[0].get('message', 'Unknown error')
                    print(f"   ⚠️  CloudFlare API error: {error_msg}")
                    break
                    
            elif response.status_code == 429:  # Rate limit
                if attempt < max_retries - 1:
                    print(f"   ⏳ Rate limited, retrying in {retry_delay}s... (attempt {attempt + 1})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    print(f"   ⚠️  Rate limit exceeded, using original URL")
                    break
            else:
                print(f"   ⚠️  HTTP error {response.status_code}, using original URL")
                break
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"   ⏳ Timeout, retrying in {retry_delay}s... (attempt {attempt + 1})")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                print(f"   ⚠️  Upload timeout, using original URL")
                break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"   ⏳ Error: {e}, retrying in {retry_delay}s... (attempt {attempt + 1})")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                print(f"   ⚠️  Upload failed: {e}, using original URL")
                break
    
    # If we get here, all retries failed - use original URL as fallback
    upload_stats['failed'] += 1
    return image_url

def process_all_images(images_str, product_title=""):
    """Process and upload all images for a product"""
    images_str = str(images_str) if images_str is not None and str(images_str) != 'nan' else ''
    if not images_str or images_str.strip() == "":
        return "", ""
    
    # Split images by pipe separator
    original_images = [img.strip() for img in images_str.split("|") if img.strip()]
    
    if not original_images:
        return "", ""
    
    # Upload all images to CloudFlare
    cloudflare_images = []
    for i, img_url in enumerate(original_images):
        if img_url:
            print(f"   📤 Uploading image {i+1}/{len(original_images)} for: {product_title[:40]}...")
            cf_url = upload_image_to_cloudflare(img_url)
            cloudflare_images.append(cf_url)
    
    if not cloudflare_images:
        return "", ""
    
    first_image = cloudflare_images[0]
    more_images = ";".join(cloudflare_images)  # All images including first
    
    return first_image, more_images

def clean_text(text):
    """Clean text for use in slugs and tags"""
    if not text:
        return ""
    # Remove special characters, keep alphanumeric and spaces
    cleaned = re.sub(r'[^\w\s-]', '', text)
    return cleaned.strip()

def create_slug(title):
    """Create URL-friendly slug from title"""
    if not title:
        return ""
    
    slug = title.lower()
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug

def create_tags(title, category, brand):
    """Create hashtags from title, category, and brand"""
    tags = []
    
    # Add brand (handle NaN values)
    brand_str = str(brand) if brand is not None and str(brand) != 'nan' else ''
    if brand_str and brand_str.strip():
        tags.append(f"#{brand_str.strip()}")
    
    # Extract key terms from title
    title_str = str(title) if title is not None and str(title) != 'nan' else ''
    if title_str:
        # Common product terms to extract
        terms = re.findall(r'\b(?:Galaxy|iPhone|Samsung|S25|Ultra|FE|Plus|\d+GB|\d+TB|\w+\s?GB)\b', title_str, re.IGNORECASE)
        for term in terms:
            clean_term = term.replace(' ', '')
            if clean_term and len(clean_term) > 1:
                tags.append(f"#{clean_term}")
    
    return " ".join(tags[:10])  # Limit to 10 tags

def extract_color(title, specs_json):
    """Extract color from title or specifications"""
    color = ""
    
    # Try from specifications first
    specs_str = str(specs_json) if specs_json is not None and str(specs_json) != 'nan' else ''
    if specs_str:
        try:
            specs = json.loads(specs_str)
            color = specs.get("Rəng", "")
            if color and str(color).strip():
                return str(color).strip()
        except:
            pass
    
    # Fallback: extract from title
    title_str = str(title) if title is not None and str(title) != 'nan' else ''
    if title_str:
        # Common colors in product titles
        colors = ['Black', 'White', 'Silver', 'Blue', 'Gray', 'Grey', 'Gold', 'Red', 'Green', 'Purple', 'Pink', 'Yellow', 'Orange', 'Titanium', 'Mint', 'Navy', 'Ice']
        title_lower = title_str.lower()
        for c in colors:
            if c.lower() in title_lower:
                return c
    
    return ""

def extract_size(title, specs_json):
    """Extract storage size from title or specifications"""
    # Try from specifications first
    specs_str = str(specs_json) if specs_json is not None and str(specs_json) != 'nan' else ''
    if specs_str:
        try:
            specs = json.loads(specs_str)
            storage = specs.get("Daxili yaddaş", "")
            if storage and str(storage).strip():
                return str(storage).strip()
        except:
            pass
    
    # Fallback: extract from title
    title_str = str(title) if title is not None and str(title) != 'nan' else ''
    if title_str:
        # Look for storage patterns like 128GB, 256 GB, 1TB etc
        storage_match = re.search(r'(\d+\s?(?:GB|TB))', title_str, re.IGNORECASE)
        if storage_match:
            return storage_match.group(1)
    
    return ""

def format_attributes(specs_json):
    """Format specifications as semicolon-separated key:value pairs"""
    specs_str = str(specs_json) if specs_json is not None and str(specs_json) != 'nan' else ''
    if not specs_str:
        return ""
    
    try:
        specs = json.loads(specs_str)
        formatted_specs = []
        
        for key, value in specs.items():
            if key and value and str(value).strip():
                # Clean up the key-value pair
                clean_key = str(key).strip()
                clean_value = str(value).strip()
                formatted_specs.append(f"{clean_key}:{clean_value}")
        
        return ";".join(formatted_specs)
    except:
        return ""

def format_images(images_str):
    """Format images as 'image1, image1;image2;image3;...'"""
    images_str = str(images_str) if images_str is not None and str(images_str) != 'nan' else ''
    if not images_str or images_str.strip() == "":
        return "", ""
    
    # Split images by pipe separator
    images = [img.strip() for img in images_str.split("|") if img.strip()]
    
    if not images:
        return "", ""
    
    first_image = images[0]
    
    # Format: image = first_image, more_images = first_image;image2;image3;...
    more_images = ";".join(images)  # All images including first
    
    return first_image, more_images

def calculate_cost_price(price, discount):
    """Calculate cost price (price - discount)"""
    try:
        # Handle NaN values
        price_str = str(price) if price is not None and str(price) != 'nan' else '0'
        discount_str = str(discount) if discount is not None and str(discount) != 'nan' else '0'
        
        price_val = float(price_str) if price_str else 0
        discount_val = float(discount_str) if discount_str else 0
        return price_val - discount_val
    except:
        return price_str if price_str else ""

def safe_str(value, default=''):
    """Safely convert value to string, handling NaN"""
    if value is None or str(value) == 'nan':
        return default
    return str(value)

def transform_row(row):
    """Transform a single row to required format"""
    # Parse specifications (handle NaN)
    specs_json = safe_str(row.get('specifications', ''))
    
    # Extract color and size
    color = extract_color(row.get('title', ''), specs_json)
    size = extract_size(row.get('title', ''), specs_json)
    
    # Process and upload images to CloudFlare
    product_title = safe_str(row.get('title', ''))
    first_image, more_images = process_all_images(row.get('images', ''), product_title)
    
    # Create slug and tags
    slug = create_slug(row.get('title', ''))
    tags = create_tags(row.get('title', ''), row.get('category', ''), row.get('brand', ''))
    
    # Calculate cost price
    cost_price = calculate_cost_price(row.get('price'), row.get('discount'))
    
    # Format attributes
    attributes = format_attributes(specs_json)
    
    # Determine stock status
    availability_str = safe_str(row.get('availability', ''))
    is_stock = 1 if availability_str.lower() == 'in stock' else 0
    
    discount_str = safe_str(row.get('discount', '0'))
    try:
        is_discount = 1 if float(discount_str) > 0 else 0
    except:
        is_discount = 0
    
    # Build transformed row with safe string conversion
    transformed = {
        'sku': safe_str(row.get('sku', '')),
        'is_added': 1,
        'is_updated': '`',
        'category': safe_str(row.get('category', ''), '`'),
        'cost_price': cost_price,
        'brand': safe_str(row.get('brand', ''), '`'),
        'type': '`',
        'attributes': attributes,
        'is_main_product': 0,
        'main_product': '`',
        'slug': slug,
        'tags': tags,
        'name': safe_str(row.get('title', '')),
        'color': color,
        'image': first_image,
        'more_images': more_images,
        'description': safe_str(row.get('title', '')),  # Using title as description for now
        'size': size,
        'price': safe_str(row.get('price', '')),
        'discount_type': '`',
        'discount_value': safe_str(row.get('discount', ''), '`'),
        'pack_size': '`',
        'tax': '`',
        'max_quantity': 5,
        'stock_count': 50,
        'variant_status': 1,
        'status': 1,
        'is_stock': is_stock,
        'is_discount': is_discount,
        'is_hot': 0,
        'is_best': 0,
        'is_most': 0,
        'intrastat': '`'
    }
    
    return transformed

def main():
    """Main transformation function"""
    input_file = 'kontakt_products_v3_20251029_175836.csv'
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        print("Available files:")
        for f in os.listdir('.'):
            if f.endswith('.csv'):
                print(f"   {f}")
        return
    
    try:
        # Initialize CloudFlare setup
        print(f"🔧 Setting up CloudFlare Images...")
        if enable_flexible_variants():
            print(f"   ✅ Flexible variants enabled")
        else:
            print(f"   ⚠️  Flexible variants setup failed, but continuing...")
        
        # Reset upload statistics
        global upload_stats
        upload_stats = {'success': 0, 'failed': 0, 'cached': 0}
        
        # Read the scraped data
        print(f"\n📖 Reading data from {input_file}...")
        df = pd.read_csv(input_file)
        print(f"   Found {len(df)} records")
        
        # Transform each row with CloudFlare image uploads
        print(f"\n🔄 Starting transformation with CloudFlare auto image uploads...")
        transformed_data = []
        start_time = time.time()
        
        for index, row in df.iterrows():
            product_title = row.get('title', 'Unknown')[:50]
            print(f"\n📦 Processing {index + 1}/{len(df)}: {product_title}...")
            
            transformed = transform_row(row)
            transformed_data.append(transformed)
            
            # Show progress every 10 items
            if (index + 1) % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / (index + 1)
                remaining = (len(df) - index - 1) * avg_time
                print(f"   📊 Progress: {index + 1}/{len(df)} ({((index + 1)/len(df)*100):.1f}%) - ETA: {remaining/60:.1f}min")
                print(f"   📈 Upload stats: ✅ {upload_stats['success']} | ⚠️  {upload_stats['failed']} | 🔄 {upload_stats['cached']}")
        
        # Create output DataFrame
        output_df = pd.DataFrame(transformed_data)
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"kontakt_transformed_cloudflare_{timestamp}.csv"
        
        # Save transformed data
        print(f"\n💾 Saving transformed data to {output_file}...")
        output_df.to_csv(output_file, index=False)
        
        # Final statistics
        total_time = time.time() - start_time
        total_images = upload_stats['success'] + upload_stats['failed'] + upload_stats['cached']
        
        print(f"\n✅ CloudFlare Auto Transformation Complete!")
        print(f"   📊 Records processed: {len(df)} → {len(output_df)}")
        print(f"   ⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"   🖼️  Image uploads:")
        print(f"      ✅ Successful uploads: {upload_stats['success']}")
        print(f"      ⚠️  Failed (using original): {upload_stats['failed']}")
        print(f"      🔄 Already CloudFlare: {upload_stats['cached']}")
        print(f"      📈 Total images processed: {total_images}")
        print(f"   💾 Output file: {output_file}")
        
        # Show sample output
        if transformed_data:
            print(f"\n📄 Sample CloudFlare transformed record:")
            sample = transformed_data[0]
            key_fields = ['sku', 'name', 'image', 'more_images', 'price', 'brand']
            for key in key_fields:
                value = sample.get(key, '')
                if key in ['image', 'more_images'] and value:
                    # Show if it's CloudFlare URL
                    cf_indicator = "☁️  CloudFlare" if 'imagedelivery.net' in str(value) else "🌐 Original"
                    display_value = str(value)[:80] + "..." if len(str(value)) > 80 else value
                    print(f"   {key}: {display_value} ({cf_indicator})")
                else:
                    display_value = str(value)[:80] + "..." if len(str(value)) > 80 else value
                    print(f"   {key}: {display_value}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error during transformation: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
