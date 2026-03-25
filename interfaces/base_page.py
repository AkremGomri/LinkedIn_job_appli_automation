from abc import ABC, abstractmethod
from interfaces.browser_adapter import BrowserAdapter

class BasePage(ABC):
    @abstractmethod
    def __init__(self, browser: BrowserAdapter):
        self.browser = browser
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """Verify the page has loaded successfully"""
        pass