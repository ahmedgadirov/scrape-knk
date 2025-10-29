#!/usr/bin/env python3
"""
Test script for knk_enhanced_v3.py
Validates core functionality without requiring actual URLs
"""

import sys
import os
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

# Add current directory to path to import our scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_price_extraction():
    """Test price extraction functionality"""
    print("🧪 Testing price extraction...")
    
    # Import the function
    from knk_enhanced_v3 import extract_price
    
    # Test HTML with GTM data
    html_gtm = '''
    <div class="product-gtm-data" data-gtm='{"price": "299.99", "discount": "50.00"}'>
    </div>
    '''
    soup_gtm = BeautifulSoup(html_gtm, 'html.parser')
    price, discount = extract_price(soup_gtm)
    
    assert price == "299.99", f"Expected 299.99, got {price}"
    assert discount == "50.00", f"Expected 50.00, got {discount}"
    print("✅ GTM price extraction works")
    
    # Test HTML with price display elements
    html_price = '''
    <div class="prodCart__prices">
        <strong><b>₼159.99</b></strong>
    </div>
    '''
    soup_price = BeautifulSoup(html_price, 'html.parser')
    price, discount = extract_price(soup_price)
    
    assert price == "159.99", f"Expected 159.99, got {price}"
    print("✅ Price display extraction works")

def test_specifications_extraction():
    """Test specifications extraction"""
    print("🧪 Testing specifications extraction...")
    
    from knk_enhanced_v3 import extract_specifications
    
    html_specs = '''
    <div class="har">
        <div class="har__row">
            <div class="har__title">Brand</div>
            <div class="har__znach">Apple</div>
        </div>
        <div class="har__row">
            <div class="har__title">Model</div>
            <div class="har__znach">iPhone 15</div>
        </div>
    </div>
    '''
    soup = BeautifulSoup(html_specs, 'html.parser')
    specs = extract_specifications(soup)
    
    assert specs.get("Brand") == "Apple", f"Expected Apple, got {specs.get('Brand')}"
    assert specs.get("Model") == "iPhone 15", f"Expected iPhone 15, got {specs.get('Model')}"
    print("✅ Specifications extraction works")

def test_images_extraction():
    """Test image extraction"""
    print("🧪 Testing image extraction...")
    
    from knk_enhanced_v3 import extract_images
    
    html_images = '''
    <div class="slider111__thumbs">
        <div class="item">
            <a href="https://kontakt.az/image1.jpg">Image 1</a>
        </div>
        <div class="item">
            <a href="https://kontakt.az/image2.jpg">Image 2</a>
        </div>
    </div>
    '''
    soup = BeautifulSoup(html_images, 'html.parser')
    images = extract_images(soup)
    
    assert len(images) == 2, f"Expected 2 images, got {len(images)}"
    assert "https://kontakt.az/image1.jpg" in images, "Image 1 not found"
    assert "https://kontakt.az/image2.jpg" in images, "Image 2 not found"
    print("✅ Image extraction works")

def test_progress_tracker():
    """Test progress tracking functionality"""
    print("🧪 Testing progress tracker...")
    
    from knk_enhanced_v3 import ProgressTracker
    
    # Create a mock tracker
    tracker = ProgressTracker()
    
    # Test adding results
    tracker.add_result("https://example.com/1", {"title": "Test Product"})
    tracker.add_result("https://example.com/2", None)  # Failed
    
    assert len(tracker.completed_urls) == 1, f"Expected 1 completed, got {len(tracker.completed_urls)}"
    assert len(tracker.failed_urls) == 1, f"Expected 1 failed, got {len(tracker.failed_urls)}"
    assert len(tracker.results) == 1, f"Expected 1 result, got {len(tracker.results)}"
    print("✅ Progress tracking works")

def test_webdriver_initialization():
    """Test WebDriver initialization (mocked)"""
    print("🧪 Testing WebDriver initialization...")
    
    # Mock the webdriver to avoid requiring actual Chrome installation
    with patch('knk_enhanced_v3.webdriver.Chrome') as mock_chrome:
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        from knk_enhanced_v3 import SimpleWebDriver
        
        # This should not raise an exception
        driver = SimpleWebDriver()
        assert driver is not None, "Driver creation failed"
        print("✅ WebDriver initialization works")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting knk_enhanced_v3.py functionality tests...\n")
    
    try:
        test_price_extraction()
        test_specifications_extraction() 
        test_images_extraction()
        test_progress_tracker()
        test_webdriver_initialization()
        
        print("\n✅ All tests passed! The scraper core functionality is working correctly.")
        print("📋 You can now add your URLs to the 'urls' list in knk_enhanced_v3.py and run it.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("🔧 Please check the implementation and try again.")
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
