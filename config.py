from dotenv import load_dotenv
import os

load_dotenv()

def get_api_key():
    return os.getenv("OPENAI_API_KEY")
