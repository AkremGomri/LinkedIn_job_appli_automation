from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from interfaces.browser_adapter  import BrowserAdapter
from interfaces.element_adapter import ElementAdapter
import time

class SeleniumElement(ElementAdapter):

    def __init__(self, webelement):
        self.webelement = webelement
    
    @property
    def raw_element(self):
        """Access the underlying Selenium WebElement for JS operations"""
        return self.webelement

    def click(self):
        self.webelement.click()

    def is_displayed(self) -> bool:  # Add this
        return self.webelement.is_displayed()

    def write_text(self, text):
        self.clear()
        self.webelement.send_keys(text)
    
    def get_text(self) -> str:
        return self.webelement.text
    
    def send_keys(self, keys):
        self.webelement.send_keys(keys)

    def clear(self):
        self.webelement.clear()
    
    def find_elements(self, locator):
        by, value = locator
        return [SeleniumElement(el) for el in self.webelement.find_elements(by, value)] # I could replace "by, value" by "*locator" but I prefer to be explicit
    
    def get_attribute(self, name: str) -> str:
        """Get an attribute value from the underlying WebElement"""
        return self.webelement.get_attribute(name)



class SeleniumBrowser(BrowserAdapter):
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def find_element(self, locator) -> SeleniumElement:
        return SeleniumElement(self.driver.find_element(*locator))

    def find_visible(self, locator) -> SeleniumElement:
        element = self.wait.until(EC.visibility_of_element_located(locator))
        return SeleniumElement(element)

    def find_clickable(self, locator) -> SeleniumElement:
        element = self.wait.until(EC.element_to_be_clickable(locator))
        return SeleniumElement(element)
    
    def click_js(self, element_adapter: ElementAdapter):
        print(f"Executing JS click on element: {element_adapter.get_text()[:20]}")
        self.driver.execute_script(
            "arguments[0].click();", 
            element_adapter.raw_element  # Use the raw WebElement here
        )
    
    def execute_script(self, script, *args):
        return self.driver.execute_script(script, *args)
    
    def navigate_to(self, url):
        self.driver.get(url)

    def scroll_to(self, element_adapter: ElementAdapter):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element_adapter.raw_element)

    def get_page_source(self):
        return self.driver.page_source
        
    def get_current_url(self):
        return self.driver.current_url
        
    def switch_to_window(self, window_handle):
        self.driver.switch_to.window(window_handle)
        
    def get_window_handles(self):
        return self.driver.window_handles
    
    def save_screenshot(context):
        """Helper to save screenshot with timestamp"""
        if 'driver' in context:
            filename = f"screenshot_{int(time.time())}.png"
            context['driver'].save_screenshot(filename)
            print(f"Screenshot saved as {filename}")
        else:
            print("No driver available for screenshot")