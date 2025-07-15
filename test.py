# test_script.py
import argparse
from drivers.Selinium_adapters import SeleniumBrowser
from pages.regular_apply_handler import RegularApplyHandler

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--website-link', required=True, help='URL to test')
    parser.add_argument('--new-browser',
                        default="True",
                        help='Open in new browser (True) or new tab (False)')
    args = parser.parse_args()

    # Convert string argument to boolean
    new_browser = args.new_browser.lower() in ('true', '1', 't', 'y', 'yes')
    
    # Initialize browser
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    try:
        # Correct driver initialization
        driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()),
                                options=options)
        
        browser = SeleniumBrowser(driver)
        
        if new_browser:
            browser.open_new_window(args.website_link)
        else:
            browser.open_new_tab(args.website_link)
        
        handler = RegularApplyHandler(browser)
        handler.handle()

    except KeyboardInterrupt:
        print("\nUser interrupted the process with Ctrl+C")
        print("Browser session will remain open for manual inspection.")
        # Don't quit the browser here
        return  # Exit the program but leave browser open
        
    except Exception as e:
        print(f"\nAn error occurred during execution: {str(e)}")
        print("Browser session will remain open for debugging.")
        # Don't quit the browser here
        return  # Exit the program but leave browser open
        
    finally:
        # Only quit the browser if we reached the end successfully
        if driver and not (KeyboardInterrupt or Exception):
            driver.quit()

if __name__ == '__main__':
    main()