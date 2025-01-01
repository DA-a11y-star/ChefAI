from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from youtube_transcript_api import YouTubeTranscriptApi
from webdriver_manager.chrome import ChromeDriverManager
import requests
import openai
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

openai.api_key = "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"


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
            indexSlice = video_id.find("&")
            embed_url = f"https://www.youtube.com/embed/{video_id[:indexSlice]}"
            print(f"Title: {video_title}")
            print(f"Video URL: {video_url}")
            print(f"Embed URL: {embed_url}")
            print(f"Video ID: {video_id}")
            return [embed_url, video_title, video_url, video_id]
    except Exception as e:
        print(f"Error while scraping YouTube: {e}")
    finally:
        driver.quit()

    return None


# Function to fetch the transcript of a YouTube video
def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = []
        print("\nTranscript:")
        for entry in transcript:
            transcript_text.append([entry["start"], entry["text"]])
        return transcript_text
    except Exception as e:
        return f"Error fetching transcript: {e}"

    #     # Make a POST request to the ChatGPT API
    #     chatgpt_api_url = "https://api.openai.com/v1/chat/completions"  # Adjust the endpoint as necessary
    #     headers = {
    #         "Authorization": f"Bearer {openai.api_key}",  # Use your OpenAI API key
    #         "Content-Type": "application/json",
    #     }
    #     data = {
    #         "model": "gpt-4-turbo",  # Specify the model
    #         "messages": [{"role": "user", "content": prompt}],
    #         "max_tokens": 500,  # Adjust max tokens as needed
    #     }

    #     try:
    #         response = requests.post(chatgpt_api_url, headers=headers, json=data)
    #         response_data = response.json()

    #         if response.status_code == 200:
    #             # Extract the response from ChatGPT
    #             chatgpt_response = response_data["choices"][0]["message"]["content"]
    #             print("-----------------------------------------------")
    #             print(chatgpt_response)
    #             print("------------------------------------------------")
    #             return jsonify({"response": chatgpt_response}), 200
    #         else:
    #             return (
    #                 jsonify({"error": "Failed to get response from ChatGPT."}),
    #                 response.status_code,
    #             )

    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 500
    # else:
    #     return jsonify({"error": "Transcript not found."}), 400


# Main Function
def main():
    search_query = "Pumpkin+Pie"  # Replace with your desired search term
    video_id = search_youtube_video(search_query)

    if video_id:
        transcript_text = fetch_transcript(video_id[3])
        print(transcript_text)
    else:
        print("No video found or failed to retrieve video ID.")


def get_info(recipe_video):
    # Access the recipevideo session variable
    # You can now use recipe_video in your logic
    if recipe_video:
        # Do something with the recipe_video
        video_info = search_youtube_video(recipe_video)
        transcript = fetch_transcript(video_info[3])
        print(transcript)
        return [video_info, [transcript]]
    else:
        return redirect(url_for("segments"))  # Redirect if no recipe_video is found


if __name__ == "__main__":
    main()
