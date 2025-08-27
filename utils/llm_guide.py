import json
from interfaces.browser_adapter import BrowserAdapter
from interfaces.llm_service import LLMService

from automation.html_cleaner import HTMLCleaner
from automation.action_executor import ActionExecutor, Action

from LLM.llm_prompt import PromptBuilder
from LLM.response_parser import LLMResponseParser

from config import settings

from config.logging_config import llm_automation_logger, llm_app_conv_logger, dual_logger

from utils.helpers import get_validated_pause_input
from utils.threading import execute_with_timeout

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
        llm_app_conv_logger.info(f'******************* Link : {self.browser.get_current_url()} *******************')
        llm_app_conv_logger.info(f'"""System: \n{system_prompt}')

    def execute_application_flow(self) -> bool:
        """Main workflow execution loop with timeout handling"""
        dual_logger.info(f"********************* new application automation for {self.browser.get_current_url()} ************************")
        for step in range(1, self.max_steps + 1):
            self.current_step = step
            llm_automation_logger.info(f"\n------------ Step {step}/{self.max_steps} --------------")
            
            executed_actions = self._process_current_state()

            feedback_msg = f"""Great job, actions are successfully executed by selenium, {"you should proceed with the job application."  if step != self.max_steps else "application is terminated !"}"""
            
            for response in executed_actions:
                print("in applicationOrchestrator :: execute_application_flow::executed_actions")
                print(response)
                print(response.get("action"))
                
                # Handle pause action with timeout
                if response.get("action").action_type == "pause":
                    reason = response.get("action").reason
                    llm_automation_logger.info("The application is paused and waiting for user interaction!")
                    
                    # Define input function for timeout handling
                    prompt = f"""\n[PAUSED] Reason: {reason}\n"
                            "Please resolve the issue then type:\n"
                            "  'solved' - If you completed the required action\n"
                            "  'continue' - To resume automation without changes\n"
                            "> """
                    user_instruction = get_validated_pause_input(prompt, 20)
                    
                    if user_instruction is None:
                        llm_automation_logger.info("Timeout waiting for user input. Terminating automation.")
                        return False
                    
                    llm_automation_logger.info(f"User responded with: {user_instruction}")
                    
                    # Process user response
                    if user_instruction == "solved":
                        feedback_msg = """{"feedback": "User resolved the issue manually. Continuing automation."}"""
                    elif user_instruction == "continue":
                        feedback_msg = """{"feedback": "Resuming automation after pause."}"""
                    else:
                        print(f"The app is not supposed to come here, too weird, user_instruction = '{user_instruction}'.")
                    
                    # Break after handling pause
                    
                
                # Handle terminate action
                if response.get("action").action_type == "terminate":
                    llm_automation_logger.info("Application terminated")
                    return True
                
                # Handle failed actions
                if response.get("status") == "Failed":
                    feedback_msg = f"""
                        Execution failed due to an error that occurred while processing the following action:

                            - action: {response.get("action")}
                            - error message: {response.get("message")}
                            - all executed actions: {executed_actions}

                        Please note:
                            - The 'status' attribute indicates whether an action was successfully executed (`Success`), failed (`Failed`), or was skipped due to a prior failure (`Not reached`).
                            - The 'message' attribute contains more details (the error if the status is Failed, What successfully got executed if status is success, and None if it wasn't reached).
                            - The 'action' attribute contains the instruction extracted by Selenium from the user's previous message.

                        Identify the action with `'status': False` to understand where the failure occurred.
                        """
                    break

            # Update conversation history
            llm_automation_logger.info(f"feedback_msg: {feedback_msg}")
            self.conversation_history.append({"role": "user", "content": feedback_msg})
            llm_app_conv_logger.info(f'User :\n{feedback_msg}"""')
        
        return False

    def _process_current_state(self) -> bool:
        """Handle current application state"""
        # Get current page state
        current_url = self.browser.get_current_url()
        llm_automation_logger.info(f"length of the page html source code: {len(self.browser.get_page_source())}")
        html = HTMLCleaner.clean(self.browser.get_page_source())
        llm_automation_logger.info(f"cleaned html length: {len(html)}")
        
        # Build user prompt
        user_prompt = self.prompt_builder.build_user_prompt(
            html=html[:settings.max_html_length],
            current_url=current_url,
            action_history=self.action_history  # Beware of how much you insert here !
        )
        self.conversation_history.append({"role": "user", "content": user_prompt})
        llm_app_conv_logger.info(f"""User: \n{user_prompt} """)

        # Get LLM guidance
        llm_response = self.llm_service.get_application_guidance(
            messages=self.conversation_history
        )

        # We don't want to keep track of the conversation
        self.conversation_history.pop()
        llm_app_conv_logger.info(f'Last message removed') 
        
        # Store assistant response in history
        self.conversation_history.append({"role": "assistant", "content": llm_response})
        llm_app_conv_logger.info(f'Assistant{llm_response} """')
        
        # Parse response
        actions = LLMResponseParser.parse_response(llm_response)
        llm_automation_logger.info(f"actions:\n%s", json.dumps(actions, indent=2))

        # Execute actions
        if not actions or self._is_completion(actions):
            return True  # Application terminate

        executed_actions = self._execute_actions(actions)

        return executed_actions

    def _is_completion(self, actions: list) -> bool:
        return any(action.get("action") == "terminate" for action in actions)

    def _execute_actions(self, actions: list) -> bool:
        """Execute parsed actions and update state"""
        executed_actions=[] #output

        for action_dict in actions:
            print("inside for loop")
            action = Action(
                action_type=action_dict.get("action_type"),
                locator=action_dict.get("locator"),
                value=action_dict.get("value"),
                reason=action_dict.get("reason")
            )

            # Add to action history
            self.action_history.append(action_dict)
            action_execution_result = self.action_executor.execute(action)
            executed_actions.append(action_execution_result)

            if action_execution_result["status"] == "Failed":
                llm_automation_logger.error(f"There is a problem with this action bellow : \n%s", action_execution_result)
                break # We can either break which means stop executing, or continue if we think that the rest of the actions are independent from this failed action.
                
            # Add wait after each action to allow page updates
            print("before self.action_executor.execute(Action(action_type='wait', value='2'))")
            self.action_executor.execute(Action(action_type="wait", value="2"))
            llm_automation_logger.info("Action successfully executed !")

        llm_automation_logger.info(f"\nexecuted_actions:\n%s", executed_actions)

        return executed_actions