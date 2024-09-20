import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#user imports
from .utils import random_delay, log_and_exit, recursive_search_with_timeout
from selenium.common.exceptions import TimeoutException

# Set the path to your ChromeDriver
service = Service('/usr/bin/chromedriver')

logger = logging.getLogger(__name__)

def send_messages(messages, keep_open=False, open_browser=True):
    """Send messages to an array of contacts."""
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

        for message_data in messages:
            number = message_data["number"]
            message = message_data["message"]

            logger.info(f"Trying to send message to {number}")
            random_delay(100, 300)

            try:
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