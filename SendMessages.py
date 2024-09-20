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
from selenium.common.exceptions import TimeoutException
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[
    logging.FileHandler("messageLogs.txt"),
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("user-data-dir=/home/kanbhaa/selenium-chrome-profile")
chrome_options.add_argument("profile-directory=Profile 2")

# Set the path to your ChromeDriver
service = Service('/usr/bin/chromedriver')

def log_and_exit(error_message):
    logger.error(error_message)
    if 'driver' in globals() and driver:
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

def recursive_search_with_timeout(element, number, timeout=3):
    """Wrapper function to add timeout to recursive_search"""
    with ThreadPoolExecutor() as executor:
        future = executor.submit(recursive_search, element, number)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            return False

def random_delay(min_ms, max_ms):
    """Generate a random delay between min and max milliseconds."""
    time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

def send_messages(messages, keep_open=False, open_browser=True):
    """Send messages to an array of contacts."""
    global driver
    driver = None

    try:
        if open_browser:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get("https://web.whatsapp.com")
            logger.info("WhatsApp Web opened successfully. Waiting for the page to load.")

            search_box = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true" and @data-tab="3"]'))
            )
            logger.info("Search box found.")
        else:
            logger.info("Browser opening skipped.")

        for message_data in messages:
            number = message_data["number"]
            message = message_data["message"]

            logger.info(f"Trying to send message to {number}")
            random_delay(100, 300)

            try:
                if open_browser:
                    search_box.click()
                    logger.info("  Trying to open the chat...")
                    random_delay(100, 300)

                    search_box.clear()
                    search_box.send_keys(number)
                    search_box.send_keys(Keys.RETURN)
                    logger.info("  Search executed, waiting for chat to open...")
                    
                    # Wait for the chat window (`main` div) to load with a 3-second timeout
                    try:
                        main_div = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.ID, "main"))
                        )
                        logger.info("  'main' div found.")
                    except TimeoutException:
                        logger.info("  Chat didn't open within 3 seconds.")
                        logger.info("  Moving to the next contact.")
                        logger.info("")  # Empty line to distinguish logs
                        continue
                else:
                    logger.info("  Chat opening skipped due to browser not being opened.")

            except Exception as e:
                logger.info(f"  Error opening chat: {str(e)}")
                logger.info("  Moving to the next contact.")
                logger.info("")  # Empty line to distinguish logs
                continue

            # Verify that the chat is open by checking for the phone number
            try:
                logger.info("  Trying to verify if the chat is open...")
                if recursive_search_with_timeout(main_div, number, timeout=3):
                    logger.info(f"  Verified that chat with {number} is open.")
                else:
                    logger.info("  Chat verification failed or timed out.")
                    logger.info("  Moving to the next contact.")
                    logger.info("")  # Empty line to distinguish logs
                    continue
            except Exception as e:
                logger.info(f"  Chat verification failed: {str(e)}")
                logger.info("  Moving to the next contact.")
                logger.info("")  # Empty line to distinguish logs
                continue

            # Wait for the message input box to appear
            try:
                logger.info("  Trying to find the message input box...")
                message_box_xpath = '//div[@contenteditable="true" and @data-tab="10"]'
                message_box = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, message_box_xpath))
                )
                logger.info("  Message box found.")
            except TimeoutException:
                logger.info("  Message box not found within 3 seconds.")
                logger.info("  Moving to the next contact.")
                logger.info("")  # Empty line to distinguish logs
                continue
            except Exception as e:
                logger.info(f"  Error finding message box: {str(e)}")
                logger.info("  Moving to the next contact.")
                logger.info("")  # Empty line to distinguish logs
                continue

            # Click the message box to make it active and type the message
            try:
                message_box.click()
                logger.info("  Typing the message...")
                for char in message:
                    message_box.send_keys(char)
                    random_delay(20, 50)  # Reduced delay between typing each character
                logger.info("  Typing done.")
                random_delay(100, 300)
            except Exception as e:
                logger.info(f"  Error typing message: {str(e)}")
                logger.info("  Moving to the next contact.")
                logger.info("")  # Empty line to distinguish logs
                continue

            # Send the message
            try:
                message_box.send_keys(Keys.RETURN)
                logger.info("  Trying to send message...")
                random_delay(500, 1000)  # Delay after clicking send
                logger.info("  Message sent successfully.")
            except Exception as e:
                logger.info(f"  Error sending message: {str(e)}")
                logger.info("  Moving to the next contact.")
                logger.info("")  # Empty line to distinguish logs
                continue

            logger.info("")  # Empty line to distinguish logs

    except Exception as e:
        log_and_exit(f"An unexpected error occurred: {e}")

    # Decide whether to keep the Selenium session open or quit
    if driver and not keep_open:
        logger.info("Closing the browser...")
        driver.quit()

# Example usage
messages = [
    { "name": "Alice", "number": "+1 (226) 899-6539", "message": "Hey Alice!" },
    { "name": "Bob", "number": "+1 (226) 123-4567", "message": "Hello Bob! How are you?" }
]

send_messages(messages, keep_open=False, open_browser=True)