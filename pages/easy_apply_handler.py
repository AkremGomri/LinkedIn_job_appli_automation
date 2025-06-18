from config import profile
from interfaces.browser_adapter import BrowserAdapter
from utils.llm_guide import LLMApplicationGuide
from services.openai_service import OpenAIService

class EasyApplyHandler:
    def __init__(self, browser: BrowserAdapter, llm_service=None):
        self.browser = browser
        print("Initializing EasyApplyHandler with browser:")
        self.llm_service = OpenAIService() #llm_service or OpenAIService()
        print("LLM Service initialized:")
        
    def handle(self):
        print("Starting LLM-guided Easy Apply...")
        guide = LLMApplicationGuide(
            browser=self.browser,
            profile_data=profile.application_profile,
            llm_service=self.llm_service
        )
        return guide.execute_application_flow()