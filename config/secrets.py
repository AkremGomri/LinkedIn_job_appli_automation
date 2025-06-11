import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

EMAIL = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")