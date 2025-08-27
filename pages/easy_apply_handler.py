from config import settings
from interfaces.browser_adapter import BrowserAdapter
from utils.llm_guide import ApplicationOrchestrator
from LLM.services.openai_service import OpenAIService

class EasyApplyHandler:
    def __init__(self, browser: BrowserAdapter, llm_service=None):
        self.browser = browser
        print("Initializing EasyApplyHandler with browser:")
        self.llm_service = OpenAIService() #llm_service or OpenAIService()
        
    def handle(self):
        guide = ApplicationOrchestrator(
            browser=self.browser,
            profile_data=settings.application_profile,
            additional_info = settings.additional_info,
            llm_service=self.llm_service,
            max_steps=25
        )
        return guide.execute_application_flow()