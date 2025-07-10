import os
import json
import requests
from interfaces.llm_service import LLMService
from config import secrets

class DeepSeekService(LLMService):
    def __init__(self, model="deepseek-chat", temperature=0.1):
        self.model = model
        self.temperature = temperature
        self.api_key = secrets.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def get_application_guidance(self, prompt: str) -> list:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert web automation assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "response_format": {"type": "json_object"}
            }
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content).get("steps", [])
        except Exception as e:
            print(f"DeepSeek API error: {e}")
            return []