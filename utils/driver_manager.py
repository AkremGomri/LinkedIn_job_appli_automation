import os
import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. DEFINE FIXED PROFILE AND PORT
USER_DATA_DIR = os.path.abspath("./chrome_profile")  # Absolute path to profile
DEBUG_PORT = "9222"                                 # Fixed debug port

# Global variables to track browser instance
PERSISTENT_BROWSER = None
BROWSER_PID = None

def start_persistent_browser():
    global PERSISTENT_BROWSER, BROWSER_PID
    
    if PERSISTENT_BROWSER:
        return PERSISTENT_BROWSER
    
    # 2. USE FIXED VALUES IN CHROME OPTIONS
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    chrome_options.add_argument(f"--remote-debugging-port={DEBUG_PORT}")
    chrome_options.add_argument("--disable-webrtc")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Ensure profile directory exists
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    
    # Start Chrome
    chrome_service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    
    # Store references
    PERSISTENT_BROWSER = driver
    BROWSER_PID = driver.service.process.pid
    
    return driver

def attach_to_running_browser():
    # 3. USE FIXED PORT FOR ATTACHMENT
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{DEBUG_PORT}")
    
    chrome_service = Service(executable_path=ChromeDriverManager().install())
    return webdriver.Chrome(service=chrome_service, options=chrome_options)

def is_browser_running():
    if not BROWSER_PID:
        return False
    try:
        os.kill(BROWSER_PID, 0)
        return True
    except OSError:
        return False

# 4. UNIFIED ACCESS FUNCTION
def get_persistent_driver():
    """Main function to get persistent browser instance"""
    global PERSISTENT_BROWSER
    
    # Case 1: We already have a driver instance in memory
    if PERSISTENT_BROWSER and is_browser_running():
        return PERSISTENT_BROWSER
        
    try:
        # Case 2: Browser running but no driver instance (e.g., from previous run)
        driver = attach_to_running_browser()
        print("Attached to existing browser session")
        PERSISTENT_BROWSER = driver
        BROWSER_PID = driver.service.process.pid
        return driver
    except (WebDriverException, ConnectionRefusedError):
        # Case 3: No running browser - start new instance
        print("Starting new persistent browser session")
        return start_persistent_browser()

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-webrtc")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
# # 5. EXAMPLE USAGE
# if __name__ == "__main__":
#     # Get persistent browser instance
#     driver = get_persistent_driver()
    
#     # Use the browser
#     driver.get("https://www.google.com")
#     print("Current URL:", driver.current_url)
    
#     # Keep browser open - DON'T CALL driver.quit()
#     input("Press Enter to close the browser...")
#     driver.quit()  # Only call when you're completely done