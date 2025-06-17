from config import profile
from interfaces.browser_adapter import BrowserAdapter
from utils.llm_guide import LLMApplicationGuide
from services.openai_service import OpenAIService

class EasyApplyHandler:
    def __init__(self, browser: BrowserAdapter, llm_service=None):
        self.browser = browser
        self.llm_service = llm_service or OpenAIService()
        
    def handle(self):
        print("Starting LLM-guided Easy Apply...")
        guide = LLMApplicationGuide(
            browser=self.browser,
            profile_data=profile.application_profile,
            llm_service=self.llm_service
        )
        return guide.execute_application_flow()