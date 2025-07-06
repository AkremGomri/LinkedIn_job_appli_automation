import os
from openai import OpenAI
import json
from interfaces.llm_service import LLMService
from config import secrets

class OpenAIService(LLMService):
    def __init__(self, model="gpt-4.1-2025-04-14", temperature=0.1):
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=secrets.LLM_API_KEY)

    def get_application_guidance(self, prompt: str) -> list:
        try:
            print("get_application_guidance is getting executed")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a web automation expert. Analyze HTML and return JSON actions for Selenium. Use XPATH locators."},
                    {"role": "user", "content": prompt}
                ],
                # reasoning={"effort": "medium"},
                response_format={"type": "json_object"},
                temperature=self.temperature
            )
            content = response.choices[0].message.content
            print("content: ",content)
            return json.loads(content).get("actions", [])
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return []