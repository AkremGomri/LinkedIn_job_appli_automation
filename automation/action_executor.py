import time
from dataclasses import dataclass
from typing import Optional
from interfaces.browser_adapter import BrowserAdapter
from selenium.webdriver.common.by import By
from pywinauto import Desktop
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

@dataclass
class Action:
    action_type: str  # 'click', 'write', 'select', 'wait', 'submit', 'complete'
    locator: Optional[str] = None
    value: Optional[str] = None

class ActionExecutor:
    def __init__(self, browser: BrowserAdapter):
        self.browser = browser
        
    def execute(self, action: Action) -> bool:
        """Execute a single browser action"""
        if not action.locator and action.action_type not in ["wait", "complete", "upload"]:
            return False
            
        try:
            if action.action_type == "click":
                return self._click(action.locator)
            elif action.action_type == "write":
                return self._write(action.locator, action.value)
            elif action.action_type == "upload":
                # self._click(action.locator)
                return self._upload_file(file_path=f"{PROJECT_ROOT / action.value}", title="Ouvrir") # title=ouvrir should change in the future. It should be passed as params.
            elif action.action_type == "select":
                return self._select(action.locator, action.value)
            elif action.action_type == "wait":
                wait_time = float(action.value) if action.value else 2
                time.sleep(wait_time)
                return True
            elif action.action_type == "submit":
                return self._click(action.locator)
            elif action.action_type == "complete":
                return True
            return False
        except Exception as e:
            print(f"Action execution failed: {action} - {str(e)}")
            return False

    def _click(self, locator: str) -> bool:
        element = self.browser.find_clickable((By.XPATH, locator))
        element.click()
        return True

    def _write(self, locator: str, value: str) -> bool:
        element = self.browser.find_visible((By.XPATH, locator))
        element.clear()
        element.write_text(value)
        return True

    def _select(self, locator: str, value: str) -> bool:
        # Implementation would go here
        return True
    
    def _upload_file(self, file_path, title="ouvrir"):
        print("file_path: ",file_path)
        escaped_path = f'"{file_path}"'
        
        dlg = Desktop().window(title=title)
        dlg["Edit"].type_keys(escaped_path)  # Send quoted path
        dlg["Ouvrir"].click()
        return True