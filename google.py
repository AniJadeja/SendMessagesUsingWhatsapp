from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service  # Import the Service class
from webdriver_manager.chrome import ChromeDriverManager  # To auto-manage ChromeDriver

# Set up Chrome WebDriver using the Service class
service = Service('/usr/bin/chromedriver')  # Provide the path to your ChromeDriver
driver = webdriver.Chrome(service=service)

# Open Google
driver.get("https://www.google.com")

# Locate the Google search box
search_box = driver.find_element(By.NAME, "q")

# Type in the search query and press Enter
search_box.send_keys("Selenium Python Tutorial")
search_box.send_keys(Keys.RETURN)

# Wait for the search results to load
time.sleep(2)

# Get search result titles
results = driver.find_elements(By.XPATH, '//h3')

# Print the titles of the first few results
for idx, result in enumerate(results[:5]):  # Limiting to the first 5 results
    print(f"Result {idx + 1}: {result.text}")

# Close the browser
driver.quit()
