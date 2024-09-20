import time
import random
import logging
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from concurrent.futures import ThreadPoolExecutor, TimeoutError

logger = logging.getLogger(__name__)

def log_and_exit(error_message):
    """Log the error message and exit the script."""
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
    """Wrapper function to add timeout to recursive_search."""
    with ThreadPoolExecutor() as executor:
        future = executor.submit(recursive_search, element, number)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            return False

def random_delay(min_ms, max_ms):
    """Generate a random delay between min and max milliseconds."""
    time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))
