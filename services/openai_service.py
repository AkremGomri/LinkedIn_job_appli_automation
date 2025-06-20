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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an assistant that helps users apply for jobs."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=self.temperature
            )
            content = response.choices[0].message.content
            return json.loads(content).get("steps", [])
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return []