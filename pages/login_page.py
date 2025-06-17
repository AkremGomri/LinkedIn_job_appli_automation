# pages/login_page.py
from selenium.webdriver.common.by import By
from interfaces.base_page import BasePage
from interfaces.element_adapter import ElementAdapter

class LoginPage(BasePage):
    USERNAME_FIELD = (By.ID, "username")
    PASSWORD_FIELD = (By.ID, "password")
    SIGN_IN_BUTTON = (By.CSS_SELECTOR, 'button[aria-label="Sign in"]')

    def __init__(self, browser):
        super().__init__(browser)

    def is_loaded(self) -> bool:
        """Check if login page is loaded"""
        return self.browser.find_visible(self.USERNAME_FIELD).is_displayed()
    
    def login(self, email: str, password: str):
        """Perform login operation"""
        # Get elements
        username_input = self.browser.find_visible(self.USERNAME_FIELD)
        password_input = self.browser.find_visible(self.PASSWORD_FIELD)
        signin_btn = self.browser.find_clickable(self.SIGN_IN_BUTTON)
        
        # Interact with elements
        username_input.write_text(email)
        password_input.write_text(password)
        signin_btn.click()