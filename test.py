from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from youtube_transcript_api import YouTubeTranscriptApi
from webdriver_manager.chrome import ChromeDriverManager
import time


# Function to scrape YouTube search results using Selenium
def search_youtube_video(search_query):
    search_url = (
        f"https://www.youtube.com/results?search_query={'+'.join(search_query.split())}"
    )

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU for headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        # Open YouTube search results page
        driver.get(search_url)
        time.sleep(2)  # Allow time for page to load

        # Find video titles and links
        video_elements = driver.find_elements(By.CSS_SELECTOR, "a#video-title")
        for video in video_elements:
            video_title = video.get_attribute("title")
            video_url = video.get_attribute("href")
            video_id = video_url.split("v=")[-1]
            print(f"Title: {video_title}")
            print(f"Video URL: {video_url}")
            print(f"Video ID: {video_id}")
            return video_id  # Return the first video ID
    except Exception as e:
        print(f"Error while scraping YouTube: {e}")
    finally:
        driver.quit()

    return None


# Function to fetch the transcript of a YouTube video
def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print("\nTranscript:")
        for entry in transcript:
            print(f"{entry['start']}: {entry['text']}")
    except Exception as e:
        print(f"Error fetching transcript: {e}")


# Main Function
def main():
    search_query = "Banana+Bread"  # Replace with your desired search term
    video_id = search_youtube_video(search_query)

    if video_id:
        fetch_transcript(video_id)
    else:
        print("No video found or failed to retrieve video ID.")


if __name__ == "__main__":
    main()
