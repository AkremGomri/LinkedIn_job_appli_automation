from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    USERNAME_FIELD = (By.ID, "username")
    PASSWORD_FIELD = (By.ID, "password")
    SIGN_IN_BUTTON = (By.CSS_SELECTOR, 'button[aria-label="Sign in"]')
    
    def login(self, email, password):
        self.send_keys(self.USERNAME_FIELD, email)
        self.send_keys(self.PASSWORD_FIELD, password)
        self.click(self.SIGN_IN_BUTTON)