import json
import time
import re
from interfaces.browser_adapter import BrowserAdapter
from interfaces.llm_service import LLMService
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class LLMApplicationGuide:
    def __init__(self, 
                 browser: BrowserAdapter, 
                 profile_data: dict, 
                 llm_service: LLMService,
                 max_steps=10):
        self.browser = browser
        self.profile = profile_data
        self.llm_service = llm_service
        self.max_steps = max_steps
        self.action_history = []
        
    def execute_application_flow(self):
        print(f"Starting application flow with max steps: {self.max_steps}")
        for step in range(1, self.max_steps + 1):
            print(f"\n--- Step {step}/{self.max_steps} ---")
            
            current_url = self.browser.get_current_url()
            html = self._clean_html(self.browser.get_page_source())
            
            prompt = self._build_prompt(html, current_url)
            actions = self.llm_service.get_application_guidance(prompt) 
            print("these are the actions returned by the LLM : ",actions)
            
            if not actions or actions == [{"action": "complete"}]:
                print("Application complete!")
                return True
                
            if not self.perform_llm_actions(actions):
                print("ooooooo")
                return False
            print("aaaaaaaaa")
        return False
                
    def _clean_html(self, html: str) -> str:
        """Clean HTML using BeautifulSoup"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unnecessary elements
        for tag in soup(['script', 'style', 'noscript', 'meta', 'link']):
            tag.decompose()
            
        # Simplify attributes
        for tag in soup.find_all(True):
            tag.attrs = {k: v for k, v in tag.attrs.items() 
                        if k in ['id', 'name', 'class', 'type', 'href', 'aria-label', 
                                 'data-testid', 'placeholder', 'for', 'role']}
        
        return str(soup.body) if soup.body else str(soup)[:20000]

    def _build_prompt(self, html: str, current_url: str) -> str:
        """Construct optimized prompt for LLM"""
        print("self.profile : ", self.profile)
        print("self.profile['personal_info']['email']: ", self.profile['personal_info']['email'])
        print("current_url: ", current_url)
        print("self.action_history: ", self.action_history)
        print("\n---------------------------------\n")
        print("len(html): ",len(html))
        print("html[:150000]: ",html[:150000])
        
        return f"""
            # Task: Help Selinium know next steps to complete job application using provided HTML
            ## User Profile
            {json.dumps(self.profile, indent=2)}

            ## Current Page
            URL: {current_url}
            Last {min(5, len(self.action_history))} actions:
            {self.action_history[-5:]}

            ## HTML Content (simplified)
            {html[:150000]}  # Truncated for token efficiency

            ## Instructions
            1. Analyze page and determine next action sequence (Determine if this page contains job application components, if it doesn't then locate a button or something to proceed to a next page).
            2. Identify elements relevant to job applications (Prioritize job application elements over navigation/login).
            3. Classify elements by priority:
            - P0: Application form inputs (resume, experience fields).
            - P1: Direct application actions ("Apply", "Submit Application").
            - P2: Application navigation ("Apply for this job").
            4. For text fields: Use profile data where applicable (for example if there is an input following a label containing a text "your email adress" where the response email adress is in User Profile section)
            5. For file uploads: Use 'write' with file path (ignore this for now)
            6. Return actions as JSON array

            ## Action Format (STRICT JSON ONLY)
            [
            {{
                "action": "click" | "write" | "send_keys" | "select" | "wait" | "complete",
                "locator": "XPATH string (REQUIRED for click/write/send_keys/select)",
                "value": "Only for write/send_keys/select/wait"
            }},
            ]

            ## Special Cases
            - Login pages: Look for "Apply as guest" links
            - Multi-page forms: Focus on current step
            - Required fields: Mark with 'required' in aria-label

            ## Response Examples
            Example 1 (Click):
            [{{"action": "click", "locator": "//button[contains(@aria-label, 'Apply')]"}}]

            Example 2 (Write):
            [{{"action": "write", "locator": "//input[@aria-label='Email Address']", "value": "{self.profile['personal_info']['email']}"}}]

            Example 3 (Send Keys):
            [{{"action": "send_keys", "locator": "//input[@id='phone']", "value": "TAB"}}]

            Example 4 (Complete):
            [{{"action": "complete"}}]

            ## Key Focus Areas
            0. Find and select elements by their uniqueness, so prioritize selection by XPATH using id for example
            1. Identify and complete all form fields with profile data
            2. Locate and click navigation buttons (Next, Continue, Submit)
            3. Handle file uploads using profile documents (ignore this for now)
            4. Detect and complete any required assessments
            5. Identify the final submission button

            ## Special Instructions
            - For file uploads: Use action "write" with the file path as value (ignore this for now)
            - For multi-page forms: Include "wait" actions between pages
            - For dropdowns: Use "select" with the visible option text
            - For checkboxes/radios: Use "click" on the input or associated label

            Return a list of json, only valid JSON, no additional text.
            """
    
    def perform_llm_actions(self, actions: list) -> bool:
        """ Execute all actions from LLM """
        print("-------------starting actions----------------")
        for action in actions:
            self._execute_single_action(action)
        print("finished all actions")
        return True


    def _execute_single_action(self, action: dict) -> bool:
        """Execute a single action from LLM"""
        print(f"Received action: {action}")
        action_type = action.get("action")
        print("action_type: ",action_type)
        locator_info = action.get("locator")
        print("locator_info: ",locator_info)
        value = action.get("value")
        print("value: ",value)
        print(f"Executing action: {action_type} with locator: {locator_info} and value: {value}")
        
        if not locator_info:
            print("Action missing locator")
            return False
            
        # by = f'By.{locator_info.get("by")}'
        by = By.XPATH
        try:
            if action_type == "click":
                print(f"Clicking element")
                element = self.browser.find_clickable((by, locator_info))
                print(f"Found element: ")
                element.click()
                print(f"Clicked")
                return True
                
            elif action_type == "write":
                print(f"Writing to element")
                element = self.browser.find_visible((by, locator_info))
                print(f"Found element: ")
                text = action.get("value", "")
                element.clear()
                print(f"Writing text: '{text}' to element")
                element.write_text(text)
                
                print(f"Wrote '{text}' to {by}={locator_info}")
                return True
                
            elif action_type == "select":
                print(f"Selecting in dropdown")
                element = self.browser.find_visible((by, locator_info))
                print(f"Found dropdown element: ")
                option_value = action.get("value", "")
                # Actual dropdown selection implementation would go here
                return True
                
            elif action_type == "wait":
                wait_time = action.get("time", 2)
                time.sleep(wait_time)
                return True
                
            elif action_type == "submit":
                print(f"Submitting form")
                element = self.browser.find_clickable((by, locator_info))
                print(f"Found submit element: ")
                element.click()
                print(f"Submitted via {by}={locator_info}")
                return True
                
            elif action_type == "finish":
                return True  # Terminate successfully
                
            print(f"Unknown action type: {action_type}")
            return False
        except Exception as e:
            print(f"Action execution failed: {action} - {str(e)}")
            return False