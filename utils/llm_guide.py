from interfaces.browser_adapter import BrowserAdapter
from interfaces.llm_service import LLMService

from automation.html_cleaner import HTMLCleaner
from automation.action_executor import ActionExecutor, Action

from LLM.llm_prompt import PromptBuilder
from LLM.response_parser import LLMResponseParser

from config import settings

class ApplicationOrchestrator:
    def __init__(self, 
                 browser: BrowserAdapter, 
                 profile_data: dict, 
                 additional_info : dict,
                 llm_service: LLMService,
                 max_steps=25):
        self.browser = browser
        self.profile = profile_data
        self.additional_info = additional_info
        self.llm_service = llm_service
        self.max_steps = max_steps
        self.current_step = 0
        self.action_history = []
        self.conversation_history = []  # Stores full LLM conversation

        self.prompt_builder = PromptBuilder(profile=profile_data, additional_info=additional_info)
        self.action_executor = ActionExecutor(browser)
        
        # Initialize with system prompt
        system_prompt = self.prompt_builder.build_system_prompt()
        self.conversation_history.append({"role": "system", "content": system_prompt})

    def execute_application_flow(self) -> bool:
        """Main workflow execution loop"""
        for step in range(1, self.max_steps + 1):
            self.current_step = step
            print(f"\n--- Step {step}/{self.max_steps} ---")
            
            if not self._process_current_state():
                return False
                
        return False  # Max steps reached

    def _process_current_state(self) -> bool:
        """Handle current application state"""
        # Get current page state
        current_url = self.browser.get_current_url()
        print("length of self.browser.get_page_source(): ",len(self.browser.get_page_source()))
        html = HTMLCleaner.clean(self.browser.get_page_source())
        print("cleaned html length: ",len(html))
        
        # Build user prompt
        user_prompt = self.prompt_builder.build_user_prompt(
            html=html[:settings.max_html_length],
            current_url=current_url,
            action_history=self.action_history[-5:]  # Last 5 actions
        )
        self.conversation_history.append({"role": "user", "content": user_prompt})
        
        # Get LLM guidance
        llm_response = self.llm_service.get_application_guidance(
            messages=self.conversation_history
        )

        print("llm_response: ",llm_response)

        # We don't want to keep track of the conversation
        self.conversation_history.pop()
        
        # Store assistant response in history
        self.conversation_history.append({"role": "assistant", "content": llm_response})
        
        # Parse response
        actions = LLMResponseParser.parse_response(llm_response)
        
        # Execute actions
        if not actions or self._is_completion(actions):
            return True  # Application complete
        
        print("executing actions")
        return self._execute_actions(actions)

    def _is_completion(self, actions: list) -> bool:
        return any(action.get("action") == "complete" for action in actions)

    def _execute_actions(self, actions: list) -> bool:
        """Execute parsed actions and update state"""
        print(f"actions are : {actions}\n")
        for action_dict in actions:
            print(f"action: {action_dict}\n")
            action = Action(
                action_type=action_dict.get("action"),
                locator=action_dict.get("locator"),
                value=action_dict.get("value")
            )
            
            print(f"action is {action}\n")
            # Add to action history
            self.action_history.append(action_dict)
            
            if not self.action_executor.execute(action):
                return False
                
            # Add wait after each action to allow page updates
            self.action_executor.execute(Action(action_type="wait", value="2"))
            print("action successfully executed !")
        return True