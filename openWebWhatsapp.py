from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Setup Chrome WebDriver
chrome_options = Options()
chrome_options.binary_location = "/usr/bin/google-chrome"  # Update to your Chrome binary location if needed
service = Service('/usr/bin/chromedriver')  # Provide the path to ChromeDriver

# Create the driver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Step 1: Open WhatsApp Web
driver.get("https://web.whatsapp.com")

# Wait for the user to scan the QR code
print("Please scan the QR code on WhatsApp Web.")
time.sleep(15)  # Adjust sleep time to allow enough time for scanning

# Step 2: Wait for the search box to be visible
try:
    # Wait for the search box element to be visible, give it up to 30 seconds to load
    search_box = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="x1hx0egp x6ikm8r x1odjw0f x6prxxf x1k6rcq7 x1whj5v" and @contenteditable="true"]'))
    )
    
    # Step 3: Click on the search box
    search_box.click()

    # Step 4: Type the phone number or contact name
    phone_number = "1234567890"  # Replace with the contact number or name
    search_box.send_keys(phone_number)
    search_box.send_keys(Keys.RETURN)  # Press Enter to select the contact

    print(f"Searched for {phone_number} successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

# Close the browser after some time
time.sleep(10)
driver.quit()
