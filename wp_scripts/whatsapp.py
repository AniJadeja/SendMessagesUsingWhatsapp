import logging
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time  # To add delay between actions

# User-defined imports
from .utils import random_delay, log_and_exit

# Set the path to your ChromeDriver
service = Service('C:\Program Files\chromedriver.exe')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_search_box_cleared(search_box):
    """Ensure the search box is empty by selecting all text and deleting it."""
    search_box.send_keys(Keys.CONTROL, "a")  # Select all text
    search_box.send_keys(Keys.DELETE)  # Delete selected text
    time.sleep(0.5)  # Delay to ensure action is registered

def write_not_sent_messages(not_sent_contacts):
    """Write the contacts that were not sent messages to a CSV file."""
    with open('./store/messagesNotSend.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for contact in not_sent_contacts:
            writer.writerow([contact['Name'], contact['Phone_Number']])  # Write each contact

def send_messages(contacts, message_template, sender_name, keep_open=False, open_browser=True):
    """Send messages to a list of contacts."""
    global driver
    driver = None
    not_sent_contacts = []  # List to store contacts that were not sent messages

    try:
        # Set up Chrome options
        chrome_options = Options()
        if not open_browser:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--window-size=1920,1080")

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
            personalized_message = message_template.replace("[Receiver Name]", receiver_name).replace("[Sender Name]", sender_name).replace('"', '\\"') #message_template.replace("[Receiver Name]", receiver_name).replace("[Sender Name]", sender_name)


            # Replace apostrophes and other special characters if needed
            personalized_message = personalized_message.replace("â€™", "'")  # Replace smart apostrophe
            #personalized_message = personalized_message.encode('utf-8').decode('utf-8')  # Ensure proper encoding

            logger.info("")  # Empty line to separate logs
            logger.info(f"Trying to send message to {receiver_name} ({phone_number})")

            random_delay(100, 300)

            try:
                search_box.click()
                random_delay(100, 300)

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
                logger.info("Verifying if the correct chat is open...")
                header_xpath = '//header//span[@title]'
                header_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, header_xpath))
                )
                chat_title = header_element.get_attribute("title")
                logger.info(f"Found chat title: {chat_title}")

                if receiver_name in chat_title or phone_number in chat_title:
                    logger.info(f"Verified chat with {receiver_name} ({phone_number}) is open.")
                elif "click here for contact info" in chat_title:
                    logger.info("Chat verification succeeded with contact info.")
                else:
                    logger.info("Chat verification failed.")
                    not_sent_contacts.append(contact)  # Add to not sent contacts
                    search_box.send_keys(Keys.ESCAPE)  # Press ESC key
                    logger.info("Moving to the next contact.")
                    continue

                # Find the message box
                message_box_xpath = '//div[@contenteditable="true" and @data-tab="10"]'
                message_box = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, message_box_xpath))
                )
                logger.info("Message box found.")

                message_box.click()
                logger.info("Typing the message...")
                for line in personalized_message.split('\n'):
                    message_box.send_keys(line)
                    message_box.send_keys(Keys.SHIFT, Keys.ENTER)  # Shift + Enter for new line
                    random_delay(50, 100)  # Delay between lines
                logger.info("Message typed.")
                random_delay(100, 300)

                message_box.send_keys(Keys.RETURN)  # Send the message
                logger.info("Attempting to send the message...")

                # Adding a delay to allow the message to send
                time.sleep(2)

                # Check for any UI changes or message confirmation
                if "Message sent" in driver.page_source:
                    logger.info("Message sent successfully.")
                else:
                    logger.warning("Message did not send successfully.")

            except Exception as e:
                logger.info(f"Error during message sending: {str(e)}")
                continue

    except Exception as e:
        log_and_exit(f"An unexpected error occurred: {e}")

    finally:
        write_not_sent_messages(not_sent_contacts)  # Write not sent messages to CSV
        if driver and not keep_open:
            logger.info("Closing the browser...")
            driver.quit()
