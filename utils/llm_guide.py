import json
import time
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
        max_iterations = self.max_steps
        print(f"Max application iterations: {max_iterations}")
        
        for iteration in range(max_iterations):
            print(f"\n--- Iteration {iteration+1}/{max_iterations} ---")
            print("Capturing current page state...")
            
            # Always capture full current state
            current_url = self.browser.get_current_url()
            full_html = self.browser.get_page_source()
            
            # Extract body content
            body_html = self._extract_body_content(full_html)
            print(f"Body content length: {len(body_html)} characters")
            
            # Apply sliding window to body content
            window_size = 5000
            window_start = iteration * window_size
            window_end = window_start + window_size
            
            # Wrap around if we exceed body length
            if window_start >= len(body_html):
                window_start = window_start % len(body_html)
                window_end = window_start + window_size
            
            # Extract windowed segment
            html_segment = body_html[window_start:window_end]
            print(f"Using segment {window_start}-{min(window_end, len(body_html))} ({len(html_segment)} chars)")
            
            # Get LLM guidance
            prompt = self._build_prompt(html_segment, current_url)
            actions = self.llm_service.get_application_guidance(prompt)
            
            if not actions:
                print("No valid actions returned. Continuing to next segment.")
                # Continue to next iteration/window position
                continue
                
            # Execute all returned actions
            for action in actions:
                print(f"Executing: {action['action']} on {action['locator']['value']}")
                if not self._execute_action(action):
                    print("Action execution failed")
                    break
                    
            # Check completion status
            if any(action.get("is_final_step", False) for action in actions):
                print("Application completed successfully!")
                return True
                
        print("Max iterations reached without completing application")
        return False

    def _extract_body_content(self, html: str) -> str:
        """Extract content within <body> tags"""
        start_tag = "<body"
        end_tag = "</body>"
        
        start_idx = html.find(start_tag)
        if start_idx == -1:
            return html  # Fallback to full HTML if no body found
        
        # Find the actual start of content (after opening tag)
        content_start = html.find(">", start_idx) + 1
        
        # Find body end
        end_idx = html.find(end_tag, content_start)
        if end_idx == -1:
            return html[content_start:]  # Return everything after body start
        
        return html[content_start:end_idx]
  
    def _build_prompt(self, html: str, current_url: str) -> str:
        """Construct the prompt for LLM"""
        return f"""
                ## Task Description
                You are controlling a web browser to complete a job application. Guide the automation by returning JSON instructions.

                ## User Profile
                {json.dumps(self.profile, indent=2)}

                ## Current Page
                URL: {current_url}

                ## Page HTML (truncated to 5000 chars)
                {html}

                ## Required Response Format
                Do not give responses with Markdown formatting, just return the json as requested.
                Return JSON with a "steps" key containing a list of action objects. Each action must have:
                - "action": "click"|"write"|"select"|"wait"|"submit"|"finish"
                - "locator": {{"by": "XPATH"|"ID"|"LINK_TEXT"|"PARTIAL_LINK_TEXT"|"NAME"|"CSS_SELECTOR"|"TAG_NAME"|"CLASS_NAME", "value": "locator-value"}}
                - "value": (only for write/select) the text to enter or option to select
                - "time": (optional for wait) seconds to wait
                - "is_final_step": (optional) true if this completes application

                ## Locator Examples
                - XPath: {{"by": "XPATH", "value": "//button[contains(text(),'Next')]"}}
                - by id: {{"by": "ID", "value": "first-name"}}
                - by Text contain: {{"by": "XPATH", "value": "//*[contains(text(), 'part of text')]"}}
                - by CSS: {{"by": "CSS_SELECTOR", "value": "input[name='email']"}}

                ## Current Instructions
                Analyze the HTML and determine the next steps to progress the application. Focus on:
                1. Filling personal information from the profile
                2. Uploading documents if requested
                3. Answering application questions
                4. Navigating through multi-page forms
                5. Submitting the final application

                ## Additional information
                - The html you got is one chunk of a series of chunks constituting the whole html of the page. Only answear this part, you will be asked to give your final response of the action list at the end after the processing of the last chunk.
                - The locators you are using are values which are going to be passed to a selinium function as parameters. So take that into account when generating a locator.
                - The order of priority of locators is as the order in which they are written above. The highest priority is XPATH, then ID, then LINK_TEXT, and so on.
                - When Selecting elements using locator, prioritise the selectors which make sure the selection is unique. And also be specific about the element you are selecting such that for example you prioritize exact text matching over contains text matching.
                - What you are given might, or might not contain what you are looking for, so don't hesitate to return nothing from time to times.

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
            
        by = locator_info.get("by")
        value = locator_info.get("value")
        
        try:
            if action_type == "click":
                print(f"Attempting to click element: {by}={value}")
                element = self.browser.find_clickable((by, value))
                print(f"Found element: {element.tag_name} with text: {element.text}")
                element.click()
                print(f"Clicked: {by}={value}")
                return True
                
            elif action_type == "write":
                print(f"Attempting to write to element: {by}={value}")
                element = self.browser.find_visible((by, value))
                print(f"Found element: {element.tag_name} with text: {element.text}")
                text = action.get("value", "")
                element.clear()
                print(f"Writing text: '{text}' to element")
                element.write_text(text)
                
                print(f"Wrote '{text}' to {by}={value}")
                return True
                
            elif action_type == "select":
                print(f"Attempting to select option in dropdown: {by}={value}")
                element = self.browser.find_visible((by, value))
                print(f"Found dropdown element: {element.tag_name} with text: {element.text}")
                option_value = action.get("value", "")
                # Implement dropdown selection logic
                # Example: Select(element).select_by_visible_text(option_value)
                print(f"Selected '{option_value}' in {by}={value}")
                return True
                
            elif action_type == "wait":
                wait_time = action.get("time", 2)
                time.sleep(wait_time)
                print(f"Waited {wait_time} seconds")
                return True
                
            elif action_type == "submit":
                print(f"Attempting to submit form: {by}={value}")
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