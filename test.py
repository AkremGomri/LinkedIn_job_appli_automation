# test_script.py
import argparse
from drivers.Selinium_adapters import SeleniumBrowser
from pages.regular_apply_handler import RegularApplyHandler
from utils.driver_manager import start_persistent_browser, attach_to_running_browser, is_browser_running, get_driver, profile_exists

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from utils.interactive_shell import launch_interactive_shell

from config import settings, secrets
import time

# import logging
# logging.basicConfig(level=logging.DEBUG, filename="logger/test.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--website-link', required=True, help='URL to test')
    parser.add_argument('--new-browser',
                        default="True",
                        help='Open in new browser (True) or new tab (False)')
    args = parser.parse_args()
    new_browser = args.new_browser.lower() in ('true', '1', 't', 'y', 'yes')
    try:
        if is_browser_running():
            driver = attach_to_running_browser()
            skip_login = True  # Skip login when attaching to existing session
        else:
            skip_login = profile_exists()
            driver = start_persistent_browser()
            # Only skip login if profile already exists
            if skip_login:
                print("Existing profile detected - skipping login")

        browser = SeleniumBrowser(driver)
        
        if new_browser:
            browser.open_new_window(args.website_link)
        else:
            browser.open_new_tab(args.website_link)
        
        handler = RegularApplyHandler(browser)
        handler.handle()

    except KeyboardInterrupt:
        print("\nUser interrupted the process with Ctrl+C")
        print("Entering interactive mode...")
        # Don't return here - let it proceed to finally
    except Exception as e:
        print(f"\nAn error occurred during execution: {str(e)}")
        print("Browser session will remain open for debugging.")
    finally:
        context = {
            'driver': driver,
            'browser': browser,
            'settings': settings,
            'secrets': secrets,
            'time': time
        }
        launch_interactive_shell(context)
        
        if driver:
            driver.quit()

if __name__ == '__main__':
    main()