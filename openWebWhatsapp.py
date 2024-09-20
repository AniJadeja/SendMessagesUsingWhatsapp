from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome options with a custom user profile
chrome_options = Options()
chrome_options.add_argument("user-data-dir=/home/kanbhaa/selenium-chrome-profile")  # New profile directory
chrome_options.add_argument("profile-directory=Profile 2")  # Use the existing profile

# Set the path to your ChromeDriver and create the driver instance
service = Service('/usr/bin/chromedriver')  # Provide the path to ChromeDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open WhatsApp Web
driver.get("https://web.whatsapp.com")

# Wait for the search box to appear
try:
    search_box = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="x1hx0egp x6ikm8r x1odjw0f x6prxxf x1k6rcq7 x1whj5v" and @contenteditable="true"]'))
    )
    
    # Click on the search box and search for the contact/number
    search_box.click()
    phone_number = "2268996539"  # The phone number you want to search for
    search_box.send_keys(phone_number)
    search_box.send_keys(Keys.RETURN)  # Press Enter to confirm the search

    # Wait for the result to appear
    time.sleep(2)  # Adjust as necessary

    # Find the chat with the exact number and click on it
    chat_xpath = f'//span[@title="{phone_number}"]'
    chat = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, chat_xpath))
    )
    chat.click()  # Click on the chat to open the message panel

    print(f"Opened chat for {phone_number} successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

# Keep the session open for a while to observe
time.sleep(10)
driver.quit()
