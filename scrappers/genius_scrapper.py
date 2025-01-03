from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchWindowException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from colorama import Fore
from tkinter import messagebox
import requests
from fuzzywuzzy import fuzz

# Function to check internet connection
def internet_connection():
    try:
        requests.get("https://www.google.com")
        return True
    except requests.ConnectionError:
        return False


def is_match(scraped_name, input_name, threshold=80):
    # Check if similarity is above the threshold
    return fuzz.partial_ratio(scraped_name, input_name) > threshold

# Refactored scrape_from_genius function
def scrape_from_genius(artist, track):
    logging.info("=== Starting Lyrics Scraper from Genius ===")

    # Check for internet connection
    if not internet_connection():
        logging.error("Network error!")
        print('Network error!')
        return

    try:
        # Open the browser
        print(Fore.GREEN + "=== Opening the Browser ===")
        logging.info("=== Opening the Browser ===")

        # Setup Chrome browser with DriverManager
        browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        browser.maximize_window()

        print(Fore.GREEN + "=== Navigating to Genius ===")
        logging.info("=== Navigating to Genius ===")

        # Navigate to Genius search results page
        browser.get(f"https://genius.com/search?q={artist} {track}")

        # Wait for the page to load
        wait = WebDriverWait(browser, 10)
        browser.implicitly_wait(5)

        # Click on 'Show more songs' if available
        try:
            show_more_songs = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Show more songs')))
            show_more_songs.click()
        except (NoSuchElementException, TimeoutException):
            print('No "Show more songs" button found or timed out.')

        # Locate the container with search results
        track_found = False
        try:
            container = wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'search-result-paginated-section')))
            cards = container.find_elements(By.TAG_NAME, 'mini-song-card')
            print(f'Found {len(cards)} cards.')

            # Loop through the cards to find the matching track
            for card in cards:
                track_name = card.find_element(By.CSS_SELECTOR, '.mini_card-title').text
                artist_name = card.find_element(By.CSS_SELECTOR, '.mini_card-subtitle').text
                if is_match(track, track_name.lower().strip()) and is_match(artist, artist_name.lower().strip()):
                    print(Fore.GREEN + "=== Track Found! Navigating to lyrics page ===")
                    logging.info("=== Track Found! Navigating to lyrics page ===")

                    # Get the track's link and open it
                    link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    browser.get(link)
                    track_found = True
                    break

        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"Error occurred while locating the track: {e}")
            print(f"Error occurred while locating the track: {e}")

        # Handle case where track is not found
        if not track_found:
            print(Fore.RED + "=== Track not found ===")
            logging.info("=== Track not found ===")
            messagebox.showinfo(
                title="Lyrics not found",
                message=f"Couldn't find lyrics for the track: {track}\nCheck the spelling and try again."
            )
            logging.info(f"Couldn't find lyrics for the track: {track}\nCheck the spelling and try again.")
            return

        # Extract the lyrics
        try:
            lyrics_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#lyrics-root')))
            lyrics_tags = lyrics_container.find_elements(By.CSS_SELECTOR, '.Lyrics-sc-1bcc94c6-1 .bzTABU')

            # if not lyrics_tags:
            #     print(Fore.RED + "=== No lyrics found ===")
            #     logging.info("=== No lyrics found ===")
            #     return

            # Combine lyrics text from all tags if applicable
            lyrics_text = "\n".join(tag.text for tag in lyrics_tags if tag.text.strip())

            print(Fore.GREEN + "=== Lyrics Extracted ===")
            logging.info("=== Lyrics Extracted ===")

            lyrics_data = {
                'artist': artist if artist else "Artist not found!",
                'track': track if track else "Track not found!",
                'lyrics': lyrics_text if lyrics_text else "Lyrics not found!"
            }
            print(Fore.GREEN + lyrics_data['lyrics'])
            return lyrics_data

        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"Error occurred while extracting lyrics: {e}")
            print(Fore.RED + f"Error occurred while extracting lyrics: {e}")

    except (WebDriverException, NoSuchWindowException) as e:
        logging.error(f"Error occurred: {e}")
        print(Fore.RED + f"Error occurred: {e}")
        messagebox.showerror(title="Error occurred", message=str(e))

    finally:
        # Ensure browser is closed in all cases
        if 'browser' in locals() and browser:
            browser.quit()

# Test the function
#scrape_from_genius(artist='kodak black', track='patty cake')

