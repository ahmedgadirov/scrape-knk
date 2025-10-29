#!/usr/bin/env python3
"""
Quick test to verify WebDriver creation works with the updated ChromeDriver
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys

def test_webdriver():
    """Test WebDriver creation and basic functionality"""
    print("🔧 Testing WebDriver creation...")
    
    try:
        # Create Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Create driver
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ WebDriver created successfully!")
        
        # Test basic navigation
        driver.get("https://example.com")
        title = driver.title
        print(f"✅ Page navigation works: {title}")
        
        # Test current URL
        current_url = driver.current_url
        print(f"✅ URL access works: {current_url}")
        
        # Cleanup
        driver.quit()
        print("✅ WebDriver cleanup successful!")
        
        print("\n🎉 All WebDriver tests PASSED! Your scraper should work properly now.")
        return True
        
    except Exception as e:
        print(f"❌ WebDriver test FAILED: {str(e)}")
        print("\nThis indicates there's still an issue with ChromeDriver.")
        print("Try running: brew reinstall chromedriver")
        return False

if __name__ == "__main__":
    success = test_webdriver()
    sys.exit(0 if success else 1)
