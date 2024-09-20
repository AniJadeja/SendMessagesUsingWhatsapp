import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time  # To add delay between backspace actions

# User-defined imports
from .utils import random_delay, log_and_exit, recursive_search_with_timeout

# Set the path to your ChromeDriver
service = Service('/usr/bin/chromedriver')

logger = logging.getLogger(__name__)

def clear_search_box_with_backspace(search_box, current_text_length):
    """Clears the search box by sending backspace keys."""
    if current_text_length == 0:
        logger.info("Search box is already empty.")
        return

    for _ in range(current_text_length):
        search_box.send_keys(Keys.BACKSPACE)
        time.sleep(0.5)  # Adding 500ms delay between each backspace (can be adjusted or commented later)

def ensure_search_box_cleared(search_box):
    """Ensure the search box is empty by selecting all text and deleting it."""
    search_box.send_keys(Keys.CONTROL, "a")  # Select all text
    search_box.send_keys(Keys.DELETE)  # Delete selected text
    time.sleep(0.5)  # Slight delay to ensure the action is registered

def send_messages(contacts, message_template, sender_name, keep_open=False, open_browser=True):
    """Send messages to a list of contacts."""
    global driver
    driver = None

    try:
        # Set up Chrome options
        chrome_options = Options()
        if not open_browser:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--window-size=1920,1080")

        chrome_options.add_argument("user-data-dir=/home/kanbhaa/selenium-chrome-profile")
        chrome_options.add_argument("profile-directory=Profile 2")

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://web.whatsapp.com")
        logger.info("WhatsApp Web opened successfully. Waiting for the page to load.")

        search_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true" and @data-tab="3"]'))
        )
        logger.info("Search box found.")

        for contact in contacts:
            receiver_name = contact["Name"]
            phone_number = contact["Phone_Number"]

            # Replace placeholders in the message template
            personalized_message = message_template.replace("[Receiver Name]", receiver_name).replace("[Sender Name]", sender_name)

            # Log with a new line before each contact attempt
            logger.info("")  # Empty line to separate logs
            logger.info(f"Trying to send message to {receiver_name} ({phone_number})")

            random_delay(100, 300)

            try:
                search_box.click()
                random_delay(100, 300)

                # Ensure the search box is completely cleared
                ensure_search_box_cleared(search_box)
                logger.info("Search box cleared.")

                random_delay(100, 300)
                
                search_box.send_keys(phone_number)
                random_delay(100, 300)
                
                search_box.send_keys(Keys.RETURN)
                logger.info("Search executed, waiting for chat to open...")

                try:
                    main_div = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "main"))
                    )
                    logger.info("'main' div found.")
                except TimeoutException:
                    logger.info("Chat didn't open within 5 seconds.")
                    logger.info("Moving to the next contact.")
                    continue

            except Exception as e:
                logger.info(f"Error opening chat: {str(e)}")
                logger.info("Moving to the next contact.")
                continue

            try:
                logger.info("Verifying if the correct chat is open (name or phone number check)...")
                header_xpath = '//header//span[@title]'
                header_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, header_xpath))
                )
                chat_title = header_element.get_attribute("title")  # Fixed get_attribute method

                if receiver_name in chat_title or phone_number in chat_title:
                    logger.info(f"Verified chat with {receiver_name} ({phone_number}) is open.")
                else:
                    logger.info("Chat verification failed: Name or phone number not found in header.")
                    logger.info("Moving to the next contact.")
                    continue

            except Exception as e:
                logger.info(f"Chat verification failed: {str(e)}")
                logger.info("Moving to the next contact.")
                continue

            try:
                logger.info("Trying to find the message input box...")
                message_box_xpath = '//div[@contenteditable="true" and @data-tab="10"]'
                message_box = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, message_box_xpath))
                )
                logger.info("Message box found.")
            except TimeoutException:
                logger.info("Message box not found within 5 seconds.")
                logger.info("Moving to the next contact.")
                continue
            except Exception as e:
                logger.info(f"Error finding message box: {str(e)}")
                logger.info("Moving to the next contact.")
                continue

            try:
                message_box.click()
                logger.info("Typing the message...")
                for line in personalized_message.split('\n'):
                    message_box.send_keys(line)
                    message_box.send_keys(Keys.SHIFT, Keys.ENTER)  # Shift + Enter for new line
                    random_delay(50, 100)  # Delay between lines
                logger.info("Message typed.")
                random_delay(100, 300)

                message_box.send_keys(Keys.RETURN)  # Send the message
                logger.info("Message sent successfully.")
                random_delay(500, 1000)
            except Exception as e:
                logger.info(f"Error typing/sending message: {str(e)}")
                logger.info("Moving to the next contact.")
                continue

            logger.info("")  # Empty line to distinguish logs

    except Exception as e:
        log_and_exit(f"An unexpected error occurred: {e}")

    if driver and not keep_open:
        logger.info("Closing the browser...")
        driver.quit()
