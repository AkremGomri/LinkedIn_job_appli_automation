import json
import re
from typing import List, Dict

class LLMResponseParser:
    @staticmethod
    def parse_response(response: str) -> List[Dict]:
        """Parse LLM response and extract actions list"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return []
                
            response_json = json.loads(json_match.group(0))
            
            # Extract actions array from the response
            if "actions" in response_json and isinstance(response_json["actions"], list):
                return response_json["actions"]
                
            return []
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Failed to parse LLM response: {str(e)}")
            return []