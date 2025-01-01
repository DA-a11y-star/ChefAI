from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import requests
import os
import time


def scrape_first_google_image(search_query):
    # Set up Selenium WebDriver with headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional)
    chrome_options.add_argument("--no-sandbox")  # Bypass OS-level sandboxing (optional)
    chrome_options.add_argument(
        "--disable-dev-shm-usage"
    )  # Avoid resource issues in some systems
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.google.com/imghp")

    # Search for the query
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)  # Allow the page to load

    try:
        # Locate the image by ID
        first_image = driver.find_elements(By.CSS_SELECTOR, "img.YQ4gaf")[
            0
        ]  # Get 150th image (0-based index)
        img_url = first_image.get_attribute("src") or first_image.get_attribute(
            "data-src"
        )

        # Download the image
        if img_url:
            print(f"Downloading the image: {img_url}")
            return img_url
        else:
            print("Failed to find a valid image URL.")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
