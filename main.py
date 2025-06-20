from drivers.Selinium_adapters import SeleniumBrowser
from utils.driver_manager import start_persistent_browser, attach_to_running_browser, is_browser_running, get_driver, profile_exists
from pages.login_page import LoginPage
from pages.jobs_page import JobsPage
from config import settings, secrets
from utils.interactive_shell import launch_interactive_shell
import time

def job_application_flow():
    # Connect to existing browser or start new
    if is_browser_running():
        print("Attaching to existing browser session")
        driver = attach_to_running_browser()
        skip_login = True  # Skip login when attaching to existing session
    else:
        print("Starting new persistent browser")
        driver = start_persistent_browser()
        # Only skip login if profile already exists
        skip_login = profile_exists()
        if skip_login:
            print("Existing profile detected - skipping login")

    browser = SeleniumBrowser(driver)
    try:
        # Conditionally handle login
        if not skip_login:
            login_page = LoginPage(browser)
            browser.navigate_to(f"{settings.LINKEDIN_URL}/login")
            login_page.login(secrets.EMAIL, secrets.PASSWORD)
            input("Complete authentication and press Enter...")
        else:
            # Ensure we're logged in by checking home page
            browser.navigate_to(settings.LINKEDIN_URL)
            time.sleep(2)  # Allow page to load
        
        # Job search
        jobs_page = JobsPage(browser)
        browser.navigate_to(settings.JOB_SEARCH_URL)
        jobs_page.search_jobs(settings.SEARCH_KEYWORDS, settings.LOCATION)
        time.sleep(3)  # Let results load
        jobs_page.apply_filters()
        print("Filters applied successfully.")
        
        # Process jobs
        total_processed = 0
        max_jobs = 25
        
        while total_processed < max_jobs:
            # Get fresh listings every iteration
            listings = jobs_page.get_job_listings()
            if not listings:
                print("No more job listings found")
                break
            
            # Process only unprocessed jobs
            for job in listings[total_processed:total_processed+1]:
                print(f"\n--- Processing job {total_processed+1}/{max_jobs} ---")
                
                try:
                    # Scroll to job using JavaScript
                    browser.scroll_to(job)
                    
                    # Click using JavaScript
                    browser.click_js(job)

                    try:
                        # Add delay for job details to load
                        time.sleep(2)
                        
                        # Call the unified application method
                        application_result = jobs_page.apply_to_job()
                        
                        if application_result:
                            print("Application process completed")
                        else:
                            print("Application failed or skipped")
                        # ... rest of your logic ...
                        
                    except Exception as e:
                        print(f"Error during application: {e}")
                        print("Retrying job processing...")
                        continue
                    
                    # Add delay for job details to load
                    time.sleep(2)
                    
                    # ... [Add your job application logic here] ...
                    
                except Exception as e:
                    print(f"Error processing job: {e}")
                    print("Element went stale, retrying...")
                    continue
                
                total_processed += 1
                if total_processed >= max_jobs:
                    break
                    
        print(f"Processed {total_processed} jobs")
    
    except Exception as e:
        print(f"Critical error: {e}")
        browser.save_screenshot("error.png")
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
        
        # Add By if needed for locators
        try:
            from selenium.webdriver.common.by import By
            context['By'] = By
        except ImportError:
            pass
        
        # Launch interactive debugging shell
        launch_interactive_shell(context)
        
        # Cleanup after shell exits
        browser.quit()

if __name__ == "__main__":
    job_application_flow()