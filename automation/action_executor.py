import json
import time
from dataclasses import dataclass
from typing import Dict, Optional
from interfaces.browser_adapter import BrowserAdapter
from selenium.webdriver.common.by import By
from pywinauto import Desktop
from pathlib import Path
import os

from config.logging_config import llm_automation_logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]

@dataclass
class Action:
    action_type: str  # 'click', 'write', 'select', 'wait', 'submit', 'terminate', 'pause'
    locator: Optional[str] = None
    value: Optional[str] = None
    reason: str = ""

    def to_dict(self):
        return {"action_type": self.action_type, "locator": self.locator, "value": self.value, "reason": self.reason}

class ActionExecutor:
    def __init__(self, browser: BrowserAdapter):
        self.browser = browser

    def _result(self, status: bool, message: str, action: Optional[Action] = None) -> Dict[str, object]:
        return {
            "status": status,
            "message": message,
            "action": action
        }
        
    def execute(self, action: Action) -> dict:
        """Execute a single browser action"""

        llm_automation_logger.info(f"executing action:\n%s", action)
        try:
            exec(action)
        except Exception as e:
            return self._result("Failed", str(e), action)
        return self._result("Success", "", action)
    #     llm_automation_logger.info(f"executing action:\n%s", json.dumps(action.to_dict(), indent=2))
    #     if not action.locator and action.action_type not in ["wait", "terminate", "upload", "pause"]:
    #         return self._result("Failed", "Missing locator for action or wrong action type.", action)

    #     try:
    #         if action.action_type == "click":
    #             return self._handle_click(action)
    #         elif action.action_type == "write":
    #             return self._handle_write(action)
    #         elif action.action_type == "upload":
    #             return self._upload_file(file_path=f"{PROJECT_ROOT / action.value}", title="Ouvrir", action=action)
    #         elif action.action_type == "select":
    #             return self._handle_select(action)
    #         elif action.action_type == "wait":
    #             return self._handle_wait(action)
    #         elif action.action_type == "submit":
    #             return self._click(action)
    #         elif action.action_type == "terminate":
    #             return self._handle_terminate(action)
    #         elif action.action_type == "pause":
    #             return self._handle_pause(action)
    #         return self._result("Failed", f"Unknown action type: {action.action_type}", action)
    #     except Exception as e:
    #         return self._result("Failed", f"Action execution failed: {e}", action)

    # def _handle_click(self, action: Action) -> Dict[str, object]:
    #     element = self.browser.find_element((By.XPATH, action.locator))
    #     element.click()
    #     return self._result("Success", f"Clicked element at {action.locator}", action)

    # def _handle_write(self, action: Action) -> Dict[str, object]:
    #     element = self.browser.find_element((By.XPATH, action.locator))
    #     element.clear()
    #     element.write_text(action.value)
    #     return self._result("Success", f"Wrote '{action.value}' to element at {action.locator}", action)

    # def _handle_select(self, action: Action) -> Dict[str, object]:
    #     return self._result("Success", f"Selected '{action.value}' in element at {action.locator}", action)

    # def _upload_file(self, file_path: str, title: str, action: Action) -> Dict[str, object]:
    #     normalized_path = os.path.normpath(file_path)
    #     escaped_path = f'"{normalized_path}"'

    #     dlg = Desktop().window(title=title)
    #     dlg["Edit"].set_text(escaped_path)
    #     time.sleep(2)
    #     dlg["Ouvrir"].click()
    #     return self._result("Success", f"Uploaded file from {file_path}.", action)


    # def _handle_wait(self, action: Action) -> Dict[str, object]:
    #     wait_time = float(action.value) if action.value else 2
    #     time.sleep(wait_time)
    #     return self._result("Success", f"Waited for {wait_time} seconds.", action)
    
    # def _handle_terminate(self, action: Action) -> Dict[str, object]:
    #     return self._result("Success", "Job application is fully terminated, and all necessary actions executed.", action)
    
    # def _handle_pause(self, action: Action) -> Dict[str, object]:
    #     return self._result("Success", "The job application process is paused to allow the user temporary control. Waiting for the user to press Enter to return control to the application and continue.", action)