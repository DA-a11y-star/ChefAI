from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import random
from selenium.webdriver.chrome.options import Options
import urllib.parse


def scrape_amazon(search_query):
    """
    Scrapes Amazon for product title, price, URL, and image for the first product found.

    :param search_query: The product to search for (e.g., 'apples')
    :return: A dictionary with product details for the first product found
    """
    # List of user-agent strings
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # Chrome on Windows 10
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Version/13.1.2 Safari/537.36",  # Safari on macOS
        "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",  # Firefox on Linux
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/94.0.992.31 Safari/537.36",  # Edge on Windows 11
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",  # Mobile Chrome on Android
    ]

    # Randomly select a user-agent
    user_agent = random.choice(user_agents)

    # Setup Selenium WebDriver (ensure you have the appropriate ChromeDriver)
    service = Service("/Users/dagemabraham/Downloads/chromedriver")
    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless mode
    chrome_options.add_argument("--no-sandbox")  # Required for some environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Amazon search URL
    base_url = "https://www.amazon.com/s?k="
    search_url = (
        base_url + search_query.replace("%20", "+") + "&i=grocery&crid=13Q2RJZJ0AK9W"
    )

    driver.get(search_url)

    # Random delay between 2 to 5 seconds
    time.sleep(random.uniform(2.0, 5.0))  # Wait for the page to load

    # Use BeautifulSoup to parse the page content
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()  # Close the driver

    # Find the first product element
    product = None
    product_elements = soup.find_all("div", {"data-component-type": "s-search-result"})
    for item in product_elements:
        sponsored_label = item.find(
            "span", {"aria-label": "View Sponsored information or leave ad feedback"}
        )
        if sponsored_label:
            continue  # Skip this product if it's sponsored
        else:
            product = item
            break

    if product:
        # Extract product title
        title = product.h2.text.strip()

        # Extract product price
        price_whole = product.find("span", "a-price-whole")
        price_fraction = product.find("span", "a-price-fraction")
        price = None
        if price_whole and price_fraction:
            price = f"{price_whole.text}{price_fraction.text}"

        # Extract product URL
        link = product.find("a", {"class": "a-link-normal"})["href"]
        full_link = "https://www.amazon.com" + link

        # Extract product image URL
        img_tag = product.find("img", {"class": "s-image"})
        image_url = img_tag["src"] if img_tag else None

        # Return a dictionary with the first product's details
        return {
            "title": title,
            "price": price,
            "url": full_link,
            "image_url": image_url,
        }
    else:
        return None


def grab_amazon():
    for item in ingredients:
        ingredient_url = urllib.parse.quote(item["ingredient"])
        for brand in item["brands"]:
            brand_url = urllib.parse.quote(brand)
            while True:
                search_term = brand_url + ", " + ingredient_url
                result = scrape_amazon(search_term)

                if result:
                    print(f"Title: {result['title']}")
                    print(f"Price: {result['price']}")
                    print(f"URL: {result['url']}")
                    print(f"Image URL: {result['image_url']}")
                    print(
                        "-------------------------------------------------------------------"
                    )
                    break
                else:
                    continue


# Example usage
if __name__ == "__main__":
    ingredients = [
        {
            "ingredient": "All-purpose flour",
            "brands": ["King Arthur Flour", "Gold Medal", "Bob's Red Mill"],
        },
        {
            "ingredient": "Baking soda",
            "brands": ["Arm & Hammer", "Bob's Red Mill", "Clabber Girl"],
        },
        {
            "ingredient": "Unsalted butter",
            "brands": ["Land O'Lakes", "Kerrygold", "Tillamook"],
        },
        {
            "ingredient": "Granulated sugar",
            "brands": ["Domino Sugar", "C&H", "Florida Crystals"],
        },
        {
            "ingredient": "Brown sugar",
            "brands": ["Domino Sugar", "C&H", "Wholesome Sweeteners"],
        },
        {
            "ingredient": "Salt",
            "brands": ["Morton", "Redmond Real Salt", "Himalayan Pink Salt"],
        },
        {
            "ingredient": "Vanilla extract",
            "brands": ["McCormick", "Nielsen-Massey", "Simply Organic"],
        },
        {
            "ingredient": "Eggs",
            "brands": ["Eggland's Best", "Vital Farms", "Happy Egg Co."],
        },
        {
            "ingredient": "Semisweet chocolate chips",
            "brands": ["Ghirardelli", "Nestlé Toll House", "Hershey's"],
        },
    ]

    for item in ingredients:
        ingredient_url = urllib.parse.quote(item["ingredient"])
        for brand in item["brands"]:
            brand_url = urllib.parse.quote(brand)
            while True:
                search_term = brand_url + ", " + ingredient_url
                result = scrape_amazon(search_term)

                if result:
                    print(f"Title: {result['title']}")
                    print(f"Price: {result['price']}")
                    print(f"URL: {result['url']}")
                    print(f"Image URL: {result['image_url']}")
                    print(
                        "-------------------------------------------------------------------"
                    )
                    break
                else:
                    continue
