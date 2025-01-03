from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from colorama import Fore
from tkinter import messagebox
from selenium.common.exceptions import (
        NoSuchElementException,
        TimeoutException,
        WebDriverException,
        NoSuchWindowException
    )
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fuzzywuzzy import fuzz

from tkinter import messagebox

from time  import sleep

import logging


def setup_logging():
    """Set up logging with fresh logs for every new search."""
    # Clear the log file by opening it in write mode ('w') at the start
    with open('lyrics_scraper_log.log', 'w'):
        pass  # This clears the content of the file
setup_logging()

# Configure logging
logging.basicConfig(
    filename='lyrics_scraper_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
)


def is_match(scraped_name, input_name, threshold=80):
    # Check if similarity is above the threshold
    return fuzz.partial_ratio(scraped_name, input_name) > threshold



#######################################################
def scrape_from_musicxmatch(artist_name, track_name, lyrics_lang):
    logging.info("=== Starting Lyrics Scraper from MusicXMatch ===")
   
    try:
            global browser
            print(Fore.GREEN + "=== Opening the Browser ===")
            logging.info("=== Opening the Browser ===")
            #Setup Chrome browser with DriverManager 
            browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            browser.maximize_window()
            print(Fore.GREEN + "=== Navigating to Musixmatch ===")
            logging.info("=== Navigating to Musixmatch ===")
            browser.get("https://www.musixmatch.com/search")
        
    except WebDriverException as wd:
            print(Fore.RED + "Error occurred" + str(wd))
            logging.info("Error occurred: " + str(wd))
            messagebox.showerror(title="Error occurred", message=str(wd))
        
    except NoSuchWindowException as nw:
            print(Fore.RED + "Error occurred" + str(nw))
            messagebox.showerror(title="Error occurred", message=str(nw))
    
    wait = WebDriverWait(browser, 10)
    browser.implicitly_wait(5)

    try:
        input_el = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div/div/input')))
        input_el.send_keys(f"{artist_name} {track_name}")
        print(Fore.GREEN + "Search bar found !")
        print(Fore.GREEN + f"Searching lyrics for: {track_name} by {artist_name} ")
        logging.info("Search bar found !")
        logging.info(f"Searching lyrics for: {track_name} by {artist_name} ")
    except TimeoutException:
        print(Fore.RED + "Search bar not found or took too long to load")
        logging.info("Search bar not found or took too long to load")
        messagebox.showerror(title="Error", message="Search bar not found or took too long to load!")
        return
    #
    if not EC.presence_of_element_located((By.XPATH,'//*[@id="__next"]/div/div/div/div[1]/div/div/div/div[2]/div/div[2]/div/div')):

     sleep(10)
    
    try:
        print(Fore.GREEN + "=== Checking if 'See All' button exists ===")
        logging.info("=== Checking if 'See All' button exists ===")
        see_all_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#__next > div > div > div > div:nth-child(1) > div > div > div > div.css-175oi2r.r-1smwm8v > div > div.css-175oi2r.r-12kyg2d.r-11c0sde > div.css-175oi2r.r-2o02ov > div:nth-child(1) > div.css-175oi2r.r-61z16t > div > div > div.css-175oi2r.r-1awozwy.r-18u37iz > div')))
        print(see_all_btn.text)
        if see_all_btn.text.lower() == "see all":
            print(Fore.GREEN + "=== Clicking on the 'See All' button ===")
            logging.info("=== Clicking on the 'See All' button ===")
            see_all_btn.click()
        else:
            #document.querySelector("")
            print(Fore.YELLOW + "=== 'See All' button not displayed, skipping ===")
            logging.info("=== 'See All' button not displayed, skipping ===")
    except TimeoutException:
        print(Fore.RED + "Timed out while trying to find 'See All' button.")
        logging.info("Timed out while trying to find 'See All' button.")
    except NoSuchElementException:
        print(Fore.RED + "=== 'See All' button not found. ===")
        logging.info("=== 'See All' button not found. ===")

    sleep(5)
    try:
        print(Fore.GREEN + "=== Finding Track Cards ===")
        logging.info("=== Finding Track Cards ===")
        parent_cards = browser.find_element(By.CSS_SELECTOR, value=".r-1wtj0ep")
        all_cards = parent_cards.find_elements(By.CSS_SELECTOR, value=".r-1f720gc")
    except NoSuchElementException:
        print(Fore.RED + "Track cards not found")
        logging.info("Track cards not found")
        messagebox.showerror(title="Element not found", message="Track cards not found!")
        return

    print(Fore.GREEN + "=== Looping through all cards ===")
    logging.info("=== Looping through all cards ===")
   
    track_found = False
    for card in all_cards:
        try:
            track_el = card.find_element(By.CSS_SELECTOR, value=".r-1wbh5a2").text.strip().lower()
            artist_el = card.find_element(By.CSS_SELECTOR, value=".r-a023e6").text.strip().lower()

            if is_match(track_el, track_name.lower().strip()) and is_match(artist_el, artist_name.lower().strip()):
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                print(Fore.GREEN + "=== Track Found! Navigating to lyrics page ===")
                logging.info("=== Track Found! Navigating to lyrics page ===")
                browser.get(link)
                track_found = True
                break
        except NoSuchElementException:
            print(Fore.GREEN + "Track or artist element not found within a card. Skipping...")
            logging.info("Track or artist element not found within a card. Skipping...")

    if not track_found:
        print(Fore.RED + "=== Track not found ===")
        logging.info("=== Track not found ===")
        messagebox.showinfo(
            title="Lyrics not found",
            message=f"Couldn't find lyrics for the track: {track_name}\nCheck the spelling and try again."
        )
        logging.info(f"Couldn't find lyrics for the track: {track_name}\nCheck the spelling and try again.")
        lyrics = {
                "artist": None,
                "track": None,
                "lyrics": None
            }
        browser.quit()
        return lyrics

    try:
        print(Fore.GREEN + "=== Loading Lyrics ===")
        logging.info("=== Loading Lyrics ===")
        if lyrics_lang:
            try:
                print(Fore.GREEN + f"=== Loading Lyrics for {lyrics_lang} language")
                logging.info(f"=== Loading Lyrics for {lyrics_lang} language")
                translation_btn = browser.find_element(By.XPATH,value='//*[@id="__next"]/div/div/div/div[1]/div/div[1]/div[1]/div[2]/div/div/div[1]/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div[2]')
                if translation_btn.text == 'Add translation':
                    print(Fore.RED + "Translation not available for the lyrics")
                    logging.info("Translation not available for the lyrics")
                    messagebox.showinfo(title="Error", message="Translation not available for the lyrics")
                    return
                
                translation_btn.click()
                translation_card = browser.find_element(By.XPATH, value='//*[@id="__next"]/div/div/div/div[3]/div/div/div[3]/div/div/div[2]/div')
                input_language = translation_card.find_element(By.TAG_NAME, 'input')
                input_language.send_keys(lyrics_lang)
                lang_card = translation_card.find_element(By.CSS_SELECTOR, value='.r-1h0z5md')
                if lang_card:
                    lang_card.click()
                else:
                    print('Lang card not found')
                    logging.info('Lang card not found')

            except NoSuchElementException:
                print(Fore.RED + "Lyrics language not found")
                logging.info("Lyrics language not found")
                response = messagebox.askokcancel(title="Error", message="Lyrics language not found. Load default lyrics?")
                if response:
                    print(Fore.GREEN + "=== Loading default lyrics ===")
                    logging.info("=== Loading default lyrics ===")
                else:
                    print(Fore.RED + "=== Closing Browser ===")
                    logging.info("=== Closing Browser ===")
                    browser.quit()
                    return

        else:
            print(Fore.GREEN + "=== Lyrics language not specified ===")
            logging.info("=== Lyrics language not specified ===")
            print(Fore.GREEN + "=== Loading default lyrics ===")
            logging.info("=== Loading default lyrics ===")
        
        sleep(5)
        print(Fore.GREEN + "=== Retrieving Lyrics ===")
        logging.info("=== Retrieving Lyrics ===")
        try:
            parent_verse = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/div[1]/div/div[1]/div[1]/div[2]/div/div/div[2]/div')))
            lyrics = {
                "artist": artist_name if artist_name else "Artist not found!",
                "track": track_name if track_name else "Track not found!",
                "lyrics": parent_verse.text + '\n' if parent_verse.text else "Lyrics not found!"
            }
            print(Fore.GREEN + "=== Lyrics Retrieved Successfully ===")
            logging.info("=== Lyrics Retrieved Successfully ===")
            #display_lyrics(lyrics)
            
            print(Fore.LIGHTBLUE_EX + "=== Closing Browser ===")
            logging.info("=== Closing Browser ===")
            browser.quit()
            return lyrics
        except NoSuchElementException:
            print(Fore.RED + "Lyrics not found")
            logging.info("Lyrics not found")
            messagebox.showerror(title="Error", message="Lyrics not found!")
            return 
    except NoSuchElementException:
        messagebox.showerror(
            title="Error",
            message=f"Failed to retrieve lyrics for: {track_name} by {artist_name}"
        )
        logging.info(f"Failed to retrieve lyrics for: {track_name} by {artist_name}")
        return
    finally:
        if browser:
            browser.quit()


