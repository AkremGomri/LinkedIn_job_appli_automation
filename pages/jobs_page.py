from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage

class JobsPage(BasePage):
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")
    LOCATION_INPUT = (By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']")
    FILTERS_BUTTON = (By.XPATH, "//button[contains(@aria-label, 'Show all filters')]")
    PAST_24H_FILTER = (By.XPATH, "//label[contains(.,'Past 24 hours')]")
    ENTRY_LEVEL_FILTER = (By.XPATH, "//label[contains(.,'Filter by Entry level')]")
    APPLY_FILTERS_BUTTON = (By.XPATH, "//button[contains(@aria-label, 'Apply current filters')]")
    JOB_LIST = (By.CSS_SELECTOR, "ul.pSsGdwVIjeECisXagTNgepJchafLXUBMWhx")
    APPLY_BUTTON = (By.CSS_SELECTOR, "div.jobs-details__main-content button.jobs-apply-button")

    def search_jobs(self, keywords, location):
        print("we reached here 3.0")
        self.write_text(self.SEARCH_INPUT, keywords)
        print("we reached here 3.1")
        location_field = self.wait.until(EC.visibility_of_element_located(self.LOCATION_INPUT))
        print("we reached here 3.2")
        location_field.clear()
        print("we reached here 3.3")
        location_field.send_keys(location)
        print("we reached here 3.4")
        location_field.send_keys(Keys.RETURN)
        print("we reached here 3.5")
        self.send_keys(self.SEARCH_INPUT, Keys.RETURN)
        print("we reached here 3.6")

    def apply_filters(self):
        self.click(self.FILTERS_BUTTON)
        self.click(self.PAST_24H_FILTER)
        self.click(self.ENTRY_LEVEL_FILTER)
        self.click(self.APPLY_FILTERS_BUTTON)

    def get_job_listings(self):
        return self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"{self.JOB_LIST[1]} li"))
        )