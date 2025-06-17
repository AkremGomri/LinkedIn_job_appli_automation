from abc import ABC, abstractmethod

class ElementAdapter(ABC):

    @abstractmethod
    def is_displayed(self) -> bool: ...

    @abstractmethod
    def click(self): ...
    
    @abstractmethod
    def write_text(self, text): ...
    
    @abstractmethod
    def clear(self): ...
    
    @abstractmethod
    def get_text(self) -> str: ...

    @abstractmethod
    def send_keys(self, keys): ...

    @abstractmethod
    def find_elements(self, by, value) -> list['ElementAdapter']: ...

    @abstractmethod
    def get_attribute(self, name: str) -> str: ...
