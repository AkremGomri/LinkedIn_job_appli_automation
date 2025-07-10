import os
from typing import List, Dict
from openai import OpenAI
import json
from interfaces.llm_service import LLMService
from config import secrets

class OpenAIService(LLMService):
    def __init__(self, model="gpt-4.1-mini", temperature=0.1):
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=secrets.LLM_API_KEY)


    def get_application_guidance(self, messages: List[Dict]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return '{"actions": []}'
        
    # def reset_conversation(self):
    #     self.conversation_history = [
    #         {"role": "system", "content": "You are a web automation expert..."}
    #     ]