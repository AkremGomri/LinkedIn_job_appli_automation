from abc import ABC, abstractmethod
import json

class LLMService(ABC):
    @abstractmethod
    def get_application_guidance(self, prompt: str) -> list:
        pass