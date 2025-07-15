import json
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.resolve()

class PromptBuilder:
    def __init__(self, profile: dict, additional_info: dict={}):
        self.profile = profile
        self.additional_info = additional_info

    def build_user_prompt(self, html: str, current_url: str, action_history: list) -> str:
        """Build user prompt with current context"""
        return f"""
            ## Current Page
            Recent actions: {action_history[-5:]}

            ## HTML Content
            {html[:150000]}

            Return ONLY valid JSON, no additional text.
            """
    
    def build_system_prompt(self) -> str:
        """Build the initial system prompt"""
        return f"""
        # Your role: Web automation expert helping automate job applications on LinkedIn
        # Task: Guide Selenium to complete job applications using provided HTML
        ## User Profile
        {json.dumps(self.profile, indent=2)}

        ## Additional Information
        {self.additional_info}
        Any doccument belonging to the user which you need to provide is located at {PROJECT_ROOT}/assets
        if the doccument is in english version then /eng should be added if it is in french then /fr
        for every job title from this list (data scientist, data engineer, llm engineer, machine learning engineer, software engineer, software developer) there is a folder with that name in camel case underwhich there are doccuments
        the name of the file is resume_Akrem_Gomri.pdf for a resume, and Motivation_Letter_Akrem_Gomri.pdf for a motivation letter

        for example, if you are looking for an english version resume for a data science post then this is the file path: {PROJECT_ROOT}/assets/eng/data_scientist/resume_Akrem_Gomri.pdf
        But if you are looking for a default resume (overlooking the job title) then this is the right file path: {PROJECT_ROOT}/assets/eng/resume_Akrem_Gomri.pdf

        ## Instructions
        1. Analyze page and determine next action sequence
        2. Identify elements relevant to job applications (prioritize form inputs > action buttons > navigation)
        3. For text fields: Use profile data where applicable
        4. Return actions as JSON object with "actions" array and "step_goal" string

        ## Action Format (STRICT JSON ONLY)
        {{
            "actions": [
                {{
                    "action": "click" | "write" | "send_keys" | "select" | "wait" | "complete",
                    "locator": "XPATH string (REQUIRED for click/write/send_keys/select)",
                    "value": "Only for write/send_keys/select/wait",
                    "reason": "Brief explanation of purpose"
                }}
            ],
            "step_goal": "Description of what these actions accomplish"
        }}

        ## Special Cases
        - Popups: if there are popus like accept cookies, then handle them first (by accepting) as a high priority before anything else. As they might block the process of the application.
        - Login pages: Look for "Apply as guest" links
        - Multi-page forms: Focus on current step
        - Required fields: Marked with 'required' in attributes

        ## Response Examples
        Example 1 (Click):
        {{
            "actions": [
                {{
                    "action": "click",
                    "locator": "//button[contains(@aria-label, 'Apply')]",
                    "reason": "Start application process"
                }}
            ],
            "step_goal": "Initiate job application"
        }}

        Example 2 (Complete):
        {{
            "actions": [
                {{"action": "complete"}}
            ],
            "step_goal": "Job application successfully completed"
        }}

        ## Key Focus Areas
        1. Complete all form fields with profile data
        2. Locate and click navigation buttons (Next, Continue, Submit)
        3. Identify final submission button
        4. Prioritize unique identifiers in XPATHs (id, data-testid)
        5. Prioritize handling blocking elements, like accept cookies popups, etc.

        ## Special Instructions
        - For dropdowns: Use "select" with visible option text
        - For checkboxes/radios: Use "click" on input or label
        - Include brief 'reason' for each action
        - Always include "step_goal" describing the purpose of the actions
        
        Return ONLY valid JSON, no additional text.
        """