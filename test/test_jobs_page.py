import unittest
from unittest.mock import MagicMock
from pages.jobs_page import JobsPage
from interfaces.browser_adapter import BrowserAdapter

class TestJobsPage(unittest.TestCase):
    def setUp(self):
        self.mock_browser = MagicMock(spec=BrowserAdapter)
        self.jobs_page = JobsPage(self.mock_browser)
        
    def test_apply_to_job_easy_apply(self):
        # Mock elements
        mock_button = MagicMock()
        mock_button.get_attribute.return_value = "Easy Apply to Company"
        self.mock_browser.find_clickable.return_value = mock_button
        
        # Mock handler
        with unittest.mock.patch('pages.jobs_page.EasyApplyHandler') as mock_handler:
            mock_handler.return_value.handle.return_value = True
            result = self.jobs_page.apply_to_job()
            self.assertTrue(result)
            
    def test_apply_to_job_regular_apply(self):
        # Mock elements
        mock_button = MagicMock()
        mock_button.get_attribute.return_value = "Apply to Company"
        self.mock_browser.find_clickable.return_value = mock_button
        
        # Mock handler
        with unittest.mock.patch('pages.jobs_page.RegularApplyHandler') as mock_handler:
            mock_handler.return_value.handle.return_value = True
            result = self.jobs_page.apply_to_job()
            self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()