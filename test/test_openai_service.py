import os
import unittest
from unittest.mock import MagicMock, patch
from services.openai_service import OpenAIService

class TestOpenAIService(unittest.TestCase):
    def setUp(self):
        os.environ["LLM_API_KEY"] = "test_api_key"
        self.service = OpenAIService()
        self.service.client = MagicMock()
        
    def test_get_application_guidance_success(self):
        # Mock response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"steps": [{"action": "click", "locator": {"by": "id", "value": "submit"}}]}'
        self.service.client.chat.completions.create.return_value = mock_response
        
        # Test
        result = self.service.get_application_guidance("Test prompt")
        self.assertEqual(result, [{"action": "click", "locator": {"by": "id", "value": "submit"}}])
        
    def test_get_application_guidance_failure(self):
        self.service.client.chat.completions.create.side_effect = Exception("API error")
        result = self.service.get_application_guidance("Test prompt")
        self.assertEqual(result, [])
        
if __name__ == '__main__':
    unittest.main()