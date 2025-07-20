from drivers.Selinium_adapters import SeleniumBrowser
from utils.driver_manager import start_persistent_browser, attach_to_running_browser, is_browser_running, get_driver, profile_exists
from utils.interactive_shell import launch_interactive_shell
from pages.login_page import LoginPage
from pages.jobs_page import JobsPage
from config import settings, secrets
import time

def job_application_flow():
    # Connect to existing browser or start new
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

    # Login
    try:
        # Conditionally handle login
        if not skip_login:
            print("Not logged in")
            login_page = LoginPage(browser)
            print("logged in pressed")
            browser.navigate_to(f"{settings.LINKEDIN_URL}/login")
            print("logged in url hit")
            login_page.login(secrets.EMAIL, secrets.PASSWORD)
            print("logged in email and password sent")
        else:
            # Ensure we're logged in by checking home page
            browser.navigate_to(settings.LINKEDIN_URL)
            time.sleep(2)  # Allow page to load
            print("leennna")
        input("Press anything to continue")
        # Job search
        jobs_page = JobsPage(browser)
        print("lenna 1")
        browser.navigate_to(settings.JOB_SEARCH_URL)
        print("lenna 2")
        jobs_page.search_jobs(settings.SEARCH_KEYWORDS, settings.LOCATION)
        print("lenna 3")
        time.sleep(3)  # Let results load
        print("applying filters")
        jobs_page.apply_filters()
        print("Filters applied successfully.")
        
        # Job processing with externalized logic
        total_processed = 0
        max_jobs = 25
        
        while total_processed < max_jobs:
            listings = jobs_page.get_job_listings()
            if not listings or total_processed >= len(listings):
                print("No more job listings available")
                break
                
            current_job = listings[total_processed]
            success = jobs_page.process_single_job(current_job, total_processed + 1)
            
            if success:
                total_processed += 1
            
            # Optional: Add delay between jobs
            time.sleep(1)
        
        print(f"Finished processing {total_processed} jobs")
    
    except Exception as e:
        print(f"Critical error: {e}")
        # browser.save_screenshot("error.png")
    finally:
        context = {
            'driver': driver,
            'browser': browser,
            'login_page': login_page if 'login_page' in locals() else None,
            'jobs_page': jobs_page,
            'settings': settings,
            'secrets': secrets,
            'time': time
        }
         
        # Launch interactive debugging shell
        launch_interactive_shell(context)
        
        # Cleanup after shell exits
        browser.quit()

if __name__ == "__main__":
    job_application_flow()