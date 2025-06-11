from selenium.webdriver.support import expected_conditions as EC
from utils.driver_manager import get_driver
from pages.login_page import LoginPage
from pages.jobs_page import JobsPage
from config import settings, secrets
import time

def job_application_flow():
    driver = get_driver()
    try:
        # Login
        login_page = LoginPage(driver)
        driver.get(f"{settings.LINKEDIN_URL}/login")
        login_page.login(secrets.EMAIL, secrets.PASSWORD)
        
        # Manual pause for 2FA/captcha
        input("Complete authentication and press Enter...")
        
        # Job search
        print("we reached here 0")
        jobs_page = JobsPage(driver)
        print("we reached here 1")
        driver.get(settings.JOB_SEARCH_URL)
        print("we reached here 2")
        jobs_page.search_jobs(settings.SEARCH_KEYWORDS, settings.LOCATION)
        print("we reached here 3")
        time.sleep(3)  # Let results load
        print("we reached here 4")
        jobs_page.apply_filters()
        print("we reached here 5")
        
        # Process jobs
        listings = jobs_page.get_job_listings()
        for idx, job in enumerate(listings[:25]):
            print(f"\n--- Processing job {idx+1}/25 ---")
            driver.execute_script("arguments[0].scrollIntoView(true);", job)
            print("Scrolled to job listing.")
            job.click()
            print("Clicked on job listing.")
            time.sleep(1.5)  # Let details load
            
            try:
                print("Attempting to apply for job...")
                apply_btn = jobs_page.wait.until(
                    EC.element_to_be_clickable(jobs_page.APPLY_BUTTON)
                )
                print(f"Found apply button: {apply_btn.text[:20]}")
                driver.execute_script("arguments[0].click();", apply_btn)
                # Add application logic here
                time.sleep(1)
            except Exception as e:
                print(f"Apply error: {str(e)[:70]}")
    
    except Exception as e:
        print(f"Critical error: {e}")
        driver.save_screenshot("error.png")
    finally:
        input("Press Enter to close browser...")
        driver.quit()

if __name__ == "__main__":
    job_application_flow()