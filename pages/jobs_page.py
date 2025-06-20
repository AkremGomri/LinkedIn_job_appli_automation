import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from interfaces.browser_adapter import BrowserAdapter


from interfaces.base_page import BasePage
from interfaces.element_adapter import ElementAdapter
from pages.easy_apply_handler import EasyApplyHandler
from pages.regular_apply_handler import RegularApplyHandler

# from services.openai_service import OpenAIService
# from config import profile

class JobsPage(BasePage):
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")
    LOCATION_INPUT = (By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']")
    FILTERS_BUTTON = (By.XPATH, "//button[contains(@aria-label, 'Show all filters')]")
    PAST_24H_FILTER = (By.XPATH, "//label[contains(.,'Past 24 hours')]")
    ENTRY_LEVEL_FILTER = (By.XPATH, "//label[contains(.,'Filter by Entry level')]")
    APPLY_FILTERS_BUTTON = (By.XPATH, "//button[contains(@aria-label, 'Apply current filters to show results')]")

    JOB_LIST_CONTAINER = (By.XPATH, "//div[contains(@class, 'scaffold-layout__list') and @tabindex='-1']")
    JOB_LIST_CONTAINER_UL_CHILD = (By.XPATH, "./div/ul")

    JOB_LIST = (By.CSS_SELECTOR, "ul.pSsGdwVIjeECisXagTNgepJchafLXUBMWhx")
    APPLY_BUTTON = (By.CSS_SELECTOR, "div.jobs-details__main-content button.jobs-apply-button")

    APPLY_BUTTON_ID = (By.ID, "jobs-apply-button-id")

    def __init__(self, browser: BrowserAdapter):
        super().__init__(browser)

    def search_jobs(self, keywords, location):
        # Get elements
        search_field = self.browser.find_visible(self.SEARCH_INPUT)
        location_field = self.browser.find_visible(self.LOCATION_INPUT)
        
        # Interact with elements
        search_field.write_text(keywords)
        
        location_field.clear()
        location_field.send_keys(location)
        location_field.send_keys(Keys.RETURN)
        search_field.send_keys(Keys.RETURN)

    def apply_filters(self):
        # Get elements
        filters_btn = self.browser.find_clickable(self.FILTERS_BUTTON)
        filters_btn.click()

        past_24h = self.browser.find_clickable(self.PAST_24H_FILTER)
        past_24h.click()

        entry_level = self.browser.find_clickable(self.ENTRY_LEVEL_FILTER)
        entry_level.click()

        apply_btn = self.browser.find_clickable(self.APPLY_FILTERS_BUTTON)
        apply_btn.click()

    def get_job_listings(self):
        container = self.browser.find_visible(self.JOB_LIST_CONTAINER)
        print("Job list container found.")
        
        # Find UL using the new direct path
        ul_elements = container.find_elements(self.JOB_LIST_CONTAINER_UL_CHILD)
        # print(f"Using ul element: {ul_element.tag_name}")
        print(len(ul_elements), "UL elements found.")
        ul_element = ul_elements[0] if ul_elements else None
        # Get all LI elements within the UL
        job_listings = ul_element.find_elements((By.XPATH, "./li"))
        print(f"Found {len(job_listings)} job listings.")
        return job_listings
    
    def is_loaded(self) -> bool:
        """Check if login page is loaded"""
        return self.browser.find_visible(self.SEARCH_INPUT).is_displayed()
    
    # Add to JobsPage class
    def is_already_applied(self):
        return self.is_element_present(self.APPLIED_LABEL)
    
    def apply_to_job(self):
        """Attempt to apply to a job, handling both Easy Apply and Regular Apply"""
        print
        try:
            apply_button = self.browser.find_clickable(self.APPLY_BUTTON_ID)
            aria_label = apply_button.get_attribute("aria-label") or ""
            
            if aria_label.startswith("Easy Apply to"):
                print("Detected Easy Apply button")
                apply_button.click()
                print("Switching to modal for Easy Apply...")
                time.sleep(2)  # Allow modal to open
                return EasyApplyHandler(self.browser).handle()
                
            elif aria_label.startswith("Apply to"):
                print("Detected Regular Apply button")
                apply_button.click()
                print("Switching to new tab if applicable...")
                time.sleep(2)  # Allow new page/tab to load
                return RegularApplyHandler(self.browser).handle()
                
            else:
                print(f"Unknown apply button type: {aria_label}")
                return False
        except Exception as e:
            print(f"Error applying to job: {e}")
            self.browser.save_screenshot("apply_error.png")
            return False