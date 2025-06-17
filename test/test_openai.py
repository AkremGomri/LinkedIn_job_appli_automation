# test_openai.py
from services.openai_service import OpenAIService

service = OpenAIService()
test_prompt = "Return JSON with: [{'action':'wait','time':1},{'action':'finish'}]"
print(service.get_application_guidance(test_prompt))