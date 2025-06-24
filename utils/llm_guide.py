import json
import time
import re
from interfaces.browser_adapter import BrowserAdapter
from interfaces.llm_service import LLMService
from selenium.webdriver.common.by import By

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
        
    def execute_application_flow(self):
        print(f"Starting application flow with max steps: {self.max_steps}")
        step_count = 0
        
        while step_count < self.max_steps:
            step_count += 1
            print(f"\n--- Step {step_count}/{self.max_steps} ---")
            
            # Capture full page state
            current_url = self.browser.get_current_url()
            full_html = self.browser.get_page_source()
            
            # Extract focused HTML content
            focused_html = self._extract_relevant_content(full_html)
            print(f"Using focused HTML: {len(focused_html)} characters")
            
            # Get LLM guidance
            prompt = self._build_prompt(focused_html, current_url)
            actions = self.llm_service.get_application_guidance(prompt)
            
            if not actions:
                print("LLM returned no actions. Retrying...")
                time.sleep(2)
                continue
                
            print(f"Executing {len(actions)} actions")
            for action in actions:
                print(f"Executing: {action['action']} on {action['locator']['value']}")
                if not self._execute_action(action):
                    print("Action execution failed")
                    return False
                    
                if action.get("is_final_step", False):
                    print("Application completed successfully!")
                    return True
                    
        print("Max steps reached without completing application")
        return False

    def _extract_relevant_content(self, html: str) -> str:
        """Extract the most relevant parts of the HTML"""
        # Prioritize form content
        form_match = re.search(r'<form[\s\S]*?</form>', html, re.IGNORECASE)
        if form_match:
            return form_match.group(0)
            
        # Fallback to main content
        main_match = re.search(r'<main[\s\S]*?</main>', html, re.IGNORECASE)
        if main_match:
            return main_match.group(0)
            
        # Fallback to body content
        body_match = re.search(r'<body[\s\S]*?</body>', html, re.IGNORECASE)
        if body_match:
            return body_match.group(0)
            
        # Ultimate fallback
        return html[:10000]  # Truncate to 10k characters if all else fails

    def _build_prompt(self, html: str, current_url: str) -> str:
        """Construct the prompt for LLM with full HTML context"""
        return f"""
            ## Task Description
            You are controlling a web browser to complete a job application using the FULL HTML content provided below. 
            Guide the automation by returning JSON instructions.

            ## User Profile
            {json.dumps(self.profile, indent=2)}

            ## Current Page
            URL: {current_url}

            ## Full Page HTML
            {html}

            ## Required Response Format
            Return JSON with a "steps" key containing a list of action objects. Each action must have:
            - "action": "click"|"write"|"send_keys"|"select" . If you return send_keys, this function will be executed : def send_keys(self, keys): self.webelement.send_keys(keys), so use that function to hit enter for example, so the value will be Keys.ENTER or Keys.RETURN. And this function for write function : def write_text(self, text): self.clear(); self.webelement.send_keys(text), use it to write text in input fields.
            - "locator": {"value": "locator-value"} . This value should be a valid XPATH locator. Selinium will use this to find the element by XPATH.
            - "value": (only for write/send_keys) the text to enter or option to select
            - "time": (optional for wait) seconds to wait
            - "is_final_step": (optional) true if this completes application

            ## Locator Priority
            1. Use ID when available
            2. Use CSS selectors for precise targeting
            3. Use XPath only when necessary
            4. Prefer exact matches over partial matches

            ## Key Focus Areas
            1. Identify and complete all form fields with profile data
            2. Locate and click navigation buttons (Next, Continue, Submit)
            3. Handle file uploads using profile documents
            4. Detect and complete any required assessments
            5. Identify the final submission button

            ## Special Instructions
            - For file uploads: Use action "write" with the file path as value
            - For multi-page forms: Include "wait" actions between pages
            - For dropdowns: Use "select" with the visible option text
            - For checkboxes/radios: Use "click" on the input or associated label

            Return only valid JSON, no additional text.
        """
    
    def _execute_action(self, action: dict) -> bool:
        """Execute a single action from LLM"""
        print(f"Received action: {action}")
        action_type = action.get("action")
        locator_info = action.get("locator")
        print(f"Executing action: {action_type} with locator {locator_info}")
        
        if not locator_info:
            print("Action missing locator")
            return False
            
        by = f'By.{locator_info.get("by")}'
        value = locator_info.get("value")
        
        try:
            if action_type == "click":
                print(f"Clicking element: {by}={value}")
                element = self.browser.find_clickable((by, value))
                print(f"Found element: {element.tag_name} with text: {element.text}")
                element.click()
                print(f"Clicked: {by}={value}")
                return True
                
            elif action_type == "write":
                print(f"Writing to element: {by}={value}")
                element = self.browser.find_visible((by, value))
                print(f"Found element: {element.tag_name} with text: {element.text}")
                text = action.get("value", "")
                element.clear()
                print(f"Writing text: '{text}' to element")
                element.write_text(text)
                
                print(f"Wrote '{text}' to {by}={value}")
                return True
                
            elif action_type == "select":
                print(f"Selecting in dropdown: {by}={value}")
                element = self.browser.find_visible((by, value))
                print(f"Found dropdown element: {element.tag_name} with text: {element.text}")
                option_value = action.get("value", "")
                # Actual dropdown selection implementation would go here
                return True
                
            elif action_type == "wait":
                wait_time = action.get("time", 2)
                time.sleep(wait_time)
                return True
                
            elif action_type == "submit":
                print(f"Submitting form: {by}={value}")
                element = self.browser.find_clickable((by, value))
                print(f"Found submit element: {element.tag_name} with text: {element.text}")
                element.click()
                print(f"Submitted via {by}={value}")
                return True
                
            elif action_type == "finish":
                return True  # Terminate successfully
                
            print(f"Unknown action type: {action_type}")
            return False
        except Exception as e:
            print(f"Action execution failed: {action} - {str(e)}")
            return False