from interfaces.browser_adapter import BrowserAdapter
from utils.llm_guide import ApplicationOrchestrator
from config import settings
from LLM.services.openai_service import OpenAIService

class RegularApplyHandler:
    def __init__(self, browser: BrowserAdapter, llm_service = None):
        self.browser = browser
        self.llm_service = OpenAIService() #llm_service or OpenAIService()
        
    def handle(self):
        # Switch to new tab if applicable
        if len(self.browser.get_window_handles()) > 1:
            self.browser.switch_to_window(self.browser.get_window_handles()[-1])
        # print("before entering ApplicationOrchestrator")
        guide = ApplicationOrchestrator(
            browser=self.browser,
            profile_data=settings.application_profile,
            additional_info = settings.additional_info,
            llm_service=self.llm_service,
            max_steps=25
        )
        # print("After Finishing ApplicationOrchestrator")
        return guide.execute_application_flow() # returns True if it has terminated, False if it tried 25 times without completion!