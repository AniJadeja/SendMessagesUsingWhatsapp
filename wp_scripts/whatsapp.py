import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# User imports
from .utils import random_delay, log_and_exit, recursive_search_with_timeout

# Set the path to your ChromeDriver
service = Service('/usr/bin/chromedriver')

logger = logging.getLogger(__name__)

def format_message(template, receiver_name, sender_name):
    """Format the message by replacing placeholders with actual names."""
    return template.replace("[Receiver Name]", receiver_name).replace("[Sender Name]", sender_name)

def send_messages(contacts, message_template, sender_name, keep_open=False, open_browser=True):
    """Send messages to a list of contacts with a given message template and sender name."""
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

            # Generate personalized message by formatting the template with receiver's and sender's names
            message = format_message(message_template, receiver_name, sender_name)

            logger.info(f"Trying to send message to {receiver_name} ({phone_number})")
            random_delay(100, 300)

            try:
                search_box.click()
                logger.info("  Trying to open the chat...")
                random_delay(100, 300)

                search_box.clear()
                search_box.send_keys(receiver_name)  # Search using the contact name
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

            # Verify that the chat is open
            try:
                logger.info("  Trying to verify if the chat is open...")
                if recursive_search_with_timeout(main_div, receiver_name, timeout=3):
                    logger.info(f"  Verified that chat with {receiver_name} is open.")
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
                
                # Split the message by newline and use Shift+Enter for new lines
                lines = message.split('\n')
                for i, line in enumerate(lines):
                    message_box.send_keys(line)
                    if i < len(lines) - 1:
                        # Use Shift + Enter to create a new line without sending the message
                        message_box.send_keys(Keys.SHIFT, Keys.ENTER)
                    random_delay(20, 50)  # Reduced delay between typing each line

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
