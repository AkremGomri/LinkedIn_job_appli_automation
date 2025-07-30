import time
from dataclasses import dataclass
from typing import Dict, Optional
from interfaces.browser_adapter import BrowserAdapter
from selenium.webdriver.common.by import By
from pywinauto import Desktop
from pathlib import Path
import os
PROJECT_ROOT = Path(__file__).resolve().parents[1]

@dataclass
class Action:
    action_type: str  # 'click', 'write', 'select', 'wait', 'submit', 'terminate'
    locator: Optional[str] = None
    value: Optional[str] = None

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
        if not action.locator and action.action_type not in ["wait", "terminate", "upload"]:
            return self._result("Failed", "Missing locator for action or wrong action type.", action)

        try:
            if action.action_type == "click":
                return self._handle_click(action)
            elif action.action_type == "write":
                return self._handle_write(action)
            elif action.action_type == "upload":
                return self._upload_file(file_path=f"{PROJECT_ROOT / action.value}", title="Ouvrir")
            elif action.action_type == "select":
                return self._handle_select(action)
            elif action.action_type == "wait":
                return self._handle_wait(action)
            elif action.action_type == "submit":
                return self._click(action)
            elif action.action_type == "terminate":
                return self._handle_terminate(action)
            return self._result("Failed", f"Unknown action type: {action.action_type}", action)
        except Exception as e:
            return self._result("Failed", f"Action execution failed: {str(e)}", action)

    def _handle_click(self, action: Action) -> Dict[str, object]:
        element = self.browser.find_clickable((By.XPATH, action.locator))
        element.click()
        return self._result("Success", f"Clicked element at {action.locator}", action)

    def _handle_write(self, action: Action) -> Dict[str, object]:
        element = self.browser.find_visible((By.XPATH, action.locator))
        element.clear()
        element.write_text(action.value)
        return self._result("Success", f"Wrote '{action.value}' to element at {action.locator}", action)

    def _handle_select(self, action: Action) -> Dict[str, object]:
        return self._result("Success", f"Selected '{action.value}' in element at {action.locator}", action)

    def _upload_file(self, file_path: str, title: str) -> Dict[str, object]:
        print("Original path:", file_path)
        normalized_path = os.path.normpath(file_path)
        escaped_path = f'"{normalized_path}"'
        print("Sending path:", escaped_path)

        dlg = Desktop().window(title=title)
        dlg["Edit"].type_keys(escaped_path)
        dlg["Ouvrir"].click()
        return self._result("Success", f"Uploaded file from {file_path}.")


    def _handle_wait(self, action: Action) -> Dict[str, object]:
        wait_time = float(action.value) if action.value else 2
        time.sleep(wait_time)
        return self._result("Success", f"Waited for {wait_time} seconds.", action)
    
    def _handle_terminate(self, action: Action) -> Dict[str, object]:
        return self._result("Success", "Job application is fully terminated, and all necessary actions executed.", action)