import logging
import csv
import hashlib
import time
import threading
import os
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_profile_hash(phone_number):
    """Create a unique hash for the given phone number."""
    return hashlib.sha256(phone_number.encode()).hexdigest()

def write_registration_record(phone_number, profile_hash):
    """Append the registration record to the CSV file."""
    os.makedirs('./store', exist_ok=True)  # Ensure the 'store' directory exists
    
    with open('./store/registrationRecords.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([phone_number, profile_hash])  # Write phone number and its hash

def open_whatsapp_web(phone_number):
    """Open WhatsApp Web, wait for the QR code, click the link, enter the phone number, and print the link code."""
    profile_hash = create_profile_hash(phone_number)
    write_registration_record(phone_number, profile_hash)
    
    # Set up Chrome options
    chrome_options = Options()
    home_dir = os.path.expanduser("~")
    chrome_options.add_argument(f"user-data-dir={os.path.join(home_dir, 'selenium-chrome-profile', profile_hash)}")
    chrome_options.add_argument("profile-directory=Profile 1")  # Use the hashed profile

    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://web.whatsapp.com")
        logger.info("WhatsApp Web opened successfully. Waiting for the page to load.")

        # Wait for QR code canvas
        qr_code_canvas_xpath = '//canvas[@aria-label="Scan this QR code to link a device!"]'
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, qr_code_canvas_xpath))
        )
        logger.info("QR code canvas found. Waiting for 2 seconds.")
        time.sleep(2)  # Wait for 2 seconds after the canvas appears

        # Click the link
        link_button_xpath = '//span[text()="Link with phone number"]'
        link_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, link_button_xpath))
        )
        logger.info("Link with phone number button found, clicking it.")
        link_button.click()

        # Wait for the phone number input field to appear
        phone_input_xpath = '//input[@aria-label="Type your phone number."]'
        phone_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, phone_input_xpath))
        )
        logger.info("Phone number input found. Entering the phone number.")
        
        # Enter the phone number
        phone_input.send_keys(phone_number)

        # Click the Next button
        next_button_xpath = '//button//div[text()="Next"]'
        next_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, next_button_xpath))
        )
        logger.info("Next button found, clicking it.")
        next_button.click()

        # Wait for the div with aria-details to appear
        link_code_div_xpath = '//div[@aria-details="link-device-phone-number-code-screen-instructions"]'
        link_code_div = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, link_code_div_xpath))
        )
        
        # Extract the data-link-code attribute
        data_link_code = link_code_div.get_attribute("data-link-code")
        logger.info(f"Data link code found: {data_link_code}")

        # Format and print the code as a full string
        formatted_code = "".join(data_link_code.split(","))
        logger.info(f"Formatted link code: {formatted_code}")

        # Keep the browser open indefinitely in a separate thread
        keep_browser_open(driver)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        logger.error(traceback.format_exc())  # Log the full traceback
    finally:
        logger.info("Closing the browser...")
        driver.quit()  # Make sure to close the browser

def keep_browser_open(driver):
    """Keep the browser open indefinitely."""
    try:
        while True:
            time.sleep(1)  # Sleep to avoid busy-waiting
    except KeyboardInterrupt:
        logger.info("Exiting loop and closing the browser.")

if __name__ == "__main__":
    # Example phone number; replace with the desired number
    open_whatsapp_web("+1234567890")
