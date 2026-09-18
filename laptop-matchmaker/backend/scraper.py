import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def scrape_amazon_price(laptop_name):
    """
    Attempts to scrape the live price of a laptop from Amazon.in.
    Returns a tuple: (price_in_inr, purchase_link) or (None, None) if blocked/failed.
    """
    # 1. Prepare the query
    query = urllib.parse.quote_plus(laptop_name + " laptop")
    url = f"https://www.amazon.in/s?k={query}"
    
    # 2. Use a disguised User-Agent to avoid immediate bot detection
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check if we got blocked or CAPTCHA'd
        if response.status_code != 200:
            return None, None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. Find the first search result that has a price
        # Amazon usually stores prices in a span with class 'a-price-whole'
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        for result in results:
            price_elem = result.find('span', {'class': 'a-price-whole'})
            link_elem = result.find('a', {'class': 'a-link-normal s-no-outline'})
            
            if price_elem and link_elem:
                # Extract the price text (e.g. "45,999") and clean it
                price_str = price_elem.text.replace(',', '').strip()
                match = re.search(r'\d+', price_str)
                if match:
                    price_inr = int(match.group(0))
                    
                    # Extract the product link
                    href = link_elem.get('href')
                    if href.startswith('/'):
                        purchase_link = f"https://www.amazon.in{href}"
                    else:
                        purchase_link = href
                        
                    return price_inr, purchase_link
                    
        return None, None
        
    except Exception as e:
        print(f"Scraping failed for {laptop_name}: {e}")
        return None, None

if __name__ == "__main__":
    # Quick manual test
    test_laptop = "Dell Inspiron 3567"
    print(f"Testing scraper for: {test_laptop}")
    price, link = scrape_amazon_price(test_laptop)
    print(f"Result -> Price: {price}, Link: {link}")
