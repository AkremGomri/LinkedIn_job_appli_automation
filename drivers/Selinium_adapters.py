from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from interfaces.browser_adapter  import BrowserAdapter
from interfaces.element_adapter import ElementAdapter
from selenium.webdriver.support.ui import Select
from utils.error_handler import handle_errors
import time

class SeleniumElement(ElementAdapter):

    def __init__(self, webelement):
        self.webelement = webelement

    # Properties to access and return various attributes of the WebElement    
    @property
    def raw_element(self):
        """Access the underlying Selenium WebElement for JS operations"""
        return self.webelement
    
    @handle_errors()
    def is_displayed(self) -> bool:  # Add this
        return self.webelement.is_displayed()

    @handle_errors()
    def get_text(self) -> str:
        return self.webelement.text
    
    @handle_errors()
    def find_elements(self, locator):
        by, value = locator
        return [SeleniumElement(el) for el in self.webelement.find_elements(by, value)] # I could replace "by, value" by "*locator" but I prefer to be explicit
    
    @handle_errors()
    def get_attribute(self, name: str) -> str:
        """Get an attribute value from the underlying WebElement"""
        return self.webelement.get_attribute(name)
    
    @handle_errors()
    def get_tag_name(self) -> str:
        """Get the tag name of the underlying WebElement"""
        return self.webelement.tag_name
    
    @handle_errors()
    # Methods to execute actions on the WebElement
    def click(self): # Buttons, links, etc.
        """Click the element, generally for buttons or links"""
        self.webelement.click()

    @handle_errors()
    def send_keys(self, keys):  # Password, file, etc.
        """Send keys to the element, generally for non text inputs, e.g., for input fields"""
        self.webelement.send_keys(keys)

    @handle_errors()
    def write_text(self, text): # Text input
        """Write text to the element, clearing it first"""
        self.clear()
        self.webelement.send_keys(text)

    @handle_errors()
    def select_option(self, value, type="visible_text"):  # Select options
        """Select an option from a dropdown or select element"""
        if not self.webelement.tag_name.lower() == 'select':
            raise ValueError("Element is not a select element")
        if type not in ["visible_text", "index", "value"]:
            raise ValueError("Invalid selection type. Use 'visible_text', 'index', or 'value'.")
        if not value:
            raise ValueError("Value cannot be empty for selecting an option")
        if type == "index" and not isinstance(value, int):
            raise ValueError("Index must be an integer when using 'index' type")
        if type in ["value", "visible_text"] and not isinstance(value, str):
            raise ValueError("Value must be a string when using 'value' type") 
        
        select = Select(self.webelement)
        try:
            if type == "visible_text":
                select.select_by_visible_text(value)
            elif type == "index":
                select.select_by_index(value)
            elif type == "value":
                select.select_by_value(value)
        except Exception as e:
            print(f"Error selecting option '{value}': {e}")
            raise

    @handle_errors()
    def submit(self): # Form submission
        """Submit the form associated with the element, if applicable"""
        self.webelement.submit()

    @handle_errors()
    def clear(self):
        self.webelement.clear()


class SeleniumBrowser(BrowserAdapter):
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    @handle_errors()
    def find_element(self, locator) -> SeleniumElement:
        return SeleniumElement(self.driver.find_element(*locator))

    @handle_errors()
    def find_visible(self, locator) -> SeleniumElement:
        element = self.wait.until(EC.visibility_of_element_located(locator))
        return SeleniumElement(element)

    @handle_errors()
    def find_clickable(self, locator) -> SeleniumElement:
        print(f"finding element with locator : {locator}")
        element = self.wait.until(EC.element_to_be_clickable(locator))
        print("element found")
        return SeleniumElement(element)
    
    @handle_errors()
    def find_presence_located(self, locator) -> SeleniumElement:
        element = self.wait.until(EC.presence_of_element_located(locator))
        return SeleniumElement(element)
    
    @handle_errors()
    def click_js(self, element_adapter: ElementAdapter):
        print(f"Executing JS click on element: {element_adapter.get_text()}")
        print(f"element_adapter.raw_element: {element_adapter.raw_element}")
        self.driver.execute_script(
            "arguments[0].click();", 
            element_adapter.raw_element  # Use the raw WebElement here
        )
    
    @handle_errors()
    def execute_script(self, script, *args):
        return self.driver.execute_script(script, *args)
    
    @handle_errors()
    def navigate_to(self, url):
        self.driver.get(url)

    @handle_errors()
    def scroll_to(self, element_adapter: ElementAdapter):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element_adapter.raw_element)

    def get_page_source(self):
        return self.driver.page_source
        
    def get_current_url(self):
        return self.driver.current_url
        
    def open_new_tab(self, url):
        self.driver.switch_to.new_window('tab')
        self.driver.get(url)
    
    def open_new_window(self, url):
        self.driver.switch_to.new_window('window')
        self.driver.get(url)

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