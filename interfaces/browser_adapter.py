from abc import ABC, abstractmethod
from interfaces.element_adapter import ElementAdapter

class BrowserAdapter(ABC):

    @abstractmethod
    def find_element(self, locator) -> ElementAdapter: ...

    @abstractmethod
    def navigate_to(self, url): pass

    @abstractmethod
    def find_visible(self, locator): pass

    @abstractmethod
    def find_clickable(self, locator): 
        print("a7na lahné hahahaha")

    @abstractmethod
    def execute_script(self, script, *args): pass
    
    @abstractmethod
    def scroll_to(self, element: ElementAdapter): pass

    @abstractmethod
    def click_js(self, script, element: ElementAdapter): pass