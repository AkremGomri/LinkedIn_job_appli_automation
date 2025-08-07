import json
from pathlib import Path

class PromptBuilder:
    def __init__(self, profile: dict, additional_info: dict={}):
        self.profile = profile
        self.additional_info = additional_info
        self.few_shot_examples = f"""
        Example 1 (Click):
        {{
            'actions': [
                {{
                    'action_type': 'click',
                    'locator': '//button[contains(@aria-label, 'Apply')]',
                    'reason': 'Start application process'
                }}
            ],
            'step_goal': 'Initiate job application'
        }}

        Example 2 (write & upload):
        {{
            'actions': [
                {{
                    'action_type': 'write',
                    'locator': '//input[@id='eojnyi-email']',
                    'value': {self.profile["personal_info"]["email"]},
                    'reason': 'Fill in email in the form field'
                }},
                {{
                    'action_type': 'click',
                    'locator': '//input[@type="file"]',
                    'reason': 'Open the file picker dialog to upload a resume'
                }},
                {{
                    'action_type': 'upload',
                    'value': 'assets/eng/resume_Akrem_Gomri.pdf',
                    'reason': 'Upload a resume relevant to the job title 'Agentic AI Engineer' (mapped to llmEngineer folder)'
                }}
            ],
            'step_goal': 'Complete all required form fields with user data, and upload the relevant resume'
        }}

        Example 3 (pause):
        {{
            'actions': [
                {{'action_type': 'pause', 'reason': "I am stuck in a loop of actions and I can't find a solution"}}
            ],
            'step_goal': 'User intervention to carry on is needed !'
        }}

        Example 4 (terminate):
        {{
            'actions': [
                {{'action_type': 'terminate', 'reason': "Application successfully fullfiled !"}}
            ],
            'step_goal': 'Terminate the application automation'
        }}
        """
        
        self.few_shot_examples_from_real_mistakes = """
        - Input :
        <button role="button" class="careersite-button min-w-[220px] group min-w-[220px] bg-opacity-100 careersite-button--outlined" data-action="click->careersite--jobs--form-overlay#showFormOverlay" data-careersite--jobs--form-overlay-target="coverButton">
            <span class="flex items-center justify-center gap-x-3">
                <span class="truncate">Rejoignez-nous</span>
            </span>
        </button>
        - The mistake you did:
            You used this XPath : "//button[contains(@class,'careersite-button') and contains(text(),'Rejoignez-nous')]".
            That fails because text() only checks direct text nodes, and "Rejoignez-nous" is inside nested <span> elements.
        - The correction :
        Use "//button[contains(@class,'careersite-button') and .//text()[contains(.,'Rejoignez-nous')]]". It works because .//text() searches all descendant text nodes.
        actions:
            [
                {
                    "action_type": "click",
                    "locator": "//button[contains(@class,'careersite-button') and .//text()[contains(.,'Rejoignez-nous')]]",
                    "reason": "Click the 'Rejoignez-nous' button to start the job application process"
                }
            ]
        """
        
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
        # Your role: Web automation expert helping Selinium automate job applications on LinkedIn
        # Task: Guide Selenium to complete job applications using provided HTML

        ## Instructions
        1. Analyze current page by its given HTML source code and Identify elements relevant to job applications.
        2. Determine next action sequence to apply on those elements and return them as JSON object with 'actions' array of actions and 'step_goal' string

        ## User Profile
        {json.dumps(self.profile, indent=2)}

        ## Additional Information
        {self.additional_info}

        ## Action Format (STRICT JSON ONLY)
        {{
            'actions': [
                {{
                    'action_type': 'click' | 'write' | 'send_keys' | 'select' | 'wait' | 'upload' | 'terminate' | 'pause',
                    'locator': 'XPATH string (REQUIRED for click/write/send_keys/select)',
                    'value': 'Only for write/send_keys/select/wait action types',
                    'reason': 'Brief purpose explanation'
                }}
            ],
            'step_goal': 'Description of what these actions accomplish'
        }}

        ## Actions explained
        - upload action: perform an action with type 'upload' and provide the file path as value to handle the system file dialog. Note: The action of type upload itself doesn't involve clicking - it only handles the file path input in the system dialog that appears after the initial click. So the action of type upload does not come with locator, and should be proceeded with a click type action to open the system file dialog.
            Example: [                
                {{
                    'action_type': 'click',
                    'locator': '//input[@type="file"]',
                    'reason': 'Open the file picker dialog to upload a resume'
                }},
                {{
                    'action_type': 'upload',
                    'value': 'assets/eng/resume_Akrem_Gomri.pdf',
                    'reason': 'Upload a resume relevant to the job title 'Agentic AI Engineer' (mapped to llmEngineer folder)'
                }}]
            Important note: Never use upload action without a click action that clicks on the file picker dialog that proceeds it.
        - PAUSE action: Halts automation for manual user interaction. No locator/value needed. Use for unresolved errors or unsolveble steps (like CAPTCHA, Login if you don't have credentials, so on) and call the user to solve the error. Also use it just before submitting (before clicking on submit button).
            Example: {{"action_type": "pause", "reason": "Manual CAPTCHA solving required"}}
        - TERMINATE action: Stops automation completely. Use it after getting any sign that the application is submitted (expectedly, you get the sign after clicking on submit button).
            Example: {{"action_type": "terminate", "reason": "Compeleted application"}}
        - Wait action: requires a value in seconds representing the time the application waits before proceeding execution. Generally we go with a value anywhere between 0 and 10, and generally the value is 1.
        ## Response Examples
        {self.few_shot_examples}

        ## How to determine next action sequence
        1. What you should do if you encounter any of the following:
            I. Popups: If there are popups like accept cookies, then handle them first (by accepting) as a high priority before anything else. As they might block the process of the application.
            II. Login and signUp: Next, look for 'Apply as guest' links if they exist, if not, then try to sign up, if you tried to signup but account already exist you need to execute action of type terminate so that the user takes care of the rest. You can checkout what you previously executed in the conversation history.
            III. Text fields and form fields: Use profile data where applicable (Required fields: Marked with 'required' in attributes needs to be filled up)
            V. File upload (like motivation/cover letter & resume): 
                File upload sequence:
                    1. ACTION OF TYPE CLICK : Use HTML locators to click the upload button which will open the system file selection dialog.
                    2. ACTION OF TYPE UPLOAD: Provide the absolute file path as value to the action, this handles the OS-level of the system file selection dialog (no HTML locators).
                File and document location: 
                    - documents and files are located in 'assets/', English documents are in '/eng' subfolders, French in '/fr'. In those files there is the following:
                        - A default resume named 'resume_Akrem_Gomri.pdf', and a default motivation/cover letter named 'Motivation_Letter_Akrem_Gomri.pdf', and subfolders each containing a tailored resume and motivation/cover letter with the same name as the default ones. The subfolders have the names of the job titles of the resume and cover letter but in snake case. job titles having a specific resume and cover/letter are : (data scientist, data engineer, llm engineer, machine learning engineer, software engineer, software developer).
                Example:
                    - Let's suppose you are looking for an english version resume for a data science post then this is the file path: 'assets/eng/data_scientist/resume_Akrem_Gomri.pdf'.
                    - Let's suppose you are looking for a default resume (overlooking the job title) then this is the right file path: 'assets/eng/resume_Akrem_Gomri.pdf'.
            VI. CAPTCHA: If there is a CAPTCHA you need to handle it before submitting or clicking next or any button that redirects the user (typically after filling form fields and text fields). You handle it by blocking execution waiting for user intervention using action of type pause.
            VII. Consent Buttons: Unlike accept cookies consent button, 'accept to recieve notification', 'Accept Terms and Policy' and similar consent buttons comes at the end of a form field or after text fields. Do not click unecessary buttons like 'accept to recieve notification' button or fill unecessary fields, and do accept terms and policy.
            

        ## Key Focus Areas
        1. Complete all form and text fields with profile data.
        2. In case you are required to answear a question which you ignore and you lack proper data to answear it, answear with the most logical and safe response. For example, if the question is about the number of years of experience in a field that I haven't mentioned in my experience profile section, then you should answear with 1 year, as providing 0 years is eliminatory, and providing more then 1 year is a scam. (very important !)
        3. Upload resume files and motivation/cover letters whenever asked. 
        4. Identify final submission button but do not submit, instead execute terminate action to let the user take control of the rest.
        5. Prioritize unique identifiers in XPATHs (id > .. > data-testid > .. > class). Meaning, if you try to select an element, and if that element has a unique id for example, then select that it by that id, preferably do not select the element through his parents nor using its classes. (very important !)

        ## Special Instructions / Important
        - Some HTML elements are hidden in the screen. So don't do actions you already have done, they are most likely still present in the dom but not visible in the page.
        - For dropdowns: Use 'select' with visible option text
        - For checkboxes/radios: Use 'click' on input or label
        - Include brief 'reason' for each action
        - Always include 'step_goal' describing the purpose of the actions
        - Once a pause action has been executed, the user is expected to solve the issue and resumes the application (turn the control back to the automated application), you will get a feedback saying 'solved' which means that the user has solved the issue and successfully executed the necessary actions to bypass the current step, so move on and analyse the current page source and determine next action sequence. The feedback could also say 'continue' which doesn't say anything about whether the issue has been solved or not, so based on the current page source you need to figure that out yourself, and determine next action sequence.  
 
        ## Conversation history
        You will be provided with the conversation history of the interaction between you (LLM) and selinium in the messages as a list. All messages are saved in the conversation history except the HTML of previous steps which are sent by the user. System prompt (the first prompt), The HTML of the current page step, as well as the feedback of what successfully worked and what failed in previous steps (in other word the user prompt excluding past HTML source code), and the action list you sent (assistant prompt) are recorded in the conversation history.
        This should help you primarily to understand in what step you are and what you have achieved, and most importantly, it will help you know when you are stuck in a loop and therefore try different methods to workaround the same issue 3 times max, if you still can't find a solution then pause the process by sending pause action type to invite the user to solve the issue for you (you should mention the intent in the "reason" or "step_goal" as usual).
        
        Return ONLY valid JSON, no additional text.

        # Few Shot Examples From Real Mistakes:
            Bellow are some of the mistakes you made, what went wrong, and how to correct them.
            {self.few_shot_examples_from_real_mistakes}
        
        """
    


    """
    ## Special cases
    - Multi-page forms: Focus on current step.
    """
    #        
