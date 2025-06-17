from interfaces.browser_adapter import BrowserAdapter
from utils.llm_guide import LLMApplicationGuide
from config import profile
from services.openai_service import OpenAIService

class RegularApplyHandler:
    def __init__(self, browser: BrowserAdapter, llm_service = None):
        self.browser = browser
        self.llm_service = llm_service or OpenAIService()
        
    def handle(self):
        # Switch to new tab if applicable
        if len(self.browser.get_window_handles()) > 1:
            self.browser.switch_to_window(self.browser.get_window_handles()[-1])
        
        guide = LLMApplicationGuide(
            browser=self.browser,
            profile_data=profile.application_profile,
            llm_service=self.llm_service
        )
        return guide.execute_application_flow()