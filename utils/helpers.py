
import time
from utils.threading import execute_with_timeout

def get_validated_pause_input(prompt: str, timeout: int = 300) -> str | None:
    """
    Get validated user input for pause resolution with timeout
    
    Args:
        reason: Reason for the pause
        timeout: Maximum time allowed in seconds (default 300s/5min)
        
    Returns:
        Valid user input ('solved' or 'continue') or None on timeout
    """

    start_time = time.time()
    remaining_time = timeout
    
    while remaining_time > 0:

        # Get input with current remaining time
        user_input, timed_out = execute_with_timeout(
            input,
            remaining_time, 
            prompt
        )
        
        # Handle timeout
        if timed_out:
            return None
        
        # Check for valid input
        if user_input.strip().lower() in ('solved', 'continue'):
            return user_input.strip().lower()
        
        # Update remaining time
        elapsed = time.time() - start_time
        remaining_time = timeout - elapsed

        # Invalid input - show message
        print(f"Invalid option '{user_input}'. Please respond with 'solved' or 'continue', remaining time : {remaining_time}")

    return None  # Timeout occurred

# import time
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# def wait_for_element(driver, locator, timeout=10, poll_frequency=0.5):
#     """Wait for element to be present and visible"""
#     return WebDriverWait(
#         driver, 
#         timeout, 
#         poll_frequency=poll_frequency
#     ).until(EC.visibility_of_element_located(locator))

# def wait_for_clickable(driver, locator, timeout=10):
#     """Wait for element to be clickable"""
#     return WebDriverWait(driver, timeout).until(
#         EC.element_to_be_clickable(locator)
#     )

# def safe_click(driver, element, max_attempts=1):
#     """Click with retry for stale elements"""
#     for attempt in range(max_attempts):
#         try:
#             element.click()
#             return True
#         except StaleElementReferenceException:
#             if attempt == max_attempts - 1:
#                 raise
#             time.sleep(1)
#     return False

# def js_click(driver, element):
#     """Click using JavaScript when normal click fails"""
#     driver.execute_script("arguments[0].click();", element)

# def scroll_into_view(driver, element):
#     """Scroll element into viewport"""
#     driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

# def take_screenshot(driver, prefix="error"):
#     """Save timestamped screenshot"""
#     from datetime import datetime
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"{prefix}_screenshot_{timestamp}.png"
#     driver.save_screenshot(filename)
#     return filename

# def is_element_present(driver, locator, timeout=3):
#     """Check if element exists without throwing exception"""
#     try:
#         wait_for_element(driver, locator, timeout)
#         return True
#     except TimeoutException:
#         return False