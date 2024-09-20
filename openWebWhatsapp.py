import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up Chrome options with a custom user profile
chrome_options = Options()
chrome_options.add_argument("user-data-dir=/home/kanbhaa/selenium-chrome-profile")  # New profile directory
chrome_options.add_argument("profile-directory=Profile 2")  # Use the existing profile

# Set the path to your ChromeDriver and create the driver instance
service = Service('/usr/bin/chromedriver')  # Provide the path to ChromeDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

def log_and_exit(error_message):
    logger.error(error_message)
    driver.quit()
    exit(1)

def recursive_search(element, number):
    """Recursively search for the phone number in the element's text."""
    if number in element.text:
        return True
    for child in element.find_elements(By.XPATH, ".//*"):
        if recursive_search(child, number):
            return True
    return False

def random_delay(min_ms, max_ms):
    """Generate a random delay between min and max milliseconds."""
    time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

def send_messages(messages, keep_open=False):
    """Send messages to an array of contacts."""
    try:
        # Open WhatsApp Web
        driver.get("https://web.whatsapp.com")
        logger.info("WhatsApp Web opened successfully. Waiting for the page to load.")

        # Wait for the search box to appear
        search_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true" and @data-tab="3"]'))
        )
        logger.info("Search box found.")

        for message_data in messages:
            number = message_data["number"]
            message = message_data["message"]

            logger.info(f"Trying to send message to {number}")
            random_delay(100, 300)  # Reduced delay

            # Click on the search box and search for the contact/number
            try:
                search_box.click()
                logger.info("  Trying to open the chat...")
                random_delay(100, 300)  # Reduced delay

                search_box.send_keys(number)
                search_box.send_keys(Keys.RETURN)  # Press Enter to confirm the search
                logger.info("  Chat opened successfully. Verifying...")
                random_delay(100, 300)  # Reduced delay
            except Exception as e:
                log_and_exit(f"Failed to interact with the search box: {e}")

            # Wait for the chat window (`main` div) to load after hitting RETURN
            def wait_for_main_div(driver, timeout=30):
                logger.info("  Waiting for the 'main' div to appear after opening chat...")
                for _ in range(timeout):
                    try:
                        main_div = driver.find_element(By.ID, "main")
                        if main_div:
                            logger.info("  'main' div found.")
                            return main_div
                    except Exception:
                        logger.info(f"  'main' div not found, retrying... ({_ + 1}/{timeout} seconds)")
                    random_delay(500, 1000)
                return None

            # Call the function to wait for the 'main' div
            main_div = wait_for_main_div(driver)
            if not main_div:
                log_and_exit(f"Failed to locate the 'main' div after 30 seconds.")

            # Verify that the chat is open by checking for the phone number in the 'main' div
            try:
                logger.info("  Trying to verify if the chat is open...")
                if recursive_search(main_div, number):
                    logger.info(f"  Verified that chat with {number} is open.")
                else:
                    log_and_exit(f"Chat with {number} is not open.")
            except Exception as e:
                log_and_exit(f"Failed to verify if the chat is open for {number}: {e}")

            # Wait for the message input box to appear
            try:
                logger.info("  Trying to find the message input box...")
                message_box_xpath = '//div[@contenteditable="true" and @data-tab="10"]'
                message_box = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, message_box_xpath))
                )
                logger.info("  Message box found.")
            except Exception as e:
                log_and_exit(f"Failed to find the message box: {e}")

            # Click the message box to make it active and type the message
            try:
                message_box.click()
                logger.info("  Typing the message...")
                for char in message:
                    message_box.send_keys(char)
                    random_delay(100, 300)  # Reduced delay between typing each character
                logger.info("  Typing done.")
                random_delay(100, 300)  # Delay before sending the message
            except Exception as e:
                log_and_exit(f"Failed to type the message: {e}")

            # Send the message
            try:
                message_box.send_keys(Keys.RETURN)  # Press Enter to send the message
                logger.info("  Trying to send message...")
                random_delay(500, 1000)  # Reduced delay after clicking send
                logger.info("  Message sent successfully.")
            except Exception as e:
                log_and_exit(f"Failed to send the message: {e}")

            logger.info("")  # Empty line to distinguish logs

    except Exception as e:
        log_and_exit(f"An unexpected error occurred: {e}")

    # Decide whether to keep the Selenium session open or quit
    if not keep_open:
        logger.info("Closing the browser...")
        driver.quit()

# Example usage
messages = [
    { "name": "Alice", "number": "+1 (226) 899-6539", "message": "Hey Alice!" },
    { "name": "Bob", "number": "+1 (226) 123-4567", "message": "Hello Bob! How are you?" }
]

send_messages(messages, keep_open=False)
